from datetime import datetime as datetime
from src.models import GroundSupportEquiptment as GroundSupportEquiptment
from tortoise.fields import Field as Field
from tortoise.models import Model
from uuid import UUID as UUID

class UserMedia(Model):
    id: Field[UUID]
    ground_support_equiptment: Field['GroundSupportEquiptment']
    file_type: Field[str]
    uploaded_at: Field[datetime]
