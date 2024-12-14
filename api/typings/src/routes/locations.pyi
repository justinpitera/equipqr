from datetime import datetime as datetime, timedelta as timedelta, timezone as timezone
from pydantic import Field as Field
from src.enums import LocationTypeEnum as LocationTypeEnum
from starlette.datastructures import FormData as FormData
from starlette.exceptions import HTTPException as HTTPException
from starlette.requests import Request as Request
from starlette.responses import JSONResponse
from uuid import UUID as UUID, uuid4 as uuid4

async def fetch_locations(request: Request) -> JSONResponse: ...
