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

def _find_certificate_key_pair(directory: Path) -> tuple[Path, Path]:
    """
    Searches for a certificate and key pair within a given directory.
    """
    if not directory.is_dir():
        raise ValueError(f"{directory} is not a valid directory.")

    cert_ext: set[str] = {".crt", ".pem"}
    key_ext: set[str] = {".key", ".pem"}
    cert_file: Path | None = None
    key_file: Path | None = None

    for file in directory.iterdir():
        if file.is_file():
            if file.suffix in cert_ext and not cert_file:
                cert_file = file
            elif file.suffix in key_ext and not key_file:
                key_file = file

            if cert_file and key_file:
                return cert_file, key_file

    raise ValueError("Valid certificate and key files not found in the directory.")


async def _main() -> None:
    ssl_cert, ssl_key = _find_certificate_key_pair(directory=Path(API_CONFIG["api"]["ssl_directory"]))

    _GRANIAN_SERVER: Granian = Granian(
        target="src.main:_",
        address=str(API_CONFIG["api"]["address"]),
        interface=Interfaces.ASGI,
        log_enabled=True,
        log_level=LogLevels.warn,
        port=int(API_CONFIG["api"]["port"]),
        ssl_cert=ssl_cert,
        ssl_key=ssl_key,
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
    finally:
        print(f"{Fore.GREEN}[SHUTDOWN]{Style.RESET_ALL} API shutdown successfully!")
