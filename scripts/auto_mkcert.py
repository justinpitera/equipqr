"""
MKCert Automation Script

This script handles the installation, and usage of MKCert for generating local development 
certificates within Harmony Bundler.

Usage:
    python auto_mkcert.py [--output <FOLDER>]

Features:
    - Automatic MKCert download and installation
    - Generation of SSL certificates for local development domains (localhost, <local_ip>, ie). 
    - Cross compatible, no libraries required other than Python's standard libraries.
        - Linux/macOS/Windows compatible and tested.
"""

import os
import platform
import subprocess
import urllib.request
import urllib.error
import json
import uuid
import hashlib
import atexit
import sys
import tempfile
from typing import Optional
import shutil
import stat
import re
import socket
from traceback import format_exc
from argparse import ArgumentParser

mkcert_filename: Optional[str] = None
STATE_FILE: str = os.path.join(tempfile.gettempdir(), 'mkcert_state.json')

# ANSI color codes
COLORS: dict[str, str] = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'reset': '\033[0m'
}


def colorful_print(message: str, color: str, emoji: str = "") -> None:
    """Print messages with colors and emojis for better readability."""
    color_code = COLORS.get(color, COLORS['white'])  # Default to white if color is not found
    reset_code = COLORS['reset']
    print(f"{emoji} {color_code}{message}{reset_code}")

def colorful_print_multicolor(message_parts: list[tuple[str, str]]) -> None:
    """Prints a message with multiple colors."""
    output = ""
    for message, color in message_parts:
        color_code = COLORS.get(color, COLORS['white'])
        reset_code = COLORS['reset']
        output += f"{color_code}{message}{reset_code}"
    print(output)

def save_state(state: dict[str, str]) -> None:
    """Save current script state to a file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)
    colorful_print("State saved successfully.", "green", "💾")

def load_state() -> dict[str, str]:
    """Load the script state from a file if it exists."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            colorful_print("Loading previous state...", "cyan", "🔄")
            return json.load(f)
    return {}

def clear_state() -> None:
    """Clear the saved state after successful completion."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    colorful_print("State cleared successfully.", "green", "🗑️")

def get_mkcert_path() -> str:
    """Get the path to the MKCert binary based on OS."""
    mkcert_filename = os.path.join(os.getcwd(), "mkcert")
    if platform.system().lower() == "windows":
        mkcert_filename += ".exe"
    return mkcert_filename

def delete_mkcert() -> None:
    """Delete the MKCert binary if it exists."""
    mkcert_path = get_mkcert_path()
    if os.path.exists(mkcert_path):
        colorful_print(f"Deleting MKCert binary at {mkcert_path}...", "yellow", "🗑️")
        try:
            os.remove(mkcert_path)
            colorful_print("MKCert binary deleted successfully.", "green", "✅")
        except Exception as e:
            colorful_print(f"Failed to delete MKCert: {e}", "red", "❌")

def register_cleanup_on_exit() -> None:
    """Register MKCert binary deletion on exit."""
    atexit.register(delete_mkcert)

def get_mac_address() -> str:
    """Gets the MAC address of the system."""
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

def generate_hwid() -> str:
    """Generates a unique hardware identifier (HWID) based on system information."""
    system_info = platform.system() + platform.machine() + platform.processor()
    mac_address = get_mac_address()
    hwid_raw = system_info + mac_address
    hwid_hashed = hashlib.sha256(hwid_raw.encode()).hexdigest()
    return hwid_hashed

def get_user_agent() -> str:
    """Generates a detailed User-Agent string."""
    unique_id = uuid.uuid4()
    hwid = generate_hwid()
    user_agent = f"Harmony-Bundler/1.0.0 ({platform.system()} {platform.machine()}; " \
                 f"https://harmonystack.org; justinpitera@gmail.com; hwid: {hwid}; uuid: {unique_id})"
    return user_agent

def is_mkcert_installed() -> bool:
    """Check if MKCert is already installed."""
    mkcert_path = get_mkcert_path()
    if os.path.exists(mkcert_path):
        colorful_print(f"MKCert binary found at {mkcert_path}. Deleting it before proceeding...", "yellow", "⚠️ ")
        delete_mkcert()
        return False  # Return False because we are forcing reinstallation
    else:
        try:
            result = subprocess.run(['mkcert', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            version = result.stdout.decode('utf-8').strip()
            colorful_print(f"MKCert is installed (Version: {version})", "green", "✅")
            return True
        except FileNotFoundError:
            colorful_print("MKCert is not installed.", "red", "❌")
            return False
        except subprocess.CalledProcessError:
            return False

def get_latest_release(repo: str) -> Optional[dict[str, Optional[str] | list[dict[str, str]]]]:
    """Fetch the latest MKCert release from GitHub using urllib."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {'User-Agent': get_user_agent()}
    try:
        colorful_print("Fetching latest release information...", "cyan", "🌐")
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            release_data = json.load(response)
            return {
                'version': release_data['tag_name'],
                'release_name': release_data['name'],
                'published_at': release_data['published_at'],
                'html_url': release_data['html_url'],
                'assets': [{'name': asset['name'], 'download_url': asset['browser_download_url']} for asset in release_data['assets']]
            }
    except urllib.error.URLError as e:
        colorful_print(f"Error fetching latest release: {e}", "red", "❌")
        return None

def get_mkcert_url(version: str) -> str:
    """Determine the correct MKCert binary URL based on OS and architecture."""
    system = platform.system().lower()
    arch = platform.machine().lower()
    base_url = f"https://github.com/FiloSottile/mkcert/releases/download/{version}/"

    if system == "linux":
        if arch == "x86_64":
            return base_url + f"mkcert-{version}-linux-amd64"
        elif arch == "arm64":
            return base_url + f"mkcert-{version}-linux-arm64"
        elif "arm" in arch:
            return base_url + f"mkcert-{version}-linux-arm"
        else:
            raise Exception(f"Unsupported architecture: {arch} on Linux")
    elif system == "darwin":  # macOS
        if arch == "x86_64":
            return base_url + f"mkcert-{version}-darwin-amd64"
        elif arch == "arm64":
            return base_url + f"mkcert-{version}-darwin-arm64"
        else:
            raise Exception(f"Unsupported architecture: {arch} on macOS")
    elif system == "windows":
        if arch in ["x86_64", "amd64"]:
            return base_url + f"mkcert-{version}-windows-amd64.exe"
        elif arch == "arm64":
            return base_url + f"mkcert-{version}-windows-arm64.exe"
        else:
            raise Exception(f"Unsupported architecture: {arch} on Windows")
    else:
        raise Exception(f"Unsupported operating system: {system}")

def download_mkcert(version: str) -> str | None:
    """Download MKCert for the current platform."""
    global mkcert_filename
    try:
        mkcert_url = get_mkcert_url(version)
    except Exception as e:
        colorful_print(f"{e}", "red", "❌")
        return None

    mkcert_filename = get_mkcert_path()

    colorful_print(f"Downloading MKCert from {mkcert_url} to {mkcert_filename}...", "blue", "⬇️ ")

    try:
        urllib.request.urlretrieve(mkcert_url, mkcert_filename)

        if platform.system().lower() != "windows":
            st = os.stat(mkcert_filename)
            os.chmod(mkcert_filename, st.st_mode | stat.S_IEXEC)

        colorful_print("Download completed successfully.", "green", "✅")
        return mkcert_filename
    except Exception as e:
        colorful_print(f"Failed to download MKCert: {e}", "red", "❌")
        return None

def install_mkcert(mkcert_path: str) -> None:
    """Install MKCert CA if not already installed."""
    colorful_print("Installing MKCert CA...", "blue", "🔧")
    try:
        result = subprocess.run([mkcert_path, "-install"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            error_output = result.stderr.decode('utf-8').strip()
            colorful_print(f"Error: MKCert installation failed with return code {result.returncode}.", "red", "❌")
            colorful_print(f"Error details: {error_output}", "red", "⚠️")

            colorful_print("The MKCert installation was not completed. Please rerun the script and choose 'Yes' to proceed.", "yellow", "⚠️")
            delete_mkcert()
            sys.exit(1)
        else:
            colorful_print("MKCert CA installed successfully.", "green", "✅")
    except subprocess.CalledProcessError as e:
        colorful_print(f"Failed to install MKCert CA: {e}", "red", "❌")
        delete_mkcert()
        sys.exit(1)

def uninstall_mkcert() -> None:
    """Uninstall MKCert CA."""
    colorful_print("Uninstalling MKCert CA...", "yellow", "🗑️")
    try:
        subprocess.run(['mkcert', '-uninstall'], check=True)
        colorful_print("MKCert CA uninstalled successfully.", "green", "✅")
    except subprocess.CalledProcessError as e:
        colorful_print(f"Failed to uninstall MKCert CA: {e}", "red", "❌")

def parse_mkcert_response(mkcert_output: str) -> tuple[list[str], Optional[str], Optional[str], Optional[str]]:
    """Extracts domain names, certificate path, key path, and expiration date from MKCert output."""
    domain_pattern = re.compile(r' - "(.*?)"')
    domains = domain_pattern.findall(mkcert_output)

    cert_pattern = re.compile(r'The certificate is at "(.*?)"')
    key_pattern = re.compile(r'the key at "(.*?)"')
    expiry_pattern = re.compile(r'It will expire on (\d+ \w+ \d+)')

    cert_path = key_path = expiry_date = None

    cert_match = cert_pattern.search(mkcert_output)
    if cert_match:
        cert_path = cert_match.group(1)

    key_match = key_pattern.search(mkcert_output)
    if key_match:
        key_path = key_match.group(1)

    expiry_match = expiry_pattern.search(mkcert_output)
    if expiry_match:
        expiry_date = expiry_match.group(1)

    return domains, cert_path, key_path, expiry_date

def generate_certificate(domains: list[str], output_dir: str) -> None:
    """Generate a certificate for the provided domains using MKCert and handle the output."""
    output_dir = os.path.abspath(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cert_file = os.path.join(output_dir, 'cert.pem')
    key_file = os.path.join(output_dir, 'key.pem')

    try:
        result = subprocess.run(['mkcert', '-key-file', key_file, '-cert-file', cert_file, *domains],
                                check=True, capture_output=True, text=True)
        mkcert_output = result.stderr if result.stderr else result.stdout  # Check STDERR first, then STDOUT

        # Parsing the output from MKCert
        domains, cert_path, key_path, expiry_date = parse_mkcert_response(mkcert_output)
        
        colorful_print_multicolor([
            ("🎉 Success! ", "green"), 
            ("Certificate generated for domains: ", "magenta"), 
            (f"{', '.join(domains)}", "green"), 
            (" 🌐", "white")
        ])

        colorful_print_multicolor([
            ("📄 Certificate Path: ", "magenta"), 
            (f"{cert_path}", "blue"), 
            (" (Keep this safe!)", "yellow")
        ])

        colorful_print_multicolor([
            ("🔑 Key Path: ", "magenta"), 
            (f"{key_path}", "blue"), 
            (" (Ensure this remains private!)", "red")
        ])

        colorful_print_multicolor([
            ("⏳ Expiration Date: ", "magenta"), 
            (f"{expiry_date}", "cyan"), 
            (" (Renew before this date!)", "yellow")
        ])

        colorful_print_multicolor([
            ("🔒 Your secure certificate is ready to use. Thank you for using MKCert! ", "green"), 
            ("🌍 Keeping the web secure, one cert at a time!", "cyan")
        ])

        colorful_print(f"Certificates generated successfully: {key_file}, {cert_file} 🎉", "green", "✅")
    except subprocess.CalledProcessError:
        error_message = "MKCert failed to generate local certificates."
        traceback_details = format_exc()
        colorful_print(f"{error_message}\nError details:\n{traceback_details}", "red", "❌")


def ensure_mkcert_installed(version: str) -> bool:
    """Ensure MKCert is installed and ready to use."""
    if is_mkcert_installed():
        colorful_print(
            "Warning: MKCert already detected by Harmony Bundler vendor grabber. "
            "Reinstalling will nullify any current valid certificate key pairs generated by MKCert.",
            "yellow", "⚠️"
        )

        while True:
            user_input = input("Do you want to proceed with reinstalling MKCert? (Y/N): ").strip().upper()
            
            if user_input == 'Y':
                colorful_print("Proceeding with MKCert reinstallation...", "cyan", "🔄")
                return True
            elif user_input == 'N':
                colorful_print("Exiting to avoid reinstallation. Process aborted.", "green", "✅")
                sys.exit(0)
            else:
                colorful_print("Invalid input. Please enter 'Y' for Yes or 'N' for No.", "red", "❌")

    else:
        colorful_print("MKCert not found, downloading and installing...", "blue", "⬇️ ")
        mkcert_path = download_mkcert(version)
        if mkcert_path:
            install_mkcert(mkcert_path)
            
            if platform.system().lower() != "windows":
                install_dir = "/usr/local/bin"
                if os.geteuid() != 0:
                    colorful_print("This action requires sudo privileges on Linux systems.", "yellow", "⚠️")
                    install_dir = os.path.expanduser("~/.local/bin")

                colorful_print(f"Moving MKCert to {install_dir}...", "cyan", "📂")
                os.makedirs(install_dir, exist_ok=True)
                shutil.move(mkcert_path, os.path.join(install_dir, "mkcert"))

            colorful_print("MKCert installed successfully", "green", "✅")
            return True
    return False

def main(domains: list[str], output_dir: str) -> None:
    """Main function to manage MKCert installation and certificate generation."""
    try:
        save_state({"status": "started"})
        
        repo_name = "FiloSottile/mkcert"
        release_info = get_latest_release(repo_name)
        if not release_info:
            colorful_print("Failed to fetch the latest release.", "red", "❌")
            sys.exit(1)

        if release_info and isinstance(release_info['version'], str):
            if not ensure_mkcert_installed(release_info['version']):
                sys.exit(1)
        else:
            colorful_print("Invalid MKCert release version.", "red", "❌")
            sys.exit(1)

        generate_certificate(domains, output_dir)
        colorful_print_multicolor([
            ("🙏 A huge thank you to the ", "cyan"),
            ("MKCert team", "green"),
            (" for helping us keep the web secure! ", "cyan"),
            ("🌍🔒", "yellow")
        ])

        colorful_print_multicolor([
            ("🔗 Learn more about their awesome work at: ", "magenta"),
            ("https://github.com/FiloSottile/mkcert", "blue")
        ])

        colorful_print_multicolor([
            ("💡 Pro Tip: ", "yellow"),
            ("Always ensure your certificates are up to date to maintain security!", "green")
        ])
        clear_state()
    except KeyboardInterrupt:
        colorful_print("\nProcess interrupted by user.", "red", "❌")
        clear_state()
        sys.exit(1)
    except Exception as e:
        colorful_print(f"An error occurred: {e}", "red", "❌")
        clear_state()
        sys.exit(1)

if __name__ == "__main__":
    parser = ArgumentParser(description="MKCert Automation Script for Harmony Bundler")
    parser.add_argument('--output', type=str, default=os.getcwd(),
                        help="Output directory for the generated certificates (default: current directory)")
    args = parser.parse_args()

    domains_to_generate = ["localhost", socket.gethostbyname(socket.gethostname())]
    main(domains_to_generate, args.output)
