#!/usr/bin/env python3
"""
Test script to verify QR code emergency contacts fix.
Run this after starting the backend server.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
DEV_USER_ID = "00000000-0000-0000-0000-000000000001"

def test_qr_contacts():
    """Test the QR code generation with emergency contacts."""
    
    print("=" * 80)
    print("QR CODE EMERGENCY CONTACTS FIX TEST")
    print("=" * 80)
    print()
    
    # Step 1: Login as dev user
    print("Step 1: Logging in as dev user...")
    login_response = requests.post(
        f"{BASE_URL}/auth/dev-login",
        json={"user_id": DEV_USER_ID}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    print()
    
    # Step 2: Check debug endpoint
    print("Step 2: Checking debug endpoint...")
    debug_response = requests.get(
        f"{BASE_URL}/emergency/medical-info/debug",
        headers=headers
    )
    
    if debug_response.status_code != 200:
        print(f"❌ Debug endpoint failed: {debug_response.status_code}")
        print(debug_response.text)
        return
    
    debug_data = debug_response.json()
    print("✅ Debug endpoint successful")
    print()
    print("Debug Information:")
    print(f"  User: {debug_data.get('user_name', 'N/A')} ({debug_data.get('user_email')})")
    print(f"  Contacts from table: {debug_data.get('emergency_contacts_table_count', 0)}")
    print(f"  Contacts from medical_info: {debug_data.get('emergency_contacts_from_medical_info_count', 0)}")
    print(f"  Which will be used: {debug_data.get('which_contacts_will_be_used', 'unknown')}")
    print()
    
    if debug_data.get('emergency_contacts_from_medical_info'):
        print("  Contacts from medical_info:")
        for contact in debug_data['emergency_contacts_from_medical_info']:
            print(f"    - {contact.get('name')}: {contact.get('phone')} ({contact.get('relationship', 'N/A')})")
        print()
    
    if debug_data.get('emergency_contacts_from_table'):
        print("  Contacts from table:")
        for contact in debug_data['emergency_contacts_from_table']:
            print(f"    - {contact.get('name')}: {contact.get('phone')} ({contact.get('relationship', 'N/A')})")
        print()
    
    # Step 3: Add test medical info with emergency contacts
    print("Step 3: Adding test medical info with emergency contacts...")
    medical_info = {
        "medications": ["Donepezil 10mg", "Memantine 20mg"],
        "allergies": ["Penicillin"],
        "conditions": ["Alzheimer's Disease"],
        "blood_type": "O+",
        "emergency_notes": "Patient may be disoriented",
        "emergency_contacts": [
            {
                "name": "Jane Doe",
                "phone": "+1-555-0101",
                "relationship": "Spouse"
            },
            {
                "name": "Dr. Smith",
                "phone": "+1-555-0102",
                "relationship": "Primary Care Physician"
            }
        ]
    }
    
    update_response = requests.put(
        f"{BASE_URL}/emergency/medical-info",
        headers=headers,
        json=medical_info
    )
    
    if update_response.status_code != 200:
        print(f"❌ Update medical info failed: {update_response.status_code}")
        print(update_response.text)
        return
    
    print("✅ Medical info updated successfully")
    print()
    
    # Step 4: Check debug endpoint again
    print("Step 4: Checking debug endpoint after update...")
    debug_response2 = requests.get(
        f"{BASE_URL}/emergency/medical-info/debug",
        headers=headers
    )
    
    if debug_response2.status_code == 200:
        debug_data2 = debug_response2.json()
        print("✅ Debug endpoint successful")
        print()
        print("Updated Debug Information:")
        print(f"  Contacts from medical_info: {debug_data2.get('emergency_contacts_from_medical_info_count', 0)}")
        print(f"  Which will be used: {debug_data2.get('which_contacts_will_be_used', 'unknown')}")
        
        if debug_data2.get('emergency_contacts_from_medical_info'):
            print("  Contacts:")
            for contact in debug_data2['emergency_contacts_from_medical_info']:
                print(f"    - {contact.get('name')}: {contact.get('phone')} ({contact.get('relationship', 'N/A')})")
        print()
    
    # Step 5: Generate QR code
    print("Step 5: Generating QR code...")
    qr_response = requests.post(
        f"{BASE_URL}/emergency/medical-info/qr-code",
        headers=headers
    )
    
    if qr_response.status_code != 200:
        print(f"❌ QR code generation failed: {qr_response.status_code}")
        print(qr_response.text)
        return
    
    qr_data = qr_response.json()
    print("✅ QR code generated successfully")
    print()
    print(f"  QR Code URL: {qr_data.get('url')}")
    print(f"  QR Code data length: {len(qr_data.get('qr_code', ''))} characters")
    print()
    
    # Step 6: Verify the QR code contains contact information
    print("Step 6: Verifying QR code content...")
    qr_code_data = qr_data.get('qr_code', '')
    
    if qr_code_data.startswith('data:image/png;base64,'):
        print("✅ QR code is a valid base64 PNG image")
        
        # Decode and check if contacts are in the QR code
        # (In a real scenario, you'd decode the QR code image to verify)
        print()
        print("=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        print()
        print("Summary:")
        print("  ✅ Login successful")
        print("  ✅ Medical info updated with emergency contacts")
        print("  ✅ QR code generated successfully")
        print()
        print("Next steps:")
        print("  1. Open the Emergency page in the frontend")
        print("  2. Click 'Generate QR Code' button")
        print("  3. Verify that emergency contacts appear in the QR code")
        print()
    else:
        print("❌ QR code format is invalid")
        print(f"  Starts with: {qr_code_data[:50]}")

if __name__ == "__main__":
    try:
        test_qr_contacts()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
