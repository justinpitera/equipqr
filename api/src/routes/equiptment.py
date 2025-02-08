"""
routes/issues.py - Routes regarding issues.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from __future__ import annotations
from typing import Any
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
        fetched_gse_model: GroundSupportEquiptment | None = await GroundSupportEquiptment.get_or_none(gse_id=gse_details_request.gse_id)

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
            issue_count=len(issues),
            type_of_fuel=fetched_gse_model.type_of_fuel,
            in_use=fetched_gse_model.in_use,
            most_recent_issue=serialized_most_recent_issue,
            lift_inspection_expires=fetched_gse_model.lift_inspection_expires.isoformat() if fetched_gse_model.lift_inspection_expires else "",
            latest_service_chassi=fetched_gse_model.latest_service_chassi,
            latest_service_unit=str(fetched_gse_model.latest_service_unit),
            capacity = float(fetched_gse_model.capacity) if fetched_gse_model.capacity is not None else 0.0, # pyright: ignore
            details="success",
            error=None
        )

        logger.success(f"{Fore.GREEN}🎉 Successfully fetched GSE details for ID: {gse_details_request.gse_id}{Style.RESET_ALL}")
        
        # Serialize and return the protobuf response
        return Response(content=response_data.SerializeToString(), media_type="application/protobuf", status_code=200)

    except OperationalError as e:
        logger.critical(f"{Fore.MAGENTA}💥 Database operation failed: {e}{Style.RESET_ALL}")
        error_response = GSEDetailsResponse(error="Database operation failed: " + str(e))
        return Response(content=error_response.SerializeToString(), media_type="application/protobuf", status_code=500)

    except Exception as e:
        logger.exception(f"{Fore.RED}🔥 Unexpected error occurred: {e}{Style.RESET_ALL}")    
        error_response = GSEDetailsResponse(error="Unexpected error occurred: " + str(e))
        return Response(content=error_response.SerializeToString(), media_type="application/protobuf", status_code=500)
    
async def fetch_gse(request: Request) -> Response:
    
    models: list[GroundSupportEquiptment] = await GroundSupportEquiptment.all()
    
    response: ListGSEReponse = ListGSEReponse()
    for model in models:
        response.gse_id.append(model.gse_id)
        
    return Response(
        status_code=200,
        content=response.SerializeToString()
    )