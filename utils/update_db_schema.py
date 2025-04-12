"""
Database Schema Update Utility

This script updates the existing SQLite database schema to add new fields for:
- Email account details
- Login domain tracking
- Browser fingerprint data
- Hardware profiles
- Login status and counts

Usage:
python utils/update_db_schema.py
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# Get the database path
DB_PATH = 'browser_sessions.db'

def check_db_exists():
    """Check if the database file exists."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    return True

def backup_database():
    """Create a backup of the database before modifications."""
    import shutil
    backup_path = f"{DB_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Database backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create database backup: {e}")
        return False

def update_schema():
    """Update the database schema to add new fields."""
    if not check_db_exists():
        return False
    
    # Create backup first
    if not backup_database():
        user_input = input("Failed to create backup. Continue anyway? (y/n): ")
        if user_input.lower() != 'y':
            return False
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # First check if the sessions table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            if not c.fetchone():
                print("❌ Sessions table not found in database.")
                return False
            
            # Get the list of existing columns
            c.execute('PRAGMA table_info(sessions)')
            columns = [column[1] for column in c.fetchall()]
            
            # Add columns if they don't exist
            new_columns = {
                'email': 'TEXT',
                'password': 'TEXT',
                'login_domain': 'TEXT',
                'login_count': 'INTEGER DEFAULT 0',
                'last_login_time': 'TEXT',
                'hardware_profile': 'TEXT',  # JSON string
                'screen_resolution': 'TEXT',
                'platform': 'TEXT',
                'language': 'TEXT',
                'fingerprint_settings': 'TEXT',  # JSON string
                'login_status': 'TEXT',  # success, failed, etc.
            }
            
            for column_name, column_type in new_columns.items():
                if column_name not in columns:
                    # SQLite doesn't support ADD COLUMN with DEFAULT or NOT NULL constraints 
                    # in ALTER TABLE statements if the table already has data
                    try:
                        c.execute(f'ALTER TABLE sessions ADD COLUMN {column_name} {column_type}')
                        print(f"✅ Added column: {column_name} ({column_type})")
                    except sqlite3.OperationalError as e:
                        print(f"❌ Could not add column {column_name}: {e}")
            
            # Commit all changes
            conn.commit()
            print("✅ Database schema updated successfully.")
            return True
            
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function to update the database schema."""
    print("🔄 Starting database schema update...")
    if update_schema():
        print("✅ Database schema update completed successfully.")
    else:
        print("❌ Database schema update failed.")

if __name__ == "__main__":
    main()