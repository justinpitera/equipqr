from itsdangerous import URLSafeTimedSerializer
from pydantic import BaseModel, EmailStr as EmailStr
from redis.asyncio import Redis as Redis
from starlette.requests import Request as Request
from starlette.responses import JSONResponse, RedirectResponse

SUCCESS_MESSAGE_REGISTER: str
SUCCESS_MESSAGE_VALIDATE: str
BASE_URL: str
TOKEN_SERIALIZER: URLSafeTimedSerializer

class _UserRegisteration(BaseModel):
    email: EmailStr

async def set_token(request: Request) -> RedirectResponse: ...
async def auth_user(request: Request) -> JSONResponse: ...
