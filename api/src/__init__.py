"""
src/__init__.py - Main initialization module.

Date: November 21, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
import toml, os
from pathlib import Path
from typing import Any, TypedDict

# Third-party
from colorama import Style
import redis.asyncio as redis


API_CONFIG: dict[str, Any] = toml.load(Path(os.getcwd()).joinpath("../private/configurations/api.config.toml"))
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
                "host": API_CONFIG["database"]["address"],
                "port": API_CONFIG["database"]["port"],
                "user": API_CONFIG["database"]["username"],
                "password": API_CONFIG["database"]["password"],
                "database": "aviator_pg",
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