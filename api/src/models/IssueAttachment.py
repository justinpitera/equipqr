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
    OnDelete # pyright: ignore
)

if TYPE_CHECKING:
    from src.models import Issue

class IssueAttachment(Model):
    """Stores attachments (photos/videos) related to Issues mapped to object storage."""
    id: UUID = UUIDField(primary_key=True, unique=True, null=False)
    issue: "Issue" = ForeignKeyField(
        model_name="models.Issue",
        related_name="attachments",
        on_delete=OnDelete.CASCADE,
    )
    file_type: str = CharField(max_length=50, null=False)
    uploaded_at: datetime = DatetimeField(auto_now_add=True)
