"""Test script to verify QR code generation with emergency contacts."""

from app.services.qr_service import generate_medical_info_qr, _format_emergency_text

# Test data with emergency contacts
test_medical_info = {
    "user_id": "test-user-123",
    "name": "John Doe",
    "email": "john@example.com",
    "emergency_contacts": [
        {
            "name": "Jane Doe",
            "phone": "+1-555-0101",
            "relationship": "Spouse",
            "email": "jane@example.com"
        },
        {
            "name": "Dr. Smith",
            "phone": "+1-555-0102",
            "relationship": "Primary Care Physician",
            "email": "drsmith@hospital.com"
        }
    ],
    "medications": [
        {
            "name": "Donepezil",
            "dosage": "10mg",
            "frequency": "Once daily"
        },
        {
            "name": "Memantine",
            "dosage": "20mg",
            "frequency": "Twice daily"
        }
    ],
    "allergies": ["Penicillin", "Sulfa drugs"],
    "conditions": ["Alzheimer's Disease", "Hypertension"],
    "blood_type": "O+",
    "medical_notes": "Patient may be disoriented. Please contact emergency contacts immediately."
}

# Test formatting
print("=" * 80)
print("TESTING QR CODE TEXT FORMATTING")
print("=" * 80)
print()

formatted_text = _format_emergency_text(test_medical_info)
print(formatted_text)
print()
print("=" * 80)
print(f"Total characters: {len(formatted_text)}")
print("=" * 80)

# Test with empty contacts
print("\n\n")
print("=" * 80)
print("TESTING WITH NO EMERGENCY CONTACTS")
print("=" * 80)
print()

test_no_contacts = {
    "name": "John Doe",
    "emergency_contacts": [],
    "medications": ["Aspirin"],
    "allergies": ["None"],
    "blood_type": "A+"
}

formatted_text_no_contacts = _format_emergency_text(test_no_contacts)
print(formatted_text_no_contacts)
print()
print("=" * 80)

# Generate actual QR code
print("\n\n")
print("=" * 80)
print("GENERATING QR CODE")
print("=" * 80)

try:
    qr_code = generate_medical_info_qr(
        medical_info=test_medical_info,
        user_id="test-user-123",
        base_url="http://localhost:3000"
    )
    print(f"QR Code generated successfully!")
    print(f"Data URI length: {len(qr_code)}")
    print(f"Starts with: {qr_code[:50]}...")
except Exception as e:
    print(f"Error generating QR code: {e}")
    import traceback
    traceback.print_exc()
