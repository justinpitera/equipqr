# Standard
from uuid import UUID

# Third-party
from tortoise.models import Model
from tortoise.fields import (
    CharField,
    UUIDField,
    Field,
    CharEnumField
)

# Local
from src.enums import LocationTypeEnum


class Location(Model):
    """Locations related to ICAO codes such as gates."""
    id                               : UUID    = UUIDField(primary_key=True, unique=True, null=False)
    icao_code                        : str     = CharField(max_length=4)
    location                         : str     = CharField(max_length=255)
    aircraft                         : str     = CharField(max_length=2048)
    location_type                    : LocationTypeEnum = CharEnumField(enum_type=LocationTypeEnum, null=False, default=LocationTypeEnum.NONE)