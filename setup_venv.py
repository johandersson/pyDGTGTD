#!/usr/bin/env python3
"""
Setup script for wxGTD virtual environment.

This script creates a virtual environment and installs all required dependencies.
Run this script before using the application for the first time.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Set up the virtual environment and install dependencies."""
    print("=" * 60)
    print("wxGTD Virtual Environment Setup")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version.split()[0]}")
    
    # Define venv path
    venv_path = Path(__file__).parent / "venv"
    
    # Create virtual environment
    if venv_path.exists():
        print(f"⚠ Virtual environment already exists at: {venv_path}")
        response = input("Do you want to recreate it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping virtual environment creation.")
        else:
            print("Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
            print("Creating new virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print(f"✓ Virtual environment created at: {venv_path}")
    else:
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print(f"✓ Virtual environment created at: {venv_path}")
    
    # Determine the pip executable path
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Upgrade pip
    print("\nUpgrading pip...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    print("✓ pip upgraded")
    
    # Install dependencies
    print("\nInstalling dependencies from requirements.txt...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
        print("✓ Dependencies installed")
    else:
        print("⚠ requirements.txt not found, skipping dependency installation")
    
    # Install the package in development mode
    print("\nInstalling wxGTD in development mode...")
    subprocess.run([str(pip_path), "install", "-e", "."], check=True)
    print("✓ wxGTD installed in development mode")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print(f"  .\\venv\\Scripts\\activate")
    else:
        print(f"  source venv/bin/activate")
    print("\nTo run wxGTD:")
    print("  python wxgtd.pyw")
    print("\nOr use the CLI version:")
    print("  python wxgtd_cli.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠ Setup interrupted by user.")
        sys.exit(1)

