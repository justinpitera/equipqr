"""
routes/health.py - Routes regarding api health.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard

# Third-party
from typing import Any
from starlette.requests import Request
from starlette.responses import JSONResponse

# Local
from .. import API_VERSION

async def get_status(request: Request) -> JSONResponse:
    response: JSONResponse = JSONResponse(
        status_code=200,
        content={
            "version": API_VERSION
        }
    )
    return response