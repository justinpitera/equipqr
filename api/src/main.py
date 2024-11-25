"""
src/main.py - Main initialization script.

Date: November 21, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
import asyncio
from pathlib import Path

# Third-party
from granian import Granian
from granian.constants import Interfaces
from granian.log import LogLevels
from colorama import Fore, Style
from starlette.applications import Starlette

# Local
from . import API_STARTUP_MESSAGE, API_CONFIG
from src.asgi import init_asgi

_: Starlette = init_asgi()

async def _main() -> None:
    _GRANIAN_SERVER: Granian = Granian(
        target="src.main:_",
        address=API_CONFIG["api"]["address"],
        interface=Interfaces.ASGI,
        log_enabled=True,            
        log_level=LogLevels.warn,
        port=API_CONFIG["api"]["port"],
        ssl_cert=Path(API_CONFIG["api"]["ssl_certfile"]),
        ssl_key=Path(API_CONFIG["api"]["ssl_keyfile"]),
        process_name="aviator_fjelmelings"
    )
    _GRANIAN_SERVER.serve()

if __name__ == "__main__":
    try:
        print(API_STARTUP_MESSAGE)
        asyncio.run(_main())
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        print(f"{Fore.GREEN}[SHUTDOWN]{Style.RESET_ALL} API shutdown successfully!")
