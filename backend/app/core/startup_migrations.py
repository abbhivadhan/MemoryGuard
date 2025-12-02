"""
Startup migrations that run automatically when the app starts.
This is useful for Render free tier where shell access is not available.
"""

import logging
from sqlalchemy import text
from app.core.database import engine

logger = logging.getLogger(__name__)


def run_startup_migrations():
    """
    Run critical migrations on startup.
    This ensures the database schema is up to date even without shell access.
    """
    try:
        logger.info("Running startup migrations...")
        
        # Migration 1: Fix photo_url column for face recognition
        fix_photo_url_column()
        
        logger.info("✅ Startup migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Startup migrations failed: {e}")
        # Don't crash the app, just log the error
        return False


def fix_photo_url_column():
    """
    Change photo_url from VARCHAR(500) to TEXT to support base64 images.
    This is idempotent - safe to run multiple times.
    """
    try:
        with engine.connect() as conn:
            # Check if the column exists and its current type
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'face_profiles' 
                AND column_name = 'photo_url'
            """))
            
            column_info = result.fetchone()
            
            if not column_info:
                logger.info("face_profiles.photo_url column doesn't exist yet - skipping migration")
                return
            
            current_type = column_info[1]
            max_length = column_info[2]
            
            # Only run migration if it's still VARCHAR
            if current_type == 'character varying' and max_length == 500:
                logger.info(f"Migrating photo_url from VARCHAR(500) to TEXT...")
                
                conn.execute(text("""
                    ALTER TABLE face_profiles 
                    ALTER COLUMN photo_url TYPE TEXT
                """))
                conn.commit()
                
                logger.info("✅ Successfully migrated photo_url to TEXT")
            elif current_type == 'text':
                logger.info("photo_url is already TEXT - migration not needed")
            else:
                logger.info(f"photo_url has unexpected type: {current_type} - skipping migration")
                
    except Exception as e:
        logger.error(f"Error in fix_photo_url_column migration: {e}")
        raise
