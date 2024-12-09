from starlette.requests import Request
from starlette.responses import FileResponse

async def homepage(request: Request) -> FileResponse:
    _= request.path_params.get("path")
    return FileResponse(path='web/index.html')
