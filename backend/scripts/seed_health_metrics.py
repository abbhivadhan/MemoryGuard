"""
Seed realistic health metrics data for demo purposes
Uses medically accurate ranges based on clinical standards
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.health_metric import HealthMetric
from app.models.user import User


def seed_realistic_health_metrics():
    """Seed realistic health metrics for existing users"""
    db = SessionLocal()
    
    try:
        # Get first user (or create demo user)
        user = db.query(User).first()
        
        if not user:
            print("No users found. Please create a user first.")
            return
        
        print(f"Seeding health metrics for user: {user.email}")
        
        # Clear existing metrics for this user
        db.query(HealthMetric).filter(HealthMetric.user_id == user.id).delete()
        
        # Generate metrics over the past 6 months
        base_date = datetime.now() - timedelta(days=180)
        
        metrics_to_add = []
        
        # COGNITIVE METRICS (realistic ranges for MCI patient)
        # MMSE: 24-26 (mild cognitive impairment range)
        for i in range(6):
            date = base_date + timedelta(days=i*30)
            mmse_score = 26 - (i * 0.3) + random.uniform(-0.5, 0.5)  # Gradual decline
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='cognitive',
                name='MMSE Score',
                value=round(mmse_score, 1),
                unit='points',
                timestamp=date,
                source='assessment'
            ))
        
        # MoCA: 22-24 (MCI range)
        for i in range(6):
            date = base_date + timedelta(days=i*30)
            moca_score = 24 - (i * 0.4) + random.uniform(-0.5, 0.5)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='cognitive',
                name='MoCA Score',
                value=round(moca_score, 1),
                unit='points',
                timestamp=date,
                source='assessment'
            ))
        
        # BIOMARKER METRICS (realistic CSF values)
        # CSF Amyloid-beta 42: 400-600 pg/mL (low = AD risk)
        for i in range(4):
            date = base_date + timedelta(days=i*45)
            ab42 = 520 - (i * 15) + random.uniform(-20, 20)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='biomarker',
                name='CSF Aβ42',
                value=round(ab42, 1),
                unit='pg/mL',
                timestamp=date,
                source='lab'
            ))
        
        # CSF Total Tau: 250-350 pg/mL (elevated in AD)
        for i in range(4):
            date = base_date + timedelta(days=i*45)
            tau = 280 + (i * 12) + random.uniform(-15, 15)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='biomarker',
                name='CSF Total Tau',
                value=round(tau, 1),
                unit='pg/mL',
                timestamp=date,
                source='lab'
            ))
        
        # CSF Phosphorylated Tau: 55-70 pg/mL (elevated in AD)
        for i in range(4):
            date = base_date + timedelta(days=i*45)
            ptau = 58 + (i * 2.5) + random.uniform(-3, 3)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='biomarker',
                name='CSF p-Tau',
                value=round(ptau, 1),
                unit='pg/mL',
                timestamp=date,
                source='lab'
            ))
        
        # IMAGING METRICS (brain volumes in cm³)
        # Hippocampal volume: 6.0-6.5 cm³ (reduced in MCI)
        for i in range(3):
            date = base_date + timedelta(days=i*60)
            hippo_vol = 6.3 - (i * 0.08) + random.uniform(-0.05, 0.05)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='imaging',
                name='Hippocampal Volume',
                value=round(hippo_vol, 2),
                unit='cm³',
                timestamp=date,
                source='device'
            ))
        
        # Entorhinal Cortex Thickness: 2.8-3.2 mm
        for i in range(3):
            date = base_date + timedelta(days=i*60)
            ec_thick = 3.0 - (i * 0.06) + random.uniform(-0.03, 0.03)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='imaging',
                name='Entorhinal Cortex Thickness',
                value=round(ec_thick, 2),
                unit='mm',
                timestamp=date,
                source='device'
            ))
        
        # Whole Brain Volume: 1100-1150 cm³
        for i in range(3):
            date = base_date + timedelta(days=i*60)
            brain_vol = 1125 - (i * 4) + random.uniform(-5, 5)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='imaging',
                name='Whole Brain Volume',
                value=round(brain_vol, 1),
                unit='cm³',
                timestamp=date,
                source='device'
            ))
        
        # LIFESTYLE METRICS
        # Physical Activity: 120-180 minutes/week
        for i in range(12):
            date = base_date + timedelta(days=i*15)
            activity = 150 + random.uniform(-30, 30)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='lifestyle',
                name='Physical Activity',
                value=round(activity, 0),
                unit='min/week',
                timestamp=date,
                source='manual'
            ))
        
        # Sleep Duration: 6-8 hours
        for i in range(12):
            date = base_date + timedelta(days=i*15)
            sleep = 7.0 + random.uniform(-1, 1)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='lifestyle',
                name='Sleep Duration',
                value=round(sleep, 1),
                unit='hours',
                timestamp=date,
                source='device'
            ))
        
        # CARDIOVASCULAR METRICS
        # Blood Pressure Systolic: 125-135 mmHg
        for i in range(12):
            date = base_date + timedelta(days=i*15)
            bp_sys = 130 + random.uniform(-5, 5)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='cardiovascular',
                name='Blood Pressure (Systolic)',
                value=round(bp_sys, 0),
                unit='mmHg',
                timestamp=date,
                source='device'
            ))
        
        # Blood Pressure Diastolic: 75-85 mmHg
        for i in range(12):
            date = base_date + timedelta(days=i*15)
            bp_dia = 80 + random.uniform(-5, 5)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='cardiovascular',
                name='Blood Pressure (Diastolic)',
                value=round(bp_dia, 0),
                unit='mmHg',
                timestamp=date,
                source='device'
            ))
        
        # Heart Rate: 65-75 bpm
        for i in range(12):
            date = base_date + timedelta(days=i*15)
            hr = 70 + random.uniform(-5, 5)
            metrics_to_add.append(HealthMetric(
                user_id=user.id,
                type='cardiovascular',
                name='Resting Heart Rate',
                value=round(hr, 0),
                unit='bpm',
                timestamp=date,
                source='device'
            ))
        
        # Add all metrics to database
        db.bulk_save_objects(metrics_to_add)
        db.commit()
        
        print(f"✓ Successfully seeded {len(metrics_to_add)} realistic health metrics")
        print("\nMetric Summary:")
        print(f"  - Cognitive: MMSE (26→24), MoCA (24→22) - showing mild decline")
        print(f"  - Biomarkers: Aβ42 (520→475 pg/mL), Tau (280→316 pg/mL)")
        print(f"  - Imaging: Hippocampus (6.3→6.1 cm³) - mild atrophy")
        print(f"  - Lifestyle: Activity (~150 min/week), Sleep (~7 hrs)")
        print(f"  - Cardiovascular: BP (~130/80), HR (~70 bpm)")
        print("\nAll values are within realistic clinical ranges for MCI patients.")
        
    except Exception as e:
        print(f"Error seeding health metrics: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding realistic health metrics...")
    seed_realistic_health_metrics()
    print("\nDone!")
