"""Script to check emergency contacts in the database."""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.emergency_contact import EmergencyContact
from app.models.user import User

def check_contacts():
    """Check all emergency contacts in the database."""
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        print(f"\n{'='*80}")
        print(f"Found {len(users)} users in database")
        print(f"{'='*80}\n")
        
        for user in users:
            print(f"User: {user.email} (ID: {user.id})")
            
            # Get emergency contacts for this user
            contacts = db.query(EmergencyContact).filter(
                EmergencyContact.user_id == user.id
            ).all()
            
            print(f"  Total contacts: {len(contacts)}")
            
            # Get active contacts
            active_contacts = db.query(EmergencyContact).filter(
                EmergencyContact.user_id == user.id,
                EmergencyContact.active == True
            ).all()
            
            print(f"  Active contacts: {len(active_contacts)}")
            
            if contacts:
                print(f"\n  Contact Details:")
                for i, contact in enumerate(contacts, 1):
                    print(f"    {i}. {contact.name}")
                    print(f"       Phone: {contact.phone}")
                    print(f"       Relationship: {contact.relationship_type}")
                    print(f"       Active: {contact.active}")
                    print(f"       Priority: {contact.priority}")
                    print(f"       ID: {contact.id}")
                    print()
            else:
                print(f"  No contacts found for this user\n")
            
            print(f"{'-'*80}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_contacts()
