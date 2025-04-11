/**
 * Browser Driver Module
 * Handles browser initialization, configuration, and automation
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const { loadSession, saveSession } = require('./session');

// Apply stealth plugin to make automation less detectable
puppeteer.use(StealthPlugin());

// Constants
const LOGIN_URL = 'https://accounts.google.com/signup';
const USER_DATA_DIR = path.join(__dirname, '..', 'browser_profiles');

// Create browser profiles directory if it doesn't exist
if (!fs.existsSync(USER_DATA_DIR)) {
  fs.mkdirSync(USER_DATA_DIR, { recursive: true });
}

/**
 * Generate a random desktop user agent string
 * @returns {string} A user agent string for desktop browsers
 */
function generateUserAgent() {
  const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
  ];
  
  return userAgents[Math.floor(Math.random() * userAgents.length)];
}

/**
 * Kill all Chrome processes
 * @returns {Promise<void>}
 */
async function killChrome() {
  return new Promise((resolve) => {
    if (process.platform === 'win32') {
      exec('taskkill /F /IM chrome.exe /T', () => resolve());
    } else {
      exec('pkill -f chrome', () => resolve());
    }
  });
}

/**
 * Launch a browser session with the specified profile
 * 
 * @param {string} profileId - Profile identifier
 * @param {string} proxy - Proxy to use in format "ip:port" or "user:pass@ip:port"
 * @returns {Promise<Browser>} Puppeteer browser instance
 */
async function launchBrowser(profileId, proxy = null) {
  console.log(`🟢 Launching browser for profile: ${profileId}`);
  
  const userDataDir = path.join(USER_DATA_DIR, profileId);
  
  // Create profile directory if it doesn't exist
  if (!fs.existsSync(userDataDir)) {
    fs.mkdirSync(userDataDir, { recursive: true });
  }
  
  // Load existing session
  const { userAgent: storedUserAgent, cookies: storedCookies } = await loadSession(profileId);
  
  // Use stored user agent or generate a new one
  const userAgent = storedUserAgent || generateUserAgent();
  
  // Setup browser launch options
  const launchOptions = {
    headless: false,
    userDataDir,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-infobars',
      '--window-size=1920,1080',
      `--user-agent=${userAgent}`
    ],
    ignoreDefaultArgs: ['--enable-automation'],
    defaultViewport: {
      width: 1920,
      height: 1080
    }
  };
  
  // Add proxy if specified
  if (proxy) {
    launchOptions.args.push(`--proxy-server=http://${proxy}`);
    console.log(`🌐 Using Proxy: ${proxy}`);
  } else {
    console.log('🚫 No proxy set.');
  }
  
  // Launch browser
  const browser = await puppeteer.launch(launchOptions);
  
  // Get the default page
  const page = (await browser.pages())[0];
  
  // Set user agent
  await page.setUserAgent(userAgent);
  
  // Apply anti-fingerprinting measures
  await page.evaluateOnNewDocument(() => {
    // Override navigator properties
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    
    // Override WebGL fingerprinting
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
      if (parameter === 37445) {
        return 'Intel Inc.';
      }
      if (parameter === 37446) {
        return 'Intel Iris Pro Graphics 580';
      }
      return getParameter.call(this, parameter);
    };
  });
  
  // Load cookies if available
  if (storedCookies && storedCookies.length > 0) {
    console.log('🟡 Loading cookies...');
    await page.goto('https://accounts.google.com/');
    
    for (const cookie of storedCookies) {
      try {
        // Clean up cookie for puppeteer format
        if (cookie.sameSite) {
          delete cookie.sameSite;
        }
        
        await page.setCookie(cookie);
      } catch (error) {
        console.error(`❌ Error setting cookie: ${error.message}`);
      }
    }
    
    await page.goto('https://mail.google.com/');
  } else {
    console.log('🟢 No cookies found. Creating new session...');
    await page.goto(LOGIN_URL);
    console.log('⚠️ Please login manually...');
    
    // Allow some time for manual login
    await new Promise(resolve => setTimeout(resolve, 30000));
    
    // Save new session
    const cookies = await page.cookies();
    await saveSession(profileId, userAgent, cookies);
  }
  
  // Return the browser instance
  return browser;
}

module.exports = {
  launchBrowser,
  killChrome
};