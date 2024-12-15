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
from magic import Magic
from google.protobuf.internal.containers import RepeatedScalarFieldContainer
from pydantic import BaseModel, ValidationError
from tortoise.exceptions import OperationalError, DoesNotExist
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.exceptions import HTTPException
from loguru import logger
from colorama import Fore, Style

# Local
from src.models import GroundSupportEquiptment, Issue, IssueAttachment
from src.tasks import upload_attachments_to_minio

# Protobufs
from src.protos.requests.v1.requests_pb2 import (
    FetchIssuesRequest,
    Attachment as ProtoAttachment,
    Issue as ProtoIssue,
    FetchIssuesResponse,
    GSEDetailsRequest,
    GSEDetailsResponse,
    MostRecentIssueResponse,
    SubmitIssueRequest,
    SubmitIssueResponse,
)

async def details_request(request: Request) -> Response:
    """POST route to handle requests to the database for GSE."""
    try:
        logger.info(f"{Fore.CYAN}📥 Received request for GSE details{Style.RESET_ALL}")
        body: bytes = await request.body()

        # Parse the body into the GSEDetailsRequest object
        gse_details_request = GSEDetailsRequest()
        gse_details_request.ParseFromString(body)
        logger.info(f"{Fore.GREEN}✅ Validation successful for GSE ID: {gse_details_request.gse_id}{Style.RESET_ALL}")

        # Query the database for the specified GSE
        logger.info(f"{Fore.YELLOW}🛠️ Querying database for GSE ID: {gse_details_request.gse_id}{Style.RESET_ALL}")
        fetched_gse_model = await GroundSupportEquiptment.get_or_none(gse_id=gse_details_request.gse_id)

        if not fetched_gse_model:
            logger.warning(f"{Fore.RED}❌ GSE model not found for ID: {gse_details_request.gse_id}{Style.RESET_ALL}")
            return Response(
                content=GSEDetailsResponse(error="The requested model could not be found.").SerializeToString(),
                media_type="application/protobuf",
                status_code=404,
            )

        # Fetch all issues for the given GSE ID
        issues = await Issue.filter(gse_id=gse_details_request.gse_id).all()
        most_recent_issue = (
            max(issues, key=lambda issue: issue.reported_at)
            if issues and max(issues, key=lambda issue: issue.reported_at).reported_at >= datetime.now(tz=timezone.utc) - timedelta(hours=5)
            else None
        )

        # Serialize most recent issue
        serialized_most_recent_issue: Any | None = (
            MostRecentIssueResponse(
                id=str(most_recent_issue.id),
                gse_id=most_recent_issue.gse_id,
                issue_description=most_recent_issue.issue_description,
                reported_at=most_recent_issue.reported_at.isoformat() if most_recent_issue.reported_at else "",
                attachments=", ".join(
                    f"{'video' if attachment.file_type.startswith('video') else 'img'}:{attachment.id}"
                    for attachment in await IssueAttachment.filter(issue=most_recent_issue)
                )
            ) if most_recent_issue else None
        )

        # Build the GSEDetailsResponse protobuf
        response_data: GSEDetailsResponse = GSEDetailsResponse(
            gse_id=fetched_gse_model.gse_id,
            old_gse_id=fetched_gse_model.old_gse_id,
            gse_type=fetched_gse_model.gse_type,
            model=fetched_gse_model.model,
            manufacturer=fetched_gse_model.manufacturer,
            location=fetched_gse_model.location,
            status=fetched_gse_model.status,
            issue_count=str(len(issues)),
            type_of_fuel=fetched_gse_model.type_of_fuel,
            in_use=fetched_gse_model.in_use,
            most_recent_issue=serialized_most_recent_issue,
            lift_inspection_expires=fetched_gse_model.lift_inspection_expires.isoformat() if fetched_gse_model.lift_inspection_expires else "",
            latest_service_chassi=str(fetched_gse_model.latest_service_chassi),
            latest_service_unit=str(fetched_gse_model.latest_service_unit),
            capacity = float(fetched_gse_model.capacity) if fetched_gse_model.capacity is not None else 0.0, # pyright: ignore
            details="",
            error=None
        )

        logger.success(f"{Fore.GREEN}🎉 Successfully fetched GSE details for ID: {gse_details_request.gse_id}{Style.RESET_ALL}")
        
        # Serialize and return the protobuf response
        return Response(content=response_data.SerializeToString(), media_type="application/protobuf", status_code=200)

    except ValidationError as e:
        logger.error(f"{Fore.RED}🚨 Validation Error: {e}{Style.RESET_ALL}")
        error_response = GSEDetailsResponse(error="Validation error: " + str(e))
        return Response(content=error_response.SerializeToString(), media_type="application/protobuf", status_code=422)

    except OperationalError as e:
        logger.critical(f"{Fore.MAGENTA}💥 Database operation failed: {e}{Style.RESET_ALL}")
        error_response = GSEDetailsResponse(error="Database operation failed: " + str(e))
        return Response(content=error_response.SerializeToString(), media_type="application/protobuf", status_code=500)

    except Exception as e:
        logger.exception(f"{Fore.RED}🔥 Unexpected error occurred: {e}{Style.RESET_ALL}")
        error_response = GSEDetailsResponse(error="Unexpected error occurred: " + str(e))
        return Response(content=error_response.SerializeToString(), media_type="application/protobuf", status_code=500)
    
async def submit_issue(request: Request) -> Response:
    """POST route to submit a new issue using multipart form-data."""

    async def _save_issue_to_db(
        gse_id: str, issue_description: str, attachments: RepeatedScalarFieldContainer[bytes], worker_id: str
    ) -> tuple[UUID, list[tuple[UUID, bytes]]]:
        """Save issue and attachment metadata to the database."""
        try:
            issue: Issue = await Issue.create(
                id=uuid4(),
                gse_id=gse_id,
                issue_description=issue_description,
                reported_by=worker_id,
            )
            mime: Magic = Magic(mime=True)
            attachment_data: list[Any] = []

            for attachment in attachments:
                attachment_id: UUID = uuid4()
                content_type: str = mime.from_buffer(buf=attachment)
                await IssueAttachment.create(
                    id=attachment_id,
                    issue=issue,
                    file_type=content_type or "application/octet-stream",
                )
                attachment_data.append((attachment_id, attachment))

            return issue.id, attachment_data
        except Exception as e:
            logger.error(f"Failed to save issue to database: {e}")
            raise HTTPException(status_code=500, detail="Failed to save issue to database.")

    async def _queue_attachments(attachments_data: list[tuple[UUID, bytes]]) -> None:
        """Queue attachment uploads."""
        try:
            mime: Magic = Magic(mime=True)
            tasks: list[dict[str, str | bytes | int | None]] = [
                {
                    "attachment_id": str(attachment_id),
                    "file_stream": attachment,
                    "content_length": len(attachment),
                    "content_type": mime.from_buffer(attachment) or "application/octet-stream",
                }
                for attachment_id, attachment in attachments_data
            ]
            logger.info(f"Queueing {len(tasks)} attachments...")
            upload_attachments_to_minio(files_data=tasks)
            logger.success("Attachments queued successfully!")
        except Exception as e:
            logger.error(f"Failed to process attachments: {e}")
            raise HTTPException(status_code=500, detail="Failed to process attachments.")


    try:
        # Parse the body into the SubmitIssueRequest object
        body: bytes = await request.body()
        submit_issue_request: SubmitIssueRequest = SubmitIssueRequest()
        submit_issue_request.ParseFromString(body)

        issue_id, attachment_data = await _save_issue_to_db(
            gse_id=submit_issue_request.gse_id,
            attachments=submit_issue_request.attachments,
            issue_description=submit_issue_request.issue_description,
            worker_id=submit_issue_request.worker_id,
        )

        await _queue_attachments(attachments_data=attachment_data)

        logger.info("\ud83d\udcec Attachments queued and issue saved successfully!")

        # Prepare the response using SubmitIssueResponse
        response: bytes = SubmitIssueResponse(id=str(issue_id)).SerializeToString()
        return Response(content=response, status_code=200)
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
        
async def fetch_issues(request: Request) -> Response:

    try:
        body: bytes = await request.body()
        filters: FetchIssuesRequest = FetchIssuesRequest()
        filters.ParseFromString(body)  
        
        # # Construct Tortoise query
        # query: Q = Q()
        # if filters.reported_by:
        #     query &= Q(reported_by__email__icontains=filters.reported_by)
        # if filters.reported_at_start:
        #     query &= Q(reported_at__gte=filters.reported_at_start)
        # if filters.reported_at_end:
        #     query &= Q(reported_at__lte=filters.reported_at_end)
        # if filters.description:
        #     query &= Q(issue_description__icontains=filters.description)

        # Pagination
        offset: int = (filters.page - 1) * filters.page_size
        limit: int = filters.page_size

        # Query database
        issues_queryset: list[Issue] = (
            await Issue.filter()#query)
            .order_by('-reported_at')
            .offset(offset)
            .limit(limit)
            .prefetch_related("attachments")
        )

        total_issues: int = await Issue.filter().count()#query).count()
        
        # Build Protobuf response
        response_message: FetchIssuesResponse = FetchIssuesResponse(
            page=filters.page,
            page_size=filters.page_size,
            total=total_issues,
        )

        for issue in issues_queryset:
            proto_issue: ProtoIssue = ProtoIssue(
                id=str(issue.id),
                gse_id=str(issue.gse_id),
                issue_description=issue.issue_description,
                reported_at=issue.reported_at.isoformat() if issue.reported_at else "",
                estimated_time=str(issue.estimated_time) if issue.estimated_time else "",
                reported_by=issue.reported_by,
                progress=issue.progress,
            )

            for attachment in (issue.attachments or []):
                proto_attachment: ProtoAttachment = ProtoAttachment(
                    id=str(attachment.id),
                    file_type=attachment.file_type,
                    uploaded_at=attachment.uploaded_at.isoformat() if attachment.uploaded_at else "",
                )
                proto_issue.attachments.append(proto_attachment)

            response_message.data.append(proto_issue)

        serialized_response: bytes = response_message.SerializeToString()
        return Response(content=serialized_response, media_type="application/protobuf")

    except DoesNotExist:
        logger.error("No issues found for the provided filters.")
        return Response(content="DoesNotExist error", media_type="text/plain", status_code=500)
    except ValueError as ve:
        logger.error("Validation error: {}", str(ve))
        return Response(content=str(ve), media_type="text/plain", status_code=422)
    except Exception as e:
        logger.error("Internal server error: {}", str(e))
        return Response(content="Internal server error", media_type="text/plain", status_code=500)


async def edit_issue(request: Request) -> None:
    """POST route for editing an issue"""
    pass