# Browser Session Manager

A comprehensive application for managing browser sessions, profiles, and automating browser interactions with advanced fingerprinting and anti-detection capabilities.

## Key Features

- **Profile Management**: Create and manage multiple browser profiles with independent cookies, settings, and session data
- **Anti-Detection Technology**: Advanced browser fingerprinting protection and anti-bot detection measures
- **Email Provider Optimization**: Specialized handling for Gmail, Yahoo, and other email providers
- **Browser Fingerprinting**: Customizable browser fingerprints with consistent hardware profiles
- **Proxy Support**: Full proxy integration for managing different IP addresses per profile
- **Chrome Extension**: Built-in extension to display and verify browser fingerprinting data
- **Multi-Platform Support**: Works on Windows, Linux, and macOS
- **Command-Line Interface**: Supports both GUI and command-line operation
- **Enhanced Database**: Store and manage detailed profile information including email accounts and login history

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome/Chromium browser
- Required Python packages:
  - undetected-chromedriver
  - selenium
  - fake-useragent
  - customtkinter (for GUI)
  - requests
  - psutil

### Install Dependencies

```bash
pip install undetected-chromedriver selenium fake-useragent customtkinter requests psutil
```

### Running the Application

#### GUI Mode

```bash
python main_standalone.py
```

#### Command-Line Mode

For easier use, we provide run scripts for both Windows and Unix systems:

##### Windows:
```
run_cli.bat list
run_cli.bat launch --profile your_profile_name
run_cli.bat launch --profile your_profile_name --proxy ip:port
run_cli.bat delete --profile your_profile_name
run_cli.bat rename --profile old_name --new-name new_name
```

##### Linux/macOS:
```bash
./run_cli.sh list
./run_cli.sh launch --profile your_profile_name
./run_cli.sh launch --profile your_profile_name --proxy ip:port
./run_cli.sh delete --profile your_profile_name
./run_cli.sh rename --profile old_name --new-name new_name
```

##### Direct Python Execution:
```bash
# List all saved profiles
python test_enhanced_browser.py list

# Launch a browser with a specific profile
python test_enhanced_browser.py launch --profile your_profile_name

# Launch with a proxy
python test_enhanced_browser.py launch --profile your_profile_name --proxy ip:port

# Delete a profile
python test_enhanced_browser.py delete --profile your_profile_name

# Rename a profile
python test_enhanced_browser.py rename --profile old_name --new-name new_name
```

## Profile Configuration

Profiles can be bulk loaded from a CSV file with the following format:

```
profile_id,proxy,email,password
gmail_account1,123.45.67.89:8080,example1@gmail.com,password123
yahoo_account1,,yahoo_user@yahoo.com,securepass456
outlook_account1,user:pass@11.22.33.44:8080,business@outlook.com,office789
```

You can use the sample CSV file provided (`sample_profiles.csv`) as a template.

## Chrome Extension

The Browser Session Manager includes a custom Chrome extension that helps verify your browser's fingerprinting by displaying:

- Current user agent
- IP address
- Screen resolution
- Language settings
- WebGL renderer information

This extension is automatically loaded when launching browsers through the Session Manager and provides a floating display that can be minimized when not needed.

## Enhanced Anti-Detection Features

- WebGL fingerprint randomization
- Canvas fingerprinting protection
- Audio fingerprinting noise
- Navigator property spoofing
- Hardware fingerprint consistency per profile
- ClientRects fingerprinting protection
- User-Agent consistency

## API Verification

The application includes API verification through inboxinnovations.org. You'll need to provide your API credentials in the application to access all features.

## Database Schema

The application uses an SQLite database to store profile information including:

- Browser cookies and user agent
- Email account details (with privacy measures)
- Login domain tracking
- Hardware profile fingerprints
- Screen resolution, platform, and language settings
- Login history and session counts

## Security Notes

- Passwords are stored in plain text in the local database by default. For production use, consider implementing encryption.
- The database is stored locally and isn't shared with any external services.
- API credentials are only used for verification and aren't stored permanently.

## License

This software is provided for educational purposes only. Use responsibly and in accordance with the terms of service of websites you interact with.

## Developers

For developers looking to extend this application, see the modular code structure:

- `main_standalone.py`: The main GUI application
- `utils/session_utils.py`: Enhanced session management utilities
- `utils/update_db_schema.py`: Database schema update tool
- `extensions/info_display/`: Chrome extension for fingerprinting verification
- `test_enhanced_browser.py`: Command-line interface for browser control