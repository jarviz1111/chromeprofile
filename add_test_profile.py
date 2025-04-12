"""
Add Test Profile

This script adds test profiles to the database for demonstration purposes.
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = 'browser_sessions.db'

# Test profiles to add
test_profiles = [
    {
        'profile_id': 'gmail_test_profile',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'cookies': json.dumps([{'name': 'test_cookie', 'value': 'test_value', 'domain': '.google.com'}]),
        'updated_at': datetime.now().isoformat(),
        'email': 'test@gmail.com',
        'login_domain': 'google.com',
        'login_count': 5,
        'last_login_time': datetime.now().isoformat(),
        'screen_resolution': '1920x1080',
        'platform': 'Win32',
        'language': 'en-US'
    },
    {
        'profile_id': 'yahoo_test_profile',
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'cookies': json.dumps([{'name': 'test_cookie', 'value': 'test_value', 'domain': '.yahoo.com'}]),
        'updated_at': datetime.now().isoformat(),
        'email': 'test@yahoo.com',
        'login_domain': 'yahoo.com',
        'login_count': 3,
        'last_login_time': datetime.now().isoformat(),
        'screen_resolution': '2560x1440',
        'platform': 'MacIntel',
        'language': 'en-US'
    }
]

def add_test_profiles():
    """Add test profiles to the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            for profile in test_profiles:
                # Check if profile already exists
                cursor.execute('SELECT 1 FROM sessions WHERE profile_id = ?', (profile['profile_id'],))
                if cursor.fetchone():
                    print(f"⚠️ Profile '{profile['profile_id']}' already exists - skipping")
                    continue
                    
                # Insert profile
                cursor.execute('''
                    INSERT INTO sessions (
                        profile_id, user_agent, cookies, updated_at, email, 
                        login_domain, login_count, last_login_time,
                        screen_resolution, platform, language
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    profile['profile_id'], profile['user_agent'], profile['cookies'],
                    profile['updated_at'], profile['email'], profile['login_domain'],
                    profile['login_count'], profile['last_login_time'],
                    profile['screen_resolution'], profile['platform'], profile['language']
                ))
                
                print(f"✅ Added test profile: {profile['profile_id']}")
                
            conn.commit()
            print("✅ All test profiles added successfully.")
            return True
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    add_test_profiles()