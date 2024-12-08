# Standard
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

# Third-party
from tortoise.models import Model
from tortoise.fields import (
    CharField,
    DatetimeField,
    TextField,
    UUIDField,
    Field,
    ReverseRelation
)

if TYPE_CHECKING:
    from src.models import IssueAttachment

class Issue(Model):
    """Stores issues relating to GroundSupportEquiptment."""
    id                               : Field[UUID]     = UUIDField(primary_key=True, unique=True, null=False)
    gse_id                           : Field[str]      = CharField(max_length=255)
    issue_description                : Field[str]      = TextField()
    reported_at                      : Field[datetime] = DatetimeField(auto_now_add=True)
    attachments                      : ReverseRelation["IssueAttachment"] | None = None
