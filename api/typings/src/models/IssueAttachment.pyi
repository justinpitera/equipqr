from datetime import datetime as datetime
from src.models import Issue as Issue
from tortoise.fields import Field as Field
from tortoise.models import Model
from uuid import UUID as UUID

class IssueAttachment(Model):
    id: Field[UUID]
    issue: Field['Issue']
    file_type: Field[str]
    uploaded_at: Field[datetime]
