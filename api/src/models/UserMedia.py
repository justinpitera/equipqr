"""
src/models/IssueAttachment.py - Tortoise-ORM model for issue attachments.

Date: December 7, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from typing import TYPE_CHECKING
from uuid import UUID
from datetime import datetime

# Third-party
from tortoise.models import Model
from tortoise.fields import (
    CharField,
    DatetimeField,
    UUIDField,
    ForeignKeyField,
    Field,
    OnDelete # pyright: ignore
)

if TYPE_CHECKING:
    from src.models import GroundSupportEquiptment

class UserMedia(Model):
    """Stores attachments (photos/videos) related to GroundSupportEquiptment used as preview images."""
    id: UUID = UUIDField(primary_key=True, unique=True, null=False)
    ground_support_equiptment: Field["GroundSupportEquiptment"] = ForeignKeyField(
        model_name="models.GroundSupportEquiptment",
        related_name="media",
        on_delete=OnDelete.CASCADE,
    )
    file_type: str = CharField(max_length=50, null=False)
    uploaded_at: datetime = DatetimeField(auto_now_add=True)
