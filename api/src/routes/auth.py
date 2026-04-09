"""
routes/auth.py - HTTP layer for authentication.

This module is intentionally thin: parse the request, call the service,
return a response.  No business logic lives here.

Date: December 9, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

from tortoise.exceptions import DoesNotExist, OperationalError
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from loguru import logger

from src import API_CONFIG
from src.protos.requests.v1.requests_pb2 import LoginRequest, LoginResponse
import src.services.auth as auth_service
from src.services.auth import build_tenant_base_url, NotATenantMember, TenantNotFound

BASE_URL: str = API_CONFIG["api"]["domain"]


def _extract_tenant_slug(request: Request) -> str | None:
    """
    Derive the tenant slug from the Host header subdomain.
    e.g.  acme.localhost  →  'acme'
          localhost        →  None
    """
    host = request.headers.get("host", "").split(":")[0]  # strip port
    parts = host.split(".")
    # A bare hostname (localhost, example.com) has no meaningful subdomain
    if len(parts) >= 2 and parts[0] not in ("www", ""):
        return parts[0]
    return None


async def set_token(request: Request) -> RedirectResponse:
    """Exchanges a one-time magic-link token for a session cookie and redirects home."""
    token = request.query_params.get("token")
    if not token:
        return RedirectResponse(url=f"{BASE_URL}/", status_code=302)

    try:
        result = await auth_service.exchange_magic_token(token)
        if result is None:
            return RedirectResponse(url=f"{BASE_URL}/", status_code=302)
        member, tenant = result
    except DoesNotExist:
        logger.error("Magic token pointed to a non-existent user or tenant.")
        return RedirectResponse(url=f"{BASE_URL}/error", status_code=302)
    except OperationalError as e:
        logger.error(f"Database error during token exchange: {e}")
        return RedirectResponse(url=f"{BASE_URL}/", status_code=302)

    access_token = await auth_service.create_session(email=member.email)
    cookie_opts = auth_service.get_cookie_settings()

    tenant_url = build_tenant_base_url(tenant.slug)
    response = RedirectResponse(url=f"{tenant_url}/", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="strict", **cookie_opts)
    response.set_cookie(key="auth", value="true", httponly=False, samesite="strict", **cookie_opts)
    response.set_cookie(key="role", value=member.position.value, httponly=False, samesite="strict", **cookie_opts)
    response.set_cookie(key="language", value=member.language_preference.lower(), httponly=False, samesite="strict", **cookie_opts)
    response.set_cookie(key="tenant_slug", value=tenant.slug, httponly=False, samesite="strict", **cookie_opts)
    response.set_cookie(key="tenant_name", value=tenant.name, httponly=False, samesite="strict", **cookie_opts)
    return response


async def auth_user(request: Request) -> Response:
    """Accepts a protobuf login request and dispatches a magic-link email."""
    try:
        body = await request.body()
        proto_request = LoginRequest()
        proto_request.ParseFromString(body)

        # Prefer the tenant_slug from the protobuf payload; fall back to Host subdomain
        tenant_slug: str | None = proto_request.tenant_slug or _extract_tenant_slug(request)

        if not tenant_slug:
            return Response(
                content=LoginResponse(message="No tenant specified. Please access via your tenant subdomain.").SerializeToString(),
                status_code=400,
            )

        tenant = await auth_service.initiate_magic_link(email=proto_request.email, tenant_slug=tenant_slug)

        return Response(
            content=LoginResponse(message="Login email sent", tenant_name=tenant.name).SerializeToString(),
            status_code=200,
        )

    except ValueError as e:
        # Email domain not on allow-list
        logger.warning(str(e))
        return Response(
            content=LoginResponse(message=str(e)).SerializeToString(),
            status_code=403,
        )
    except TenantNotFound:
        return Response(
            content=LoginResponse(message="Tenant not found.").SerializeToString(),
            status_code=404,
        )
    except NotATenantMember:
        return Response(
            content=LoginResponse(message="User is not a member of this tenant.").SerializeToString(),
            status_code=403,
        )
    except Exception as e:
        logger.error(f"Unexpected error in auth_user: {e}")
        return Response(
            content=LoginResponse(message="Unexpected error occurred").SerializeToString(),
            status_code=500,
        )
