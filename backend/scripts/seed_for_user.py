"""
Seed health metrics and predictions for a specific user
"""
import sys
import os
from datetime import datetime, timedelta
import random
from uuid import UUID

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.health_metric import HealthMetric
from app.models.prediction import Prediction, RiskCategory
from app.models.user import User


def seed_for_user(user_id: str):
    """Seed data for a specific user"""
    db = SessionLocal()
    
    try:
        user_uuid = UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
        
        if not user:
            print(f"User {user_id} not found")
            return
        
        print(f"Seeding data for user: {user.email} ({user_id})")
        
        # Delete existing data
        db.query(HealthMetric).filter(HealthMetric.user_id == user_uuid).delete()
        db.query(Prediction).filter(Prediction.user_id == user_uuid).delete()
        db.commit()
        
        # Seed health metrics
        now = datetime.utcnow()
        metrics = []
        
        # Cognitive scores (6 months of data)
        for i in range(6):
            date = now - timedelta(days=30 * (5 - i))
            
            # MMSE declining from 26 to 24
            metrics.append(HealthMetric(
                user_id=user_uuid,
                type='COGNITIVE',
                name='MMSE Score',
                value=26.0 - (i * 0.3),
                unit='points',
                source='ASSESSMENT',
                timestamp=date
            ))
            
            # MoCA declining from 24 to 22
            metrics.append(HealthMetric(
                user_id=user_uuid,
                type='COGNITIVE',
                name='MoCA Score',
                value=24.0 - (i * 0.4),
                unit='points',
                source='ASSESSMENT',
                timestamp=date
            ))
        
        # Biomarkers
        for i in range(6):
            date = now - timedelta(days=30 * (5 - i))
            
            # Amyloid beta declining (bad)
            metrics.append(HealthMetric(
                user_id=user_uuid,
                type='BIOMARKER',
                name='Amyloid Beta 42',
                value=520 - (i * 9),
                unit='pg/mL',
                source='LAB',
                timestamp=date
            ))
            
            # Tau increasing (bad)
            metrics.append(HealthMetric(
                user_id=user_uuid,
                type='BIOMARKER',
                name='Total Tau',
                value=280 + (i * 7),
                unit='pg/mL',
                source='LAB',
                timestamp=date
            ))
        
        db.bulk_save_objects(metrics)
        db.commit()
        print(f"✓ Seeded {len(metrics)} health metrics")
        
        # Seed predictions
        predictions = []
        for i in range(5):
            date = now - timedelta(days=30 * (4 - i))
            risk = 0.35 + (i * 0.015) + random.uniform(-0.01, 0.01)
            
            predictions.append(Prediction(
                user_id=user_uuid,
                risk_score=risk,
                risk_category=RiskCategory.MODERATE,
                confidence_interval_lower=max(0.0, risk - 0.08),
                confidence_interval_upper=min(1.0, risk + 0.08),
                model_version='ensemble_v1.0.0',
                model_type='ensemble',
                prediction_date=date,
                created_at=date,
                input_features={
                    'mmse_score': 26.0 - (i * 0.3),
                    'moca_score': 24.0 - (i * 0.4),
                    'age': 68,
                    'apoe4_status': 1
                },
                feature_importance={
                    'mmse_score': 0.25,
                    'moca_score': 0.22,
                    'age': 0.18,
                    'apoe4_status': 0.15,
                    'hippocampal_volume': 0.12,
                    'tau_protein': 0.08
                },
                forecast_six_month=min(1.0, risk + 0.02),
                forecast_twelve_month=min(1.0, risk + 0.04),
                forecast_twenty_four_month=min(1.0, risk + 0.08),
                recommendations=[
                    'Continue cognitive training exercises',
                    'Maintain regular physical activity',
                    'Monitor biomarker levels quarterly'
                ]
            ))
        
        db.bulk_save_objects(predictions)
        db.commit()
        print(f"✓ Seeded {len(predictions)} predictions")
        print("\nDone!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_for_user.py <user_id>")
        sys.exit(1)
    
    seed_for_user(sys.argv[1])
