from dagster import sensor, RunRequest
import mysql.connector
from datetime import datetime, timedelta
from app.ops.gcs_file_write import gcs_job  # Import the job

# Define a function to connect to the MySQL database and check for new records
def check_for_new_records():
    conn = mysql.connector.connect(
        host="local_mysql_container",  # Ensure this matches your service name in docker-compose
        user="root",
        password="",
        database="database2"
    )
    cursor = conn.cursor()
    # Assuming there's a timestamp column to check for new records
    one_month_ago = datetime.now() - timedelta(days=30)
    query = "SELECT COUNT(*) FROM users WHERE your_timestamp_column > %s"
    cursor.execute(query, (one_month_ago,))
    result = cursor.fetchone()
    conn.close()
    return result[0] > 0  # Return True if new records exist, False otherwise

# Define the sensor
@sensor(job=gcs_job)  # Ensure this matches the job you want to trigger
def mysql_sensor(context):
    if check_for_new_records():
        yield RunRequest(run_key=None)
