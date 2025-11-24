#!/usr/bin/env python3
"""
Debug script to check medication adherence data in the database.
Run this to see what's actually stored for your medications.
"""
import sys
sys.path.insert(0, '/Users/kiro/alzheimers-web-app')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.medication import Medication
from app.models.user import User
from datetime import datetime, timezone
import json


def debug_medications():
    """Check all medications and their adherence data"""
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        print(f"\n{'='*80}")
        print(f"Found {len(users)} users in database")
        print(f"{'='*80}\n")
        
        for user in users:
            print(f"\n📧 User: {user.email} (ID: {user.id})")
            print(f"{'─'*80}")
            
            # Get medications for this user
            medications = db.query(Medication).filter(
                Medication.user_id == user.id
            ).all()
            
            if not medications:
                print("  ❌ No medications found")
                continue
            
            print(f"  Found {len(medications)} medication(s):\n")
            
            for med in medications:
                print(f"  💊 {med.name}")
                print(f"     ID: {med.id}")
                print(f"     Dosage: {med.dosage}")
                print(f"     Frequency: {med.frequency}")
                print(f"     Active: {med.active}")
                print(f"     Created: {med.created_at}")
                
                # Check schedule
                if med.schedule:
                    print(f"     ✅ Schedule: {len(med.schedule)} doses")
                    print(f"        First: {med.schedule[0] if med.schedule else 'N/A'}")
                    print(f"        Last: {med.schedule[-1] if med.schedule else 'N/A'}")
                    
                    # Count doses in last 7 days
                    now = datetime.now(timezone.utc)
                    from datetime import timedelta
                    cutoff = now - timedelta(days=7)
                    recent_scheduled = [
                        d for d in med.schedule 
                        if (d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d) >= cutoff
                        and (d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d) <= now
                    ]
                    print(f"        In last 7 days: {len(recent_scheduled)} doses")
                else:
                    print(f"     ❌ Schedule: EMPTY (This is the problem!)")
                
                # Check adherence log
                if med.adherence_log:
                    print(f"     ✅ Adherence Log: {len(med.adherence_log)} entries")
                    for i, log in enumerate(med.adherence_log[-3:], 1):  # Show last 3
                        status = "✓ Taken" if not log.get("skipped") else "✗ Skipped"
                        print(f"        {i}. {status} - {log.get('scheduled_time', 'N/A')}")
                else:
                    print(f"     ❌ Adherence Log: EMPTY")
                
                # Calculate what adherence would be
                if med.schedule and med.adherence_log:
                    now = datetime.now(timezone.utc)
                    from datetime import timedelta
                    cutoff = now - timedelta(days=7)
                    
                    # Count scheduled in last 7 days
                    scheduled_count = len([
                        d for d in med.schedule 
                        if cutoff <= (d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d) <= now
                    ])
                    
                    # Count taken in last 7 days
                    taken_count = 0
                    for log in med.adherence_log:
                        try:
                            sched_time = datetime.fromisoformat(log.get("scheduled_time", ""))
                            if sched_time.tzinfo is None:
                                sched_time = sched_time.replace(tzinfo=timezone.utc)
                            if cutoff <= sched_time <= now:
                                if not log.get("skipped") and log.get("taken_time"):
                                    taken_count += 1
                        except:
                            pass
                    
                    if scheduled_count > 0:
                        rate = (taken_count / scheduled_count) * 100
                        print(f"     📊 Calculated Adherence (7 days):")
                        print(f"        Scheduled: {scheduled_count}")
                        print(f"        Taken: {taken_count}")
                        print(f"        Rate: {rate:.1f}%")
                    else:
                        print(f"     ⚠️  No scheduled doses in last 7 days")
                elif not med.schedule:
                    print(f"     ⚠️  Cannot calculate adherence - NO SCHEDULE")
                elif not med.adherence_log:
                    print(f"     ⚠️  Cannot calculate adherence - NO LOGS")
                
                print()
        
        print(f"\n{'='*80}")
        print("DIAGNOSIS:")
        print(f"{'='*80}")
        
        # Check for common issues
        all_meds = db.query(Medication).all()
        meds_without_schedule = [m for m in all_meds if not m.schedule]
        meds_without_logs = [m for m in all_meds if not m.adherence_log]
        
        if meds_without_schedule:
            print(f"\n❌ PROBLEM: {len(meds_without_schedule)} medication(s) have NO SCHEDULE")
            print("   Solution: Delete these medications and recreate them using the")
            print("   'Add Medication' button in the Medication Reminders tab.")
            for med in meds_without_schedule:
                print(f"   - {med.name} (ID: {med.id})")
        
        if meds_without_logs:
            print(f"\n⚠️  INFO: {len(meds_without_logs)} medication(s) have NO ADHERENCE LOGS")
            print("   This is normal if you haven't marked any reminders as taken yet.")
            for med in meds_without_logs:
                print(f"   - {med.name} (ID: {med.id})")
        
        if not meds_without_schedule and not meds_without_logs:
            print("\n✅ All medications have schedules and logs!")
            print("   If adherence is still showing 0%, check:")
            print("   1. The scheduled doses are within the selected time period")
            print("   2. The browser console for errors")
            print("   3. The Network tab to see API responses")
        
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    debug_medications()
