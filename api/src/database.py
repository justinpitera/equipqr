"""
src/database.py - This file contains various database methods used throughout the lifespan of the api.

Date: November 25, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""
# Standard
import re
import csv
import math
from uuid import uuid4
from datetime import datetime

# Third-party
from loguru import logger
import pandas as pd
import pytz

# Local
from src import API_CONFIG
from src.models import GroundSupportEquiptment, ImportMetadata, Location
from src.enums import LocationTypeEnum

# Constants
LEGACY_CSV_PATH: str = API_CONFIG["database"]["importer"]["legacy_path"]
TIMEZONE = pytz.UTC


def clean_value(value: object, field_name: str) -> str | None:
    """Converts NaN or invalid values to None for database compatibility."""
    if isinstance(value, (float, int)):
        if math.isnan(value):  # Handles NaN
            return None
    elif value is None or (isinstance(value, str) and not value.strip()):
        return None
    return str(value)



def clean_numeric_value(value: object, field_name: str, numeric_type: type[int | float] = int) -> int | float | None:
    """
    Cleans numeric values by removing non-numeric characters and converts to the specified numeric type.
    """
    try:
        if value is None or math.isnan(value):
            return None

        match value:
            case int() | float():
                return numeric_type(value)
            case str():
                cleaned_value = re.sub(r"[^\d.]", "", value)
                return numeric_type(cleaned_value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid numeric value in field '{field_name}': {value}. Error: {e}")
    return None


def safe_parse_date(value: object, field_name: str) -> datetime | None:
    """Safely parses a date, handling multiple formats and logging invalid inputs."""
    try:
        if pd.isna(value) or value is None:
            return None

        match value:
            case int() | float():
                return datetime.fromtimestamp(value, tz=TIMEZONE)
            case str():
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    return datetime.strptime(value, "%m/%d/%Y")
    except Exception as e:
        logger.warning(f"Invalid date in field '{field_name}': {value}. Error: {e}")
    return None


async def parse_gse_row(row: pd.Series) -> GroundSupportEquiptment | None:
    """Parses and cleans a row into a GroundSupportEquiptment record."""
    try:
        return GroundSupportEquiptment(
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
            manufacturing_year_chassi=clean_numeric_value(row["manufacturing_year_chassi"], "manufacturing_year_chassi", int),
            hour_meter_chassi=clean_numeric_value(row["hour_meter_chassi"], "hour_meter_chassi", float),
            km_chassi=clean_numeric_value(row["km_chassi"], "km_chassi", float),
            status=clean_value(row["status"], "status"),
            purchase_date=safe_parse_date(row["purchase_date"], "purchase_date"),
            agreement_expire_date=safe_parse_date(row["agreement_expire_date"], "agreement_expire_date"),
            path="/default"  # Add a default path value
        )
    except Exception as e:
        logger.error(f"Row parsing failed: {row.to_dict()} | Error: {e}")
    return None


async def database_importer() -> None:
    """Imports data from the legacy CSV database."""
    logger.info("Starting legacy database import...")

    file_name = LEGACY_CSV_PATH.split("/")[-1]
    existing_import = await ImportMetadata.filter(file_name=file_name).first()

    if existing_import:
        logger.warning(f"Database '{file_name}' already imported on {existing_import.imported_at}. Skipping.")
        return

    try:
        df = pd.read_csv(LEGACY_CSV_PATH)
    except Exception as e:
        logger.error(f"Error reading CSV file '{file_name}': {e}")
        return

    parsed_records: list[GroundSupportEquiptment] = [
        record
        for _, row in df.iterrows()
        if (record := await parse_gse_row(row)) is not None
    ]

    if parsed_records:
        await GroundSupportEquiptment.bulk_create(parsed_records, batch_size=100)
        logger.info(f"Imported {len(parsed_records)} records successfully.")
    else:
        logger.warning("No valid records found for import.")

    await ImportMetadata.create(file_name=file_name, imported_at=datetime.now(TIMEZONE))
    logger.info("Legacy database import completed.")


async def location_importer(file_path: str, icao_code: str) -> None:
    """Imports location data from a CSV file into the Location table."""
    logger.info(f"Starting location import from {file_path} for ICAO code {icao_code}.")

    try:
        with open(file_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)

            locations: list[Location] = []
            for row in reader:
                location_name = row.get("location")
                location_type = row.get("type")
                aircraft = row.get("aircraft")

                if not all([location_name, location_type, aircraft]):
                    logger.warning(f"Skipping incomplete row: {row}")
                    continue

                try:
                    location_type_enum = LocationTypeEnum[location_type.upper()]
                except KeyError:
                    logger.warning(f"Invalid location type '{location_type}' in row: {row}")
                    continue

                locations.append(
                    Location(
                        id=uuid4(),
                        icao_code=icao_code,
                        location=location_name,
                        aircraft=aircraft,
                        location_type=location_type_enum,
                    )
                )

            if locations:
                await Location.bulk_create(locations, batch_size=50)
                logger.info(f"Imported {len(locations)} locations successfully.")
            else:
                logger.warning("No valid locations found for import.")
    except Exception as e:
        logger.error(f"An error occurred while importing locations: {e}")
