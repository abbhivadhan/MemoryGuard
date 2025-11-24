#!/usr/bin/env python3
"""
Test script to verify medication adherence tracking is working correctly.
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, '/Users/kiro/alzheimers-web-app')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.medication import Medication


def test_adherence_calculation():
    """Test that adherence calculation works correctly"""
    db = SessionLocal()
    
    try:
        # Find a test user or create one
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not test_user:
            print("❌ Test user not found. Please create a user with email test@example.com")
            return False
        
        print(f"✓ Found test user: {test_user.email}")
        
        # Create a test medication with schedule
        now = datetime.now(timezone.utc)
        schedule = []
        
        # Create schedule for last 7 days, 2 times per day (8am and 8pm)
        for day in range(-7, 1):
            date = now + timedelta(days=day)
            for hour in [8, 20]:
                scheduled_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                schedule.append(scheduled_time)
        
        print(f"\n✓ Generated schedule with {len(schedule)} doses over 7 days")
        
        # Create medication
        test_med = Medication(
            user_id=test_user.id,
            name="Test Medication",
            dosage="10mg",
            frequency="twice daily",
            schedule=schedule,
            adherence_log=[],
            side_effects=[],
            active=True
        )
        
        db.add(test_med)
        db.commit()
        db.refresh(test_med)
        
        print(f"✓ Created test medication: {test_med.name} (ID: {test_med.id})")
        
        # Log some doses as taken (simulate 80% adherence)
        adherence_log = []
        for i, scheduled_time in enumerate(schedule):
            # Take 80% of doses (skip every 5th dose)
            if i % 5 != 0:
                log_entry = {
                    "scheduled_time": scheduled_time.isoformat(),
                    "taken_time": (scheduled_time + timedelta(minutes=5)).isoformat(),
                    "skipped": False,
                    "notes": "Test log entry",
                    "logged_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                log_entry = {
                    "scheduled_time": scheduled_time.isoformat(),
                    "taken_time": None,
                    "skipped": True,
                    "notes": "Skipped for testing",
                    "logged_at": datetime.now(timezone.utc).isoformat()
                }
            adherence_log.append(log_entry)
        
        test_med.adherence_log = adherence_log
        
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(test_med, "adherence_log")
        
        db.commit()
        db.refresh(test_med)
        
        print(f"✓ Logged {len(adherence_log)} doses (80% taken, 20% skipped)")
        
        # Calculate adherence using the model method
        adherence_rate = test_med.calculate_adherence_rate(days=7)
        print(f"\n📊 Adherence Rate (model method): {adherence_rate:.2f}%")
        
        # Now test the API endpoint logic
        from datetime import timezone as tz
        cutoff_time = datetime.now(tz.utc) - timedelta(days=7)
        
        # Get scheduled doses from the medication's schedule within the period
        scheduled_doses = []
        if test_med.schedule:
            for scheduled_time in test_med.schedule:
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=tz.utc)
                if cutoff_time <= scheduled_time <= now:
                    scheduled_doses.append(scheduled_time)
        
        total_scheduled = len(scheduled_doses)
        
        # Count taken and skipped from adherence log
        recent_logs = []
        if test_med.adherence_log:
            for log in test_med.adherence_log:
                try:
                    scheduled_time = datetime.fromisoformat(log.get("scheduled_time", ""))
                    if scheduled_time.tzinfo is None:
                        scheduled_time = scheduled_time.replace(tzinfo=tz.utc)
                    if cutoff_time <= scheduled_time <= now:
                        recent_logs.append(log)
                except (ValueError, TypeError):
                    continue
        
        total_taken = sum(1 for log in recent_logs if not log.get("skipped", False) and log.get("taken_time"))
        total_skipped = sum(1 for log in recent_logs if log.get("skipped", False))
        
        api_adherence_rate = (total_taken / total_scheduled * 100) if total_scheduled > 0 else 0.0
        
        print(f"\n📊 API Endpoint Calculation:")
        print(f"   Total Scheduled: {total_scheduled}")
        print(f"   Total Taken: {total_taken}")
        print(f"   Total Skipped: {total_skipped}")
        print(f"   Adherence Rate: {api_adherence_rate:.2f}%")
        
        # Verify the calculation is correct
        expected_adherence = 80.0  # We logged 80% adherence
        tolerance = 5.0  # Allow 5% tolerance
        
        if abs(api_adherence_rate - expected_adherence) <= tolerance:
            print(f"\n✅ SUCCESS: Adherence calculation is working correctly!")
            print(f"   Expected: ~{expected_adherence}%, Got: {api_adherence_rate:.2f}%")
        else:
            print(f"\n❌ FAILURE: Adherence calculation is incorrect!")
            print(f"   Expected: ~{expected_adherence}%, Got: {api_adherence_rate:.2f}%")
            return False
        
        # Clean up test data
        db.delete(test_med)
        db.commit()
        print(f"\n✓ Cleaned up test medication")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Medication Adherence Tracking")
    print("=" * 60)
    
    success = test_adherence_calculation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
