"""
src/models/CrewMember.py - Tortoise-ORM model for Crew Members.

Date: November 24, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from uuid import UUID
from typing import TYPE_CHECKING

# Third-party
from tortoise.fields import (
    BooleanField,
    Field,
    ForeignKeyField,
    UUIDField,
    CharField,
    ReverseRelation,
    CharEnumField,
)
from tortoise.models import Model

# Local
from src.enums import CrewMemberPositionEnum

if TYPE_CHECKING:
    from src.models import Issue, Tenant


class Member(Model):
    """Database model to represent various types of crew memberss (ground crew, mechanics, etc) and degree of authority."""
    id                               : UUID = UUIDField(primary_key=True, unique=True, null=False)
    email                            : str = CharField(unique=True, max_length=255, null=False, db_index=True)
    language_preference              : str = CharField(max_length=50, null=False)
    position                         : CrewMemberPositionEnum = CharEnumField(enum_type=CrewMemberPositionEnum, null=False)
    # Soon to be obsolete
    is_master                        : bool = BooleanField(default=False)
    tenant                           : "Tenant" = ForeignKeyField(
        "models.Tenant",
        related_name="members",
        on_delete="CASCADE"   
    )
    reported_issues                  : ReverseRelation["Issue"]

