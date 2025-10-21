#!/bin/bash
# Worklog Manager - Unix/Linux/Mac Startup Script
# Version 2.0.0
#
# This shell script provides an easy way to start Worklog Manager on Unix-like systems

echo "Worklog Manager - Unix/Linux/Mac Startup"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.7 or higher"
        echo "Ubuntu/Debian: sudo apt install python3"
        echo "macOS: brew install python3 or download from https://python.org"
        echo "Other: Check your distribution's package manager"
        read -p "Press Enter to exit..."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$(${PYTHON_CMD} -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python ${PYTHON_VERSION}"

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Run the startup script
echo "Starting Worklog Manager..."
${PYTHON_CMD} start_worklog.py

# Check exit code
EXIT_CODE=$?
if [ ${EXIT_CODE} -ne 0 ]; then
    echo ""
    echo "Application exited with error code ${EXIT_CODE}"
    read -p "Press Enter to exit..."
fi

exit ${EXIT_CODE}