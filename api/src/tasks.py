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

def _verify_bucket(minio_client: Minio, bucket_name: str) -> None:
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
    except (S3Error, InvalidResponseError) as e:
        logger.error(f"Error while checking/creating bucket '{bucket_name}': {e}")
        raise RuntimeError(f"Failed to prepare bucket '{bucket_name}': {e}")

@celery_app.task
def upload_attachments_to_minio(files_data: list[dict[str, bytes | str | int | None]]) -> None:
    """
    Celery task to upload multiple files to MinIO in batch with improved error handling.

    Args:
        files_data: A list of dictionaries containing file metadata and content:
            - file_stream: The raw byte content of the file.
            - attachment_id: Unique identifier for the file.
            - content_length: Length of the file in bytes.
            - content_type: The MIME type of the file.
    """
    client: Minio = Minio(
        endpoint=f"{API_CONFIG['object_storage']['address']}:{API_CONFIG['object_storage']['port']}",
        access_key=API_CONFIG['object_storage']['access_key'],
        secret_key=API_CONFIG['object_storage']['secret_key'],
        secure=API_CONFIG['object_storage']['secure'],
    )

    bucket_name: str = "attachments"
    _verify_bucket(minio_client=client, bucket_name=bucket_name)

    for file_data in files_data:
        try:
            # Type checking for each file_data entry
            if not all(k in file_data for k in ("file_stream", "attachment_id", "content_length", "content_type")):
                raise KeyError("Missing required keys in file_data.")
            if not isinstance(file_data["file_stream"], bytes):
                raise TypeError("file_stream must be of type bytes.")
            if not isinstance(file_data["attachment_id"], str):
                raise TypeError("attachment_id must be of type str.")
            if not isinstance(file_data["content_length"], int):
                raise TypeError("content_length must be of type int.")
            if not isinstance(file_data["content_type"], str):
                raise TypeError("content_type must be of type str.")

            # Wrap file content
            file_stream: BytesIO = BytesIO(initial_bytes=file_data["file_stream"])
            _ = client.put_object(
                bucket_name=bucket_name,
                object_name=file_data["attachment_id"],
                data=file_stream,
                length=file_data["content_length"],
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