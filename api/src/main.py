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
from colorama import Fore, Style, init as init_colorama
from starlette.applications import Starlette

# Local
from . import API_STARTUP_MESSAGE, API_CONFIG
from src.asgi import init_asgi

# Initialization
_: Starlette = init_asgi()
init_colorama(autoreset=True)


async def _main() -> None:

    _GRANIAN_SERVER: Granian = Granian(
        target="src.main:_",
        address="0.0.0.0",
        interface=Interfaces.ASGI,
        log_enabled=True,
        log_level=LogLevels.warn,
        port=7879,
        ssl_cert=Path("../private/certificates/localhost+2.pem"),
        ssl_key=Path("../private/certificates/localhost+2-key.pem"),
        process_name="aviator_fjelmelings",
        pid_file=Path("./.pid")
    )
    _GRANIAN_SERVER.serve()


if __name__ == "__main__":
    try:
        print(API_STARTUP_MESSAGE)
        asyncio.run(main=_main())
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    except Exception as e:
        print(e)
    finally:
        print(f"{Fore.GREEN}[SHUTDOWN]{Style.RESET_ALL} API shutdown successfully!")
