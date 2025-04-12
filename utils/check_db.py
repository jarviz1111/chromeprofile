"""
Database Schema Checker
----------------------
Utility to check the current database schema and table structure.
"""

import sqlite3
import os
import sys
import json

# Define the database path
DB_PATH = 'browser_sessions.db'

def check_db_schema():
    """Check and print the database schema."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found: {DB_PATH}")
        return False
        
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print("No tables found in the database.")
                return False
                
            print(f"📊 Database contains {len(tables)} tables:")
            
            # Check each table's schema
            for table in tables:
                table_name = table[0]
                print(f"\n📋 Table: {table_name}")
                print("=" * 50)
                
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print(f"Columns ({len(columns)}):")
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    pk_mark = "🔑 " if pk else "   "
                    print(f"{pk_mark}{col_id}: {col_name} ({col_type})")
                    
                # Check sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample_row = cursor.fetchone()
                if sample_row:
                    print("\nSample data (1 row):")
                    for i, col in enumerate(columns):
                        col_name = col[1]
                        value = sample_row[i]
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..." 
                        print(f"  {col_name}: {value}")
                else:
                    print("\nNo data in this table.")
                
        return True
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    print("🔍 Checking database schema...")
    check_db_schema()

if __name__ == "__main__":
    main()