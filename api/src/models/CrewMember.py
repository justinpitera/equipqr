"""
src/models/CrewMember.py - Tortoise-ORM model for Crew Memembers.

Date: November 24, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from uuid import UUID

# Third-party
from tortoise.fields import (
    Field,
    UUIDField,
    CharField,
)
from tortoise.models import Model


class CrewMember(Model):
    """Database model to represent various types of crew memberss (ground crew, mechanics, etc) and degree of authority."""
    id                               : Field[UUID] = UUIDField(primary_key=True, unique=True, null=False)
    email                            : Field[str] = CharField(unique=True, max_length=255, null=False, db_index=True)
    first_name                       : Field[str] = CharField(max_length=50, null=False)
    last_name                        : Field[str] = CharField(max_length=50, null=False)
    language_preference              : Field[str] = CharField(max_length=50, null=False)
    position                         : Field[str] = CharField(max_length=255, null=False) # TODO: Change to enum-based type.
