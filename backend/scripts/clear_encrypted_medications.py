"""Clear medications that were encrypted with old ephemeral keys."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.medication import Medication

def clear_encrypted_medications():
    """Delete all medications that can't be decrypted."""
    db = SessionLocal()
    try:
        # Get all medications
        medications = db.query(Medication).all()
        print(f"Found {len(medications)} medications")
        
        deleted_count = 0
        for med in medications:
            try:
                # Try to access encrypted fields
                _ = med.name
                _ = med.dosage
                _ = med.frequency
                print(f"✓ Medication {med.id} can be decrypted")
            except Exception as e:
                # If decryption fails, delete the medication
                print(f"✗ Medication {med.id} cannot be decrypted, deleting...")
                db.delete(med)
                deleted_count += 1
        
        if deleted_count > 0:
            db.commit()
            print(f"\n✓ Deleted {deleted_count} medications with invalid encryption")
        else:
            print("\n✓ All medications can be decrypted successfully")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_encrypted_medications()
