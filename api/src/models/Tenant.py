from uuid import UUID

from tortoise.fields import UUIDField, CharField, DatetimeField, BooleanField
from tortoise.models import Model


class Tenant(Model):
    id: UUID = UUIDField(pk=True)
    name: str = CharField(max_length=255, unique=True)
    slug: str = CharField(max_length=255, unique=True)
    is_active: bool = BooleanField(default=True)

    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:
        table = "tenants"

    def __str__(self) -> str:
        return self.name