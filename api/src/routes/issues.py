"""
routes/issues.py - Routes regarding issues.

    Includes:
        
        - Viewing issue(s)
        - Submitting issues.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from uuid import UUID, uuid4
from datetime import datetime

# Third-party
from typing import Any
from pydantic import BaseModel, ValidationError
from tortoise.exceptions import OperationalError
from starlette.datastructures import UploadFile  # Import UploadFile
from tortoise.transactions import atomic
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from loguru import logger
from colorama import Fore, Style

# Local
from src.models import GroundSupportEquiptment, Issue, IssueAttachment
from src.tasks import upload_attachments_to_minio

async def details_request(request: Request) -> JSONResponse:
    """POST route to handle requests to the database for GSE."""

    class _GSEDetailsRequest(BaseModel):
        """Pydantic validation model for incoming GSE detail requests."""
        gse_id: str

    try:
        logger.info(f"{Fore.CYAN}📥 Received request for GSE details{Style.RESET_ALL}")
        body: dict[str, Any] = await request.json()
        logger.debug(f"{Fore.LIGHTBLUE_EX}🔍 Request body: {body}{Style.RESET_ALL}")
        
        gse_details_request_data: _GSEDetailsRequest = _GSEDetailsRequest(**body)
        logger.info(f"{Fore.GREEN}✅ Validation successful for GSE ID: {gse_details_request_data.gse_id}{Style.RESET_ALL}")

        # Query the database for the specified GSE
        logger.info(f"{Fore.YELLOW}🛠️ Querying database for GSE ID: {gse_details_request_data.gse_id}{Style.RESET_ALL}")
        fetched_gse_model: GroundSupportEquiptment | None = await GroundSupportEquiptment.get_or_none(
            gse_id=gse_details_request_data.gse_id
        )

        if not fetched_gse_model:
            logger.warning(f"{Fore.RED}❌ GSE model not found for ID: {gse_details_request_data.gse_id}{Style.RESET_ALL}")
            return JSONResponse(
                status_code=404,
                content={"error": "The requested model could not be found."}
            )

        fields_to_include: list[str] = [
            "gse_id",
            "gse_type",
            "model",
            "manufacturer",
            "location",
            "lift_inspection_expires",
            "latest_service_chassi",
            "latest_service_unit",
            "status",
            "type_of_fuel",
            "in_use",
            "capacity",
        ]

        def serialize_field(value: Any) -> Any:
            """Serializes datetime fields"""
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        response_data = {field: serialize_field(getattr(fetched_gse_model, field, None)) for field in fields_to_include}
        logger.success(f"{Fore.GREEN}🎉 Successfully fetched GSE details for ID: {gse_details_request_data.gse_id}{Style.RESET_ALL}")
        
        return JSONResponse(status_code=200, content=response_data)

    except ValidationError as e:
        logger.error(f"{Fore.RED}🚨 Validation Error: {e}{Style.RESET_ALL}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": e.errors()
            }
        )
    except OperationalError as e:
        logger.critical(f"{Fore.MAGENTA}💥 Database operation failed: {e}{Style.RESET_ALL}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database operation failed",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.exception(f"{Fore.RED}🔥 Unexpected error occurred: {e}{Style.RESET_ALL}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Unexpected error occurred",
                "details": str(e)
            }
        )

async def submit_issue(request: Request) -> JSONResponse:
    """POST route to submit a new issue using multipart form-data."""

    class _IssueSubmission(BaseModel):
        """Pydantic model to validate issue submission data."""
        gse_id: str
        is_operable: bool
        issue_description: str

    async def _extract_form_data():
        """Extract and validate form data."""
        try:
            form = await request.form()

            gse_id = str(form.get("gse_id", "")).strip()
            issue_description = str(form.get("issue_description", "")).strip()
            is_operable_raw = form.get("is_operable", "false")
            is_operable = str(is_operable_raw).strip().lower() == "true"

            if not gse_id or not issue_description:
                raise HTTPException(status_code=400, detail="Missing required form fields.")

            validated_data = _IssueSubmission(
                gse_id=gse_id,
                is_operable=is_operable,
                issue_description=issue_description,
            )

            attachments = [
                {
                    "filename": value.filename,
                    "content_type": value.content_type,
                    "file_content": await value.read(),
                }
                for _, value in form.multi_items() if isinstance(value, UploadFile)
            ]
            return validated_data, attachments
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail="; ".join(f"{err['loc']}: {err['msg']}" for err in e.errors()),
            )
        except Exception as e:
            logger.error(f"Error parsing form data: {e}")
            raise HTTPException(status_code=400, detail="Invalid form data.")

    async def _save_issue_to_db(validated_data, attachments):
        """Save issue and attachment metadata to the database."""
        try:
            issue = await Issue.create(
                id=uuid4(),
                gse_id=validated_data.gse_id,
                issue_description=validated_data.issue_description,
            )
            for attachment in attachments:
                attachment_id = uuid4()
                await IssueAttachment.create(
                    id=attachment_id,
                    issue=issue,
                    file_type=attachment["content_type"],
                )
            return issue.id
        except Exception as e:
            logger.error(f"Failed to save issue to database: {e}")
            raise HTTPException(status_code=500, detail="Failed to save issue to database.")

    async def _save_issue_and_queue_attachments(issue_id, attachments):
        """Save issue and queue attachment uploads."""
        try:
            tasks = [
                {
                    "attachment_id": str(uuid4()),
                    "file_stream": att["file_content"],
                    "content_length": len(att["file_content"]),
                    "content_type": att["content_type"],
                }
                for att in attachments
            ]
            upload_attachments_to_minio(tasks)
        except Exception as e:
            logger.error(f"Failed to process attachments: {e}")
            raise HTTPException(status_code=500, detail="Failed to process attachments.")

    try:
        validated_data, attachments = await _extract_form_data()
        issue_id = await _save_issue_to_db(validated_data, attachments)
        await _save_issue_and_queue_attachments(issue_id, attachments)
        return JSONResponse(
            status_code=201,
            content={"message": "Issue submitted successfully.", "issue_id": str(issue_id)},
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit issue.")
