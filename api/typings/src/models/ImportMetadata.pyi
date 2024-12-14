from datetime import datetime as datetime
from tortoise.fields import Field as Field
from tortoise.models import Model

class ImportMetadata(Model):
    file_name: Field[str]
    imported_at: Field[datetime]
