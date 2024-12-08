"""
src/tasks.py - This script contains various backend background tasks.

Date: December 7, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""
# Standard

# Third-party
from loguru import logger
from celery import Celery
from minio.error import S3Error, InvalidResponseError
from minio import Minio

# Local
from . import API_CONFIG

celery_app: Celery = Celery(
    main="tasks",
    broker=f"redis://:{API_CONFIG["redis"]["password"]}@{API_CONFIG["redis"]["address"]}:{API_CONFIG["redis"]["port"]}/0",
    backend=f"redis://:{API_CONFIG["redis"]["password"]}@{API_CONFIG["redis"]["address"]}:{API_CONFIG["redis"]["port"]}/0",
)

from io import BytesIO

@celery_app.task
def upload_attachments_to_minio(files_data: list[dict]) -> None:
    """
    Celery task to upload multiple files to MinIO in batch with improved error handling.
    """
    client: Minio = Minio(
        endpoint=f"{API_CONFIG['object_storage']['address']}:{API_CONFIG['object_storage']['port']}",
        access_key=f"{API_CONFIG['object_storage']['access_key']}",
        secret_key=f"{API_CONFIG['object_storage']['secret_key']}",
        secure=API_CONFIG['object_storage']['secure'],
    )

    bucket_name = "attachments"
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
    except (S3Error, InvalidResponseError) as e:
        logger.error(f"Error while checking/creating bucket '{bucket_name}': {e}")
        raise RuntimeError(f"Failed to prepare bucket '{bucket_name}': {e}")

    for file_data in files_data:
        try:
            # Wrap file content in BytesIO to provide a file-like object
            file_stream = BytesIO(file_data["file_stream"])
            _ = client.put_object(
                bucket_name,
                file_data["attachment_id"],
                file_stream,
                file_data["content_length"],
                content_type=file_data["content_type"],
            )
            logger.info(f"Successfully uploaded file: {file_data['attachment_id']}")
        except (S3Error, InvalidResponseError) as e:
            logger.error(
                f"Error uploading file {file_data['attachment_id']} to bucket '{bucket_name}': {e}"
            )
            raise RuntimeError(
                f"Failed to upload file {file_data['attachment_id']}: {e}"
            )
        except Exception as e:
            logger.exception(
                f"Unexpected error while uploading file {file_data['attachment_id']}: {e}"
            )
            raise RuntimeError(
                f"Unexpected error during upload of file {file_data['attachment_id']}: {e}"
            )
