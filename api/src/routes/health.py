"""
routes/health.py - Routes regarding api health.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Third-party
from starlette.requests import Request
from starlette.responses import Response

# Local
from src import API_VERSION

# Protobufs
from src.protos.requests.v1.requests_pb2 import HealthStatusResponse

async def get_status(_: Request) -> Response:
    response: HealthStatusResponse = HealthStatusResponse(
        status="healthy",
        version=API_VERSION
    )
    return Response(
        status_code=200,
        content=response.SerializeToString()
    )
