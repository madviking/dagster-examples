import os

from dagster import asset, Config, AssetExecutionContext
from typing import Dict, List
from pathlib import Path
from app.resources.gcs_files import get_local_file_list, upload_to_gcs
from google.cloud import storage

# Configuration classes
class LocalFileListConfig(Config):
    local_path: str = "/your_path/public}"

class GcsFilesConfig(Config):
    local_path: str = "/your_path/public"
    bucket_name: str = "your_bucket"
    base_folder_name: str = "public"

# Asset definitions
@asset(key="local_file_list", group_name="FileSync", description="Local public file list", compute_kind='excel')
def local_file_list(context: AssetExecutionContext, config: LocalFileListConfig) -> Dict[str, str]:
    return get_local_file_list(Path(config.local_path), context)

@asset(key="gcs_files", group_name="FileSync", description="Google cloud storage bucket", compute_kind='googlecloud')
def gcs_files(context: AssetExecutionContext, config: GcsFilesConfig, local_file_list: Dict[str, str]) -> List[str]:
    return upload_to_gcs(local_file_list, config, context)
