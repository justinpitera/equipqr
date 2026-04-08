"""
src/__init__.py - Main initialization module.

Date: November 21, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
import os
from pathlib import Path
from typing import Any, TypedDict

# Third-party
from colorama import Style
from dotenv import load_dotenv
import redis.asyncio as redis

# Load .env — root repo .env first, then api/.env overrides (higher priority)
load_dotenv(Path(os.getcwd()).parent / ".env")
load_dotenv(Path(os.getcwd()) / ".env", override=True)


def _csv(val: str | None, default: list[str] | None = None) -> list[str]:
    """Parse a comma-separated env var into a list."""
    if not val:
        return default if default is not None else ["*"]
    return [v.strip() for v in val.split(",") if v.strip()]


API_CONFIG: dict[str, Any] = {
    "api": {
        "mode":    os.getenv("API_MODE", "development"),
        "address": os.getenv("API_ADDRESS", "0.0.0.0"),
        "port":    int(os.getenv("API_PORT", "7879")),
        "domain":  os.getenv("API_DOMAIN", "http://localhost:7879"),
        "performance": {
            "workers":          int(os.getenv("API_WORKERS", "4")),
            "threads":          int(os.getenv("API_THREADS", "4")),
            "blocking_threads": int(os.getenv("API_BLOCKING_THREADS", "2")),
        },
    },
    "cors": {
        "allow_credentials": os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
        "allow_origins":     _csv(os.getenv("CORS_ALLOW_ORIGINS"), ["*"]),
        "allow_methods":     _csv(os.getenv("CORS_ALLOW_METHODS"), ["*"]),
        "allow_headers":     _csv(os.getenv("CORS_ALLOW_HEADERS"), ["*"]),
    },
    "auth": {
        "mode":   os.getenv("AUTH_MODE", "magic"),
        "master": os.getenv("AUTH_MASTER", "admin@example.com"),
        "magic": {
            "allowed_domains": _csv(os.getenv("AUTH_MAGIC_ALLOWED_DOMAINS"), []),
        },
        "credentials": {
            "min_password_length": int(os.getenv("AUTH_MIN_PASSWORD_LENGTH", "14")),
        },
        "jwt": {
            "secret":             os.getenv("AUTH_JWT_SECRET", ""),
            "expires_in":         int(os.getenv("AUTH_JWT_EXPIRES_IN", "30")),
            "refresh_expires_in": int(os.getenv("AUTH_JWT_REFRESH_EXPIRES_IN", "7")),
        },
    },
    "smtp": {
        "host":     os.getenv("SMTP_HOST", "smtp.example.com"),
        "domain":   os.getenv("SMTP_DOMAIN", "example.com"),
        "port":     int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USERNAME", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
    },
    "database": {
        "engine":   os.getenv("DB_ENGINE", "tortoise.backends.asyncpg"),
        "address":  os.getenv("POSTGRES_HOST", "localhost"),
        "port":     int(os.getenv("POSTGRES_PORT", "5432")),
        "username": os.getenv("POSTGRES_USERNAME", "equipqr"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "name":     os.getenv("POSTGRES_DATABASE", "aviator_pg"),
        "importer": {
            "legacy_path": os.getenv("DB_IMPORTER_LEGACY_PATH", ""),
        },
    },
    "object_storage": {
        "address":    os.getenv("MINIO_ADDRESS", "localhost"),
        "port":       int(os.getenv("MINIO_PORT", "9000")),
        "secure":     os.getenv("MINIO_SECURE", "false").lower() == "true",
        "access_key": os.getenv("MINIO_ACCESS_KEY", ""),
        "secret_key": os.getenv("MINIO_SECRET_KEY", ""),
    },
    "redis": {
        "address":  os.getenv("REDIS_ADDRESS", "localhost"),
        "port":     int(os.getenv("REDIS_PORT", "6379")),
        "secure":   os.getenv("REDIS_SECURE", "false").lower() == "true",
        "password": os.getenv("REDIS_PASSWORD", ""),
    },
}

API_VERSION: str = (lambda line: line.split(sep="=")[1].strip().strip('"') if line.startswith("version") else "Unknown")(line=open(file="pyproject.toml").readlines()[2].strip())
API_STARTUP_MESSAGE: str = f"""
╭━━╮╱╱╱╭╮╱╱╭╮
┃╭╮┣━┳━╋╋━╮┃╰┳━┳┳╮
┃┣┫┣╮┃╭┫┃╋╰┫╭┫╋┃╭╯
╰╯╰╯╰━╯╰┻━━┻━┻━┻╯  {Style.BRIGHT} Reporter {API_VERSION}{Style.RESET_ALL}\n
=================
Listening on {API_CONFIG["api"]["address"]}:{API_CONFIG["api"]["port"]}
"""
TORTOISE_CONFIG: dict[str, Any] = {
    "connections": {
        "default": {
            "engine": API_CONFIG["database"]["engine"],
            "credentials": {
                "host":     API_CONFIG["database"]["address"],
                "port":     API_CONFIG["database"]["port"],
                "user":     API_CONFIG["database"]["username"],
                "password": API_CONFIG["database"]["password"],
                "database": API_CONFIG["database"]["name"],
            }
        }
    },
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}

class RedisConfig(TypedDict):
    address: str
    port: int
    secure: bool
    password: str

_redis_cfg: RedisConfig = API_CONFIG["redis"]
_REDIS_URL: str = (
    f"{'rediss' if _redis_cfg.get('secure', False) else 'redis'}://"
    f"{f':{_redis_cfg.get('password')}@' if _redis_cfg.get('password') else ''}"
    f"{_redis_cfg['address']}:{_redis_cfg['port']}"
)
            
class RedisClient:
    _clients: dict[int, redis.Redis] = {}

    @classmethod
    async def get_client(cls, db: int = 0) -> redis.Redis:
        """
        Get or create a Redis client for the specified database.
        """
        if db not in cls._clients:
            cls._clients[db] = redis.Redis.from_url(url=_REDIS_URL, decode_responses=True, db=db)
        return cls._clients[db]

    @classmethod
    async def close_all(cls) -> None:
        """
        Close all Redis client connections.
        """
        for client in cls._clients.values():
            await client.close()
        cls._clients.clear()