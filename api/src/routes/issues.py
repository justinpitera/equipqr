"""
routes/issues.py - Routes regarding issues.

    Includes:
        - Viewing issue(s)
        - Submitting issues.

Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard

# Third-party
from pydantic import BaseModel
from starlette.requests import Request

# Local

# Initialization
class _GSEDetailsRequest(BaseModel):
    gse_id: str

class _GSEIssueSubmission(BaseModel):
    gse_id: str

async def submit_issue(request: Request):
    return