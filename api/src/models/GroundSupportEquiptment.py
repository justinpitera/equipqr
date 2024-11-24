"""
src/models/__init__.py - Database initialization module.

Date: November 23, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from datetime import datetime
from uuid import UUID

# Third-party
from tortoise.fields import (
    Field,
    UUIDField,
    CharField,
    DatetimeField,
    IntField,
    BooleanField,
)
from tortoise.models import Model


class GroundSupportEquiptment(Model):
    """
    Database model to represent various ground support equiptment (GSEs).
    """
    id                               : Field[UUID]   = UUIDField(pk=True)
    gse_id                           : Field[str]    = CharField(max_length=255)
    old_gse_id                       : Field[str]    = CharField(null=True, max_length=255)
    gse_type                         : Field[str]    = CharField(max_length=255)
    model                            : Field[str]    = CharField(null=True, max_length=255)
    manufacturer                     : Field[str]    = CharField(null=True, max_length=255)
    location                         : Field[str]    = CharField(max_length=255)
    lift_inspection_expire           : Field[datetime] = DatetimeField(null=True)
    latest_service_chassi            : Field[datetime] = DatetimeField(null=True)
    latest_service_unit              : Field[datetime] = DatetimeField(null=True)
    chassi_nrvehicle                 : Field[int]    = IntField(null=True)
    chassi_nrunit                    : Field[int]    = IntField(null=True)
    manufacutring_year_chassi        : Field[int]    = IntField(null=True)
    manufacutring_year_unit          : Field[int]    = IntField(null=True)
    hour_meter_chassi                : Field[int]    = IntField(null=True)
    hour_meter_unit                  : Field[int]    = IntField(null=True)
    km_chassi                        : Field[int]    = IntField(null=True)
    local_vehicle_permit             : Field[str]    = CharField(null=True, max_length=255)
    vehicle_permition_nr             : Field[str]    = CharField(null=True, max_length=255)
    vehicle_permit_valid_until       : Field[str]    = CharField(null=True, max_length=255)
    in_use                           : Field[bool]   = BooleanField()
    net_weight_kg                    : Field[int]    = IntField(null=True)
    total_weight_kg                  : Field[int]    = IntField(null=True)
    status                           : Field[str]    = CharField(null=True, max_length=255)
    type_of_fuel                     : Field[str]    = CharField(null=True, max_length=255)
    emission_standard                : Field[str]    = CharField(null=True, max_length=255)
    regnrif_applicable               : Field[str]    = CharField(null=True, max_length=255)
    heating                          : Field[str]    = CharField(null=True, max_length=255)
    deice_type                       : Field[str]    = CharField(null=True, max_length=255)
    hot_type4                        : Field[bool]   = BooleanField()
    glycol                           : Field[bool]   = BooleanField(null=True)
    capacity                         : Field[str]    = CharField(null=True, max_length=255)
    actype                           : Field[str]    = CharField(null=True, max_length=255)
    singel_double_max_ppm            : Field[str]    = CharField(null=True, max_length=255)
    power                            : Field[str]    = CharField(null=True, max_length=255)
    cabin                            : Field[bool]   = BooleanField()
    gen2                             : Field[bool]   = BooleanField()
    length_m                         : Field[int]    = IntField(null=True)
    height_min_max_mm                : Field[str]    = CharField(null=True, max_length=255)
    self_propp                       : Field[bool]   = BooleanField()
    owned_by_company                 : Field[str]    = CharField(null=True, max_length=255)
    owned_by_company2                : Field[str]    = CharField(null=True, max_length=255)
    type_of_lease                    : Field[str]    = CharField(null=True, max_length=255)
    term_of_termination              : Field[str]    = CharField(null=True, max_length=255)
    purchase_date                    : Field[datetime] = DatetimeField(null=True)
    agreement_expire_date            : Field[datetime] = DatetimeField(null=True)
    risk_assessment                  : Field[bool]   = BooleanField()
    training_documentation_available : Field[bool]   = BooleanField()
    item_type                        : Field[str]    = CharField(max_length=255)
    path                             : Field[str]    = CharField(max_length=255)

    def generate_qr_code(self) -> None:
        """
        Generates the QR Code for the GSE upon creation in the database.
        
        Paramaters:
            self - The instance of GSE.
        """
        # TODO: Implement functionality to generate QR code based on self.gse_id.
        pass