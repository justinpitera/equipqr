"""
src/models/Asset.py

Generic asset model for EquipQR.
Keeps core searchable fields as real columns and stores
customer-specific fields in JSONB via `custom_data`.
"""

# Standard
from uuid import UUID
from typing import Any

# Third-party
from tortoise.fields import (
    UUIDField,
    CharField,
    DatetimeField,
    BooleanField,
    JSONField,
)
from tortoise.models import Model


class Asset(Model):
    """
    Generic asset model.

    Use real columns for fields that are common across nearly all customers.
    Use `custom_data` for customer-specific or asset-type-specific fields.
    """

    id: UUID = UUIDField(pk=True)
    tenant_id: UUID = UUIDField(index=True)
    name: str = CharField(max_length=255)

    # Customer-visible identifier that goes on labels and QR codes.
    asset_tag: str = CharField(max_length=255, index=True)
    # Broad category/type. Later this can become a ForeignKey to AssetType.
    asset_type: str | None = CharField(max_length=255, null=True, index=True)

    # Keep common fields as first-class columns because they are widely filtered/searched.
    manufacturer: str | None = CharField(max_length=255, null=True)
    model: str | None = CharField(max_length=255, null=True)
    serial_number: str | None = CharField(max_length=255, null=True, index=True)
    status: str | None = CharField(max_length=255, null=True, index=True)
    location: str | None = CharField(max_length=255, null=True, index=True)

    # Operational flags
    in_use: bool | None = BooleanField(null=True)
    is_active: bool = BooleanField(default=True)

    # Flexible customer-specific data
    # Examples:
    # {
    #   "fuel_type": "diesel",
    #   "lift_inspection_expires": "2026-04-01T00:00:00Z",
    #   "net_weight_kg": 1200,
    #   "deice_type": "Type IV",
    #   "airport_zone": "B12"
    # }
    custom_data: dict[str, Any] | list[Any] = JSONField(default=dict)

    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:
        table = "assets"
        unique_together = (("tenant_id", "asset_tag"),)

    def __str__(self) -> str:
        return f"{self.asset_tag} - {self.name}"

    def get_custom_field(self, key: str, default=None):
        """Safe helper for reading custom fields."""
        if not isinstance(self.custom_data, dict):
            return default
        return self.custom_data.get(key, default)

    def set_custom_field(self, key: str, value) -> None:
        """Safe helper for updating custom fields."""
        data = dict(self.custom_data or {})
        data[key] = value
        self.custom_data = data
