"""
setup.py - This script is responsible for configurable deployment of the api.

What it does:
    1. Prompts user for configuration details including:
        - Host configuration (address, listening port, TLS/SSL details, etc).
        - Database configuration.
        - Docker deployment.
        
Date: December 4, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

import os
import socket
import secrets
import toml
import random
from datetime import datetime


def find_random_open_port(start=20000, end=30000):
    """Find a random open port in the given range."""
    for _ in range(100):  # Limit attempts to find a port
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    raise RuntimeError(f"No open ports found in the range {start}-{end}.")


def generate_secure_credentials():
    """Generate secure username and password."""
    username = secrets.token_urlsafe(16)
    password = secrets.token_urlsafe(16)
    return username, password


def generate_jwt_secret():
    """Generate a 32-byte hex token for JWT."""
    return secrets.token_hex(32)


def backup_existing_file(filepath):
    """Backup an existing file with a timestamped .old extension."""
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = f"{filepath}.{timestamp}.old"
        os.rename(filepath, backup_path)
        print(f"Existing file {filepath} backed up as {backup_path}")


def create_api_config_file(api_port, db_port, db_username, db_password, jwt_secret):
    """Create the API configuration file with the specified settings."""
    local_network = "192.168.*.*"  # Allow only devices on the local network
    config = {
        "api": {
            "address": "0.0.0.0",
            "port": api_port,
            "ssl_certfile": "../private/certificates/local/192.168.0.102+4.pem",
            "ssl_keyfile": "../private/certificates/local/192.168.0.102+4-key.pem",
        },
        "database": {
            "legacy_path": "database.csv",
            "engine": "tortoise.backends.asyncpg",
            "address": "localhost",
            "port": db_port,
            "username": db_username,
            "password": db_password,
        },
        "cors": {
            "allow_credentials": True,
            "allow_origins": [local_network],
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],  # Limit to essential methods
            "allow_headers": ["Content-Type", "Authorization"],  # Limit to necessary headers
        },
        "jwt": {
            "secret": jwt_secret,
        },
    }
    config_path = "private/configurations/api.config.toml"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # Backup existing configuration file
    backup_existing_file(config_path)

    # Write new configuration
    with open(config_path, "w") as f:
        toml.dump(config, f)
    print(f"API configuration file created at {config_path}")


def create_docker_env_file(db_username, db_password, db_port):
    """Create the Docker .env file with the specified settings."""
    env_content = f"""POSTGRES_USERNAME="{db_username}"
POSTGRES_PASSWORD="{db_password}"
POSTGRES_DATABASE="aviator_pg"
POSTGRES_PORT={db_port}
"""
    env_path = "docker/.env"
    os.makedirs(os.path.dirname(env_path), exist_ok=True)

    # Backup existing .env file
    backup_existing_file(env_path)

    # Write new .env file
    with open(env_path, "w") as f:
        f.write(env_content)
    print(f"Docker .env file created at {env_path}")


def main():
    # Find random secure ports
    api_port = find_random_open_port()
    db_port = find_random_open_port()

    # Generate secure credentials
    db_username, db_password = generate_secure_credentials()

    # Generate a secure JWT secret
    jwt_secret = generate_jwt_secret()

    # Create configuration files
    create_api_config_file(api_port, db_port, db_username, db_password, jwt_secret)
    create_docker_env_file(db_username, db_password, db_port)


if __name__ == "__main__":
    main()
