#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def check_python_version():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    return run_command("pip install -r requirements.txt", "Installing dependencies")


def run_tests():
    return run_command("python test_solution.py", "Running test suite")


def validate_schema():
    return run_command("python validate_schema.py", "Validating schema")


def main():
    print("Challenge 1B Setup")
    print("=" * 50)
    
    if not check_python_version():
        sys.exit(1)
    
    if not install_dependencies():
        print("Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    print("\nRunning tests...")
    if not run_tests():
        print("Some tests failed. Please check the output above.")
        return False
    
    print("\nValidating schema...")
    if not validate_schema():
        print("Schema validation failed. Please check the output above.")
        return False
    
    print("\n" + "=" * 50)
    print("✓ Setup completed successfully!")
    print("\nYou can now run the processor:")
    print("  python process.py")
    print("  python main.py")
    print("\nOr run tests:")
    print("  python test_solution.py")
    print("  python validate_schema.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 