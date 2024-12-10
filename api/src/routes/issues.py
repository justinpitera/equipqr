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
from datetime import datetime, timedelta, timezone

# Third-party
from pydantic import BaseModel, ValidationError
from tortoise.exceptions import OperationalError
from starlette.datastructures import FormData, UploadFile
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
        body: dict[str, str] = await request.json()
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
            "old_gse_id",
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

        def serialize_field(value: str | datetime | None) -> str | None:
            """Serializes datetime fields to ISO format. Returns other values as-is."""
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        def serialize_issue(issue: Issue) -> dict[str, str | None]:
            """Serializes an issue instance into a dictionary."""
            return {
                "id": str(issue.id),
                "gse_id": issue.gse_id,
                "issue_description": issue.issue_description,
                "reported_at": serialize_field(issue.reported_at),
                "attachments": None if issue.attachments is None else "Attachments are present",
            }

        # Fetch all issues for the given GSE ID
        issues: list[Issue] = await Issue.filter(gse_id=gse_details_request_data.gse_id).all()
        
        logger.info(f"Successfully fetched {len(issues)} issues from the database for {gse_details_request_data.gse_id}")

        # Get the most recent issue if available and within the last 5 hours
        most_recent_issue: Issue | None = (
            max(issues, key=lambda issue: issue.reported_at) 
            if issues and max(issues, key=lambda issue: issue.reported_at).reported_at >= datetime.now(tz=timezone.utc) - timedelta(hours=5) 
            else None
        )

        # Fetch and serialize attachments for the most recent issue
        attachment_ids: list[str] | None = (
            [
                f"{'video' if attachment.file_type.startswith('video') else 'img'}:{attachment.id}"
                for attachment in await IssueAttachment.filter(issue=most_recent_issue)
            ]
            if most_recent_issue else None
        )

        # Serialize most recent issue including categorized attachments
        serialized_most_recent_issue: dict[str, str | None] | None = (
            {
                **serialize_issue(issue=most_recent_issue),
                "attachments": ", ".join(attachment_ids) if attachment_ids else None
            } if most_recent_issue else None
        )

        logger.info(f"Recent issue for {gse_details_request_data.gse_id} {"discovered, including in response details..." if most_recent_issue else "not found..."}")

        # Serialize GSE model fields
        response_data: dict[str, str | None | bool | dict[str, str | None]] = {
            field: serialize_field(value=getattr(fetched_gse_model, field, None)) for field in fields_to_include
        }
        response_data["issue_count"] = str(len(issues))
        response_data["most_recent_issue"] = serialized_most_recent_issue

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

    async def _extract_form_data() -> tuple[_IssueSubmission, list[dict[str, str | bytes | None]]]:
        """Extract and validate form data."""
        try:
            form: FormData = await request.form()

            gse_id: str = str(form.get("gse_id", "")).strip()
            issue_description: str = str(form.get("issue_description", "")).strip()
            is_operable_raw: UploadFile | str = form.get("is_operable", "false")
            is_operable: bool = str(is_operable_raw).strip().lower() == "true"

            if not gse_id or not issue_description:
                logger.warning("⚠️ Missing required form fields: gse_id or issue_description.")
                raise HTTPException(status_code=400, detail="Missing required form fields.")

            validated_data: _IssueSubmission = _IssueSubmission(
                gse_id=gse_id,
                is_operable=is_operable,
                issue_description=issue_description,
            )

            attachments: list[dict[str, str | bytes | None]] = [
                {
                    "filename": value.filename,
                    "content_type": value.content_type,
                    "file_content": await value.read(),
                }
                for _, value in form.multi_items() if isinstance(value, UploadFile)
            ]
            logger.info(f"📄 Extracted form data: {validated_data} and {len(attachments)} attachments.")
            return validated_data, attachments    
        except ValidationError as e:
            logger.error(f"❌ Validation error: {e}")
            raise HTTPException(
                status_code=400,
                detail="; ".join(f"{err['loc']}: {err['msg']}" for err in e.errors()),
            )
        except Exception as e:
            logger.error(f"❌ Error parsing form data: {e}")
            raise HTTPException(status_code=400, detail="Invalid form data.")

    async def _save_issue_to_db(validated_data: _IssueSubmission, attachments: list[dict[str, str | bytes | None]]) -> UUID:
        """Save issue and attachment metadata to the database."""
        try:
            issue: Issue = await Issue.create(
                id=uuid4(),
                gse_id=validated_data.gse_id,
                issue_description=validated_data.issue_description,
            )
            for attachment in attachments:
                attachment_id: UUID = uuid4()
                attachment["attachment_id"] = str(attachment_id)
                _ = await IssueAttachment.create(
                    id=attachment_id,
                    issue=issue,
                    file_type=attachment["content_type"],
                )
            return issue.id
        except Exception as e:
            logger.error(f"Failed to save issue to database: {e}")
            raise HTTPException(status_code=500, detail="Failed to save issue to database.")

    async def _queue_attachments(_, attachments: list[dict[str, str | bytes | None]]) -> None:
        """Queue attachment uploads."""
        try:
            tasks: list[dict[str, str | bytes | int | None]] = [
                {
                    "attachment_id": att["attachment_id"],
                    "file_stream": att["file_content"],
                    "content_length": len(att["file_content"]) if att["file_content"] is not None else 0,
                    "content_type": att["content_type"],
                }
                for att in attachments
            ]
            logger.info(f"📂 Queueing {len(attachments)} attachments...")
            upload_attachments_to_minio(files_data=tasks)
            logger.success("✅ Attachments queued successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to process attachments: {e}")
            raise HTTPException(status_code=500, detail="Failed to process attachments.")

    try:
        validated_data, attachments = await _extract_form_data()
        issue_id: UUID = await _save_issue_to_db(validated_data, attachments)
        await _queue_attachments(_=issue_id, attachments=attachments)
        logger.info("📬 Attachments queued and issue saved successfully!")
        return JSONResponse(
            status_code=201,
            content={"message": "Issue submitted successfully.", "issue_id": str(issue_id)},
        )
    except HTTPException as e:
        logger.warning(f"⚠️ HTTPException encountered: {e.detail}")
        raise e
    except Exception as e:
        logger.critical(f"🔥 Unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit issue.")
