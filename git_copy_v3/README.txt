Browser Session Manager (Python Edition) v1.0.0
==============================================

INSTALLATION INSTRUCTIONS:

Windows:
1. Make sure Python 3.7 or higher is installed on your system.
   You can download Python from https://www.python.org/downloads/
   Be sure to check "Add Python to PATH" during installation.
   
2. Double-click on "start_browser_manager.bat" to launch the application.
   - This will check for required dependencies and install them if needed.
   - The application will start automatically after dependencies are installed.

macOS/Linux:
1. Make sure Python 3.7 or higher is installed on your system.
   You can install Python using your package manager or from https://www.python.org/downloads/
   
2. Open Terminal and navigate to the application directory:
   $ cd /path/to/browser_session_manager
   
3. Make the launcher script executable:
   $ chmod +x start_browser_manager.sh
   
4. Run the launcher script:
   $ ./start_browser_manager.sh

USAGE:
1. Enter your API credentials (User ID and API Key)
2. Select a CSV file containing profiles (use the Browse button)
3. Optionally, enter a global proxy to use for all profiles
4. Click "Start Processing" to begin automating browser sessions
5. Browser sessions will be saved automatically and can be resumed later

CSV FORMAT:
The application expects a CSV file with the following format:
- First row: header with column names "profile_id,proxy"
- Subsequent rows: profile ID and optional proxy for each profile

Example:
profile_id,proxy
profile1,
profile2,123.456.789.012:8080
profile3,user:pass@123.456.789.012:8080

REQUIREMENTS:
- Python 3.7 or higher
- CustomTkinter
- Undetected-ChromeDriver
- Selenium
- Fake-UserAgent
- Requests
- psutil

The launcher script will automatically install these dependencies if needed.

For more information, please visit: https://inboxinnovations.org