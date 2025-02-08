import uvicorn
from starlette.applications import Starlette
from starlette.responses import FileResponse
from starlette.routing import Route
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from pathlib import Path

app = Starlette()
app.add_middleware(HTTPSRedirectMiddleware)

INDEX_PATH = Path.cwd() / "index.html"

async def index(request):
    if not INDEX_PATH.exists():
        return FileResponse(INDEX_PATH, status_code=404)
    return FileResponse(INDEX_PATH)

app.routes.append(Route("/", index))

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9443,
        ssl_keyfile="server.key",
        ssl_certfile="server.crt",
        ssl_ca_certs="ca.crt",
        ssl_cert_reqs=2  # Enforce client certificate verification
    )
