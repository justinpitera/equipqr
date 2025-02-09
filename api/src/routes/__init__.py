"""
src/routes/__init__.py - API Routes initialization module.

Date: December 9, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

from src.routes.index import homepage
from src.routes.health import get_status
from src.routes.equiptment import fetch_gse, details_request, upload_field_image, retrieve_field_image
from src.routes.issues import delete_issues, submit_issue, fetch_issues, leave_comment, edit_issue
from src.routes.auth import auth_user, set_token
from src.routes.media import fetch_issue_attachment
from src.routes.locations import fetch_locations

__all__: list[str] = [
    "homepage",
    "upload_field_image",
    "retrieve_field_image",
    "get_status",
    "submit_issue",
    "fetch_gse",
    "details_request",
    "fetch_issues",
    "leave_comment",
    "edit_issue",
    "delete_issues",
    "auth_user",
    "set_token",
    "fetch_issue_attachment",
    "fetch_locations"
]