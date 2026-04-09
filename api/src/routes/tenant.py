"""
routes/tenant.py - Routes related to tenant metadata (logo, etc.)

Date: April 9, 2026

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
import io
import re
from uuid import uuid4

# Third-party
from minio import Minio
from minio.error import S3Error
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from loguru import logger
from tortoise.exceptions import IntegrityError

# Local
from src import API_CONFIG
from src.enums import CrewMemberPositionEnum
from src.models import Member, Tenant
import src.services.auth as auth_service

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,62}$")
_LOGO_BUCKET = "tenant-logos"
_LOGO_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_MIME_TO_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
}


def _get_minio_client() -> Minio:
    return Minio(
        endpoint=f"{API_CONFIG['object_storage']['address']}:{API_CONFIG['object_storage']['port']}",
        access_key=API_CONFIG['object_storage']['access_key'],
        secret_key=API_CONFIG['object_storage']['secret_key'],
        secure=API_CONFIG['object_storage']['secure'],
    )


def _extract_tenant_slug(request: Request) -> str | None:
    """Extract the tenant slug from the Host header subdomain."""
    host: str = request.headers.get("host", "")
    hostname = host.split(":")[0]  # strip port if present
    parts = hostname.split(".")
    if len(parts) >= 2 and parts[0] not in ("www", ""):
        return parts[0]
    return None


async def fetch_tenant_logo(request: Request) -> Response:
    """
    GET /api/tenant/logo

    Returns the tenant's logo image from the ``tenant-logos`` Minio bucket.
    The object key is the tenant slug (e.g. ``acme``).
    Responds with 404 when no logo has been uploaded yet so the frontend
    can fall back gracefully to the default logo.
    """
    slug = _extract_tenant_slug(request)
    if not slug:
        return Response(status_code=404)

    tenant = await Tenant.get_or_none(slug=slug)
    if not tenant:
        return Response(status_code=404)

    client = _get_minio_client()
    bucket = _LOGO_BUCKET

    # Try common image extensions in order of preference
    for ext in ("png", "jpg", "jpeg", "gif", "webp", "svg"):
        object_name = f"{slug}.{ext}"
        mime_map = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
            "svg": "image/svg+xml",
        }
        try:
            response = client.get_object(bucket_name=bucket, object_name=object_name)
            content: bytes = response.read()
            response.close()
            response.release_conn()
            logger.info(f"Serving logo '{object_name}' for tenant '{slug}'")
            return Response(
                content=content,
                media_type=mime_map[ext],
                headers={"Cache-Control": "public, max-age=3600"},
            )
        except S3Error as e:
            if e.code == "NoSuchKey":
                continue
            logger.warning(f"S3Error fetching logo '{object_name}': {e.code} - {e.message}")
            return Response(status_code=500)

    logger.info(f"No logo found in bucket '{bucket}' for tenant '{slug}'")
    return Response(status_code=404)


async def register_tenant(request: Request) -> Response:
    """
    POST /api/tenant/register

    Public self-service endpoint.  Creates a new tenant and a master member,
    optionally uploads a logo, then dispatches a magic-link invite email so
    the founder can log in immediately.

    Accepts ``multipart/form-data`` with fields::

        name     str   — organisation display name
        slug     str   — lowercase alphanumeric + dashes (max 63 chars)
        email    str   — founding master member's email address
        language str   — preferred language code (default "en")
        logo     file  — optional logo image (PNG/JPEG/GIF/WebP/SVG ≤ 5 MB)

    Returns 201 with ``{"tenant_slug", "tenant_name"}`` on success.
    """
    try:
        form = await request.form()
    except Exception:
        return JSONResponse({"error": "Expected multipart/form-data"}, status_code=400)

    name: str     = str(form.get("name")     or "").strip()
    slug: str     = str(form.get("slug")     or "").strip().lower()
    email: str    = str(form.get("email")    or "").strip().lower()
    language: str = str(form.get("language") or "en").strip().lower()
    logo_file     = form.get("logo")

    if not name:
        return JSONResponse({"error": "'name' is required"}, status_code=400)
    if not slug or not _SLUG_RE.match(slug):
        return JSONResponse(
            {"error": "'slug' must be lowercase alphanumeric with optional dashes (max 63 chars)"},
            status_code=400,
        )
    if not email or "@" not in email:
        return JSONResponse({"error": "'email' must be a valid email address"}, status_code=400)

    # ── Logo validation ──────────────────────────────────────────────────────
    logo_bytes: bytes | None = None
    logo_ext:   str   | None = None
    logo_mime:  str   | None = None

    if logo_file and hasattr(logo_file, "read"):
        content_type: str = (getattr(logo_file, "content_type", "") or "").lower()
        if content_type not in _MIME_TO_EXT:
            return JSONResponse(
                {"error": "Logo must be a PNG, JPEG, GIF, WebP, or SVG image"},
                status_code=400,
            )
        logo_bytes = await logo_file.read()
        if len(logo_bytes) > _LOGO_MAX_BYTES:
            return JSONResponse({"error": "Logo must be under 5 MB"}, status_code=400)
        logo_ext  = _MIME_TO_EXT[content_type]
        logo_mime = content_type

    # ── Create Tenant ────────────────────────────────────────────────────────
    try:
        tenant = await Tenant.create(id=uuid4(), name=name, slug=slug)
    except IntegrityError:
        return JSONResponse(
            {"error": "A tenant with that name or slug already exists"},
            status_code=409,
        )

    # ── Create master Member (roll back tenant if email already taken) ───────
    try:
        await Member.create(
            id=uuid4(),
            email=email,
            language_preference=language,
            position=CrewMemberPositionEnum.MANAGEMENT,
            tenant=tenant,
        )
    except IntegrityError:
        await tenant.delete()
        return JSONResponse(
            {"error": "That email address is already associated with another organisation"},
            status_code=409,
        )

    logger.success(f"Self-registered tenant '{slug}' (founder: {email})")

    # ── Upload logo (non-fatal) ──────────────────────────────────────────────
    if logo_bytes and logo_ext and logo_mime:
        try:
            client = _get_minio_client()
            if not client.bucket_exists(_LOGO_BUCKET):
                client.make_bucket(_LOGO_BUCKET)
            client.put_object(
                bucket_name=_LOGO_BUCKET,
                object_name=f"{slug}.{logo_ext}",
                data=io.BytesIO(logo_bytes),
                length=len(logo_bytes),
                content_type=logo_mime,
            )
            logger.info(f"Registration logo uploaded: {_LOGO_BUCKET}/{slug}.{logo_ext}")
        except Exception as exc:
            logger.warning(f"Logo upload failed for new tenant '{slug}': {exc}")

    # ── Send magic-link invite so the founder can log straight in ────────────
    invite_warning: str | None = None
    try:
        await auth_service.invite_member(email=email, tenant_slug=slug)
    except Exception as e:
        logger.warning(f"Tenant '{slug}' registered but invite email failed: {e}")
        invite_warning = "Tenant created but the invite email could not be sent."

    return JSONResponse(
        {
            "tenant_slug": slug,
            "tenant_name": name,
            **({"warning": invite_warning} if invite_warning else {}),
        },
        status_code=201,
    )


async def upload_tenant_logo(request: Request) -> Response:
    """
    POST /api/tenant/logo

    Upload (or replace) the logo for the current tenant.
    Caller must be authenticated as a *master* member of the tenant identified
    by the ``Host`` header subdomain.

    Accepts ``multipart/form-data`` with a single ``logo`` file field.
    Maximum file size: 5 MB.  Supported types: PNG, JPEG, GIF, WebP, SVG.
    """
    auth = await auth_service.get_authenticated_member(request)
    if auth is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    member, tenant = auth
    if member.position != CrewMemberPositionEnum.MANAGEMENT:
        return JSONResponse({"error": "Only master members may upload the tenant logo"}, status_code=403)

    try:
        form = await request.form()
    except Exception:
        return JSONResponse({"error": "Expected multipart/form-data"}, status_code=400)

    logo_file = form.get("logo")
    if logo_file is None or not hasattr(logo_file, "read"):
        return JSONResponse({"error": "'logo' file field is required"}, status_code=400)

    content_type: str = logo_file.content_type or "image/png"
    ext = _MIME_TO_EXT.get(content_type)
    if ext is None:
        return JSONResponse(
            {"error": f"Unsupported content type '{content_type}'. Allowed: {list(_MIME_TO_EXT)}"},
            status_code=415,
        )

    content: bytes = await logo_file.read()
    if not content:
        return JSONResponse({"error": "Uploaded file is empty"}, status_code=400)
    if len(content) > _LOGO_MAX_BYTES:
        return JSONResponse({"error": "Logo must be under 5 MB"}, status_code=413)

    object_name = f"{tenant.slug}.{ext}"
    try:
        client = _get_minio_client()
        if not client.bucket_exists(_LOGO_BUCKET):
            client.make_bucket(_LOGO_BUCKET)
        client.put_object(
            bucket_name=_LOGO_BUCKET,
            object_name=object_name,
            data=io.BytesIO(content),
            length=len(content),
            content_type=content_type,
        )
    except Exception as e:
        logger.error(f"MinIO upload error for '{object_name}': {e}")
        return JSONResponse({"error": "Failed to upload logo"}, status_code=500)

    logger.success(f"Logo '{object_name}' uploaded for tenant '{tenant.slug}'")
    return JSONResponse({"object_name": object_name}, status_code=200)


async def invite_tenant_member(request: Request) -> Response:
    """
    POST /api/tenant/invite

    Add a member to the current tenant and optionally send them a magic-link
    invite email.  Caller must be authenticated as a *master* member.

    Request body (JSON)::

        {
            "email":               "user@example.com",
            "position":            "employee" | "mechanic" | "master",
            "language_preference": "en",     // optional, default "en"
            "send_invite":         true       // optional, default true
        }

    Returns 201 with ``{"id", "email"}`` on success.
    """
    auth = await auth_service.get_authenticated_member(request)
    if auth is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    member, tenant = auth
    if member.position != CrewMemberPositionEnum.MANAGEMENT:
        return JSONResponse({"error": "Only master members may invite users"}, status_code=403)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    email: str = (body.get("email") or "").strip().lower()
    position_raw: str = (body.get("position") or "employee").strip().lower()
    language: str = (body.get("language_preference") or "en").strip().lower()
    send_invite: bool = bool(body.get("send_invite", True))

    if not email or "@" not in email:
        return JSONResponse({"error": "'email' must be a valid address"}, status_code=400)

    try:
        position = CrewMemberPositionEnum(position_raw)
    except ValueError:
        valid = [e.value for e in CrewMemberPositionEnum]
        return JSONResponse({"error": f"'position' must be one of: {valid}"}, status_code=400)

    try:
        new_member = await Member.create(
            id=uuid4(),
            email=email,
            language_preference=language,
            position=position,
            tenant=tenant,
        )
    except IntegrityError:
        return JSONResponse({"error": "A member with that email already exists"}, status_code=409)

    if send_invite:
        try:
            await auth_service.invite_member(email=email, tenant_slug=tenant.slug)
        except Exception as e:
            logger.warning(f"Member '{email}' created in '{tenant.slug}' but invite email failed: {e}")
            return JSONResponse(
                {
                    "id": str(new_member.id),
                    "email": new_member.email,
                    "warning": "Member added but invite email could not be sent",
                },
                status_code=201,
            )

    logger.success(f"Invited '{email}' to tenant '{tenant.slug}' (position={position.value})")
    return JSONResponse({"id": str(new_member.id), "email": new_member.email}, status_code=201)
