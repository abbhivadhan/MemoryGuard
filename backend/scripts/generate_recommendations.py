#!/usr/bin/env python3
"""
Script to generate recommendations for users based on their latest predictions.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.prediction import Prediction
from app.models.health_metric import HealthMetric
from app.services.recommendation_service import RecommendationService
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_latest_metrics(db: Session, user_id: str) -> dict:
    """Get latest health metrics for a user."""
    metrics = {}
    
    # Get recent health metrics (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    health_metrics = db.query(HealthMetric).filter(
        HealthMetric.user_id == user_id,
        HealthMetric.recorded_at >= thirty_days_ago
    ).order_by(HealthMetric.recorded_at.desc()).all()
    
    if health_metrics:
        # Get most recent values for each metric type
        latest_metric = health_metrics[0]
        
        metrics['heart_rate'] = latest_metric.heart_rate
        metrics['blood_pressure_systolic'] = latest_metric.blood_pressure_systolic
        metrics['blood_pressure_diastolic'] = latest_metric.blood_pressure_diastolic
        metrics['glucose'] = latest_metric.glucose_level
        metrics['sleep_hours'] = latest_metric.sleep_hours
        metrics['sleep_quality'] = latest_metric.sleep_quality
        metrics['physical_activity_minutes'] = latest_metric.steps / 20 if latest_metric.steps else 0  # Rough estimate
        metrics['weight'] = latest_metric.weight
    
    return metrics


def generate_recommendations_for_user(db: Session, user_id: str) -> None:
    """Generate recommendations for a specific user."""
    logger.info(f"Generating recommendations for user {user_id}")
    
    # Get latest prediction
    latest_prediction = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.prediction_date.desc()).first()
    
    if not latest_prediction:
        logger.warning(f"No prediction found for user {user_id}. Skipping.")
        return
    
    # Get risk factors from feature importance
    risk_factors = latest_prediction.feature_importance or {}
    
    # Get current metrics
    current_metrics = get_latest_metrics(db, user_id)
    
    if not current_metrics:
        logger.warning(f"No health metrics found for user {user_id}. Using defaults.")
        current_metrics = {
            'sleep_hours': 7.0,
            'physical_activity_minutes': 30,
            'glucose': 90,
            'sleep_quality': 7,
            'social_interactions_per_week': 3
        }
    
    # Generate recommendations
    service = RecommendationService(db)
    recommendations = service.generate_recommendations(
        user_id=user_id,
        risk_factors=risk_factors,
        current_metrics=current_metrics
    )
    
    logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
    
    for rec in recommendations:
        logger.info(f"  - {rec.category.value}: {rec.title} (Priority: {rec.priority.value})")


def generate_recommendations_for_all_users(db: Session) -> None:
    """Generate recommendations for all users with predictions."""
    users = db.query(User).all()
    
    logger.info(f"Found {len(users)} users")
    
    for user in users:
        try:
            generate_recommendations_for_user(db, str(user.id))
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user.id}: {e}")
            continue


def main():
    """Main function."""
    db = SessionLocal()
    
    try:
        if len(sys.argv) > 1:
            # Generate for specific user
            user_id = sys.argv[1]
            generate_recommendations_for_user(db, user_id)
        else:
            # Generate for all users
            generate_recommendations_for_all_users(db)
        
        logger.info("Recommendation generation complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
