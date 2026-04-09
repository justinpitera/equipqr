"""
services/auth.py - Business logic layer for authentication.

Orchestrates repositories and notifications; knows the *rules* of auth
but has no knowledge of HTTP request/response objects.
"""

import secrets
from urllib.parse import urlparse

from itsdangerous import URLSafeTimedSerializer
from loguru import logger
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
# Cookie helpers (used by the route layer)
# ---------------------------------------------------------------------------

def get_cookie_settings() -> dict:
    """Return shared cookie flags derived from the configured domain."""
    secure = urlparse(_BASE_URL).scheme == "https"
    domain = urlparse(_BASE_URL).hostname
    return {"secure": secure, "domain": domain}


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
        DoesNotExist:   if the tenant slug is invalid or the email is not a
                        member of that tenant.
        ValueError:     if the email domain is not on the allow-list.
    """
    # 1. Resolve the tenant
    tenant: Tenant = await auth_repo.get_tenant_by_slug(tenant_slug)

    # 2. Domain allow-list check
    email_domain = email.split("@")[-1]
    if _ALLOWED_DOMAINS and email_domain not in _ALLOWED_DOMAINS:
        logger.warning(f"Email domain '{email_domain}' is restricted.")
        raise ValueError("The email domain is not allowed to receive magic links.")

    # 3. Verify the user exists as a member of this tenant (raises DoesNotExist if not)
    await auth_repo.get_member_by_email_and_tenant(email=email, tenant=tenant)
    logger.info(f"Sending magic-link to {email} for tenant '{tenant_slug}'")

    # 4. Mint a one-time token and store it alongside the tenant slug
    random_token = secrets.token_urlsafe(nbytes=32)
    await auth_repo.store_magic_token(token=random_token, email=email, tenant_slug=tenant_slug, expires_seconds=600)

    # 5. Build the set-token URL and send the email
    api_prefix = "/api" if API_CONFIG["api"]["mode"] == "production" else ""
    set_token_link = f"{_BASE_URL}{api_prefix}/api/set-token?token={random_token}"
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


async def create_session(email: str) -> str:
    """
    Mint a new signed session token, persist it in Redis, and return it.
    """
    access_token: str = _TOKEN_SERIALIZER.dumps(obj=secrets.token_urlsafe(nbytes=32))
    await auth_repo.store_access_token(access_token=access_token, email=email, expires_seconds=3600)
    return access_token
