"""
routes/admin.py - Admin-only provisioning endpoints.

Every route here requires the X-Admin-Secret header to match the
ADMIN_SECRET environment variable.  If ADMIN_SECRET is not set the
endpoints refuse all requests (fail-secure).

Endpoints
---------
POST /api/admin/tenant          — create a new tenant
POST /api/admin/tenant/invite   — add a member to a tenant and send an invite

Date: April 9, 2026

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
import re
import secrets as _secrets
from uuid import uuid4

# Third-party
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from tortoise.exceptions import DoesNotExist, IntegrityError

# Local
from src import API_CONFIG
from src.enums import CrewMemberPositionEnum
from src.models import Member, Tenant
import src.services.auth as auth_service

_ADMIN_SECRET: str = API_CONFIG["admin"]["secret"]
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,62}$")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _check_auth(request: Request) -> bool:
    """Return True if the request carries the correct admin secret."""
    if not _ADMIN_SECRET:
        # No secret configured — refuse all requests for safety.
        return False
    provided = request.headers.get("X-Admin-Secret", "")
    return _secrets.compare_digest(provided, _ADMIN_SECRET)


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

async def create_tenant(request: Request) -> Response:
    """
    POST /api/admin/tenant

    Create a new tenant.

    Request body (JSON)::

        {
            "name": "Acme Airlines",
            "slug": "acme"          // lowercase, alphanumeric + dashes
        }

    Returns 201 with ``{"id", "name", "slug"}`` on success.
    """
    if not _check_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    name: str = (body.get("name") or "").strip()
    slug: str = (body.get("slug") or "").strip().lower()

    if not name:
        return JSONResponse({"error": "'name' is required"}, status_code=400)
    if not slug or not _SLUG_RE.match(slug):
        return JSONResponse(
            {"error": "'slug' must be lowercase alphanumeric with optional dashes (max 63 chars)"},
            status_code=400,
        )

    try:
        tenant = await Tenant.create(id=uuid4(), name=name, slug=slug)
    except IntegrityError:
        return JSONResponse(
            {"error": "A tenant with that name or slug already exists"},
            status_code=409,
        )

    logger.success(f"Admin created tenant '{slug}' (id={tenant.id})")
    return JSONResponse(
        {"id": str(tenant.id), "name": tenant.name, "slug": tenant.slug},
        status_code=201,
    )


async def invite_user(request: Request) -> Response:
    """
    POST /api/admin/tenant/invite

    Add a member to a tenant and optionally send them a magic-link invite
    email so they can log in immediately.

    Request body (JSON)::

        {
            "email":               "user@example.com",
            "tenant_slug":         "acme",
            "position":            "employee" | "mechanic" | "master",
            "language_preference": "en",          // optional, default "en"
            "send_invite":         true            // optional, default true
        }

    Returns 201 with ``{"id", "email", "tenant"}`` on success.
    """
    if not _check_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    email: str = (body.get("email") or "").strip().lower()
    tenant_slug: str = (body.get("tenant_slug") or "").strip().lower()
    position_raw: str = (body.get("position") or "").strip().lower()
    language: str = (body.get("language_preference") or "en").strip().lower()
    send_invite: bool = bool(body.get("send_invite", True))

    if not email or "@" not in email:
        return JSONResponse(
            {"error": "'email' is required and must be a valid address"},
            status_code=400,
        )
    if not tenant_slug:
        return JSONResponse({"error": "'tenant_slug' is required"}, status_code=400)

    try:
        position = CrewMemberPositionEnum(position_raw)
    except ValueError:
        valid = [e.value for e in CrewMemberPositionEnum]
        return JSONResponse({"error": f"'position' must be one of: {valid}"}, status_code=400)

    tenant = await Tenant.get_or_none(slug=tenant_slug, is_active=True)
    if not tenant:
        return JSONResponse({"error": f"Tenant '{tenant_slug}' not found"}, status_code=404)

    try:
        member = await Member.create(
            id=uuid4(),
            email=email,
            language_preference=language,
            position=position,
            tenant=tenant,
        )
    except IntegrityError:
        return JSONResponse(
            {"error": "A member with that email already exists"},
            status_code=409,
        )

    logger.success(f"Admin created member '{email}' in tenant '{tenant_slug}'")

    if send_invite:
        try:
            await auth_service.invite_member(email=email, tenant_slug=tenant_slug)
        except Exception as e:
            logger.warning(f"Member created but invite email failed: {e}")
            return JSONResponse(
                {
                    "id": str(member.id),
                    "email": member.email,
                    "tenant": tenant_slug,
                    "warning": "Member created but invite email could not be sent",
                },
                status_code=201,
            )

    return JSONResponse(
        {"id": str(member.id), "email": member.email, "tenant": tenant_slug},
        status_code=201,
    )
