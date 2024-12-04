"""
routes/issues.py - Routes regarding issues.

    Includes:
        
        - Viewing issue(s)
        - Submitting issues.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Third-party
from typing import Any
from pydantic import BaseModel, ValidationError
from tortoise.exceptions import DoesNotExist, OperationalError
from starlette.requests import Request
from starlette.responses import JSONResponse
from loguru import logger
from colorama import Fore, Style

# Local
from src.models import GroundSupportEquiptment


async def details_request(request: Request) -> JSONResponse:
    """GET route to handle requests to the database for GSE."""
    
    class _GSEDetailsRequest(BaseModel):
        """Pydantic validation model for incoming GSE detail requests."""
        gse_id: str

    try:
        # Parse and validate the request body
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

        # Safely construct the response data
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
        response_data = {field: getattr(fetched_gse_model, field, None) for field in fields_to_include}
        logger.success(f"{Fore.GREEN}🎉 Successfully fetched GSE details for ID: {gse_details_request_data.gse_id}{Style.RESET_ALL}")
        
        return JSONResponse(status_code=200, content=response_data)

    except ValidationError as e:
        logger.error(f"{Fore.RED}🚨 Validation Error: {e}{Style.RESET_ALL}")
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "details": e.errors()}
        )
    except (OperationalError, DoesNotExist) as e:
        logger.critical(f"{Fore.MAGENTA}💥 Database operation failed: {e}{Style.RESET_ALL}")
        return JSONResponse(
            status_code=500,
            content={"error": "Database operation failed", "details": str(e)}
        )
    except Exception as e:
        logger.exception(f"{Fore.RED}🔥 Unexpected error occurred: {e}{Style.RESET_ALL}")
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected error occurred", "details": str(e)}
        )

# async def submit_issue(request: Request) -> JSONResponse:
# class _GSEIssueSubmission(BaseModel):
#     """Pydantic validation model for incoming GSE issue submissions."""
#     gse_id: str
#     is_operable: bool
#     issue_description: str
#     # TODO: Add field for attachments
#     body: dict[str, Any] = await request.json()
#     submitted_issue_data: _GSEIssueSubmission = _GSEIssueSubmission(**body)
    
#     # Generated data (by api)
#     new_issue_id: UUID = uuid4()
    
#     # Submitted (validated data)
#     is_operable: bool = submitted_issue_data.is_operable
#     issue_description: str = submitted_issue_data.issue_description
    
#     return