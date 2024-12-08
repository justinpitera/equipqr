"""
src/__init__.py - Main initialization module.

Date: November 21, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
import toml, os
from pathlib import Path
from typing import Any

# Third-party
from colorama import Style

API_CONFIG: dict[str, Any] = toml.load(Path(os.getcwd()).joinpath("../private/configurations/api.config.toml"))
API_VERSION: str = (lambda line: line.split(sep="=")[1].strip().strip('"') if line.startswith("version") else "Unknown")(line=open(file="pyproject.toml").readlines()[2].strip())
API_STARTUP_MESSAGE: str = f"""
╭━━╮╱╱╱╭╮╱╱╭╮
┃╭╮┣━┳━╋╋━╮┃╰┳━┳┳╮
┃┣┫┣╮┃╭┫┃╋╰┫╭┫╋┃╭╯
╰╯╰╯╰━╯╰┻━━┻━┻━┻╯  {Style.BRIGHT} Reporter {API_VERSION}{Style.RESET_ALL}\n
=================
Listening on {API_CONFIG["api"]["address"]}:{API_CONFIG["api"]["port"]}
"""
TORTOISE_CONFIG: dict[str, Any] = {
    "connections": {
        "default": {
            "engine": API_CONFIG["database"]["engine"],
            "credentials": {
                "host": API_CONFIG["database"]["address"],
                "port": API_CONFIG["database"]["port"],
                "user": API_CONFIG["database"]["username"],
                "password": API_CONFIG["database"]["password"],
                "database": "aviator_pg",
            }
        }
    },
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}
