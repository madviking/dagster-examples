import os

import mysql.connector
from dagster import ConfigurableResource, asset, Output, AssetMaterialization, resource
from pydantic import BaseModel
from typing import List, Optional

class MySQLResource(ConfigurableResource):
    host: str
    user: str
    password: str
    database: str

    def get_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    def get_name(self):
        return self.database

class Database1ProductionResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database1',
            password=os.environ.get('--REDACTED--', ''),
            database='database1'
        )

class Database1LocalResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database1',
            password=os.environ.get('--REDACTED--', ''),
            database='database1'
        )

class Database1StagingResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database1',
            password=os.environ.get('--REDACTED--', ''),
            database='database1'
        )



@resource
def database1_production_resource(init_context):
    return Database1ProductionResource()

@resource
def database1_local_resource(init_context):
    return Database1LocalResource()

@resource
def database1_staging_resource(init_context):
    return Database1StagingResource()


class Database2ProductionResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database2',
            password=os.environ.get('--REDACTED--', ''),
            database='database2'
        )

class Database2LocalResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database2',
            password=os.environ.get('--REDACTED--', ''),
            database='database2'
        )

class Database2StagingResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database2',
            password=os.environ.get('--REDACTED--', ''),
            database='database2'
        )

@resource
def database2_production_resource(init_context):
    return Database2ProductionResource()

@resource
def database2_local_resource(init_context):
    return Database2LocalResource()

@resource
def database2_staging_resource(init_context):
    return Database2StagingResource()



class Database3ProductionResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database3',
            password=os.environ.get('--REDACTED--', ''),
            database='database3'
        )

class Database3LocalResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database3',
            password=os.environ.get('--REDACTED--', ''),
            database='database3'
        )

class Database3StagingResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database3',
            password=os.environ.get('--REDACTED--', ''),
            database='database3'
        )

@resource
def database3_production_resource(init_context):
    return Database3ProductionResource()

@resource
def database3_local_resource(init_context):
    return Database3LocalResource()

@resource
def database3_staging_resource(init_context):
    return Database3StagingResource()


class Database4LocalResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database1',
            password=os.environ.get('--REDACTED--', ''),
            database='database1'
        )


class Database4StagingResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database4',
            password=os.environ.get('--REDACTED--', ''),
            database='database4'
        )


class Database4ProductionResource(MySQLResource):
    def __init__(self):
        super().__init__(
            host='redacted',
            user='database4',
            password=os.environ.get('--REDACTED--', ''),
            database='database4'
        )


@resource
def database_4_local_resource(init_context):
    return Database4LocalResource()


@resource
def database_4_staging_resource(init_context):
    return Database4StagingResource()


@resource
def database_4_production_resource(init_context):
    return Database4ProductionResource()
