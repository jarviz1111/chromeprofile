/**
 * Browser Session Manager Desktop Application
 * Electron main process
 */

const { app, BrowserWindow, Menu, dialog, shell } = require('electron');
const path = require('path');
const url = require('url');
const fs = require('fs');
const express = require('express');
const server = require('./app');
const port = 5000;

// Keep a global reference of the window object to avoid garbage collection
let mainWindow;

// Create the browser window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: path.join(__dirname, 'generated-icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    }
  });

  // Load the app from the Express server
  mainWindow.loadURL(`http://localhost:${port}`);

  // Open DevTools in development mode
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  // Emitted when the window is closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create menu
  const menuTemplate = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Export Sessions',
          click: async () => {
            const { filePath } = await dialog.showSaveDialog({
              title: 'Export Sessions',
              defaultPath: 'browser_sessions.json',
              filters: [
                { name: 'JSON Files', extensions: ['json'] }
              ]
            });
            
            if (filePath) {
              try {
                // Load sessions from the server
                const response = await fetch(`http://localhost:${port}/api/sessions`);
                const sessions = await response.json();
                fs.writeFileSync(filePath, JSON.stringify(sessions, null, 2));
                dialog.showMessageBox({
                  type: 'info',
                  message: 'Sessions exported successfully'
                });
              } catch (error) {
                dialog.showErrorBox('Export Error', error.message);
              }
            }
          }
        },
        {
          label: 'Import Sessions',
          click: async () => {
            const { filePaths } = await dialog.showOpenDialog({
              title: 'Import Sessions',
              filters: [
                { name: 'JSON Files', extensions: ['json'] }
              ],
              properties: ['openFile']
            });
            
            if (filePaths && filePaths.length > 0) {
              try {
                const data = fs.readFileSync(filePaths[0], 'utf8');
                const sessions = JSON.parse(data);
                
                // Import sessions to the server
                await fetch(`http://localhost:${port}/api/sessions/import`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ sessions })
                });
                
                dialog.showMessageBox({
                  type: 'info',
                  message: 'Sessions imported successfully'
                });
                
                // Refresh the page
                mainWindow.reload();
              } catch (error) {
                dialog.showErrorBox('Import Error', error.message);
              }
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Command+Q' : 'Ctrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => {
            shell.openExternal('https://inboxinnovations.org/docs');
          }
        },
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox({
              type: 'info',
              title: 'About Browser Session Manager',
              message: 'Browser Session Manager v1.0.0\nCopyright © 2025 Inbox Innovations',
              detail: 'A powerful tool for managing browser sessions and automating web interactions.'
            });
          }
        }
      ]
    }
  ];
  
  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);
}

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  console.log('Starting Browser Session Manager Desktop Application...');
  
  // Start the Express server
  server.listen(port, '127.0.0.1', () => {
    console.log(`Server running on port ${port} (localhost only)`);
    createWindow();
  });
  
  app.on('activate', () => {
    // On macOS it's common to re-create a window in the app when the dock icon is clicked
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle app quit
app.on('quit', () => {
  // Perform any cleanup tasks here
  console.log('Application shutting down...');
  process.exit(0);
});