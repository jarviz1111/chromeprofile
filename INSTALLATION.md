# Browser Session Manager Installation Guide

This guide will help you install and get started with the Browser Session Manager, a tool for managing browser sessions, profiles, and automating browser interactions.

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher
- **Chrome/Chromium**: Latest version recommended
- **Disk Space**: At least 100 MB for the application and additional space for browser profiles

## Installation Steps

### 1. Install Python

If you don't have Python 3.8+ installed:

- **Windows**: Download and run the installer from [python.org](https://www.python.org/downloads/)
- **macOS**: Use Homebrew (`brew install python3`) or download from [python.org](https://www.python.org/downloads/)
- **Linux**: Use your package manager (`apt install python3 python3-pip` for Ubuntu/Debian)

### 2. Clone or Download the Repository

Download the latest version:

```bash
git clone https://github.com/yourusername/browser-session-manager.git
cd browser-session-manager
```

Alternatively, download the ZIP file and extract it.

### 3. Install Dependencies

```bash
pip install -r dependencies.txt
```

Or install the dependencies individually:

```bash
pip install undetected-chromedriver selenium fake-useragent customtkinter requests psutil ttkthemes
```

Or use the included convenience script:

```bash
# On Windows
run_cli.bat

# On macOS/Linux
chmod +x run_cli.sh
./run_cli.sh
```

These scripts will check for and install any missing dependencies.

### 4. Run the Application

#### GUI Mode:

```bash
python main_standalone.py
```

#### Command-Line Mode:

```bash
# List all saved profiles
./run_cli.sh list

# Launch a browser with a profile
./run_cli.sh launch --profile your_profile_name
```

On Windows, use `run_cli.bat` instead of `./run_cli.sh`.

## Configuration

### Setting Up Profiles

1. **CSV Import**: Create a CSV file with the following columns:
   ```
   profile_id,proxy,email,password
   ```
   Example: `sample_profiles.csv` is included as a template.

2. **Manual Setup**: Use the GUI to create and manage profiles.

3. **CLI Setup**: Launch a browser and log in manually, then the session will be saved.

### Chrome Extension

The included Chrome extension will be automatically loaded when launching browsers through the Session Manager. It displays browser fingerprinting information in a floating panel.

## Troubleshooting

### Common Issues

1. **ChromeDriver Issues**:
   - Make sure you have Chrome/Chromium installed
   - Try launching with the `--headless` flag for servers without a display
   - The application will attempt to download the appropriate ChromeDriver version

2. **Dependencies Installation**:
   - If you encounter errors related to missing modules, run:
     ```bash
     pip install -r dependencies.txt
     ```

3. **Profile Database**:
   - If encountering database errors, try:
     ```bash
     python utils/update_db_schema.py
     ```

## Getting Support

If you encounter issues or need help:

- Check the README.md file for detailed usage instructions
- Run `./run_cli.sh` (or `run_cli.bat` on Windows) without arguments for a list of commands
- File an issue on the project's GitHub repository

## Security Notes

- Passwords for profiles are stored in plain text in the local database by default
- Consider running in a secure environment if storing sensitive credentials
- API credentials are only used for verification and aren't stored permanently