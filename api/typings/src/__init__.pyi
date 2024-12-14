import redis.asyncio as redis
from typing import Any, TypedDict

API_CONFIG: dict[str, Any]
API_VERSION: str
API_STARTUP_MESSAGE: str
TORTOISE_CONFIG: dict[str, Any]

class RedisConfig(TypedDict):
    address: str
    port: int
    secure: bool
    password: str

class RedisClient:
    @classmethod
    async def get_client(cls, db: int = 0) -> redis.Redis: ...
    @classmethod
    async def close_all(cls) -> None: ...
