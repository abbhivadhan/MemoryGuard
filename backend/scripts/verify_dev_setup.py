#!/usr/bin/env python3
"""
Verify dev setup is correct
"""
import sys
sys.path.insert(0, '/Users/abbhivadhan/Desktop/AI4A/backend')

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token
import uuid

def main():
    db = SessionLocal()
    try:
        # Check if dev user exists
        dev_user_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
        user = db.query(User).filter(User.id == dev_user_id).first()
        
        if not user:
            print("❌ Dev user not found!")
            return False
        
        print("✅ Dev user exists:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.name}")
        print()
        
        # Generate a test token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name
        }
        
        test_token = create_access_token(token_data)
        print("✅ Test token generated successfully")
        print(f"   Token (first 50 chars): {test_token[:50]}...")
        print()
        
        print("✅ Dev setup is correct!")
        print()
        print("To fix the QR code issue:")
        print("1. Clear your browser's localStorage (or log out)")
        print("2. Log back in using dev-login")
        print("3. Try generating the QR code again")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
