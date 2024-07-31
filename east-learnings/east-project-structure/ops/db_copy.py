import mysql.connector
from MySQLdb import IntegrityError
from dagster import op, Out, In, get_dagster_logger

# Assuming Database2ProductionResource and Database2LocalResource are defined elsewhere
from app.resources.mysql import Database2ProductionResource, Database2LocalResource

logger = get_dagster_logger()

"""
General DB sync ops for moving entire databases around. Intended to be used with Mysql.
"""
@op(required_resource_keys={"source_db"}, out=Out())
def fetch_data_from_source_db(context):
    source_conn = context.resources.source_db.get_connection()
    cursor = source_conn.cursor()

    # Fetch tables
    cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
    tables = cursor.fetchall()

    # Fetch views
    cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
    views = cursor.fetchall()

    data = {}

    # Process tables
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()

        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        create_table_query = cursor.fetchone()[1]
        data[f"{table_name}_create_query"] = create_table_query

        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()

        # Convert rows to list of dictionaries with column names as keys
        column_names = [col[0] for col in columns]
        data[table_name] = [dict(zip(column_names, row)) for row in rows]

        # Store column types for setting default values
        data[f"{table_name}_column_types"] = {col[0]: col[1] for col in columns}

    # Process views
    for view in views:
        view_name = view[0]
        cursor.execute(f"SHOW CREATE VIEW `{view_name}`")
        create_view_query = cursor.fetchone()[1]
        data[f"{view_name}_create_view"] = create_view_query

    cursor.close()
    source_conn.close()
    return data

@op(required_resource_keys={"target_db"}, ins={"data": In()})
def load_data_to_target_db(context, data):
    target_conn = context.resources.target_db.get_connection()
    cursor = target_conn.cursor()

    cursor.execute("SET SESSION sql_mode = 'NO_ENGINE_SUBSTITUTION'")
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")

    # First, drop all existing tables and views
    cursor.execute("SHOW FULL TABLES")
    all_objects = cursor.fetchall()
    for obj in all_objects:
        obj_name = obj[0]
        obj_type = obj[1]
        if obj_type == 'BASE TABLE':
            cursor.execute(f"DROP TABLE IF EXISTS `{obj_name}`")
        elif obj_type == 'VIEW':
            cursor.execute(f"DROP VIEW IF EXISTS `{obj_name}`")

    # Recreate tables and insert data
    for item, content in data.items():
        if item.endswith('_create_query'):
            table_name = item[:-13]  # Remove '_create_query'
            cursor.execute(content)

            if table_name in data:
                rows = data[table_name]
                column_types = data.get(f"{table_name}_column_types", {})
                if rows:
                    for row in rows:
                        for col, value in row.items():
                            if value is None:
                                col_type = column_types.get(col, "").lower()
                                if "int" in col_type or "decimal" in col_type or "float" in col_type:
                                    row[col] = 0
                                elif "varchar" in col_type or "text" in col_type:
                                    row[col] = ""
                                elif "json" in col_type:
                                    row[col] = "{}"
                                else:
                                    row[col] = "default"  # Set a generic default for other types

                        columns = ", ".join([f"`{col}`" for col in row.keys()])
                        placeholders = ", ".join(["%s"] * len(row))
                        insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
                        try:
                            cursor.execute(insert_query, list(row.values()))
                        except IntegrityError as e:
                            context.log.error(f"IntegrityError for {table_name}: {e}")
                        except Exception as e:
                            context.log.error(f"Error for {table_name}: {e}")

        elif item.endswith('_create_view'):
            cursor.execute(content)

    target_conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    cursor.close()
    target_conn.close()
