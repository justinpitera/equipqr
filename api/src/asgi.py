"""
src/main.py - ASGI app initialization script.

Date: November 25, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

# Third-party
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from loguru import logger

# Local
from . import API_CONFIG, TORTOISE_CONFIG
from src.database import database_importer
from src.routes.index import homepage
from src.routes.health import get_status
from src.routes.issues import details_request, submit_issue

@asynccontextmanager
async def _lifespan(_app: Starlette) -> AsyncGenerator[None, None]:
    """Lifespan to handle the runtime duration of the Starlette app."""
    # Startup
    logger.info("Connecting to database...")    
    await Tortoise.init(config=TORTOISE_CONFIG) # pyright: ignore[reportUnknownMemberType]
    await Tortoise.generate_schemas()
    
    await database_importer()
    logger.success("Startup completed successfully!")    
    yield # Yielding to Starlette to run the server.
    # Shutdown
    await Tortoise.close_connections()
    logger.success("Database connections closed successfully!")    
    
def init_asgi() -> Starlette:
    """Initializes the Starlette API."""
    _ASGI: Starlette = Starlette(
        debug=False,
        lifespan=lambda app: _lifespan(_app=app)
    )
    
    _ASGI.add_middleware(
        CORSMiddleware,
        allow_credentials=API_CONFIG["cors"]["allow_credentials"], 
        allow_origins=API_CONFIG["cors"]["allow_origins"],
        allow_methods=API_CONFIG["cors"]["allow_methods"],
        allow_headers=API_CONFIG["cors"]["allow_headers"]
    )

    # api route prefix (used for production only)
    _API_ROUTE_PREFIX = "/api" if API_CONFIG["api"]["mode"] == "production" else ""

    # Health
    _ASGI.add_route(f"{_API_ROUTE_PREFIX}/health/status", get_status, methods=["GET"])
    
    # GroundSupportEquiptment (GSEs) related
    _ASGI.add_route(f"{_API_ROUTE_PREFIX}/gse/details", details_request, methods=["POST"])
    _ASGI.add_route(f"{_API_ROUTE_PREFIX}/gse/issues/submit", submit_issue, methods=["POST"])
        
    # Index    
    _ASGI.mount("/", StaticFiles(directory="web", html=True), name="_app")
    _ASGI.add_route("/{path:path}", homepage, methods=["GET"]) # Handles Index subpaths
    
    return _ASGI