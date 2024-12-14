from starlette.requests import Request as Request
from starlette.responses import Response

async def fetch_issue_attachment(request: Request) -> Response: ...
