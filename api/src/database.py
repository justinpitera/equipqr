"""
src/database.py - This file contains various database methods used throughout the lifespan of the api.

Date: November 25, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
import math
from datetime import datetime

# Third-party
from loguru import logger
import pandas as pd

# Local
from . import API_CONFIG
from src.models import GroundSupportEquiptment, ImportMetadata

# Init
LEGACY_CSV_PATH: str = API_CONFIG["database"]["legacy_path"]

def clean_value(value, field_name):
    """Converts NaN or invalid values to None for database compatibility."""
    if pd.isna(value) or (isinstance(value, float) and math.isnan(value)):
        return None
    return value

def clean_numeric_value(value, field_name, numeric_type=int):
    """Cleans numeric values by removing commas and converting them to integers or floats."""
    value = clean_value(value, field_name)
    if value is None:
        return None
    try:
        if isinstance(value, str):
            # Remove commas and convert to the specified numeric type
            value = numeric_type(value.replace(",", ""))
        return numeric_type(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid numeric value in field '{field_name}': {value}. Error: {e}")
    return None

def safe_parse_date(value, field_name):
    """Safely parses a date, logging issues for invalid inputs."""
    try:
        if pd.isna(value):
            return None
        if isinstance(value, (float, int)):
            # Handle UNIX timestamps
            return datetime.fromtimestamp(value)
        if isinstance(value, str):
            return datetime.fromisoformat(value)
    except Exception as e:
        logger.warning(f"Invalid date in field '{field_name}': {value}. Error: {e}")
    return None

async def database_importer() -> None:
    """Imports data from the legacy CSV-style database with detailed logging for invalid data."""
    logger.info("Importing legacy database...")
    file_name = LEGACY_CSV_PATH.split("/")[-1]
    existing_import = await ImportMetadata.filter(file_name=file_name).first()
    
    if existing_import:
        logger.warning(f"Legacy database '{file_name}' has already been imported on {existing_import.imported_at}. Skipping import...")
        return

    try:
        df = pd.read_csv(LEGACY_CSV_PATH)
    except Exception as e:
        logger.error(f"Failed to read CSV file '{LEGACY_CSV_PATH}'. Error: {e}")
        return

    records = []
    for index, row in df.iterrows():
        try:
            record = GroundSupportEquiptment(
                gse_id=row["gse_id"],
                old_gse_id=clean_value(row["old_gse_id"], "old_gse_id"),
                gse_type=clean_value(row["gse_type"], "gse_type"),
                model=clean_value(row["model"], "model"),
                manufacturer=clean_value(row["manufacturer"], "manufacturer"),
                location=clean_value(row["location"], "location"),
                lift_inspection_expires=safe_parse_date(row["lift_inspection_expires"], "lift_inspection_expires"),
                latest_service_chassi=safe_parse_date(row["latest_service_chassi"], "latest_service_chassi"),
                latest_service_unit=safe_parse_date(row["latest_service_unit"], "latest_service_unit"),
                chassi_nr_vehicle=clean_value(row["chassi_nr_vehicle"], "chassi_nr_vehicle"),
                chassi_nr_unit=clean_value(row["chassi_nr_unit"], "chassi_nr_unit"),
                manufacturing_year_chassi=clean_numeric_value(row["manufacturing_year_chassi"], "manufacturing_year_chassi", int),
                manufacturing_year_unit=clean_numeric_value(row["manufacturing_year_unit"], "manufacturing_year_unit", int),
                hour_meter_chassi=clean_numeric_value(row["hour_meter_chassi"], "hour_meter_chassi", float),
                hour_meter_unit=clean_numeric_value(row["hour_meter_unit"], "hour_meter_unit", float),
                km_chassi=clean_numeric_value(row["km_chassi"], "km_chassi", float),
                local_vehicle_permit=clean_value(row["local_vehicle_permit"], "local_vehicle_permit"),
                vehicle_permit_nr=clean_value(row["vehicle_permit_nr"], "vehicle_permit_nr"),
                vehicle_permit_valid_until=safe_parse_date(row["vehicle_permit_valid_until"], "vehicle_permit_valid_until"),
                in_use=clean_value(row["in_use"], "in_use"),
                net_weight_kg=clean_numeric_value(row["net_weight_kg"], "net_weight_kg", float),
                total_weight_kg=clean_numeric_value(row["total_weight_kg"], "total_weight_kg", float),
                status=clean_value(row["status"], "status"),
                type_of_fuel=clean_value(row["type_of_fuel"], "type_of_fuel"),
                emission_standard=clean_value(row["emission_standard"], "emission_standard"),
                reg_nr_if_applicable=clean_value(row["reg_nr_if_applicable"], "reg_nr_if_applicable"),
                heating=clean_value(row["heating"], "heating"),
                deice_type=clean_value(row["deice_type"], "deice_type"),
                hot_type4=clean_value(row["hot_type4"], "hot_type4"),
                glycol=clean_value(row["glycol"], "glycol"),
                capacity=clean_numeric_value(row["capacity"], "capacity", float),
                ac_type=clean_value(row["ac_type"], "ac_type"),
                single_double_max_ppm=clean_numeric_value(row["single_double_max_ppm"], "single_double_max_ppm", float),
                power=clean_numeric_value(row["power"], "power", float),
                cabin=clean_value(row["cabin"], "cabin"),
                gen2=clean_value(row["gen2"], "gen2"),
                length_m=clean_numeric_value(row["length_m"], "length_m", float),
                height_min_max_mm=clean_value(row["height_min_max_mm"], "height_min_max_mm"),
                self_propelled=clean_value(row["self_propelled"], "self_propelled"),
                owned_by_company=clean_value(row["owned_by_company"], "owned_by_company"),
                owned_by_company2=clean_value(row["owned_by_company2"], "owned_by_company2"),
                type_of_lease=clean_value(row["type_of_lease"], "type_of_lease"),
                term_of_termination=clean_value(row["term_of_termination"], "term_of_termination"),
                purchase_date=safe_parse_date(row["purchase_date"], "purchase_date"),
                agreement_expire_date=safe_parse_date(row["agreement_expire_date"], "agreement_expire_date"),
                risk_assessment=clean_value(row["risk_assessment"], "risk_assessment"),
                training_documentation_available=clean_value(row["training_documentation_available"], "training_documentation_available"),
                item_type=clean_value(row["item_type"], "item_type"),
                path=clean_value(row["path"], "path"),
            )

            records.append(record)
        except Exception as e:
            logger.error(f"Failed to process row {index}: {row.to_dict()}. Error: {e}")

    if records:
        try:
            await GroundSupportEquiptment.bulk_create(records)
            logger.success("Legacy database imported successfully!")
        except Exception as e:
            logger.error(f"Failed to bulk insert records. Error: {e}")
    else:
        logger.warning("No valid records to import.")
