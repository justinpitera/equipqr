"""
routes/issues.py - Routes regarding issues.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from __future__ import annotations

# Third-party
from pydantic import BaseModel, ValidationError, field_validator
from tortoise.expressions import Q
from tortoise.exceptions import OperationalError, DoesNotExist
from starlette.requests import Request
from starlette.responses import JSONResponse
from loguru import logger
from colorama import Fore, Style

# Local
from src.models import Location


async def fetch_locations(request: Request) -> JSONResponse:
    """POST route for requesting airport locations"""

    class _FetchLocationRequest(BaseModel):
        """Pydantic model to validate incoming requests to request airport locations."""
        icao_code: str

        @field_validator("icao_code")
        def validate_icao_code(cls, value: str) -> str:
            if not value.isalnum() or len(value) != 4:
                raise ValueError("icao_code must be a 4-character alphanumeric string.")
            return value

    try:
        body = await request.json()
        icao_code = body.get("icao_code", "").strip()
        validated_request: _FetchLocationRequest = _FetchLocationRequest(icao_code=icao_code)
    except ValidationError as e:
        logger.error(f"{Fore.RED}Validation Error: {e}{Style.RESET_ALL}")
        return JSONResponse(
            content={"error": "Invalid input data", "details": e.errors()}, status_code=400
        )
    except Exception as e:
        logger.error(f"{Fore.RED}Unexpected Error: {e}{Style.RESET_ALL}")
        return JSONResponse(
            content={"error": "An unexpected error occurred"}, status_code=500
        )

    try:
        locations: list[Location] = await Location.filter(Q(icao_code=validated_request.icao_code)).all()
        if not locations:
            return JSONResponse(
                content={"error": "No locations found for the provided ICAO code"}, status_code=404
            )

        location_data: list[dict[str, str]] = [
            {
                "id": str(location.id),
                "icao_code": location.icao_code,
                "location": location.location,
                "aircraft": location.aircraft,
                "location_type": location.location_type.name,
            }
            for location in locations
        ]

        return JSONResponse(content={"locations": location_data}, status_code=200)

    except DoesNotExist as e:
        logger.warning(f"{Fore.YELLOW}DoesNotExist Error: {e}{Style.RESET_ALL}")
        return JSONResponse(
            content={"error": "Location not found", "details": str(e)}, status_code=404
        )
    except OperationalError as e:
        logger.error(f"{Fore.RED}Database Operational Error: {e}{Style.RESET_ALL}")
        return JSONResponse(
            content={"error": "Database error occurred", "details": str(e)}, status_code=500
        )
    except Exception as e:
        logger.error(f"{Fore.RED}Unexpected Error: {e}{Style.RESET_ALL}")
        return JSONResponse(
            content={"error": "An unexpected error occurred", "details": str(e)}, status_code=500
        )
