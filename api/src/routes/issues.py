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
from typing import Any
from pydantic import BaseModel
from starlette.requests import Request

# Local

# Initialization
class _GSEDetailsRequest(BaseModel):
    gse_id: str

class _GSEIssueSubmission(BaseModel):
    gse_id: str
    is_operable: bool
    issue_

async def submit_issue(request: Request):
    body: dict[str, Any] = await request.json()
    submitted_issue_data: _GSEIssueSubmission = _GSEIssueSubmission(**body)
    
    is_operable: bool = submitted_issue_data.is_operable
    issue_desc
    return