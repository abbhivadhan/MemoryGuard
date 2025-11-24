#!/usr/bin/env python3
"""
Test script to verify reminder creation works.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def test_reminder_creation():
    """Test creating a reminder."""
    
    print("=" * 80)
    print("REMINDER CREATION TEST")
    print("=" * 80)
    print()
    
    # Step 1: Login as dev user
    print("Step 1: Logging in as dev user...")
    login_response = requests.post(
        f"{BASE_URL}/auth/dev-login",
        json={"email": "dev@example.com"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    print()
    
    # Step 2: Create a reminder
    print("Step 2: Creating a reminder...")
    
    # Schedule for 1 hour from now
    scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    reminder_data = {
        "title": "Test Reminder",
        "description": "This is a test reminder",
        "reminder_type": "custom",
        "scheduled_time": scheduled_time,
        "frequency": "once",
        "send_notification": True
    }
    
    print(f"Reminder data: {json.dumps(reminder_data, indent=2)}")
    print()
    
    create_response = requests.post(
        f"{BASE_URL}/reminders/",
        headers=headers,
        json=reminder_data
    )
    
    if create_response.status_code != 201:
        print(f"❌ Create reminder failed: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        
        # Try to parse error details
        try:
            error_data = create_response.json()
            print(f"\nError details:")
            print(json.dumps(error_data, indent=2))
        except:
            pass
        return
    
    reminder = create_response.json()
    print("✅ Reminder created successfully")
    print(f"Reminder ID: {reminder['id']}")
    print(f"Title: {reminder['title']}")
    print(f"Scheduled: {reminder['scheduled_time']}")
    print()
    
    # Step 3: Verify reminder was saved
    print("Step 3: Fetching reminders...")
    get_response = requests.get(
        f"{BASE_URL}/reminders/",
        headers=headers
    )
    
    if get_response.status_code != 200:
        print(f"❌ Get reminders failed: {get_response.status_code}")
        print(get_response.text)
        return
    
    reminders_data = get_response.json()
    print(f"✅ Found {reminders_data['total']} reminder(s)")
    
    if reminders_data['total'] > 0:
        print("\nReminders:")
        for r in reminders_data['reminders']:
            print(f"  - {r['title']} (ID: {r['id']})")
    print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    
    if reminders_data['total'] > 0:
        print("✅ Reminders are being saved correctly!")
    else:
        print("❌ Reminder was created but not found in list")

if __name__ == "__main__":
    try:
        test_reminder_creation()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
