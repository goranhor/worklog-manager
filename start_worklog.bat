@echo off
REM Worklog Manager - Windows Startup Script
REM Version 2.0.0
REM 
REM This batch file provides an easy way to start Worklog Manager on Windows

echo Worklog Manager - Windows Startup
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

REM Change to the script directory
cd /d "%~dp0"

REM Run the startup script
echo Starting Worklog Manager...
python start_worklog.py

REM Pause if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)