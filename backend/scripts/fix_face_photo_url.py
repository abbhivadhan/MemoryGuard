#!/usr/bin/env python3
"""
Quick fix script to update photo_url column to TEXT type
Run this on Render if migrations aren't working
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import engine
from sqlalchemy import text

def fix_photo_url_column():
    """Change photo_url from VARCHAR(500) to TEXT"""
    
    print("🔧 Fixing photo_url column in face_profiles table...")
    
    try:
        with engine.connect() as conn:
            # Check current type
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'face_profiles' 
                AND column_name = 'photo_url'
            """))
            
            current = result.fetchone()
            if current:
                print(f"Current: {current[0]} - {current[1]}({current[2]})")
            
            # Alter column to TEXT
            print("\n📝 Changing column type to TEXT...")
            conn.execute(text("""
                ALTER TABLE face_profiles 
                ALTER COLUMN photo_url TYPE TEXT
            """))
            conn.commit()
            
            # Verify change
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'face_profiles' 
                AND column_name = 'photo_url'
            """))
            
            updated = result.fetchone()
            if updated:
                print(f"Updated: {updated[0]} - {updated[1]}({updated[2]})")
            
            print("\n✅ Successfully updated photo_url column to TEXT!")
            print("You can now store base64-encoded images.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_photo_url_column()
