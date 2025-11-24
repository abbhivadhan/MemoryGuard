#!/usr/bin/env python3
"""Test bcrypt fix"""
import sys
sys.path.insert(0, '/Users/abbhivadhan/Desktop/AI4A/backend')

from app.core.security import get_password_hash, verify_password

# Test password hashing
password = "123456"
print(f"Testing password: {password}")

try:
    hashed = get_password_hash(password)
    print(f"✓ Password hashed successfully: {hashed[:20]}...")
    
    # Test verification
    is_valid = verify_password(password, hashed)
    print(f"✓ Password verification: {is_valid}")
    
    # Test wrong password
    is_invalid = verify_password("wrong", hashed)
    print(f"✓ Wrong password rejected: {not is_invalid}")
    
    print("\n✓ Bcrypt fix working correctly!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
