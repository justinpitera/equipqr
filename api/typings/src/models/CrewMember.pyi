from src.enums import CrewMemberPositionEnum as CrewMemberPositionEnum
from src.models import Issue as Issue
from tortoise.fields import Field as Field, ReverseRelation as ReverseRelation
from tortoise.models import Model
from uuid import UUID as UUID

class CrewMember(Model):
    id: Field[UUID]
    email: Field[str]
    language_preference: Field[str]
    position: CrewMemberPositionEnum
    is_master: Field[bool]
    reported_issues: ReverseRelation['Issue']
