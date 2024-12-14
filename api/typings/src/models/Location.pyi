from src.enums import LocationTypeEnum as LocationTypeEnum
from tortoise.fields import Field as Field
from tortoise.models import Model
from uuid import UUID as UUID

class Location(Model):
    id: Field[UUID]
    icao_code: Field[str]
    location: Field[str]
    aircraft: Field[str]
    location_type: LocationTypeEnum
