"""
routes/issues.py - Routes regarding issues.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from __future__ import annotations
from typing import Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone

# Third-party
from pydantic import BaseModel, ValidationError, Field, field_validator
from tortoise.expressions import Q
from tortoise.exceptions import OperationalError, DoesNotExist
from starlette.datastructures import FormData, UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from loguru import logger
from colorama import Fore, Style

# Local
from src.models import GroundSupportEquiptment, Issue, IssueAttachment
from src.tasks import upload_attachments_to_minio
from src.enums import IssueProgressEnum


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
                "reported_at": serialize_field(value=issue.reported_at),
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
        worker_id: str

    async def _extract_form_data() -> tuple[_IssueSubmission, list[dict[str, str | bytes | None]], str]:
        """Extract and validate form data."""
        try:
            form: FormData = await request.form()

            gse_id: str = str(form.get("gse_id", "")).strip()
            issue_description: str = str(form.get("issue_description", "")).strip()
            worker_id: str = str(form.get("worker_id", "")).strip()
            is_operable_raw: UploadFile | str = form.get("is_operable", "false")
            is_operable: bool = str(is_operable_raw).strip().lower() == "true"

            if not gse_id or not issue_description:
                logger.warning("⚠️ Missing required form fields: gse_id or issue_description.")
                raise HTTPException(status_code=400, detail="Missing required form fields.")

            validated_data: _IssueSubmission = _IssueSubmission(
                gse_id=gse_id,
                is_operable=is_operable,
                issue_description=issue_description,
                worker_id=worker_id
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
            return validated_data, attachments, worker_id
        except ValidationError as e:
            logger.error(f"❌ Validation error: {e}")
            raise HTTPException(
                status_code=400,
                detail="; ".join(f"{err['loc']}: {err['msg']}" for err in e.errors()),
            )
        except Exception as e:
            logger.error(f"❌ Error parsing form data: {e}")
            raise HTTPException(status_code=400, detail="Invalid form data.")

    async def _save_issue_to_db(validated_data: _IssueSubmission, attachments: list[dict[str, str | bytes | None]], worker_id: str) -> UUID:
        """Save issue and attachment metadata to the database."""
        try:
            issue: Issue = await Issue.create(
                id=uuid4(),
                gse_id=validated_data.gse_id,
                issue_description=validated_data.issue_description,
                reported_by=worker_id,
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
        validated_data, attachments, worker_id = await _extract_form_data()
        issue_id: UUID = await _save_issue_to_db(validated_data, attachments, worker_id=worker_id)
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


async def delete_issues(request: Request) -> JSONResponse:
    """POST route to delete issue, given its issue_id"""

    class _DeleteIssuesRequest(BaseModel):
        """Pydantic validation model for incoming requests to delete issues based on their id."""
        ids: list[str]

    try:
        logger.info(f"{Fore.CYAN}📥 Received request to delete issues{Style.RESET_ALL}")
        body: dict[str, list[str]] = await request.json()
        logger.debug(f"{Fore.LIGHTBLUE_EX}🔍 Request body: {body}{Style.RESET_ALL}")

        delete_issues_request: _DeleteIssuesRequest = _DeleteIssuesRequest(**body)
        logger.info(f"{Fore.GREEN}✅ Validation successful for Issue IDs: {delete_issues_request.ids}{Style.RESET_ALL}")

        logger.info(f"{Fore.YELLOW}🛠️ Querying database for Issue IDs: {delete_issues_request.ids}{Style.RESET_ALL}")
        fetched_issues: list[Issue] = await Issue.filter(id__in=delete_issues_request.ids).all()

        if not fetched_issues:
            logger.warning(f"{Fore.RED}❌ No issues found for the provided IDs: {delete_issues_request.ids}{Style.RESET_ALL}")
            return JSONResponse(
                status_code=404,
                content={"error": "None of the requested issues could be found."}
            )

        fetched_issues_ids: set[str] = {str(issue.id) for issue in fetched_issues}
        not_found_ids: list[str] = list(set(delete_issues_request.ids) - fetched_issues_ids)

        if not_found_ids:
            logger.warning(f"{Fore.RED}⚠️ The following IDs were not found and will not be deleted: {not_found_ids}{Style.RESET_ALL}")

        logger.info(f"{Fore.GREEN}✅ Deleting fetched issues: {list(fetched_issues_ids)}{Style.RESET_ALL}")
        await Issue.filter(id__in=fetched_issues_ids).delete()

        logger.info(f"{Fore.GREEN}✅ Successfully deleted requested issues.{Style.RESET_ALL}")
        response_content: dict[str, str | list[str]] = {"message": "Issues deleted successfully.", "deleted_ids": list(fetched_issues_ids)}
        if not_found_ids:
            response_content["not_found_ids"] = not_found_ids
            return JSONResponse(status_code=207, content=response_content)

        return JSONResponse(status_code=200, content=response_content)

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
        
async def fetch_issues(request: Request) -> JSONResponse:

    class _IssueFilters(BaseModel):
        """Pydantic model to validate request body for fetching issues."""
        reported_by: str | None = None
        reported_at_start: datetime | None = None
        reported_at_end: datetime | None = None
        estimated_time: str | None = None
        description: str | None = None
        progress: str | None = None
        location: str | None = None
        page: int = Field(default=1, ge=1)
        page_size: int = Field(default=10, ge=1, le=100)

        @field_validator("reported_at_start", "reported_at_end")
        @classmethod
        def validate_date_format(cls, value: str | None) -> datetime | None:
            if value is None:
                return None
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValueError("Invalid ISO 8601 date format.")

    try:
        # Parse the request body as JSON
        data: dict[str, str | datetime | int | None] = await request.json()
        filters: _IssueFilters = _IssueFilters(**data) # pyright: ignore[reportArgumentType]

        # Construct Tortoise query
        query: Q = Q()
        if filters.reported_by:
            query &= Q(reported_by__email__icontains=filters.reported_by)
        if filters.reported_at_start:
            query &= Q(reported_at__gte=filters.reported_at_start)
        if filters.reported_at_end:
            query &= Q(reported_at__lte=filters.reported_at_end)
        if filters.description:
            query &= Q(issue_description__icontains=filters.description)

        # Pagination
        offset: int = (filters.page - 1) * filters.page_size
        limit: int = filters.page_size

        # Query database
        issues_queryset = (
            await Issue.filter(query)
            .offset(offset)
            .limit(limit)
            .prefetch_related("attachments")
        )

        total_issues: int = await Issue.filter(query).count()
        
        # Initialize issues_data as a list
        issues_data: list[dict[str, str | IssueProgressEnum | list[dict[str, str | Any | None]] | None]] = []

        # Loop through issues_queryset and append issue data
        for issue in issues_queryset:
            issues_data.append({
                "id": str(issue.id),
                "gse_id": str(issue.gse_id),
                "issue_description": issue.issue_description,
                "reported_at": issue.reported_at.isoformat() if issue.reported_at else None,
                "estimated_time": str(issue.estimated_time) if issue.estimated_time else None,
                "reported_by": issue.reported_by,
                "progress": issue.progress,
                "attachments": [
                    {
                        "id": str(attachment.id),
                        "file_type": attachment.file_type,
                        "uploaded_at": attachment.uploaded_at.isoformat() if attachment.uploaded_at else None,
                    }
                    for attachment in (issue.attachments or [])
                ],
            })

        # Build response
        response: dict[str, Any] = {
            "total": total_issues,
            "page": filters.page,
            "page_size": filters.page_size,
            "data": issues_data,
        }

        logger.info("Successfully fetched issues with filters: {}", data)
        return JSONResponse(status_code=200, content=response)

    except DoesNotExist:
        logger.error("No issues found for the provided filters: {}", data)
        return JSONResponse(status_code=404, content={"error": "No issues found."})
    except ValueError as ve:
        logger.error("Validation error: {}", str(ve))
        return JSONResponse(status_code=422, content={"error": str(ve)})
    except Exception as e:
        logger.error("Internal server error: {}", str(e))
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

async def edit_issue(request: Request) -> None:
    """POST route for editing an issue"""
    
    class _EditIssueRequest(BaseModel):
        """Pydantic model to validate incoming requests to edit issues."""
        gse_id: str # query
        
        # Modifiables:
        progress: str | None = None
