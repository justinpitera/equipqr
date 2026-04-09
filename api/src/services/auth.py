"""
services/auth.py - Business logic layer for authentication.

Orchestrates repositories and notifications; knows the *rules* of auth
but has no knowledge of HTTP request/response objects.
"""

import secrets
from urllib.parse import urlparse

from itsdangerous import URLSafeTimedSerializer
from loguru import logger
from starlette.requests import Request
from tortoise.exceptions import DoesNotExist, OperationalError

from src import API_CONFIG
from src.models import Member, Tenant
from src import repositories  # type: ignore[attr-defined]
import src.repositories.auth as auth_repo
from src.notifications.email import send_magic_link_email

# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

_TOKEN_SERIALIZER = URLSafeTimedSerializer(API_CONFIG["auth"]["jwt"]["secret"])
_BASE_URL: str = API_CONFIG["api"]["domain"]
_ALLOWED_DOMAINS: list[str] = API_CONFIG["auth"]["magic"]["allowed_domains"]


# ---------------------------------------------------------------------------
# Custom auth exceptions
# ---------------------------------------------------------------------------

class TenantNotFound(Exception):
    """Raised when no active tenant matches the requested slug."""


class NotATenantMember(Exception):
    """Raised when the email is not registered as a member of the requested tenant."""


# ---------------------------------------------------------------------------
# Cookie helpers (used by the route layer)
# ---------------------------------------------------------------------------

def get_cookie_settings() -> dict:
    """Return shared cookie flags derived from the configured domain.

    Domain is intentionally omitted so the browser uses the default host-only
    binding (i.e. the exact hostname that set the cookie, e.g. acme.localhost).
    Explicitly setting domain=localhost is rejected by browsers because
    'localhost' is treated as a public-suffix TLD.
    """
    secure = urlparse(_BASE_URL).scheme == "https"
    return {"secure": secure}


def build_tenant_base_url(tenant_slug: str) -> str:
    """Return the base URL with *tenant_slug* inserted as an immediate subdomain.

    Example:
        _BASE_URL = "http://localhost:7878"  →  "http://acme.localhost:7878"
    """
    parsed = urlparse(_BASE_URL)
    netloc = f"{tenant_slug}.{parsed.hostname}"
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    return f"{parsed.scheme}://{netloc}"


# ---------------------------------------------------------------------------
# Auth use-cases
# ---------------------------------------------------------------------------

async def initiate_magic_link(email: str, tenant_slug: str) -> Tenant:
    """
    Validate the tenant exists, the user is a member of that tenant, ensure
    their email domain is allowed, generate a one-time token and fire off the
    magic-link email.

    Returns the Tenant so the caller can include its name in the response.

    Raises:
        TenantNotFound:   if the tenant slug does not match an active tenant.
        NotATenantMember: if the email is not registered as a member of that tenant.
        ValueError:       if the email domain is not on the allow-list.
    """
    # 1. Resolve the tenant
    try:
        tenant: Tenant = await auth_repo.get_tenant_by_slug(tenant_slug)
    except DoesNotExist:
        logger.warning(f"Magic-link requested for unknown tenant slug '{tenant_slug}'")
        raise TenantNotFound(tenant_slug)

    # 2. Domain allow-list check
    email_domain = email.split("@")[-1]
    if _ALLOWED_DOMAINS and email_domain not in _ALLOWED_DOMAINS:
        logger.warning(f"Email domain '{email_domain}' is restricted.")
        raise ValueError("The email domain is not allowed to receive magic links.")

    # 3. Verify the user exists as a member of this tenant
    try:
        await auth_repo.get_member_by_email_and_tenant(email=email, tenant=tenant)
    except DoesNotExist:
        logger.warning(f"Login attempt for '{email}' who is not a member of tenant '{tenant_slug}'")
        raise NotATenantMember(email)
    logger.info(f"Sending magic-link to {email} for tenant '{tenant_slug}'")

    # 4. Mint a one-time token and store it alongside the tenant slug
    random_token = secrets.token_urlsafe(nbytes=32)
    await auth_repo.store_magic_token(token=random_token, email=email, tenant_slug=tenant_slug, expires_seconds=600)

    # 5. Build the set-token URL rooted at the tenant's subdomain and send the email
    api_prefix = "/api" if API_CONFIG["api"]["mode"] == "production" else ""
    tenant_base = build_tenant_base_url(tenant_slug)
    set_token_link = f"{tenant_base}{api_prefix}/api/set-token?token={random_token}"
    send_magic_link_email(email=email, set_token_link=set_token_link)

    return tenant


async def exchange_magic_token(token: str) -> tuple[Member, Tenant] | None:
    """
    Validate a magic-link token, consume it, and return the corresponding
    (Member, Tenant) pair.  Returns None if the token is missing or expired.

    Raises:
        DoesNotExist:     if the stored email/tenant no longer map to records.
        OperationalError: on database errors.
    """
    email = await auth_repo.get_magic_token_email(token)
    if email is None:
        return None

    tenant_slug = await auth_repo.get_magic_token_tenant(token)
    if tenant_slug is None:
        return None

    # Consume the one-time token immediately
    await auth_repo.delete_magic_token(token)

    tenant: Tenant = await auth_repo.get_tenant_by_slug(tenant_slug)
    member: Member = await auth_repo.get_member_by_email_and_tenant(email=email, tenant=tenant)
    logger.info(f"Logged in {email} for tenant '{tenant_slug}'")
    return member, tenant


async def invite_member(email: str, tenant_slug: str) -> None:
    """
    Send a magic-link invite to an *already-created* member, bypassing the
    domain allow-list check.  Intended for use by admin provisioning flows
    where the domain restriction should not apply.

    Raises:
        DoesNotExist: if the tenant slug is invalid.
    """
    tenant: Tenant = await auth_repo.get_tenant_by_slug(tenant_slug)

    random_token = secrets.token_urlsafe(nbytes=32)
    await auth_repo.store_magic_token(token=random_token, email=email, tenant_slug=tenant_slug, expires_seconds=600)

    api_prefix = "/api" if API_CONFIG["api"]["mode"] == "production" else ""
    tenant_base = build_tenant_base_url(tenant_slug)
    set_token_link = f"{tenant_base}{api_prefix}/api/set-token?token={random_token}"
    send_magic_link_email(email=email, set_token_link=set_token_link)
    logger.info(f"Invite email sent to {email} for tenant '{tenant_slug}'")


async def create_session(email: str) -> str:
    """
    Mint a new signed session token, persist it in Redis, and return it.
    """
    access_token: str = _TOKEN_SERIALIZER.dumps(obj=secrets.token_urlsafe(nbytes=32))
    await auth_repo.store_access_token(access_token=access_token, email=email, expires_seconds=3600)
    return access_token


async def get_authenticated_member(request: Request) -> tuple[Member, Tenant] | None:
    """
    Validate the ``access_token`` cookie and return the authenticated
    ``(Member, Tenant)`` pair, or ``None`` if the session is missing, expired,
    or the member/tenant can no longer be found.

    The tenant is resolved from the Host-header subdomain so callers don't have
    to pass it separately.
    """
    access_token = request.cookies.get("access_token")
    if not access_token:
        logger.debug("get_authenticated_member: no access_token cookie in request")
        return None

    email = await auth_repo.get_session_email(access_token)
    if email is None:
        logger.debug("get_authenticated_member: access_token not found in Redis (expired or invalid)")
        return None

    # Derive tenant slug from the Host-header subdomain (e.g. acme.localhost → "acme")
    host = request.headers.get("host", "").split(":")[0]
    parts = host.split(".")
    if len(parts) < 2 or parts[0] in ("www", ""):
        logger.debug(f"get_authenticated_member: could not extract tenant slug from Host header '{request.headers.get('host', '')}'")
        return None
    tenant_slug = parts[0]

    try:
        tenant = await auth_repo.get_tenant_by_slug(tenant_slug)
        member = await auth_repo.get_member_by_email_and_tenant(email=email, tenant=tenant)
        return member, tenant
    except DoesNotExist:
        logger.debug(f"get_authenticated_member: tenant '{tenant_slug}' or member '{email}' not found in DB")
        return None
