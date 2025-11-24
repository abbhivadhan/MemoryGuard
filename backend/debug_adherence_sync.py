#!/usr/bin/env python3
"""
Synchronous debug script to identify why adherence calculation shows 0%
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.medication import Medication


def debug_adherence_calculation():
    """Debug the adherence calculation issue."""
    
    print("=" * 80)
    print("ADHERENCE CALCULATION DEBUG")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Get all active medications
        medications = db.query(Medication).filter(Medication.active == True).all()
        
        if not medications:
            print("\n❌ No active medications found")
            return
        
        print(f"\n✅ Found {len(medications)} active medication(s)")
        
        for med in medications:
            print(f"\n{'=' * 80}")
            print(f"Medication: {med.name}")
            print(f"ID: {med.id}")
            print(f"Frequency: {med.frequency}")
            print(f"Created: {med.created_at}")
            
            # Get adherence log
            adherence_log = med.adherence_log or []
            
            print(f"\n📊 Total log entries: {len(adherence_log)}")
            
            if adherence_log:
                print("\nRecent log entries:")
                for i, log in enumerate(adherence_log[-5:]):  # Show last 5
                    print(f"\n  Entry {i+1}:")
                    print(f"    Scheduled: {log.get('scheduled_time')}")
                    print(f"    Taken: {log.get('taken_time')}")
                    print(f"    Skipped: {log.get('skipped', False)}")
                    
                    # Parse times
                    if log.get('scheduled_time'):
                        try:
                            scheduled = datetime.fromisoformat(log['scheduled_time'].replace('Z', '+00:00'))
                            print(f"    Scheduled (parsed): {scheduled}")
                        except Exception as e:
                            print(f"    Error parsing scheduled time: {e}")
                    
                    if log.get('taken_time'):
                        try:
                            taken = datetime.fromisoformat(log['taken_time'].replace('Z', '+00:00'))
                            print(f"    Taken (parsed): {taken}")
                        except Exception as e:
                            print(f"    Error parsing taken time: {e}")
            
            # Calculate expected doses in last 7 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            print(f"\n📅 Checking period: {start_date.date()} to {end_date.date()}")
            
            # Count scheduled doses in period
            scheduled_in_period = []
            schedule = med.schedule or []
            print(f"Total schedule entries: {len(schedule)}")
            
            for dt in schedule:
                if start_date <= dt <= end_date:
                    scheduled_in_period.append(dt)
            
            print(f"Scheduled doses in period: {len(scheduled_in_period)}")
            
            # Count taken doses from adherence log
            taken_count = 0
            skipped_count = 0
            
            for log in adherence_log:
                if log.get('scheduled_time'):
                    try:
                        scheduled = datetime.fromisoformat(log['scheduled_time'].replace('Z', '+00:00'))
                        if start_date <= scheduled <= end_date:
                            if not log.get('skipped', True) and log.get('taken_time'):
                                taken_count += 1
                            elif log.get('skipped'):
                                skipped_count += 1
                    except Exception as e:
                        print(f"    Error processing log: {e}")
            
            print(f"Taken doses: {taken_count}")
            print(f"Skipped doses: {skipped_count}")
            
            # Calculate adherence using model method
            try:
                model_adherence = med.calculate_adherence_rate(days=7)
                print(f"\n🎯 Model Calculated Adherence: {model_adherence:.1f}%")
            except Exception as e:
                print(f"\n❌ Error calculating model adherence: {e}")
            
            # Calculate manually
            if len(scheduled_in_period) > 0:
                manual_adherence = (taken_count / len(scheduled_in_period)) * 100
                print(f"🎯 Manual Calculated Adherence: {manual_adherence:.1f}%")
            else:
                print(f"⚠️  Cannot calculate adherence (no scheduled doses in period)")
            
            # Check for time matching issues
            print("\n🔍 DETAILED LOG ANALYSIS:")
            
            if adherence_log:
                for i, log in enumerate(adherence_log[-3:]):  # Last 3
                    print(f"\n  Entry {i+1}:")
                    print(f"    Raw data: {log}")
                    
                    if log.get('scheduled_time'):
                        try:
                            scheduled = datetime.fromisoformat(log['scheduled_time'].replace('Z', '+00:00'))
                            in_period = start_date <= scheduled <= end_date
                            print(f"    In period: {in_period}")
                            
                            if log.get('taken_time'):
                                taken = datetime.fromisoformat(log['taken_time'].replace('Z', '+00:00'))
                                time_diff = abs((taken - scheduled).total_seconds())
                                print(f"    Time difference: {time_diff} seconds ({time_diff/60:.1f} minutes)")
                        except Exception as e:
                            print(f"    Error: {e}")
            
            # Show schedule times
            print("\n🔍 SCHEDULE ANALYSIS:")
            print(f"  Total scheduled times: {len(schedule)}")
            if schedule:
                print("  Recent scheduled times:")
                for dt in schedule[-5:]:
                    print(f"    - {dt}")
                    in_period = start_date <= dt <= end_date
                    print(f"      In period: {in_period}")
    
    finally:
        db.close()
    
    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    debug_adherence_calculation()
