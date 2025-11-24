#!/usr/bin/env python3
"""
Create dev user in database for testing.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.services.auth_service import AuthService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_dev_user():
    """Create dev user in database."""
    db = SessionLocal()
    
    try:
        email = "abbhivadhan279@gmail.com"
        password = "123456"
        name = "Dev User"
        
        # Check if user already exists
        existing_user = AuthService.get_user_by_email(db, email)
        
        if existing_user:
            logger.info(f"Dev user already exists: {email}")
            logger.info(f"User ID: {existing_user.id}")
            return
        
        # Create new user
        user = AuthService.create_user_with_password(
            db=db,
            email=email,
            password=password,
            name=name
        )
        
        logger.info(f"✓ Dev user created successfully!")
        logger.info(f"  Email: {email}")
        logger.info(f"  Password: {password}")
        logger.info(f"  User ID: {user.id}")
        logger.info(f"\nYou can now login with these credentials.")
        
    except Exception as e:
        logger.error(f"Error creating dev user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_dev_user()
