import secrets

from redis.asyncio import Redis
from tortoise.exceptions import DoesNotExist, OperationalError

from src import RedisClient
from src.models import Member, Tenant


# ---------------------------------------------------------------------------
# Redis helpers
# ---------------------------------------------------------------------------

async def _totp_client() -> Redis:
    return await RedisClient.get_client(db=2)


async def get_magic_token_email(token: str) -> str | None:
    """Return the email address stored under *token*, or None if missing/expired."""
    client = await _totp_client()
    value = await client.get(name=token)
    if value is None:
        return None
    return value if isinstance(value, str) else value.decode()


async def get_magic_token_tenant(token: str) -> str | None:
    """Return the tenant_slug stored alongside a magic token, or None."""
    client = await _totp_client()
    value = await client.get(name=f"{token}:tenant")
    if value is None:
        return None
    return value if isinstance(value, str) else value.decode()


async def store_magic_token(token: str, email: str, tenant_slug: str, expires_seconds: int = 600) -> None:
    """Persist a one-time magic-link token → email + tenant mapping in Redis."""
    client = await _totp_client()
    await client.set(name=token, value=email, ex=expires_seconds)
    await client.set(name=f"{token}:tenant", value=tenant_slug, ex=expires_seconds)


async def delete_magic_token(token: str) -> None:
    """Remove a consumed magic-link token (and its tenant key) from Redis."""
    client = await _totp_client()
    await client.delete(token, f"{token}:tenant")


async def store_access_token(access_token: str, email: str, expires_seconds: int = 3600) -> None:
    """Persist a session access-token → email mapping in Redis."""
    client = await _totp_client()
    await client.set(name=access_token, value=email, ex=expires_seconds)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

async def get_tenant_by_slug(slug: str) -> Tenant:
    """
    Fetch a Tenant by slug.

    Raises:
        DoesNotExist: if no matching tenant exists.
    """
    return await Tenant.get(slug=slug, is_active=True)


async def get_member_by_email_and_tenant(email: str, tenant: Tenant) -> Member:
    """
    Fetch a Member by email scoped to a specific tenant.

    Raises:
        DoesNotExist:     if no matching record exists.
        OperationalError: on database connectivity / query failures.
    """
    return await Member.get(email=email, tenant=tenant)
