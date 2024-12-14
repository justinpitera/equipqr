from src.routes.auth import auth_user as auth_user, set_token as set_token
from src.routes.health import get_status as get_status
from src.routes.index import homepage as homepage
from src.routes.issues import delete_issues as delete_issues, details_request as details_request, fetch_issues as fetch_issues, submit_issue as submit_issue
from src.routes.locations import fetch_locations as fetch_locations
from src.routes.media import fetch_issue_attachment as fetch_issue_attachment

__all__ = ['homepage', 'get_status', 'details_request', 'submit_issue', 'fetch_issues', 'delete_issues', 'auth_user', 'set_token', 'fetch_issue_attachment', 'fetch_locations']
