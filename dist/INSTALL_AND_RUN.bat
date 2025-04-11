@echo off
setlocal enabledelayedexpansion

echo Browser Session Manager - Installation Helper
echo ============================================
echo.

:: Set current directory to the script location
cd /d "%~dp0"

:: Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Node.js is not installed. Would you like to download and install it?
  echo.
  echo 1. Yes, download and install Node.js (recommended)
  echo 2. No, I'll install it myself
  echo.
  set /p choice="Enter your choice (1 or 2): "
  
  if "!choice!"=="1" (
    echo.
    echo Downloading Node.js installer...
    echo This might take a moment depending on your internet connection.
    
    :: Download Node.js installer
    powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.1/node-v20.11.1-x64.msi' -OutFile 'node-installer.msi'}"
    
    if %ERRORLEVEL% NEQ 0 (
      echo Failed to download Node.js installer.
      echo Please download and install Node.js manually from https://nodejs.org/
      echo.
      echo After installing Node.js, run BrowserSessionManager.bat to start the application.
      pause
      exit /b 1
    )
    
    echo.
    echo Installing Node.js...
    echo A new window will open. Please follow the installation instructions.
    echo.
    
    start /wait node-installer.msi
    
    echo.
    echo Cleaning up...
    del node-installer.msi
    
    echo.
    echo Node.js installation completed.
  ) else (
    echo.
    echo Please install Node.js manually from https://nodejs.org/
    echo After installing Node.js, run BrowserSessionManager.bat to start the application.
    pause
    exit /b 0
  )
)

:: Install dependencies if not already installed
if not exist node_modules (
  echo Installing application dependencies...
  echo This might take a few minutes.
  
  call npm install
  
  if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
  )
  
  echo Dependencies installed successfully.
)

:: Ask if the user wants to create a desktop shortcut
echo.
echo Would you like to create a desktop shortcut?
echo.
echo 1. Yes, create a desktop shortcut
echo 2. No, skip this step
echo.
set /p shortcut="Enter your choice (1 or 2): "

if "%shortcut%"=="1" (
  echo Creating desktop shortcut...
  
  :: Create a shortcut on the desktop
  powershell -Command "& {$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\Browser Session Manager.lnk'); $Shortcut.TargetPath = '%~dp0BrowserSessionManager.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Browser Session Manager'; $Shortcut.Save()}"
  
  echo Desktop shortcut created.
)

:: Start the application
echo.
echo Starting Browser Session Manager...
echo.

call BrowserSessionManager.bat

exit /b 0