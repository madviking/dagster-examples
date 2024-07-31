import gzip
import os
import pickle
from datetime import datetime

from dagster import job, op, get_dagster_logger
from google.cloud import storage
import mysql.connector
import csv
from io import StringIO, BytesIO

from app.resources.mysql import MySQLResource
from ep.ep.query.query_base import QueryBase

@op
def fetch_data_from_mysql():
    obj = QueryBase()
    query = "SELECT * FROM users"
    return obj.fetch_query_with_column_names(query,True)

@op
def write_to_gcs(context, data):
    column_names, rows = data
    client = storage.Client()
    bucket_name = 'test.dagster.east.fi'
    destination_blob_name = 'users_data.csv'

    # Create a CSV file in memory
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(column_names)  # Write header
    writer.writerows(rows)  # Write data

    # Upload CSV file to GCS
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(csv_file.getvalue(), content_type='text/csv')

    context.log.info(f'File written to {bucket_name}/{destination_blob_name}')
    return f'File written to {bucket_name}/{destination_blob_name}'

@op
def sql_backup_to_gcs(data, source_db: MySQLResource):
    client = storage.Client()
    db_name = source_db.get_name()
    bucket_name = 'backups.east.fi'

    # day name (mon,tue, wed, etc)
    day_name = datetime.now().strftime('%a')
    month = datetime.now().strftime('%Y-%m')
    day = datetime.now().strftime('%d')
    destination_blob_name = f'{db_name}/{day_name}.gzip'

    # save temporary file to disk
    dump_file = open('data.sql', 'wb')
    pickle.dump(data, dump_file)
    file = open('data.sql', 'rb')

    # Compress the serialized data using gzip
    gzip_file = BytesIO()
    with gzip.GzipFile(fileobj=gzip_file, mode='wb') as f:
        f.write(file.read())

    gzip_file.seek(0)  # Move to the beginning of the BytesIO object
    # Upload the gzip file to GCS
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(gzip_file, content_type='application/octet-stream')

    if day == '15':
        # Create a new folder for the month
        blob = bucket.blob(f'{db_name}/{month}/')
        blob.upload_from_string('', content_type='application/octet-stream')

    # Clean up
    dump_file.close()
    os.remove('data.sql')

    logger = get_dagster_logger()
    logger.info(f'File written to {bucket_name}/{destination_blob_name}')
    return f'File written to {bucket_name}/{destination_blob_name}'

