# Standard
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

# Third-party
from tortoise.models import Model
from tortoise.fields import (
    BooleanField,
    CharField,
    DatetimeField,
    TextField,
    UUIDField,
    ForeignKeyField,
    ReverseRelation,
    Field,
    CharEnumField
)

if TYPE_CHECKING:
    from src.models import Issue

class IssueComment(Model):
    """Stores comments related to an issue."""
    id           : UUID            = UUIDField(primary_key=True, unique=True, null=False)
    issue        : Field["Issue"]    = ForeignKeyField("models.Issue", related_name="comments", on_delete="CASCADE")
    comment      : str             = TextField()
    commented_by : str             = CharField(max_length=3)
    commented_at : datetime        = DatetimeField(auto_now_add=True)
