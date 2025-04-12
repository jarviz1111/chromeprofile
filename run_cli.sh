#!/bin/bash
# Browser Session Manager CLI Launcher
# This script makes it easier to run command-line operations

# Set executable permission for this script if not already set
if [ ! -x "$0" ]; then
    chmod +x "$0"
    echo "✅ Made script executable"
fi

# Check if python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check for required packages
echo "🔍 Checking dependencies..."
python -c "import undetected_chromedriver, selenium, fake_useragent" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ Required packages not found. Would you like to install them? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
        echo "📦 Installing required packages..."
        pip install undetected-chromedriver selenium fake-useragent requests psutil
    else
        echo "❌ Cannot continue without required packages."
        exit 1
    fi
fi

# Check for ChromeDriver
echo "🔍 Checking for Chrome/Chromium browser..."
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️ Chrome or Chromium browser not detected. The application may not work properly."
    echo "Please install Chrome or Chromium browser before continuing."
    echo "Press Enter to continue anyway or Ctrl+C to abort..."
    read
fi

# Show available commands
if [ $# -eq 0 ]; then
    echo "
🌟 Browser Session Manager CLI 🌟
--------------------------------
Available commands:

1. List all saved profiles:
   ./run_cli.sh list

2. Launch a browser with a profile:
   ./run_cli.sh launch --profile PROFILE_NAME [--proxy IP:PORT] [--headless]

3. Delete a profile:
   ./run_cli.sh delete --profile PROFILE_NAME

4. Rename a profile:
   ./run_cli.sh rename --profile OLD_NAME --new-name NEW_NAME

Examples:
   ./run_cli.sh list
   ./run_cli.sh launch --profile gmail_account1 --proxy 123.45.67.89:8080
   ./run_cli.sh delete --profile unwanted_profile
   ./run_cli.sh rename --profile old_name --new-name better_name
--------------------------------
"
    exit 0
fi

# Run the requested command
echo "🚀 Executing command: $*"
python test_enhanced_browser.py "$@"