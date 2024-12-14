"""
routes/health.py - Routes regarding api health.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Third-party
from starlette.requests import Request
from starlette.responses import JSONResponse

# Local
from src import API_VERSION

async def get_status(_: Request) -> JSONResponse:
    response: JSONResponse = JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "version": API_VERSION
        }
    )
    return response