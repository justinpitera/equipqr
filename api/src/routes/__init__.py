"""
src/routes/__init__.py - API Routes initialization module.

Date: December 9, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

from src.routes.index import homepage
from src.routes.health import get_status
from src.routes.issues import details_request, submit_issue
from src.routes.auth import auth_user, set_token
from src.routes.media import fetch_issue_attachment

__all__: list[str] = [
    "homepage",
    "get_status",
    "details_request",
    "submit_issue",
    "auth_user",
    "set_token",
    "fetch_issue_attachment",
]