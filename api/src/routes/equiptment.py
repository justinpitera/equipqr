"""
routes/issues.py - Routes regarding issues.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from __future__ import annotations
from datetime import datetime, timedelta, timezone

# Third-party
from tortoise.exceptions import OperationalError
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
from colorama import Fore, Style

# Local
from src.models import GroundSupportEquiptment, Issue, IssueAttachment

# Protobufs
from src.protos.requests.v1.requests_pb2 import (
    GSEDetailsRequest,
    GSEDetailsResponse,
    ListGSEReponse,
    MostRecentIssueResponse,
    UploadFieldImage,
    UploadFieldImageResponse
)

async def serialize_most_recent_issue(most_recent_issue: Issue) -> MostRecentIssueResponse:
    """Serialize the most recent issue into a protobuf response."""
    attachments = await IssueAttachment.filter(issue=most_recent_issue)
    attachment_strings = [
        f"{'video' if att.file_type.startswith('video') else 'img'}:{att.id}"
        for att in attachments
    ]
    
    return MostRecentIssueResponse(
        id=str(most_recent_issue.id),
        gse_id=most_recent_issue.gse_id,
        issue_description=most_recent_issue.issue_description,
        reported_at=most_recent_issue.reported_at.isoformat() if most_recent_issue.reported_at else "",
        attachments=", ".join(attachment_strings)
    )

def format_date(date: datetime | None) -> str:
    """Format datetime object to ISO format string."""
    return date.isoformat() if date else ""

async def create_gse_response(gse_model: GroundSupportEquiptment, issues: list[Issue], recent_issue: Issue | None) -> GSEDetailsResponse:
    """Create a GSEDetailsResponse from a GSE model and its issues."""
    serialized_issue = await serialize_most_recent_issue(recent_issue) if recent_issue else None
    
    return GSEDetailsResponse(
        gse_id=gse_model.gse_id or "N/A",
        old_gse_id=gse_model.old_gse_id or "N/A",
        gse_type=gse_model.gse_type or "N/A",
        model=gse_model.model or "N/A",
        manufacturer=gse_model.manufacturer or "N/A",
        location=gse_model.location or "N/A",
        status=gse_model.status or "N/A",
        issue_count=len(issues),
        type_of_fuel=gse_model.type_of_fuel or "N/A",
        in_use=gse_model.in_use or False,
        most_recent_issue=serialized_issue,
        lift_inspection_expires=format_date(gse_model.lift_inspection_expires),
        latest_service_chassi=format_date(gse_model.latest_service_chassi),
        latest_service_unit=format_date(gse_model.latest_service_unit),
        capacity=float(gse_model.capacity or 0.0),
        details="success",
        error=None
    )

async def details_request(request: Request) -> Response:
    """POST route to handle requests for GSE details."""
    try:
        logger.info(f"{Fore.CYAN}📥 Received request for GSE details{Style.RESET_ALL}")
        
        # Parse request
        gse_details_request = GSEDetailsRequest()
        gse_details_request.ParseFromString(await request.body())
        logger.info(f"{Fore.GREEN}✅ Validation successful for GSE ID: {gse_details_request.gse_id}{Style.RESET_ALL}")

        # Fetch GSE model
        gse_model = await GroundSupportEquiptment.get_or_none(gse_id=gse_details_request.gse_id)
        if not gse_model:
            logger.warning(f"{Fore.RED}❌ GSE model not found for ID: {gse_details_request.gse_id}{Style.RESET_ALL}")
            return Response(
                content=GSEDetailsResponse(error="The requested model could not be found.").SerializeToString(),
                media_type="application/protobuf",
                status_code=404,
            )

        # Get issues and most recent issue
        issues = await Issue.filter(gse_id=gse_details_request.gse_id).all()
        recent_cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=5)
        most_recent_issue = next(
            (issue for issue in sorted(issues, key=lambda x: x.reported_at, reverse=True)
             if issue.reported_at >= recent_cutoff),
            None
        ) if issues else None

        # Create and return response
        response_data = await create_gse_response(gse_model, issues, most_recent_issue)
        logger.success(f"{Fore.GREEN}🎉 Successfully fetched GSE details for ID: {gse_details_request.gse_id}{Style.RESET_ALL}")
        
        return Response(
            content=response_data.SerializeToString(),
            media_type="application/protobuf",
            status_code=200
        )

    except OperationalError as e:
        logger.critical(f"{Fore.MAGENTA}💥 Database operation failed: {e}{Style.RESET_ALL}")
        return Response(
            content=GSEDetailsResponse(error=f"Database operation failed: {str(e)}").SerializeToString(),
            media_type="application/protobuf",
            status_code=500
        )

    except Exception as e:
        logger.exception(f"{Fore.RED}🔥 Unexpected error occurred: {e}{Style.RESET_ALL}")
        return Response(
            content=GSEDetailsResponse(error=f"Unexpected error occurred: {str(e)}").SerializeToString(),
            media_type="application/protobuf",
            status_code=500
        )
    
async def fetch_gse(request: Request) -> Response:
    
    models: list[GroundSupportEquiptment] = await GroundSupportEquiptment.all()
    
    response: ListGSEReponse = ListGSEReponse()
    for model in models:
        response.gse_id.append(model.gse_id or "N/A")
        
    return Response(
        status_code=200,
        content=response.SerializeToString()
    )
    
async def upload_field_image(request: Request) -> Response:
    
    # Parse request
    upload_image_request: UploadFieldImage = UploadFieldImage()
    upload_image_request.ParseFromString(await request.body())
    logger.info(f"{Fore.GREEN}✅ Validation successful for GSE ID: {upload_image_request.gse_id}{Style.RESET_ALL}")

    gse: GroundSupportEquiptment | None = await GroundSupportEquiptment.get_or_none(id=upload_image_request.gse_id)
    
    if not gse:
        error_response: UploadFieldImageResponse = UploadFieldImageResponse(
            success="false",
            error="GSE not found."
        )
        return Response(
            status_code=400,
            content=error_response.SerializeToString()
        )
        
    gse.field_image = upload_image_request.image
    await gse.save()
    
    response: UploadFieldImageResponse = UploadFieldImageResponse (
        success="true"
    )
    
    return Response(
        status_code=200,
        content=response.SerializeToString()
    )