/**
 * Database Connection Module
 * Handles PostgreSQL database connections and initialization
 */

const { Pool } = require('pg');

// Create a connection pool using the DATABASE_URL environment variable
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false // Necessary for some PostgreSQL hosting providers
  }
});

/**
 * Initialize the database with required tables
 * @returns {Promise<void>}
 */
async function initDatabase() {
  const client = await pool.connect();
  try {
    console.log('📊 Initializing PostgreSQL database...');
    
    // Create sessions table if it doesn't exist
    await client.query(`
      CREATE TABLE IF NOT EXISTS sessions (
        profile_id TEXT PRIMARY KEY,
        user_agent TEXT,
        cookies TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // Check if the table is empty, and if so, create a sample entry
    const countResult = await client.query("SELECT count(*) as count FROM sessions");
    
    if (countResult.rows && countResult.rows[0].count == 0) {
      console.log("📊 Creating sample profile entry for testing...");
      // Create a sample entry for testing
      await client.query(`
        INSERT INTO sessions (profile_id, user_agent, cookies, last_updated)
        VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
      `, [
        "sample_profile", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        JSON.stringify([{"name": "sample_cookie", "value": "test_value", "domain": ".example.com"}])
      ]);
    }
    
    console.log('✅ PostgreSQL database initialized successfully');
  } catch (error) {
    console.error('❌ Database initialization error:', error.message);
    throw error;
  } finally {
    client.release();
  }
}

/**
 * Execute a database query
 * @param {string} text - SQL query text
 * @param {Array} params - Query parameters
 * @returns {Promise<QueryResult>} - Query result
 */
async function query(text, params) {
  try {
    const result = await pool.query(text, params);
    return result;
  } catch (error) {
    console.error('❌ Database query error:', error.message);
    throw error;
  }
}

module.exports = {
  initDatabase,
  query,
  pool
};