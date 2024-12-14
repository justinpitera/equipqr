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
    Field,
    ReverseRelation,
    CharEnumField
)

# Local
from src.enums import IssueProgressEnum

if TYPE_CHECKING:
    from src.models import (
        IssueAttachment,
        Location
    )

class Issue(Model):
    """Stores issues relating to GroundSupportEquiptment."""
    id                               : Field[UUID]     = UUIDField(primary_key=True, unique=True, null=False)
    gse_id                           : Field[str]      = CharField(max_length=255)
    issue_description                : Field[str]      = TextField()
    reported_at                      : Field[datetime] = DatetimeField(auto_now_add=True)
    reported_by                      : Field[str]      = CharField(max_length=3)
    is_operable                      : Field[bool]     = BooleanField(default=True)
   # Location                         : Field["Location"] = 
    progress                         : IssueProgressEnum = CharEnumField(enum_type=IssueProgressEnum, null=False, default=IssueProgressEnum.REPORTED)
    estimated_time                   : Field[datetime] = DatetimeField(null=True)
    attachments                      : ReverseRelation["IssueAttachment"] | None = None
