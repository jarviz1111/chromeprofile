#!/bin/bash
# Browser Session Manager Launcher for Linux/macOS

echo "===================================="
echo "Browser Session Manager Launcher"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed or not in PATH!"
    echo ""
    echo "Please install Python from https://www.python.org/downloads/"
    echo "or use your package manager (apt, brew, etc.)"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Make the script executable
chmod +x launch_browser_manager.py

# Run the launcher script
echo "Starting Browser Session Manager..."
python3 launch_browser_manager.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Browser Session Manager exited with an error."
    echo ""
    read -p "Press Enter to exit..."
fi

exit $?