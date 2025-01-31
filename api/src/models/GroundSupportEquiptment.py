"""
src/models/GroundSupportEquiptment.py - Tortoise-ORM model for Ground Support Equiptment used throughout various airport services.

Date: November 23, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from datetime import datetime
from uuid import UUID

# Third-party
from tortoise.fields import (
    FloatField,
    UUIDField,
    CharField,
    DatetimeField,
    IntField,
    BooleanField,
    BinaryField
)
from tortoise.models import Model


class GroundSupportEquiptment(Model):
    """Database model to represent various ground support equiptment (GSEs)."""
    id                               : UUID   = UUIDField(pk=True)
    gse_id                           : str    = CharField(max_length=255)
    old_gse_id                       : str | None = CharField(null=True, max_length=255)
    gse_type                         : str    = CharField(max_length=255)
    model                            : str | None = CharField(null=True, max_length=255)
    manufacturer                     : str | None = CharField(null=True, max_length=255)
    location                         : str    = CharField(max_length=255)
    lift_inspection_expires          : datetime | None = DatetimeField(null=True)
    latest_service_chassi            : datetime | None = DatetimeField(null=True)
    latest_service_unit              : datetime | None = DatetimeField(null=True)
    chassi_nr_vehicle                : str | None = CharField(null=True, max_length=255)
    chassi_nr_unit                   : int | None = IntField(null=True)
    manufacturing_year_chassi        : int | None = IntField(null=True)
    manufacturing_year_unit          : int | None = IntField(null=True)
    hour_meter_chassi                : str | None = CharField(null=True, max_length=255)
    hour_meter_unit                  : int | None = IntField(null=True)
    km_chassi                        : int | None = IntField(null=True)
    local_vehicle_permit             : str | None = CharField(null=True, max_length=255)
    vehicle_permit_nr                : str | None = CharField(null=True, max_length=255)
    vehicle_permit_valid_until       : str | None = CharField(null=True, max_length=255)
    in_use                           : bool = BooleanField()
    net_weight_kg                    : int | None = IntField(null=True)
    total_weight_kg                  : int | None = IntField(null=True)
    status                           : str | None = CharField(null=True, max_length=255)
    type_of_fuel                     : str | None = CharField(null=True, max_length=255)
    emission_standard                : str | None = CharField(null=True, max_length=255)
    reg_nr_if_applicable             : str | None = CharField(null=True, max_length=255)
    heating                          : str | None = CharField(null=True, max_length=255)
    deice_type                       : str | None = CharField(null=True, max_length=255)
    hot_type4                        : bool = BooleanField()
    glycol                           : bool | None = BooleanField(null=True)
    capacity                         : float | None = FloatField(null=True)
    ac_type                          : str | None = CharField(null=True, max_length=255)
    single_double_max_ppm            : str | None = CharField(null=True, max_length=255)
    power                            : str | None = CharField(null=True, max_length=255)
    cabin                            : bool = BooleanField()
    gen2                             : bool = BooleanField()
    length_m                         : int | None = IntField(null=True)
    height_min_max_mm                : str | None = CharField(null=True, max_length=255)
    self_propelled                   : bool | None = BooleanField()
    owned_by_company                 : str | None = CharField(null=True, max_length=255)
    owned_by_company2                : str | None = CharField(null=True, max_length=255)
    type_of_lease                    : str | None = CharField(null=True, max_length=255)
    term_of_termination              : str | None = CharField(null=True, max_length=255)
    purchase_date                    : datetime | None = DatetimeField(null=True)
    agreement_expire_date            : datetime | None = DatetimeField(null=True)
    risk_assessment                  : bool = BooleanField()
    training_documentation_available : bool = BooleanField()
    item_type                        : str = CharField(max_length=255)
    path                             : str = CharField(max_length=255)
    field_image                      : bytes | None  = BinaryField(null=True)

    def generate_qr_code(self) -> None:
        """
        Generates the QR Code for the GSE upon creation in the database.
        
        Paramaters:
            self - The instance of GSE.
        """
        # TODO: Implement functionality to generate QR code based on self.gse_id.
        pass