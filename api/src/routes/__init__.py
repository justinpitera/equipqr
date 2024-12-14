"""
src/routes/__init__.py - API Routes initialization module.

Date: December 9, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

from src.routes.index import homepage
from src.routes.health import get_status
from src.routes.issues import delete_issues, details_request, submit_issue, fetch_issues
from src.routes.auth import auth_user, set_token
from src.routes.media import fetch_issue_attachment
from src.routes.locations import fetch_locations

__all__: list[str] = [
    "homepage",
    "get_status",
    "details_request",
    "submit_issue",
    "fetch_issues",
    "delete_issues",
    "auth_user",
    "set_token",
    "fetch_issue_attachment",
    "fetch_locations"
]