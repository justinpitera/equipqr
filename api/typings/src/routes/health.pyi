from starlette.requests import Request as Request
from starlette.responses import JSONResponse

async def get_status(_: Request) -> JSONResponse: ...
