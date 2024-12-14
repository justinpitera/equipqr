"""
src/routes/index.py - This file contains routes for the index of the frontend.

Date: December 11, 2024

Authors:
    Justin Pitera (justinpitera@gmail.com)
"""

# Third-party
from starlette.requests import Request
from starlette.responses import FileResponse


async def homepage(request: Request) -> FileResponse:
    """Route for the index. Handles all traffic to the frontend."""
    _= request.path_params.get("path")
    return FileResponse(path='web/index.html')
