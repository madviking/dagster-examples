import sys
import os
from pathlib import Path
import importlib.util
from typing import Dict, List, Union

from dagster import (
    JobDefinition, GraphDefinition, ScheduleDefinition, SensorDefinition,
    AssetsDefinition, OpDefinition, ResourceDefinition, repository,
    Definitions, ConfigurableIOManager
)

import google.auth
sys.path.append(os.path.join('/opt/dagster/app/src'))

def test_google_auth():
    print("Testing Google Cloud authentication")
    try:
        credentials, project = google.auth.default()
        print(f"Authenticated with project: {project}")
        return True
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        return False

if not test_google_auth():
    raise Exception("Google Cloud authentication failed")

DagsterObject = Union[JobDefinition, GraphDefinition, ScheduleDefinition, SensorDefinition, AssetsDefinition, OpDefinition, ResourceDefinition]

# Global registry to avoid duplicate definitions
global_registry = {
    'jobs': {}, 'graphs': {}, 'schedules': {}, 'sensors': {}, 'assets': {}, 'ops': {}, 'resources': {}
}

def import_from_directory(directory: str) -> Dict[str, Dict[str, Union[DagsterObject, ConfigurableIOManager]]]:
    skip = [
       # 'enrich_target_client_contact.py'
    ]

    if directory == 'dagster_assets':
        directory = f"/opt/dagster/app/src/ep/ep/dagster_assets"
    else:
        directory = f"/opt/dagster/app/src/app/{directory}"

    skip_directories = ['__pycache__', 'tests']

    print(f'Importing from {directory}')
    items: Dict[str, Dict[str, DagsterObject]] = {
        'jobs': {}, 'graphs': {}, 'schedules': {}, 'sensors': {}, 'assets': {}, 'ops': {}, 'resources': {}
    }

    for file in Path(directory).rglob('*.py'):
        if any(skip in file.parts for skip in skip_directories):
            continue

        if file.stem in skip:
            continue

        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for item_name in dir(module):
            item = getattr(module, item_name)
            if isinstance(item, JobDefinition) and item_name not in global_registry['jobs']:
                global_registry['jobs'][item_name] = item
                items['jobs'][item_name] = item
            elif isinstance(item, GraphDefinition) and item_name not in global_registry['graphs']:
                global_registry['graphs'][item_name] = item
                items['graphs'][item_name] = item
            elif isinstance(item, ScheduleDefinition) and item_name not in global_registry['schedules']:
                global_registry['schedules'][item_name] = item
                items['schedules'][item_name] = item
            elif isinstance(item, SensorDefinition) and item_name not in global_registry['sensors']:
                global_registry['sensors'][item_name] = item
                items['sensors'][item_name] = item
            elif isinstance(item, AssetsDefinition) and item_name not in global_registry['assets']:
                global_registry['assets'][item_name] = item
                items['assets'][item_name] = item
            elif isinstance(item, OpDefinition) and item_name not in global_registry['ops']:
                global_registry['ops'][item_name] = item
                items['ops'][item_name] = item
            elif isinstance(item, ResourceDefinition) and item_name not in global_registry['resources']:
                global_registry['resources'][item_name] = item
                items['resources'][item_name] = item
            elif isinstance(item, ConfigurableIOManager) and 'io_manager' not in global_registry['resources']:
                global_registry['resources']['io_manager'] = ResourceDefinition.hardcoded_resource(item)
                items['resources']['io_manager'] = ResourceDefinition.hardcoded_resource(item)

    return items

def import_all_dagster_objects(directories: List[str]) -> Dict[str, Dict[str, DagsterObject]]:
    all_items: Dict[str, Dict[str, DagsterObject]] = {
        'jobs': {}, 'graphs': {}, 'schedules': {}, 'sensors': {}, 'assets': {}, 'ops': {}, 'resources': {}
    }
    for directory in directories:
        items = import_from_directory(directory)
        for key in all_items:
            all_items[key].update(items[key])
    return all_items

# List of directories to scan
directories_to_scan = ['jobs', 'schedules', 'sensors', 'assets', 'ops', 'resources']

# Import all Dagster objects
all_dagster_objects = import_all_dagster_objects(directories_to_scan)

# Define your repository
@repository
def deploy_docker_repository():
    print('Deploying repository')
    return {
        "jobs": {job.name: job for job in all_dagster_objects['jobs'].values()},
        "schedules": {schedule.name: schedule for schedule in all_dagster_objects['schedules'].values()},
    }

# Define Dagster Definitions
defs = Definitions(
    assets=list(all_dagster_objects['assets'].values()),
    jobs=list(all_dagster_objects['jobs'].values()),
    resources=all_dagster_objects['resources'],
    sensors=list(all_dagster_objects['sensors'].values()),
    schedules=list(all_dagster_objects['schedules'].values()),
)
