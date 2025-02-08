"""
routes/issues.py - Routes regarding issues.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from __future__ import annotations

# Third-party
from tortoise.expressions import Q
from tortoise.exceptions import OperationalError, DoesNotExist
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from loguru import logger
from colorama import Fore, Style

# Local
from src.models import Location

# Protobufs
from src.protos.requests.v1.requests_pb2 import FetchGatesRequest, FetchGatesResponse


async def fetch_locations(request: Request) -> Response | JSONResponse:
    """POST route for requesting airport locations"""

    try:
        body: bytes = await request.body()
        fetch_locations_request: FetchGatesRequest = FetchGatesRequest()
        fetch_locations_request.ParseFromString(body)
    except Exception as e:
        logger.error(f"{Fore.RED}Unexpected Error: {e}{Style.RESET_ALL}")
        return JSONResponse(
            content={"error": "An unexpected error occurred"}, status_code=500
        )

    try:
        locations: list[Location] = await Location.filter(Q(icao_code=fetch_locations_request.icao_code)).all()
        if not locations:
            error_response: FetchGatesResponse = FetchGatesResponse()
            error_response.error = "No locations found for the provided ICAO code"
            return Response(
                content=error_response.SerializeToString(), 
                media_type="application/x-protobuf",
                status_code=404
            )

        fetch_gates_response = FetchGatesResponse()
        for location in locations:
            gate = fetch_gates_response.gates.add()
            gate.id = str(location.id)
            gate.name = location.location  # Assuming "location" is the name; adjust as needed
            gate.type = location.location_type

        return Response(
            content=fetch_gates_response.SerializeToString(), 
            media_type="application/x-protobuf",
            status_code=200
        )

    except DoesNotExist as e:
        logger.warning(f"{Fore.YELLOW}DoesNotExist Error: {e}{Style.RESET_ALL}")
        dne_error: FetchGatesResponse = FetchGatesResponse()
        dne_error.error = "No locations found for the provided ICAO code"
        return Response(
            content=dne_error.SerializeToString(), 
            media_type="application/x-protobuf",
            status_code=404
        )
    except OperationalError as e:
        logger.error(f"{Fore.RED}Database Operational Error: {e}{Style.RESET_ALL}")
        operational_error: FetchGatesResponse = FetchGatesResponse()
        operational_error.error = f"OperationalError occurred: {e}"
        return Response(
            content=operational_error.SerializeToString(), 
            media_type="application/x-protobuf",
            status_code=404
        )
    except Exception as e:
        logger.error(f"{Fore.RED}Unexpected Error: {e}{Style.RESET_ALL}")
        unhandled_exception: FetchGatesResponse = FetchGatesResponse()
        unhandled_exception.error = f"OperationalError occurred: {e}"
        return Response(
            content=unhandled_exception.SerializeToString(), 
            media_type="application/x-protobuf",
            status_code=404
        )
