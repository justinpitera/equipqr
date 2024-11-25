from starlette.responses import FileResponse

async def homepage(request) -> FileResponse:
    _ = request.path_params.get("path")
    return FileResponse('web/index.html')
