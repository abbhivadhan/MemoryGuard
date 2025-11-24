#!/usr/bin/env python3
"""
Setup demo recommendations for testing.
This script creates sample recommendations for the first user in the database.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.prediction import Prediction
from app.services.recommendation_service import RecommendationService
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_demo_recommendations():
    """Setup demo recommendations for testing."""
    db = SessionLocal()
    
    try:
        # Get first user
        user = db.query(User).first()
        
        if not user:
            logger.error("No users found. Please create a user first.")
            return
        
        logger.info(f"Setting up demo recommendations for user: {user.email}")
        
        # Check if user has predictions
        from app.models.prediction import Prediction as PredictionModel, RiskCategory
        import uuid
        
        prediction = db.query(PredictionModel).filter(
            PredictionModel.user_id == user.id
        ).first()
        
        if not prediction:
            logger.info("No prediction found. Creating sample prediction...")
            
            prediction = PredictionModel(
                id=uuid.uuid4(),
                user_id=user.id,
                risk_score=0.35,
                risk_category=RiskCategory.MODERATE,
                confidence_interval_lower=0.28,
                confidence_interval_upper=0.42,
                feature_importance={
                    'cognitive_decline': 0.35,
                    'cardiovascular_risk': 0.28,
                    'diabetes_risk': 0.15,
                    'poor_sleep': 0.22,
                    'social_isolation': 0.18,
                    'sedentary_lifestyle': 0.25
                },
                recommendations=[],
                model_version="1.0.0",
                model_type="ensemble",
                input_features={},
                prediction_date=datetime.utcnow()
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            logger.info("Sample prediction created")
        
        # Define sample risk factors and metrics
        risk_factors = prediction.feature_importance or {
            'cognitive_decline': 0.35,
            'cardiovascular_risk': 0.28,
            'diabetes_risk': 0.15,
            'poor_sleep': 0.22,
            'social_isolation': 0.18,
            'sedentary_lifestyle': 0.25
        }
        
        current_metrics = {
            'sleep_hours': 6.5,
            'physical_activity_minutes': 45,
            'glucose': 105,
            'sleep_quality': 6,
            'social_interactions_per_week': 2,
            'cholesterol': 220,
            'blood_pressure': 135,
            'weight': 180
        }
        
        # Generate recommendations
        logger.info("Generating recommendations...")
        service = RecommendationService(db)
        
        recommendations = service.generate_recommendations(
            user_id=str(user.id),
            risk_factors=risk_factors,
            current_metrics=current_metrics
        )
        
        logger.info(f"\n✓ Successfully generated {len(recommendations)} recommendations!")
        logger.info("\nRecommendations by category:")
        
        categories = {}
        for rec in recommendations:
            cat = rec.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(rec)
        
        for category, recs in categories.items():
            logger.info(f"\n{category.upper()} ({len(recs)} recommendations):")
            for rec in recs:
                logger.info(f"  • {rec.title}")
                logger.info(f"    Priority: {rec.priority.value}, Evidence: {rec.evidence_strength}")
        
        # Create some sample adherence records
        logger.info("\nCreating sample adherence records...")
        from datetime import timedelta
        
        for i, rec in enumerate(recommendations[:5]):  # Track first 5 recommendations
            for day in range(7):  # Last 7 days
                completed = (i + day) % 3 != 0  # Vary completion
                service.track_adherence(
                    recommendation_id=str(rec.id),
                    user_id=str(user.id),
                    completed=completed
                )
        
        # Get adherence stats
        stats = service.get_adherence_stats(str(user.id), days=30)
        
        logger.info("\nAdherence Statistics:")
        logger.info(f"  Total Records: {stats['total_records']}")
        logger.info(f"  Completed: {stats['completed']}")
        logger.info(f"  Adherence Rate: {stats['adherence_rate']:.1%}")
        
        logger.info("\n✓ Demo recommendations setup complete!")
        logger.info(f"\nYou can now view recommendations at: http://localhost:5173/recommendations")
        logger.info(f"User email: {user.email}")
        
    except Exception as e:
        logger.error(f"Error setting up demo recommendations: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_demo_recommendations()
