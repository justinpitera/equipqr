"""
src/main.py - ASGI app initialization script.

Date: November 25, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from typing import Literal
from uuid import uuid4

# Third-party
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from tortoise import Tortoise # pyright: ignore
from loguru import logger

# Local
from src import API_CONFIG, TORTOISE_CONFIG, RedisClient
from src.models import CrewMember
from src.database import database_importer, location_importer
from src.enums import CrewMemberPositionEnum

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
    fetch_locations
)


async def _validate_master_account(email: str = API_CONFIG["auth"]["master"]) -> None:
    """
    Validates the master account, ensuring only one account has is_master=True.
    Creates or updates the master account as needed.
    """
    logger.info(f"Validating master account: {email}...")

    # Find current master and reset if needed
    if (current_master := await CrewMember.filter(is_master=True).first()) and current_master.email != email:
        logger.warning(f"Updating master from {current_master.email} to {email}...")
        current_master.is_master = False
        await current_master.save()

    # Get or create the crew member
    crew_member: CrewMember | None = await CrewMember.filter(email=email).first()
    if not crew_member:
        logger.warning(f"Master account for {email} does not exist, creating a new account now...")
        _ = await CrewMember.create(
            id=uuid4(),
            email=email,
            language_preference="EN",
            position=CrewMemberPositionEnum.MANAGEMENT,
            is_master=True,
        )
    else:
        crew_member.is_master = True
        crew_member.position = CrewMemberPositionEnum.MANAGEMENT
        await crew_member.save()

    logger.success(f"Validated master account for {email} successfully!")

async def startup() -> None:
    # Startup
    logger.info("Connecting to database...")    
    await Tortoise.init(config=TORTOISE_CONFIG) # pyright: ignore[reportUnknownMemberType]
    await Tortoise.generate_schemas()
    
    await _validate_master_account()
    # await generate_issues()
    await database_importer()
    await location_importer("./locations.csv", "EKCH")
    logger.success("Startup completed successfully!") 

async def shutdown() -> None:
    await Tortoise.close_connections()
    logger.success("Database connections closed successfully!")
    await RedisClient.close_all()
    logger.success("Redis connections closed successfully!")
    
def init_asgi() -> Starlette:
    """Initializes the Starlette API."""
    _ASGI: Starlette = Starlette(
        on_startup=[startup],
        on_shutdown=[shutdown]
    )
    
    _ASGI.add_middleware(
        middleware_class=CORSMiddleware,
        allow_credentials=API_CONFIG["cors"]["allow_credentials"], 
        allow_origins=API_CONFIG["cors"]["allow_origins"],
        allow_methods=API_CONFIG["cors"]["allow_methods"],
        allow_headers=API_CONFIG["cors"]["allow_headers"]
    )

    # api route prefix (used for production only)
    _API_ROUTE_PREFIX: Literal["/api", ""] = "/api" if API_CONFIG["api"]["mode"] == "production" else ""

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

    # Media
    _ASGI.add_route(path=f"{_API_ROUTE_PREFIX}/media/attachment", route=fetch_issue_attachment, methods=["GET"])
    
    # Index
    _ASGI.mount(path="/", app=StaticFiles(directory="web", html=True), name="_app")
    _ASGI.add_route(path="/{path:path}", route=homepage, methods=["GET"]) # Handles Index subpaths
    
    return _ASGI