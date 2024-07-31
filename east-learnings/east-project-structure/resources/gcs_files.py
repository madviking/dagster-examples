import os

from dagster import asset, Config, AssetExecutionContext
from typing import Dict, List
from pathlib import Path

from google.cloud import storage



def get_local_file_list(local_path: Path, context: AssetExecutionContext) -> Dict[str, str]:
    file_dict = {}
    for root, _, files in os.walk(local_path):
        for file in files:
            file_path = Path(root) / file
            if file_path.is_symlink():
                context.log.info(f"Skipping symlink: {file_path}")
                continue
            relative_path = file_path.relative_to(local_path).as_posix()
            try:
                mtime = file_path.stat().st_mtime
                file_dict[relative_path] = str(mtime)
            except OSError as e:
                context.log.error(f"Error accessing file {file_path}: {e}")
    context.log.info(f"Found {len(file_dict)} files (excluding symlinks) in {local_path} and its subdirectories")
    return file_dict


def upload_to_gcs(local_files: Dict[str, str], config, context: AssetExecutionContext) -> List[str]:
    local_path = Path(config.local_path)
    client = storage.Client()
    bucket = client.bucket(config.bucket_name)
    uploaded_files = []

    existing_files = {blob.name: blob.metadata.get('local_mtime', '') if blob.metadata else ''
                      for blob in bucket.list_blobs(prefix=config.base_folder_name)}

    for relative_path, local_mtime in local_files.items():
        file_path = local_path / relative_path
        destination_blob_name = f"{config.base_folder_name}/{relative_path}"

        if destination_blob_name not in existing_files or existing_files[destination_blob_name] != local_mtime:
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(str(file_path))
            blob.metadata = {'local_mtime': local_mtime}
            blob.patch()
            context.log.info(f'File {relative_path} uploaded to {config.bucket_name}/{destination_blob_name}')
            uploaded_files.append(relative_path)
        else:
            context.log.info(f'File {relative_path} already up to date in {config.bucket_name}/{destination_blob_name}')

    context.log.info(
        f'Uploaded or updated {len(uploaded_files)} files to {config.bucket_name}/{config.base_folder_name}')
    return uploaded_files
