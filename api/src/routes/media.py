"""
src/routes/media.py - This file contains several routes used for media queries.

Date: December 9, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard

# Third-party
from starlette.requests import Request
from starlette.responses import JSONResponse

# Local

async def fetch_issue_attachment(request: Request) -> JSONResponse:
    
    return JSONResponse(status_code=200, content="WIP")