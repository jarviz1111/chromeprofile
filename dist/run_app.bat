@echo off
echo Browser Session Manager
echo =====================
echo Initializing application...

:: Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: Node.js is not installed or not in PATH.
  echo Please install Node.js from https://nodejs.org/
  echo Press any key to exit...
  pause >nul
  exit /b 1
)

:: Check if dependencies are installed
if not exist node_modules (
  echo Installing dependencies...
  npm install
  if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies.
    echo Press any key to exit...
    pause >nul
    exit /b 1
  )
)

echo Starting Browser Session Manager...
echo The application will open in your default browser.
echo Please do not close this window while using the application.

:: Start the application server
start /B node app.js

:: Wait a moment for the server to start
timeout /t 2 /nobreak >nul

:: Open browser to the application
start http://localhost:5000

echo.
echo Browser Session Manager is running.
echo To stop the application, close this window.
echo.

pause
taskkill /F /IM node.exe
exit /b 0