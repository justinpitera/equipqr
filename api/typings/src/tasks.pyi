from . import API_CONFIG as API_CONFIG
from celery import Celery

celery_app: Celery

def upload_attachments_to_minio(files_data: list[dict[str, bytes | str | int | None]]) -> None: ...
