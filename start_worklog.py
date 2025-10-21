#!/usr/bin/env python3
"""
Worklog Manager - Easy Startup Script

This script provides an easy way to start the Worklog Manager application
with proper environment setup and error handling.

Usage:
    python start_worklog.py
    or
    double-click this file if Python is properly configured

Author: GitHub Copilot
Version: 1.5.0
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements."""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required.")
        print(f"Current Python version: {sys.version}")
        print("\nPlease update Python and try again.")
        input("Press Enter to exit...")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are available."""
    missing_deps = []
    
    # Core dependencies that should be available
    required_modules = [
        'tkinter',
        'sqlite3',
        'threading',
        'json',
        'csv',
        'datetime',
        'pathlib'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)
    
    # Optional dependencies for advanced features
    optional_modules = {
        'win32api': 'Windows API support (system tray)',
        'plyer': 'Cross-platform notifications', 
        'reportlab': 'PDF export functionality'
    }
    
    missing_optional = []
    for module, description in optional_modules.items():
        try:
            __import__(module)
        except ImportError:
            missing_optional.append(f"{module} - {description}")
    
    if missing_deps:
        print("ERROR: Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install missing dependencies and try again.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if missing_optional:
        print("WARNING: Some optional features may not work:")
        for dep in missing_optional:
            print(f"  - {dep}")
        print("\nTo install optional dependencies, run:")
        print("  pip install plyer reportlab pywin32  # (Windows)")
        print("  pip install plyer reportlab  # (Linux/Mac)")
        print("\nContinuing with basic functionality...")
        print("-" * 50)

def setup_environment():
    """Setup the application environment."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Change to the application directory
    os.chdir(script_dir)
    
    # Add to Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    return script_dir

def start_application():
    """Start the Worklog Manager application."""
    try:
        # Import and run the main application
        from main import main
        print("Starting Worklog Manager...")
        print("=" * 50)
        main()
        
    except ImportError as e:
        print(f"ERROR: Could not import main application: {e}")
        print("Make sure all application files are present in the current directory.")
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"ERROR: Application failed to start: {e}")
        print("\nFor detailed error information, check the log files in the 'logs' directory.")
        input("Press Enter to exit...")
        sys.exit(1)

def main():
    """Main startup function."""
    print("Worklog Manager - Startup Script v1.5.0")
    print("=" * 50)
    
    # Check system requirements
    print("Checking Python version...")
    check_python_version()
    
    print("Checking dependencies...")
    check_dependencies()
    
    print("Setting up environment...")
    app_dir = setup_environment()
    
    print(f"Working directory: {app_dir}")
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()