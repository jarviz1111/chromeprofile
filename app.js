/**
 * Browser Session Manager - Node.js Version
 * 
 * This application provides a web interface for managing browser sessions,
 * handling profiles, and automating browser interactions.
 */

const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const csvParser = require('csv-parser');
// Use PostgreSQL version of the session module
const { initDb, saveSession, loadSession, getAllProfiles, deleteProfile } = require('./modules/session_pg');
const { verifyApi } = require('./modules/api');
const { launchBrowser, killChrome } = require('./modules/driver');

// App Setup
const app = express();
const port = process.env.PORT || 5000;

// View engine setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Configure file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  }
});
const upload = multer({ storage });
fs.mkdirSync('uploads', { recursive: true });
fs.mkdirSync('browser_profiles', { recursive: true });

// Global variables
let currentDriver = null;
let currentIndex = -1;
let profilesList = [];

// Initialize DB
initDb();

// Routes
app.get('/', async (req, res) => {
  try {
    const profiles = await getAllProfiles();
    res.render('index', { 
      title: 'Browser Session Manager',
      profiles: profiles
    });
  } catch (error) {
    console.error('Error getting profiles:', error);
    res.render('index', { 
      title: 'Browser Session Manager',
      profiles: []
    });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'ok', 
    message: 'Browser Session Manager is running',
    nodejs: true,
    time: new Date().toISOString()
  });
});

// Database status endpoint
app.get('/db-status', async (req, res) => {
  try {
    const { query, pool } = require('./modules/database');
    const result = await query('SELECT NOW() as server_time');
    const dbInfo = {
      server_time: result.rows[0].server_time,
      connection_pool: {
        total: pool.totalCount,
        idle: pool.idleCount,
        waiting: pool.waitingCount
      },
      database_url: process.env.DATABASE_URL ? 'Connected (URL exists)' : 'Missing',
      database_type: 'PostgreSQL'
    };
    
    res.status(200).json({
      status: 'ok',
      message: 'Database connection successful',
      db_info: dbInfo
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: 'Database connection failed',
      error: error.message
    });
  }
});

// API verification
app.post('/verify-api', async (req, res) => {
  const { apiUserId, apiKeyId } = req.body;
  
  try {
    const result = await verifyApi(apiUserId, apiKeyId);
    if (result) {
      res.json({ success: true });
    } else {
      res.json({ success: false, message: 'Invalid API credentials' });
    }
  } catch (error) {
    res.json({ success: false, message: error.message });
  }
});

// Upload and process CSV
app.post('/upload-csv', upload.single('csvFile'), (req, res) => {
  const { globalProxy } = req.body;
  
  if (!req.file) {
    return res.json({ success: false, message: 'No file uploaded' });
  }
  
  const results = [];
  fs.createReadStream(req.file.path)
    .pipe(csvParser())
    .on('data', (data) => results.push(data))
    .on('end', () => {
      profilesList = results.map(row => {
        const profileId = row.profile_id ? row.profile_id.trim() : '';
        if (!profileId) return null;
        
        const proxy = globalProxy && globalProxy.trim() 
          ? globalProxy.trim() 
          : (row.proxy ? row.proxy.trim() : null);
          
        return { profileId, proxy };
      }).filter(Boolean);
      
      res.json({ 
        success: true, 
        message: `Loaded ${profilesList.length} profiles from CSV`,
        profiles: profilesList
      });
    });
});

// Launch browser for next profile
app.post('/process-next', async (req, res) => {
  // First, save and close current session if exists
  if (currentDriver) {
    try {
      console.log('Saving current session...');
      const cookies = await currentDriver.cookies();
      const userAgent = await currentDriver.evaluate(() => navigator.userAgent);
      const profileId = profilesList[currentIndex].profileId;
      
      const saveResult = await saveSession(profileId, userAgent, cookies);
      if (saveResult) {
        console.log(`Session saved for profile: ${profileId}`);
      } else {
        console.log(`Warning: Could not save session for ${profileId}`);
      }
      
      // Close browser
      console.log('Closing browser...');
      await currentDriver.close();
      currentDriver = null;
      
      // Ensure Chrome processes are killed
      await killChrome();
    } catch (error) {
      console.error(`Warning: ${error}`);
      currentDriver = null;
      await killChrome();
    }
  }
  
  // Move to next profile
  currentIndex++;
  
  // Check if there are more profiles to process
  if (currentIndex < profilesList.length) {
    const profile = profilesList[currentIndex];
    const { profileId, proxy } = profile;
    console.log(`Starting profile ${currentIndex + 1}/${profilesList.length}: ${profileId}`);
    console.log(`Proxy: ${proxy || 'None'}`);
    
    // Launch browser with retries
    const maxRetries = 2;
    let success = false;
    let error = null;
    
    for (let retry = 0; retry <= maxRetries; retry++) {
      try {
        console.log(`Launching browser (attempt ${retry + 1}/${maxRetries + 1})...`);
        currentDriver = await launchBrowser(profileId, proxy);
        success = true;
        break;
      } catch (err) {
        console.error(`Error launching browser for ${profileId}: ${err}`);
        error = err;
        if (retry < maxRetries) {
          console.log(`Retrying in 3 seconds...`);
          await new Promise(resolve => setTimeout(resolve, 3000));
        }
      }
    }
    
    if (success) {
      res.json({ 
        success: true, 
        message: `Started profile ${profileId}`,
        currentProfile: profile,
        progress: {
          current: currentIndex + 1,
          total: profilesList.length
        }
      });
    } else {
      // Failed after all retries, skip to next profile
      res.json({ 
        success: false, 
        message: `Failed to launch browser for ${profileId} after ${maxRetries + 1} attempts`,
        error: error.message,
        nextAvailable: currentIndex < profilesList.length - 1
      });
    }
  } else {
    res.json({ 
      success: true, 
      message: 'All profiles processed',
      complete: true
    });
  }
});

// Delete a profile
app.post('/delete-profile', async (req, res) => {
  const { profileId } = req.body;
  
  try {
    const result = await deleteProfile(profileId);
    if (result) {
      res.json({ success: true, message: `Profile ${profileId} deleted` });
    } else {
      res.json({ success: false, message: `Failed to delete profile ${profileId}` });
    }
  } catch (error) {
    console.error(`Error deleting profile: ${error.message}`);
    res.json({ success: false, message: `Error: ${error.message}` });
  }
});

// Start processing
app.post('/start-processing', (req, res) => {
  // Reset current index
  currentIndex = -1;
  
  res.json({ 
    success: true, 
    message: 'Processing started',
    totalProfiles: profilesList.length
  });
});

// Start the server
app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 Browser Session Manager server running on port ${port}`);
  console.log(`Access the web interface using the "Show" button in Replit or via the webview tab`);
  console.log('Please upload a CSV file with profiles and enter your API credentials in the web interface.');
});

// Handle shutdown
process.on('SIGINT', async () => {
  console.log('Shutting down...');
  if (currentDriver) {
    try {
      await currentDriver.close();
    } catch (e) {
      console.error(e);
    }
  }
  await killChrome();
  process.exit(0);
});