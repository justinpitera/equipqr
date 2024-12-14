# Standard

# Third-party
from starlette.requests import Request
from starlette.responses import Response
from minio import Minio
from minio.error import S3Error
from loguru import logger

# Local
from src import API_CONFIG
from src.models import IssueAttachment


async def fetch_issue_attachment(request: Request) -> Response:
    """Returns attachment data from S3 storage."""
    attachment_id: str | None = request.query_params.get("id")
    logger.info(f"Received request to fetch attachment with ID: {attachment_id}")

    if not attachment_id:
        logger.warning("Missing 'id' query parameter in the request")
        return Response(content="Missing 'id' query parameter", status_code=400)

    try:
        logger.debug(f"Looking up attachment in database: ID={attachment_id}")
        attachment: IssueAttachment | None = await IssueAttachment.get_or_none(id=attachment_id)
        if not attachment:
            logger.warning(f"No attachment found in the database for ID: {attachment_id}")
            return Response(content="Attachment not found", status_code=404)

        object_name: str = str(attachment_id)
        logger.info("Initializing MinIO client for S3 interaction")
        client: Minio = Minio(
            endpoint=f"{API_CONFIG['object_storage']['address']}:{API_CONFIG['object_storage']['port']}",
            access_key=API_CONFIG['object_storage']['access_key'],
            secret_key=API_CONFIG['object_storage']['secret_key'],
            secure=API_CONFIG['object_storage']['secure'],
        )

        logger.debug(
            f"Attempting to fetch object from bucket: attachments | Object name: {object_name}"
        )
        response = client.get_object(bucket_name="attachments", object_name=object_name)
        content: bytes = response.read()
        response.close()
        response.release_conn()

        logger.info(f"Successfully fetched object {object_name} from S3 storage")
        return Response(
            content=content,
            media_type=attachment.file_type,
            headers={"Content-Disposition": f"inline; filename={object_name}"},
        )
    except S3Error as e:
        logger.error(
            f"S3Error while fetching object '{attachment_id}': {e.code} - {e.message}",
            exc_info=True,
        )
        if e.code == "NoSuchKey":
            return Response(
                content=f"Object '{attachment_id}' does not exist in the S3 bucket.",
                status_code=404,
            )
        return Response(
            content=f"Error fetching attachment from S3: {e.message}",
            status_code=500,
        )
    except Exception as e:
        logger.exception(f"Unexpected error occurred while fetching attachment: {e}")
        return Response(
            content="An unexpected error occurred while processing your request.",
            status_code=500,
        )