"""
Session Utilities
----------------
Helper functions for session management with enhanced profile data support.
"""

import sqlite3
import json
from datetime import datetime
import os

# Define the database path
DB_PATH = 'browser_sessions.db'

def init_db():
    """Initialize the database with required tables."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            # Check if sessions table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            table_exists = c.fetchone()
            
            if not table_exists:
                # Create new table with correct column name profile_id
                c.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        profile_id TEXT PRIMARY KEY,
                        user_agent TEXT,
                        cookies TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT,
                        email TEXT,
                        password TEXT,
                        login_domain TEXT,
                        login_count INTEGER DEFAULT 0,
                        last_login_time TEXT,
                        hardware_profile TEXT,
                        screen_resolution TEXT,
                        platform TEXT,
                        language TEXT,
                        fingerprint_settings TEXT,
                        login_status TEXT
                    )
                ''')
                print("✅ Created new sessions table with profile_id as primary key")
            else:
                print("✅ Sessions table already exists")
            conn.commit()
        print("✅ Database initialized successfully.")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

def save_enhanced_session(profile, user_agent, cookies, email=None, password=None, login_domain=None, 
                          hardware_profile=None, fingerprint_settings=None, 
                          timezone=None, screen_resolution=None, platform=None,
                          language=None, login_status=None):
    """Save browser session with enhanced data to the database.
    
    Args:
        profile (str): Profile identifier.
        user_agent (str): Browser user agent string.
        cookies (list): Browser cookies.
        email (str, optional): Email address associated with this profile.
        password (str, optional): Password for this profile (stored encrypted).
        login_domain (str, optional): Domain for login (e.g., google.com, yahoo.com).
        hardware_profile (dict, optional): Hardware fingerprint data.
        fingerprint_settings (dict, optional): Browser fingerprint settings.
        timezone (str, optional): Timezone setting.
        screen_resolution (str, optional): Screen resolution string.
        platform (str, optional): Platform identifier.
        language (str, optional): Browser language setting.
        login_status (str, optional): Login status (success, failed, etc).
        
    Returns:
        bool: True if save was successful, False otherwise.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Check if this profile already exists
            c.execute('SELECT login_count FROM sessions WHERE profile_id = ?', (profile,))
            existing_data = c.fetchone()
            
            # Increment login count if this is an existing profile
            login_count = 1
            if existing_data and existing_data[0]:
                login_count = existing_data[0] + 1
            
            # Convert hardware profile and fingerprint settings to JSON
            if hardware_profile and isinstance(hardware_profile, dict):
                hardware_profile = json.dumps(hardware_profile)
            
            if fingerprint_settings and isinstance(fingerprint_settings, dict):
                fingerprint_settings = json.dumps(fingerprint_settings)
            
            # Current timestamp
            current_time = datetime.now().isoformat()
            
            # Convert cookies to string
            cookies_str = json.dumps(cookies) if cookies else None
            
            # Prepare query parameters
            params = (
                profile, user_agent, cookies_str, current_time,
                email, password, login_domain, login_count, current_time,
                hardware_profile, screen_resolution, platform, language,
                fingerprint_settings, login_status
            )
            
            # Execute SQL
            c.execute('''
                INSERT OR REPLACE INTO sessions 
                (profile_id, user_agent, cookies, updated_at, 
                 email, password, login_domain, login_count, last_login_time,
                 hardware_profile, screen_resolution, platform, language,
                 fingerprint_settings, login_status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', params)
            
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Session save error: {e}")
        return False

def load_enhanced_session(profile):
    """Load enhanced browser session data from the database.
    
    Args:
        profile (str): Profile identifier.
        
    Returns:
        dict: Session data including user agent, cookies, and enhanced fields.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT user_agent, cookies, email, password, login_domain,
                       hardware_profile, screen_resolution, platform, language,
                       fingerprint_settings, login_status, login_count, last_login_time
                FROM sessions WHERE profile_id = ?
            ''', (profile,))
            
            session_data = c.fetchone()
            if not session_data:
                return None
                
            # Create a session data dictionary
            result = {
                'user_agent': session_data[0],
                'cookies': json.loads(session_data[1]) if session_data[1] else None,
                'email': session_data[2],
                'password': session_data[3],
                'login_domain': session_data[4],
                'hardware_profile': json.loads(session_data[5]) if session_data[5] else None,
                'screen_resolution': session_data[6],
                'platform': session_data[7],
                'language': session_data[8],
                'fingerprint_settings': json.loads(session_data[9]) if session_data[9] else None,
                'login_status': session_data[10],
                'login_count': session_data[11],
                'last_login_time': session_data[12]
            }
            
            return result
    except Exception as e:
        print(f"❌ Session load error: {e}")
        return None

def get_all_profiles():
    """Get all profiles from the database with enhanced information.
    
    Returns:
        list: List of profile data with enhanced details.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT profile_id, updated_at, email, login_domain, login_count, last_login_time,
                       screen_resolution, platform
                FROM sessions 
                ORDER BY updated_at DESC
            ''')
            return c.fetchall()
    except Exception as e:
        print(f"❌ Profile list error: {e}")
        return []

def delete_profile(profile):
    """Delete a profile from the database.
    
    Args:
        profile (str): Profile identifier.
        
    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM sessions WHERE profile_id = ?', (profile,))
            conn.commit()
            return c.rowcount > 0
    except Exception as e:
        print(f"❌ Profile deletion error: {e}")
        return False

def rename_profile(old_profile_name, new_profile_name):
    """Rename a profile in the database.
    
    Args:
        old_profile_name (str): Current profile name
        new_profile_name (str): New profile name
        
    Returns:
        bool: True if rename was successful, False otherwise
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM sessions WHERE profile_id = ?', (old_profile_name,))
            old_profile_data = c.fetchone()
            
            if not old_profile_data:
                print(f"❌ Profile not found: {old_profile_name}")
                return False
                
            # Check if the new name already exists
            c.execute('SELECT * FROM sessions WHERE profile_id = ?', (new_profile_name,))
            if c.fetchone():
                print(f"❌ Cannot rename: Profile '{new_profile_name}' already exists")
                return False
                
            # Update the profile name
            c.execute('UPDATE sessions SET profile_id = ? WHERE profile_id = ?', 
                     (new_profile_name, old_profile_name))
            conn.commit()
            
            print(f"✅ Profile renamed from '{old_profile_name}' to '{new_profile_name}'")
            return True
            
    except Exception as e:
        print(f"❌ DB Rename Error: {e}")
        return False