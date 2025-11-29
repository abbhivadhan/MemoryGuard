"""
Seed realistic prediction data for demo purposes
"""
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.prediction import Prediction
from app.models.user import User


def seed_realistic_predictions():
    """Seed realistic predictions for existing users"""
    db = SessionLocal()
    
    try:
        user = db.query(User).first()
        
        if not user:
            print("No users found. Please create a user first.")
            return
        
        print(f"Seeding predictions for user: {user.email}")
        
        # Clear existing predictions
        db.query(Prediction).filter(Prediction.user_id == user.id).delete()
        
        # Create predictions over time showing progression
        base_date = datetime.now() - timedelta(days=150)
        
        predictions_to_add = []
        
        # Generate 5 predictions over 5 months
        for i in range(5):
            date = base_date + timedelta(days=i*30)
            
            # Risk increases slightly over time (0.35 → 0.42)
            # This represents MCI with mild progression
            base_risk = 0.35 + (i * 0.015)
            risk = base_risk + random.uniform(-0.02, 0.02)
            risk = max(0.0, min(1.0, risk))  # Clamp to [0, 1]
            
            # Determine risk level
            if risk < 0.3:
                risk_level = 'low'
            elif risk < 0.6:
                risk_level = 'moderate'
            else:
                risk_level = 'high'
            
            # Confidence intervals (±0.08)
            conf_lower = max(0.0, risk - 0.08)
            conf_upper = min(1.0, risk + 0.08)
            
            # Confidence score (0.75-0.85)
            confidence = 0.80 + random.uniform(-0.05, 0.05)
            
            prediction = Prediction(
                user_id=user.id,
                risk_score=risk,
                risk_category=risk_level,
                confidence_interval_lower=conf_lower,
                confidence_interval_upper=conf_upper,
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
            )
            
            predictions_to_add.append(prediction)
        
        # Add all predictions
        db.bulk_save_objects(predictions_to_add)
        db.commit()
        
        print(f"✓ Successfully seeded {len(predictions_to_add)} realistic predictions")
        print("\nPrediction Summary:")
        print(f"  - Risk progression: 35% → 42% over 5 months")
        print(f"  - Risk level: Moderate (MCI range)")
        print(f"  - Confidence: ~80% (typical for ensemble models)")
        print(f"  - Model: ensemble_v1.0.0")
        print("\nValues represent realistic MCI progression patterns.")
        
    except Exception as e:
        print(f"Error seeding predictions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding realistic predictions...")
    seed_realistic_predictions()
    print("\nDone!")
