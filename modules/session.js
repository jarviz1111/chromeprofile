/**
 * Session Management Module
 * Handles browser session storage, loading, and saving
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Database setup
const DB_PATH = path.join(__dirname, '..', 'browser_sessions.db');
let db = null;

/**
 * Initialize the database with required tables
 */
function initDb() {
  if (db) return;
  
  // Create DB directory if it doesn't exist
  const dbDir = path.dirname(DB_PATH);
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
  }
  
  db = new sqlite3.Database(DB_PATH);
  
  db.serialize(() => {
    db.run(`
      CREATE TABLE IF NOT EXISTS sessions (
        profile_id TEXT PRIMARY KEY,
        user_agent TEXT,
        cookies TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
  });
  
  console.log(`✅ Database initialized at ${DB_PATH}`);
}

/**
 * Save browser session to the database
 * @param {string} profileId - Profile identifier
 * @param {string} userAgent - Browser user agent string
 * @param {Array} cookies - Browser cookies
 * @returns {boolean} True if save was successful, False otherwise
 */
function saveSession(profileId, userAgent, cookies) {
  if (!db) initDb();
  
  try {
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO sessions (profile_id, user_agent, cookies, last_updated)
      VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    `);
    
    stmt.run(
      profileId,
      userAgent,
      JSON.stringify(cookies)
    );
    
    stmt.finalize();
    return true;
  } catch (error) {
    console.error(`❌ Failed to save session: ${error.message}`);
    return false;
  }
}

/**
 * Load browser session from the database
 * @param {string} profileId - Profile identifier
 * @returns {Object} Object containing user_agent and cookies, or null values if not found
 */
function loadSession(profileId) {
  if (!db) initDb();
  
  return new Promise((resolve, reject) => {
    db.get(
      'SELECT user_agent, cookies FROM sessions WHERE profile_id = ?',
      [profileId],
      (err, row) => {
        if (err) {
          console.error(`❌ Error loading session: ${err.message}`);
          return resolve({ userAgent: null, cookies: null });
        }
        
        if (!row) {
          return resolve({ userAgent: null, cookies: null });
        }
        
        try {
          const cookies = row.cookies ? JSON.parse(row.cookies) : null;
          resolve({ userAgent: row.user_agent, cookies });
        } catch (error) {
          console.error(`❌ Error parsing cookies: ${error.message}`);
          resolve({ userAgent: row.user_agent, cookies: null });
        }
      }
    );
  });
}

/**
 * Get all profiles from the database
 * @returns {Array} List of profile names with their last update time
 */
function getAllProfiles() {
  if (!db) initDb();
  
  return new Promise((resolve, reject) => {
    db.all(
      'SELECT profile_id, last_updated FROM sessions ORDER BY last_updated DESC',
      function(err, rows) {
        if (err) {
          console.error(`❌ Error getting profiles: ${err.message}`);
          return resolve([]);
        }
        
        // Check if the database has been created but doesn't have any sessions yet
        if (!rows || !rows.length) {
          return resolve([]);
        }
        
        resolve(rows);
      }
    );
  });
}

/**
 * Delete a profile from the database
 * @param {string} profileId - Profile identifier
 * @returns {boolean} True if deletion was successful, False otherwise
 */
function deleteProfile(profileId) {
  if (!db) initDb();
  
  return new Promise((resolve, reject) => {
    db.run(
      'DELETE FROM sessions WHERE profile_id = ?',
      [profileId],
      function(err) {
        if (err) {
          console.error(`❌ Error deleting profile: ${err.message}`);
          return resolve(false);
        }
        
        // Check if any rows were affected
        resolve(this.changes > 0);
      }
    );
  });
}

module.exports = {
  initDb,
  saveSession,
  loadSession,
  getAllProfiles,
  deleteProfile
};