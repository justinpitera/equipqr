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
    ReverseRelation,
    CharEnumField
)

# Local
from src.enums import IssueProgressEnum

if TYPE_CHECKING:
    from src.models import (
        IssueAttachment,
        IssueComment
    )

class Issue(Model):
    """Stores issues relating to GroundSupportEquiptment."""
    id                               : UUID     = UUIDField(primary_key=True, unique=True, null=False)
    gse_id                           : str      = CharField(max_length=255)
    issue_description                : str      = TextField()
    reported_at                      : datetime = DatetimeField(auto_now_add=True)
    reported_by                      : str      = CharField(max_length=3)
    is_operable                      : bool     = BooleanField(default=True)
   # Location                         : "Location" = 
    progress                         : IssueProgressEnum = CharEnumField(enum_type=IssueProgressEnum, null=False, default=IssueProgressEnum.REPORTED)
    estimated_time                   : datetime | None = DatetimeField(null=True)
    attachments                      : ReverseRelation["IssueAttachment"] | None = None
    comments                         : ReverseRelation["IssueComment"] | None = None