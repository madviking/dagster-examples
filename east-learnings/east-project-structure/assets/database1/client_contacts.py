from dagster import asset, get_dagster_logger, AutoMaterializePolicy, AssetIn, op, job
from typing import List

from app.resources.mysql import database1_production_resource
from ep.ep.query.database1_base import Database1Base
from ep.ep.utils.mds_jobs import MdsJobs

logger = get_dagster_logger()


# we use a simple centralised locking system
def remove_jobs(contacts, owner):
    mds_jobs = MdsJobs()
    jobs = mds_jobs.get_job_ids(owner)

    if not jobs:
        return contacts

    # remove contacts which are already in jobs
    return [contact for contact in contacts if contact['id_zoho'] not in jobs]

# Define the assets
@asset(
    group_name="Database1TargetClients",
    tags={"kind": "sql"},
    auto_materialize_policy=AutoMaterializePolicy.eager(),
    description="Target people",
    required_resource_keys={"database1_production_resource"},
    compute_kind='sql')
def target_client_contacts(context) -> List:
    connection = context.resources.database1_production_resource.get_connection()
    query_obj = Database1Base(connection=connection)

    # example query, redacted
    sql = """
        SELECT  *
        FROM Contacts 
        ORDER BY Contacts.updated_at DESC;
        """

    result = query_obj.fetch_query(sql, [], True)
    logger.info(f"Retrieved {len(result)} records from 'from' database")
    return result

@asset(
    group_name="Database1TargetClients",
    key="tcc_without_mobile",
    tags={"kind": "sql"},
    ins={"target_client_contacts": AssetIn(key="target_client_contacts")},
    auto_materialize_policy=AutoMaterializePolicy.eager(),
    description="Target people without mobile",
    compute_kind='sql')
def tcc_without_mobile(context, target_client_contacts) -> List:
    # remove the records which don't have LinkedIn set or its NULL
    contacts = [contact for contact in target_client_contacts if contact['Mobile'] is None or contact['Mobile'] is '']
    contacts = remove_jobs(contacts, 'tcc_without_mobile')
    logger.info(f"Retrieved {len(contacts)} records without Mobile")
    return contacts

@asset(
    group_name="Database1TargetClients",
    key="fi_tcc_without_mobile",
    tags={"kind": "sql"},
    ins={"target_client_contacts": AssetIn(key="target_client_contacts")},
    auto_materialize_policy=AutoMaterializePolicy.eager(),
    description="Target people without mobile for Finland",
    compute_kind='sql')
def fi_tcc_without_mobile(context, target_client_contacts) -> List:
    # remove the records which don't have LinkedIn set or its NULL
    contacts = [contact for contact in target_client_contacts if contact['Mobile'] is None or contact['Mobile'] is '']
    contacts = [contact for contact in contacts if contact['Country'] is 'Finland' or contact['Mailing_Country'] is 'Finland']
    contacts = remove_jobs(contacts, 'fi_tcc_without_mobile')
    logger.info(f"Retrieved {len(contacts)} records without Mobile")
    return contacts

