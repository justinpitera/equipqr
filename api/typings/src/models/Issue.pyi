from datetime import datetime as datetime
from src.enums import IssueProgressEnum as IssueProgressEnum
from src.models import IssueAttachment as IssueAttachment, Location as Location
from tortoise.fields import Field as Field, ReverseRelation as ReverseRelation
from tortoise.models import Model
from uuid import UUID as UUID

class Issue(Model):
    id: Field[UUID]
    gse_id: Field[str]
    issue_description: Field[str]
    reported_at: Field[datetime]
    reported_by: Field[str]
    is_operable: Field[bool]
    progress: IssueProgressEnum
    estimated_time: Field[datetime]
    attachments: ReverseRelation['IssueAttachment'] | None
