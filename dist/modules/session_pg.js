/**
 * Session Management Module
 * Handles browser session storage, loading, and saving using PostgreSQL
 */

const { initDatabase, query } = require('./database');

/**
 * Initialize the database with required tables
 */
async function initDb() {
  await initDatabase();
}

/**
 * Save browser session to the database
 * @param {string} profileId - Profile identifier
 * @param {string} userAgent - Browser user agent string
 * @param {Array} cookies - Browser cookies
 * @returns {boolean} True if save was successful, False otherwise
 */
async function saveSession(profileId, userAgent, cookies) {
  try {
    await query(`
      INSERT INTO sessions (profile_id, user_agent, cookies, last_updated)
      VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
      ON CONFLICT (profile_id) 
      DO UPDATE SET 
        user_agent = $2,
        cookies = $3,
        last_updated = CURRENT_TIMESTAMP
    `, [
      profileId,
      userAgent,
      JSON.stringify(cookies)
    ]);
    
    console.log(`✅ Session saved for profile: ${profileId}`);
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
async function loadSession(profileId) {
  try {
    const result = await query(
      'SELECT user_agent, cookies FROM sessions WHERE profile_id = $1',
      [profileId]
    );
    
    if (result.rows && result.rows.length > 0) {
      const row = result.rows[0];
      try {
        const cookies = row.cookies ? JSON.parse(row.cookies) : null;
        return { userAgent: row.user_agent, cookies };
      } catch (error) {
        console.error(`❌ Error parsing cookies: ${error.message}`);
        return { userAgent: row.user_agent, cookies: null };
      }
    }
    
    return { userAgent: null, cookies: null };
  } catch (error) {
    console.error(`❌ Error loading session: ${error.message}`);
    return { userAgent: null, cookies: null };
  }
}

/**
 * Get all profiles from the database
 * @returns {Array} List of profile names with their last update time
 */
async function getAllProfiles() {
  try {
    const result = await query(
      'SELECT profile_id, last_updated FROM sessions ORDER BY last_updated DESC',
      []
    );
    
    if (result.rows && result.rows.length > 0) {
      return result.rows;
    }
    
    return [];
  } catch (error) {
    console.error(`❌ Error getting profiles: ${error.message}`);
    return [];
  }
}

/**
 * Delete a profile from the database
 * @param {string} profileId - Profile identifier
 * @returns {boolean} True if deletion was successful, False otherwise
 */
async function deleteProfile(profileId) {
  try {
    const result = await query(
      'DELETE FROM sessions WHERE profile_id = $1',
      [profileId]
    );
    
    // Check if any rows were affected
    return result.rowCount > 0;
  } catch (error) {
    console.error(`❌ Error deleting profile: ${error.message}`);
    return false;
  }
}

module.exports = {
  initDb,
  saveSession,
  loadSession,
  getAllProfiles,
  deleteProfile
};