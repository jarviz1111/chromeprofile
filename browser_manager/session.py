"""
Session Management Module
------------------------
Handles browser session storage, loading, and saving.
"""
import json
import sqlite3
from datetime import datetime

class SessionManager:
    """Manages browser sessions storage and retrieval."""
    
    def __init__(self, db_path='browser_sessions.db'):
        """Initialize the session manager with the database path.
        
        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                profile TEXT PRIMARY KEY,
                user_agent TEXT,
                cookies TEXT
            )''')
            c.execute("PRAGMA table_info(sessions)")
            columns = [col[1] for col in c.fetchall()]
            if 'updated_at' not in columns:
                c.execute("ALTER TABLE sessions ADD COLUMN updated_at TEXT")
            conn.commit()
    
    def save_session(self, profile, user_agent, cookies):
        """Save browser session to the database.
        
        Args:
            profile (str): Profile identifier.
            user_agent (str): Browser user agent string.
            cookies (list): Browser cookies.
            
        Returns:
            bool: True if save was successful, False otherwise.
        """
        try:
            with sqlite3.connect(self.db_path, timeout=10) as conn:
                c = conn.cursor()
                now = datetime.utcnow().isoformat()
                c.execute('''INSERT OR REPLACE INTO sessions 
                            (profile, user_agent, cookies, updated_at)
                            VALUES (?, ?, ?, ?)''',
                        (profile, user_agent, json.dumps(cookies), now))
                conn.commit()
            return True
        except Exception as e:
            print(f"❌ DB Save Error: {e}")
            return False
    
    def load_session(self, profile):
        """Load browser session from the database.
        
        Args:
            profile (str): Profile identifier.
            
        Returns:
            tuple: (user_agent, cookies) if found, (None, None) otherwise.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('SELECT user_agent, cookies FROM sessions WHERE profile = ?', (profile,))
                result = c.fetchone()
                if result:
                    return result[0], json.loads(result[1]) if result[1] else None
                return None, None
        except Exception as e:
            print(f"❌ DB Load Error: {e}")
            return None, None
    
    def get_all_profiles(self):
        """Get all profiles from the database.
        
        Returns:
            list: List of profile names with their last update time.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('SELECT profile, updated_at FROM sessions ORDER BY updated_at DESC')
                return c.fetchall()
        except Exception as e:
            print(f"❌ DB Query Error: {e}")
            return []
    
    def delete_profile(self, profile):
        """Delete a profile from the database.
        
        Args:
            profile (str): Profile identifier.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('DELETE FROM sessions WHERE profile = ?', (profile,))
                conn.commit()
            return True
        except Exception as e:
            print(f"❌ DB Delete Error: {e}")
            return False
