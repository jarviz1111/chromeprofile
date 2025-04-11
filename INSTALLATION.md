# Browser Session Manager Desktop Application

## Installation Instructions

### Prerequisites
- Node.js 16 or above
- NPM 7 or above

### Installation Methods

#### 1. Download the Pre-built Installer (Recommended)

1. Download the appropriate installer for your operating system:
   - Windows: `BrowserSessionManager-Setup-1.0.0.exe`
   - macOS: `BrowserSessionManager-1.0.0.dmg`
   - Linux: `browser-session-manager_1.0.0_amd64.deb` or `browser-session-manager-1.0.0.AppImage`

2. Run the installer and follow the on-screen instructions.

3. Launch the application from your Start Menu/Applications folder.

#### 2. Manual Installation from Source

1. Extract the source files from the distribution package.

2. Install the dependencies:
   ```bash
   npm install
   ```

3. Start the application:
   ```bash
   npm start
   ```

   Or for desktop mode:
   ```bash
   npm run start-desktop
   ```

### Linux-specific Notes

For Linux systems, you may need to install additional dependencies for Chromium:

```bash
sudo apt-get update
sudo apt-get install -y libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

### macOS-specific Notes

On macOS, you might need to allow the app in System Preferences > Security & Privacy if you get a security warning when trying to open the app for the first time.

### Windows-specific Notes

On Windows, the installer will prompt you to create a desktop shortcut during installation.

## Usage Notes

- The application requires an internet connection for API verification.
- Browser automation features work best with a stable internet connection.
- For best results, use with proxy services that support HTTP proxies.

## Support

For support inquiries, please contact support@inboxinnovations.org

## License

This software is proprietary. See the included license file for details.