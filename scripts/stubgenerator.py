import os
import subprocess
from pathlib import Path

# Paths
SRC_DIR = "./src"
TYPINGS_DIR = "./typings/src"

def ensure_directory(path):
    """Ensure that the given directory exists."""
    os.makedirs(path, exist_ok=True)

def file_exists(file_path):
    """Check if a file already exists."""
    return os.path.exists(file_path)

def confirm_overwrite(file_path):
    """Ask the user if they want to overwrite an existing file."""
    response = input(f"File '{file_path}' already exists. Overwrite? (y/n): ").strip().lower()
    return response == "y"

def generate_stubs():
    """Generate stubs for all modules in the src directory."""
    ensure_directory(TYPINGS_DIR)
    
    # Set PYTHONPATH to include the src directory
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(SRC_DIR)
    
    # Find all Python modules in the source directory
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(".py"):
                relative_path = os.path.relpath(root, SRC_DIR)
                module_name = relative_path.replace(os.path.sep, ".")
                if module_name == ".":
                    module_name = file[:-3]  # Handle top-level modules
                else:
                    module_name = f"{module_name}.{file[:-3]}"

                # Output stub file path
                stub_file_path = os.path.join(TYPINGS_DIR, f"{module_name.replace('.', '/')}.pyi")
                ensure_directory(os.path.dirname(stub_file_path))
                
                if file_exists(stub_file_path) and not confirm_overwrite(stub_file_path):
                    print(f"Skipping {module_name}...")
                    continue

                # Generate the stub
                print(f"Generating stub for {module_name}...")
                try:
                    subprocess.run(
                        ["stubgen", "-m", module_name, "-o", TYPINGS_DIR],
                        check=True,
                        env=env
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Failed to generate stub for {module_name}: {e}")

if __name__ == "__main__":
    generate_stubs()
