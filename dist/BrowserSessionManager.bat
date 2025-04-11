@echo off
echo Browser Session Manager
echo =====================
echo.
echo Starting Browser Session Manager...

:: Set current directory to the script location
cd /d "%~dp0"

:: Run the application
call run_app.bat

exit /b 0