from starlette.requests import Request as Request
from starlette.responses import FileResponse

async def homepage(request: Request) -> FileResponse: ...
