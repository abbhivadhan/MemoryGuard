#!/usr/bin/env python3
"""
Quick script to verify the MedicalInfo schema includes emergency_contacts.
"""

import sys
sys.path.insert(0, '.')

from app.api.v1.emergency import MedicalInfo, EmergencyContactInfo
from pydantic import ValidationError

print("=" * 80)
print("SCHEMA VERIFICATION")
print("=" * 80)
print()

# Test 1: Check if EmergencyContactInfo exists
print("Test 1: EmergencyContactInfo schema")
try:
    contact = EmergencyContactInfo(
        name="Jane Doe",
        phone="+1-555-0101",
        relationship="Spouse"
    )
    print("✅ EmergencyContactInfo schema exists and works")
    print(f"   Contact: {contact.dict()}")
except Exception as e:
    print(f"❌ EmergencyContactInfo schema failed: {e}")
print()

# Test 2: Check if MedicalInfo accepts emergency_contacts
print("Test 2: MedicalInfo with emergency_contacts")
try:
    medical_info = MedicalInfo(
        medications=["Aspirin 81mg"],
        allergies=["Penicillin"],
        blood_type="O+",
        emergency_contacts=[
            {
                "name": "Jane Doe",
                "phone": "+1-555-0101",
                "relationship": "Spouse"
            },
            {
                "name": "Dr. Smith",
                "phone": "+1-555-0102",
                "relationship": "Doctor"
            }
        ]
    )
    print("✅ MedicalInfo accepts emergency_contacts")
    print(f"   Contacts count: {len(medical_info.emergency_contacts)}")
    print(f"   First contact: {medical_info.emergency_contacts[0].dict()}")
except ValidationError as e:
    print(f"❌ MedicalInfo validation failed: {e}")
except Exception as e:
    print(f"❌ MedicalInfo failed: {e}")
print()

# Test 3: Check if MedicalInfo works without emergency_contacts (optional field)
print("Test 3: MedicalInfo without emergency_contacts (should work)")
try:
    medical_info = MedicalInfo(
        medications=["Aspirin 81mg"],
        blood_type="O+"
    )
    print("✅ MedicalInfo works without emergency_contacts (optional)")
    print(f"   Emergency contacts: {medical_info.emergency_contacts}")
except Exception as e:
    print(f"❌ MedicalInfo failed: {e}")
print()

# Test 4: Verify the schema fields
print("Test 4: MedicalInfo schema fields")
print("   Fields in MedicalInfo:")
for field_name, field_info in MedicalInfo.__fields__.items():
    required = field_info.required
    field_type = field_info.annotation
    print(f"   - {field_name}: {field_type} {'(required)' if required else '(optional)'}")
print()

# Check if emergency_contacts is in the schema
if 'emergency_contacts' in MedicalInfo.__fields__:
    print("✅ emergency_contacts field is present in MedicalInfo schema")
else:
    print("❌ emergency_contacts field is MISSING from MedicalInfo schema")
    print("   This means the backend will ignore emergency_contacts in requests!")
print()

print("=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
print()

if 'emergency_contacts' in MedicalInfo.__fields__:
    print("✅ Schema is correct - emergency contacts will be saved")
    print()
    print("Next steps:")
    print("1. Restart the backend if it's running")
    print("2. Test adding emergency contacts via the UI")
    print("3. Generate QR code and verify contacts appear")
else:
    print("❌ Schema is incorrect - emergency contacts will NOT be saved")
    print()
    print("Fix required:")
    print("1. Check backend/app/api/v1/emergency.py")
    print("2. Ensure MedicalInfo includes emergency_contacts field")
    print("3. Restart the backend")
