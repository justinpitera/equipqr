from tortoise.models import Model
from tortoise.fields import CharField, DatetimeField, Field
from datetime import datetime

class ImportMetadata(Model):
    """Tracks the import status of legacy databases."""
    file_name: Field[str] = CharField(max_length=255, unique=True)
    imported_at: Field[datetime] = DatetimeField(auto_now_add=True)
