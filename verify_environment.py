#!/usr/bin/env python
"""
Script to verify that we're working in the correct virtual environment
and that all dependencies are properly installed.
"""

import sys
import os
import subprocess

def check_virtual_environment():
    """Check if we're in the correct virtual environment"""
    print("=== Environment Verification ===")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("✓ Running in virtual environment")
        print(f"  Virtual environment: {sys.prefix}")
    else:
        print("✗ NOT running in virtual environment")
        print("  Please activate the virtual environment before running this script")
        return False
    
    return True

def check_python_version():
    """Check Python version"""
    print(f"\n✓ Python version: {sys.version}")
    
    # Check if it's the expected version (3.13.5 based on our installation)
    if "3.13.5" in sys.version:
        print("  This is the expected Python version for this project")
    else:
        print("  Warning: Different Python version than expected")

def check_required_packages():
    """Check if required packages are installed"""
    print("\n=== Package Verification ===")
    
    required_packages = [
        'Django',
        'Pillow',
        'reportlab',
        'openpyxl',
        'icalendar',
        'django-crispy-forms',
        'crispy-tailwind'
    ]
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        installed_packages = result.stdout.lower()
        
        for package in required_packages:
            if package.lower() in installed_packages:
                print(f"✓ {package} is installed")
            else:
                print(f"✗ {package} is NOT installed")
                
    except Exception as e:
        print(f"Error checking packages: {e}")

def check_environment_variables():
    """Check relevant environment variables"""
    print("\n=== Environment Variables ===")
    
    env_vars = ['PYTHONPATH', 'DJANGO_SETTINGS_MODULE']
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")

def main():
    """Main verification function"""
    print("EventoSys Environment Verification Script")
    print("=" * 40)
    
    if not check_virtual_environment():
        sys.exit(1)
    
    check_python_version()
    check_required_packages()
    check_environment_variables()
    
    print("\n=== Summary ===")
    print("If all checks show ✓, you're ready to work on the EventoSys project!")
    print("Always remember to activate the virtual environment before working on this project.")

if __name__ == "__main__":
    main()