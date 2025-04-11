@echo off
title Browser Session Manager Launcher
echo ====================================
echo Browser Session Manager Launcher
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Run the launcher script
echo Starting Browser Session Manager...
python launch_browser_manager.py
if %errorlevel% neq 0 (
    echo.
    echo Browser Session Manager exited with an error.
    echo.
    pause
)

exit /b %errorlevel%