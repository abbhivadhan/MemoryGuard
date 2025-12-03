"""Test encryption key and medication data."""
import os
from dotenv import load_dotenv

load_dotenv()

# Check if encryption key is set
encryption_key = os.getenv('DATA_ENCRYPTION_KEY')
print(f"Encryption key set: {bool(encryption_key)}")
if encryption_key:
    print(f"Key length: {len(encryption_key)}")
    print(f"Key (first 10 chars): {encryption_key[:10]}...")

# Test database connection and medication data
from app.core.database import SessionLocal
from app.models.medication import Medication

db = SessionLocal()
try:
    medications = db.query(Medication).all()
    print(f"\nTotal medications: {len(medications)}")
    
    if medications:
        print("\nFirst medication:")
        med = medications[0]
        print(f"  ID: {med.id}")
        print(f"  User ID: {med.user_id}")
        try:
            print(f"  Name: {med.name}")
            print(f"  Dosage: {med.dosage}")
            print(f"  Frequency: {med.frequency}")
            print("  ✓ Decryption successful!")
        except Exception as e:
            print(f"  ✗ Decryption failed: {e}")
finally:
    db.close()
