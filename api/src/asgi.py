"""
src/main.py - ASGI app initialization script.

Date: November 25, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from typing import Literal
from uuid import uuid4
from contextlib import asynccontextmanager

# Third-party
from fastapi.applications import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import RegisterTortoise
from loguru import logger

# Local
from src import API_CONFIG, TORTOISE_CONFIG, RedisClient
from src.database import database_importer, location_importer

from src.routes import (
    retrieve_field_image,
    upload_field_image,
    get_status,
    fetch_gse,
    details_request,
    leave_comment,
    submit_issue,
    edit_issue,
    delete_issues,
    fetch_issues,
    fetch_issue_attachment,
    auth_user,
    set_token,
    homepage,
    fetch_locations,
    fetch_tenant_logo,
    register_tenant,
    upload_tenant_logo,
    invite_tenant_member,
    create_tenant,
    invite_user,
)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Startup
    logger.info("Connecting to database...")
    async with RegisterTortoise(app=app, config=TORTOISE_CONFIG, generate_schemas=True):
        # await generate_issues()
        await database_importer()
        await location_importer("./locations.csv", "EKCH")
        logger.success("Startup completed successfully!")

        yield
        # RegisterTortoise.__aexit__ closes DB connections

    # Shutdown
    logger.success("Database connections closed successfully!")
    await RedisClient.close_all()
    logger.success("Redis connections closed successfully!")
    
def init_asgi() -> FastAPI:
    """Initializes the Starlette API."""
    _ASGI: FastAPI = FastAPI(
        lifespan=_lifespan,
    )
    
    _ASGI.add_middleware(
        middleware_class=CORSMiddleware,
        allow_credentials=API_CONFIG["cors"]["allow_credentials"], 
        allow_origins=API_CONFIG["cors"]["allow_origins"],
        allow_methods=API_CONFIG["cors"]["allow_methods"],
        allow_headers=API_CONFIG["cors"]["allow_headers"]
    )

    # api route prefix (used for production only)
    _API_ROUTE_PREFIX: Literal["/api", ""] = "/api" if API_CONFIG["api"]["mode"] == "production" else "/api"

    # Health
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/health/status", route=get_status, methods=["GET"])
    
    # GroundSupportEquiptment (GSEs) related
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/details", route=details_request, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/all", route=fetch_gse, methods=["GET"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/image/upload", route=upload_field_image, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/image/retrieve", route=retrieve_field_image, methods=["POST"])
    
    # Issues
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/issues/submit", route=submit_issue, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/issues/delete", route=delete_issues, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/issues/fetch", route=fetch_issues, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/issues/comment", route=leave_comment, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/gse/issues/edit", route=edit_issue, methods=["POST"])

    # Locations
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/locations/fetch", route=fetch_locations, methods=["POST"])
    
    # Authentication
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/auth", route=auth_user, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/set-token", route=set_token, methods=["GET"])

    # Tenant
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/tenant/logo", route=fetch_tenant_logo, methods=["GET"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/tenant/logo", route=upload_tenant_logo, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/tenant/register", route=register_tenant, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/tenant/invite", route=invite_tenant_member, methods=["POST"])

    # Self-service registration (public)
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/register", route=register_tenant, methods=["POST"])

    # Admin provisioning
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/admin/tenant", route=create_tenant, methods=["POST"])
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/admin/tenant/invite", route=invite_user, methods=["POST"])

    # Media
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/media/attachment", route=fetch_issue_attachment, methods=["GET"])
    
    # Index
    _ASGI.mount(path="/", app=StaticFiles(directory="web", html=True), name="_app")
    _ASGI.add_route(path="/{path:path}", route=homepage, methods=["GET"]) # Handles Index subpaths
    
    return _ASGI