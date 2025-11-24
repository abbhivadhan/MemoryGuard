#!/usr/bin/env python3
"""
Test script for recommendations functionality.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.recommendation import Recommendation, RecommendationAdherence
from app.services.recommendation_service import RecommendationService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_recommendations():
    """Test recommendations functionality."""
    db = SessionLocal()
    
    try:
        # Get first user
        user = db.query(User).first()
        
        if not user:
            logger.error("No users found in database")
            return
        
        logger.info(f"Testing recommendations for user: {user.email}")
        
        # Check existing recommendations
        existing_recs = db.query(Recommendation).filter(
            Recommendation.user_id == user.id
        ).all()
        
        logger.info(f"Found {len(existing_recs)} existing recommendations")
        
        if existing_recs:
            for rec in existing_recs[:5]:  # Show first 5
                logger.info(f"  - {rec.category.value}: {rec.title}")
                logger.info(f"    Priority: {rec.priority.value}, Active: {rec.is_active}")
                logger.info(f"    Adherence Score: {rec.adherence_score}")
        
        # Check adherence records
        adherence_records = db.query(RecommendationAdherence).filter(
            RecommendationAdherence.user_id == user.id
        ).all()
        
        logger.info(f"\nFound {len(adherence_records)} adherence records")
        
        # Get adherence stats
        service = RecommendationService(db)
        stats = service.get_adherence_stats(str(user.id), days=30)
        
        logger.info("\nAdherence Statistics:")
        logger.info(f"  Total Records: {stats['total_records']}")
        logger.info(f"  Completed: {stats['completed']}")
        logger.info(f"  Adherence Rate: {stats['adherence_rate']:.1%}")
        logger.info(f"  Categories: {list(stats['by_category'].keys())}")
        
        # Test generating new recommendations
        logger.info("\nGenerating new recommendations...")
        
        risk_factors = {
            'cognitive_decline': 0.3,
            'cardiovascular_risk': 0.4,
            'diabetes_risk': 0.2
        }
        
        current_metrics = {
            'sleep_hours': 6.5,
            'physical_activity_minutes': 45,
            'glucose': 105,
            'sleep_quality': 6,
            'social_interactions_per_week': 2
        }
        
        new_recs = service.generate_recommendations(
            user_id=str(user.id),
            risk_factors=risk_factors,
            current_metrics=current_metrics
        )
        
        logger.info(f"\nGenerated {len(new_recs)} new recommendations:")
        for rec in new_recs:
            logger.info(f"  - {rec.category.value}: {rec.title}")
            logger.info(f"    Priority: {rec.priority.value}")
            logger.info(f"    Evidence: {rec.evidence_strength}")
            logger.info(f"    Citations: {len(rec.research_citations)}")
        
        logger.info("\n✓ Recommendations test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error testing recommendations: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    test_recommendations()
