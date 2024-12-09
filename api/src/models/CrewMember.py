"""
src/models/CrewMember.py - Tortoise-ORM model for Crew Members.

Date: November 24, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from email.policy import default
from uuid import UUID

# Third-party
from tortoise.fields import (
    BooleanField,
    Field,
    UUIDField,
    CharField,
    CharEnumField,
)
from tortoise.models import Model

# Local
from src.enums import CrewMemberPositionEnum


class CrewMember(Model):
    """Database model to represent various types of crew memberss (ground crew, mechanics, etc) and degree of authority."""
    id                               : Field[UUID] = UUIDField(primary_key=True, unique=True, null=False)
    email                            : Field[str] = CharField(unique=True, max_length=255, null=False, db_index=True)
    language_preference              : Field[str] = CharField(max_length=50, null=False)
    position                         : CrewMemberPositionEnum = CharEnumField(enum_type=CrewMemberPositionEnum, null=False)
    is_master                        : Field[bool] = BooleanField(default=False)
