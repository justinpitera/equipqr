import csv
import re
import inflect
from typing import Dict, List
from datetime import datetime

# Initialize inflect engine for pluralization/singularization
inflector = inflect.engine()

# Predefined units to detect (you can extend this list)
UNIT_PATTERNS = [
    r"\b(?:kg|lbs|oz|g|mg)\b",    # Weight units
    r"\b(?:m|cm|mm|km|in|ft)\b",  # Length units
    r"\b(?:s|ms|min|hr|h)\b",     # Time units
    r"\b(?:°C|°F|K)\b",           # Temperature units
    r"\b(?:l|ml|gal|qt|pt)\b",    # Volume units
    r"\b(?:%|ppm|ppt|ppb)\b",     # Concentration units
]

UNIT_TYPE_MAPPING = {
    "weight": "FloatField", 
    "length": "FloatField",
    "time": "FloatField",
    "temperature": "FloatField",
    "volume": "FloatField",
    "concentration": "FloatField",
}

def to_snake_case(name: str) -> str:
    """
    Convert a string to snake_case.
    """
    name = inflector.singular_noun(name) or name  # Singularize column names
    name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)  # Handle camelCase
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name)  # Replace non-alphanumeric with underscores
    return name.lower().strip("_")

def is_date(value: str) -> bool:
    """
    Check if a value is a valid date.
    """
    date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"]
    for fmt in date_formats:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False

def is_float(value: str) -> bool:
    """
    Check if a value is a valid float (including scientific notation).
    """
    try:
        float(value)
        return True
    except ValueError:
        return False

def detect_units(value: str) -> str:
    """
    Detect if a value contains a unit and return its type if matched.
    """
    for pattern, unit_type in zip(UNIT_PATTERNS, UNIT_TYPE_MAPPING.keys()):
        if re.search(pattern, value, re.IGNORECASE):
            return UNIT_TYPE_MAPPING[unit_type]
    return ""

def infer_consistent_type(values: List[str]) -> str:
    """
    Infer the most consistent type for a list of values.
    """
    has_float = has_int = has_bool = has_datetime = has_text = has_units = False
    unit_type = ""
    
    for value in values:
        value = value.strip()
        if not value:  # Skip null or empty values
            continue
        if detect_units(value):
            has_units = True
            unit_type = detect_units(value)
        elif value.isdigit():
            has_int = True
        elif is_float(value):
            has_float = True
        elif is_date(value):
            has_datetime = True
        elif value.lower() in {"true", "false"}:
            has_bool = True
        elif len(value) > 255:
            has_text = True

    if has_text:
        return "TextField"
    if has_units:
        return unit_type
    if has_datetime:
        return "DatetimeField"
    if has_bool:
        return "BooleanField"
    if has_float:
        return "FloatField"
    if has_int:
        return "IntField"
    return "CharField"

def get_first_non_null_value(values: List[str]) -> str:
    """
    Get the first non-null, non-empty value from a list.
    """
    for value in values:
        if value.strip():  # Ignore null or empty values
            return value.strip()
    return "N/A"  # Default if no valid values exist

def analyze_csv_and_generate_model(csv_file: str, model_name: str, output_file: str, rationale_file: str) -> None:
    """
    Analyze a CSV file and generate a Tortoise ORM model with advanced type checking,
    along with a rationale file explaining type decisions.
    """
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        if not rows:
            raise ValueError("CSV file is empty!")

    # Collect all values for each column to determine the most consistent type
    field_types: Dict[str, List[str]] = {to_snake_case(col): [] for col in rows[0].keys()}
    for row in rows:
        for column, value in row.items():
            field_types[to_snake_case(column)].append(value)

    # Generate model fields with inferred types
    field_definitions = []
    rationale = []
    for field, values in field_types.items():
        inferred_type = infer_consistent_type(values)
        sample_value = get_first_non_null_value(values)  # Get a non-null sample value

        # Add explanation to rationale
        rationale.append(f"Field: {field}\nSample Value: {sample_value}\nInferred Type: {inferred_type}\n")

        # Generate model field definition
        if inferred_type == "TextField":
            field_definitions.append(f'    {field} = fields.TextField()')
        elif inferred_type == "DatetimeField":
            field_definitions.append(f'    {field} = fields.DatetimeField()')
        elif inferred_type == "BooleanField":
            field_definitions.append(f'    {field} = fields.BooleanField()')
        elif inferred_type == "FloatField":
            field_definitions.append(f'    {field} = fields.FloatField()')
        elif inferred_type == "IntField":
            field_definitions.append(f'    {field} = fields.IntField()')
        else:  # Default to CharField
            field_definitions.append(f'    {field} = fields.CharField(max_length=255)')

    # Create the Tortoise ORM model code
    model_code = f"""
from tortoise import fields
from tortoise.models import Model


class {model_name}(Model):
    id = fields.IntField(pk=True)  # Default primary key
{"\n".join(field_definitions)}
    """

    # Save the model code to the output file
    with open(output_file, "w") as f:
        f.write(model_code.strip())

    # Save the rationale to the rationale file
    with open(rationale_file, "w") as f:
        f.write("\n".join(rationale))

    print(f"Model code has been saved to {output_file}!")
    print(f"Rationale has been saved to {rationale_file}!")


# Usage example
if __name__ == "__main__":
    csv_path = "input.csv"  # Replace with your CSV file path
    model_name = "GeneratedModel"  # Replace with your desired model name
    output_file = "generated_model.py"  # File to save the model code
    rationale_file = "model_rationale.txt"  # File to save the rationale
    analyze_csv_and_generate_model(csv_path, model_name, output_file, rationale_file)
