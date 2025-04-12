@echo off
REM Browser Session Manager CLI Launcher
REM This script makes it easier to run command-line operations

echo Browser Session Manager CLI
echo --------------------------------

REM Check if python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo X Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check for required packages
echo Checking dependencies...
python -c "import undetected_chromedriver, selenium, fake_useragent" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Required packages not found. Would you like to install them? (y/n)
    set /p response=
    if /i "%response%"=="y" (
        echo Installing required packages...
        pip install undetected-chromedriver selenium fake-useragent requests psutil
    ) else (
        echo Cannot continue without required packages.
        exit /b 1
    )
)

REM Show available commands if no arguments provided
if "%~1"=="" (
    echo.
    echo Browser Session Manager CLI
    echo --------------------------------
    echo Available commands:
    echo.
    echo 1. List all saved profiles:
    echo    run_cli.bat list
    echo.
    echo 2. Launch a browser with a profile:
    echo    run_cli.bat launch --profile PROFILE_NAME [--proxy IP:PORT] [--headless]
    echo.
    echo 3. Delete a profile:
    echo    run_cli.bat delete --profile PROFILE_NAME
    echo.
    echo 4. Rename a profile:
    echo    run_cli.bat rename --profile OLD_NAME --new-name NEW_NAME
    echo.
    echo Examples:
    echo    run_cli.bat list
    echo    run_cli.bat launch --profile gmail_account1 --proxy 123.45.67.89:8080
    echo    run_cli.bat delete --profile unwanted_profile
    echo    run_cli.bat rename --profile old_name --new-name better_name
    echo --------------------------------
    exit /b 0
)

REM Run the requested command
echo Executing command: %*
python test_enhanced_browser.py %*