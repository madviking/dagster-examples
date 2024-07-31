import os

import mysql.connector
from MySQLdb import IntegrityError
from dagster import op, job, graph, Out, In, get_dagster_logger, graph_asset, schedule, ScheduleEvaluationContext, \
    RunRequest

from app.ops.db_copy import fetch_data_from_source_db, load_data_to_target_db
from app.ops.gcs_file_write import sql_backup_to_gcs
from app.resources.mysql import Database2ProductionResource, Database2LocalResource, database2_production_resource, \
    database2_local_resource, database1_production_resource, database1_local_resource, database1_staging_resource, \
    database2_staging_resource, database3_production_resource, database3_local_resource, database3_staging_resource

import mysql.connector
from dagster import asset, Definitions, ResourceDefinition

# Assuming Database2ProductionResource and Database2LocalResource are defined elsewhere
from app.resources.mysql import Database2ProductionResource, Database2LocalResource

logger = get_dagster_logger()

"""
Entire databases assets and jobs for moving databases around.
"""

###############
#### DATABASE1 ####
###############
@graph_asset(resource_defs={"source_db": database1_production_resource})
def database1_production():
    return fetch_data_from_source_db()

@job(resource_defs={"source_db": database1_production_resource, "target_db": database1_local_resource})
def database1_to_local():
    data = database1_production()
    load_data_to_target_db(data)

@job(resource_defs={"source_db": database1_production_resource, "target_db": database1_staging_resource})
def database1_to_staging():
    data = database1_production()
    load_data_to_target_db(data)

@job(resource_defs={"source_db": database1_production_resource})
def database1_backup():
    data = database1_production()
    sql_backup_to_gcs(data)


###############
#### DATABASE2 ####
###############
@job(resource_defs={"source_db": database2_production_resource, "target_db": database2_local_resource})
def database2_to_local():
    data = fetch_data_from_source_db()
    load_data_to_target_db(data)

@job(resource_defs={"source_db": database2_production_resource, "target_db": database2_staging_resource})
def database2_to_staging():
    data = fetch_data_from_source_db()
    load_data_to_target_db(data)

@job(resource_defs={"source_db": database2_production_resource})
def database2_backup():
    data = fetch_data_from_source_db()
    sql_backup_to_gcs(data)


###############
#### DATABASE3 ####
###############
@job(resource_defs={"source_db": database3_production_resource, "target_db": database3_local_resource})
def database3_to_local():
    data = fetch_data_from_source_db()
    load_data_to_target_db(data)

@job(resource_defs={"source_db": database3_production_resource, "target_db": database3_staging_resource})
def database3_to_staging():
    data = fetch_data_from_source_db()
    load_data_to_target_db(data)

@job(resource_defs={"source_db": database3_production_resource})
def database3_backup():
    data = fetch_data_from_source_db()
    sql_backup_to_gcs(data)

#####################
###### BACKUPS ######
#####################
# NOTE: I couldn't get these to work from the schedules module. :(

# @job
# def backup_all():
#     database1_backup.execute_in_process()
#     database2_backup.execute_in_process()
#     database3_backup.execute_in_process()

env_owner = os.getenv("APP_ENV_OWNER")

def should_run_backups(context):
    print(f"Running backups for {env_owner}")
    return env_owner == "timo"

@schedule(job=database1_backup, cron_schedule="@daily", should_execute=should_run_backups)
def run_database1_backup(context: ScheduleEvaluationContext):
    print(f"Running database1 backups for {env_owner}")
    return RunRequest(
        run_key=None,
    )

@schedule(job=database2_backup, cron_schedule="@daily", should_execute=should_run_backups)
def run_database2_backup(context: ScheduleEvaluationContext):
    print(f"Running database2 backups for {env_owner}")
    return RunRequest(
        run_key=None,
    )

@schedule(job=database3_backup, cron_schedule="@daily", should_execute=should_run_backups)
def run_database3_backup(context: ScheduleEvaluationContext):
    print(f"Running database2 backups for {env_owner}")
    return RunRequest(
        run_key=None,
    )

