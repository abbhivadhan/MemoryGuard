"""
Quick setup script to initialize the system with demo data.

This creates:
1. Database tables (runs migrations)
2. A demo user
3. Sample health metrics
4. Synthetic training data for ML models
5. Trains basic ML models

Usage:
    python scripts/setup_demo_system.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.health_metric import HealthMetric
from app.models.assessment import Assessment
from datetime import datetime, timedelta
import random
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations."""
    logger.info("Running database migrations...")
    os.system("cd backend && alembic upgrade head")
    logger.info("✓ Migrations complete")


def create_demo_user(db: Session) -> User:
    """Create a demo user for testing."""
    logger.info("Creating demo user...")
    
    # Check if user exists
    user = db.query(User).filter(User.email == "demo@memoryguard.com").first()
    if user:
        logger.info("✓ Demo user already exists")
        return user
    
    user = User(
        id="demo-user-123",
        email="demo@memoryguard.com",
        full_name="Demo User",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"✓ Created demo user: {user.email}")
    return user


def create_sample_health_metrics(db: Session, user_id: str):
    """Create sample health metrics for the demo user."""
    logger.info("Creating sample health metrics...")
    
    # Check if metrics exist
    existing = db.query(HealthMetric).filter(HealthMetric.user_id == user_id).count()
    if existing > 0:
        logger.info(f"✓ {existing} health metrics already exist")
        return
    
    # Create metrics for the past 6 months
    base_date = datetime.utcnow() - timedelta(days=180)
    
    metrics = []
    for i in range(30):  # 30 data points over 6 months
        date = base_date + timedelta(days=i * 6)
        
        metric = HealthMetric(
            user_id=user_id,
            metric_type="cognitive_score",
            value=random.uniform(20, 28),  # MMSE-like score
            unit="points",
            recorded_at=date,
            source="manual_entry"
        )
        metrics.append(metric)
        
        # Add some biomarker data
        if i % 5 == 0:
            metrics.append(HealthMetric(
                user_id=user_id,
                metric_type="amyloid_beta",
                value=random.uniform(400, 800),
                unit="pg/mL",
                recorded_at=date,
                source="lab_test"
            ))
            
            metrics.append(HealthMetric(
                user_id=user_id,
                metric_type="tau_protein",
                value=random.uniform(200, 500),
                unit="pg/mL",
                recorded_at=date,
                source="lab_test"
            ))
    
    db.bulk_save_objects(metrics)
    db.commit()
    
    logger.info(f"✓ Created {len(metrics)} sample health metrics")


def create_sample_assessments(db: Session, user_id: str):
    """Create sample cognitive assessments."""
    logger.info("Creating sample assessments...")
    
    existing = db.query(Assessment).filter(Assessment.user_id == user_id).count()
    if existing > 0:
        logger.info(f"✓ {existing} assessments already exist")
        return
    
    base_date = datetime.utcnow() - timedelta(days=90)
    
    assessments = []
    for i in range(3):
        date = base_date + timedelta(days=i * 30)
        
        assessment = Assessment(
            user_id=user_id,
            assessment_type="MMSE",
            score=random.randint(22, 28),
            max_score=30,
            completed_at=date,
            notes="Demo assessment"
        )
        assessments.append(assessment)
    
    db.bulk_save_objects(assessments)
    db.commit()
    
    logger.info(f"✓ Created {len(assessments)} sample assessments")


def generate_synthetic_training_data():
    """Generate synthetic data for ML model training."""
    logger.info("Generating synthetic training data...")
    
    output_dir = Path("backend/data/training")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 1000 synthetic samples
    n_samples = 1000
    
    # Features
    data = {
        'age': np.random.normal(70, 10, n_samples),
        'education_years': np.random.normal(14, 3, n_samples),
        'mmse_score': np.random.normal(24, 4, n_samples),
        'amyloid_beta': np.random.normal(600, 150, n_samples),
        'tau_protein': np.random.normal(350, 100, n_samples),
        'hippocampal_volume': np.random.normal(3500, 500, n_samples),
        'apoe4_status': np.random.choice([0, 1, 2], n_samples),
    }
    
    # Generate diagnosis based on features (simplified logic)
    diagnosis = []
    for i in range(n_samples):
        risk_score = (
            (data['age'][i] - 70) * 0.02 +
            (25 - data['mmse_score'][i]) * 0.1 +
            (data['amyloid_beta'][i] - 600) * 0.0005 +
            data['apoe4_status'][i] * 0.3 +
            np.random.normal(0, 0.2)
        )
        diagnosis.append(1 if risk_score > 0.5 else 0)
    
    data['diagnosis'] = diagnosis
    
    import pandas as pd
    df = pd.DataFrame(data)
    
    output_file = output_dir / "synthetic_alzheimer_data.csv"
    df.to_csv(output_file, index=False)
    
    logger.info(f"✓ Generated {n_samples} synthetic samples")
    logger.info(f"✓ Saved to {output_file}")
    logger.info(f"  - Positive cases: {sum(diagnosis)}")
    logger.info(f"  - Negative cases: {n_samples - sum(diagnosis)}")


def train_ml_models():
    """Train ML models with synthetic data."""
    logger.info("Training ML models...")
    logger.info("Note: This uses synthetic data for demonstration only")
    
    try:
        # Run the training script
        result = os.system("cd backend && python scripts/train_models.py --data-path data/training/synthetic_alzheimer_data.csv")
        if result == 0:
            logger.info("✓ ML models trained successfully")
        else:
            logger.warning("⚠ ML model training had issues (this is normal for demo)")
    except Exception as e:
        logger.warning(f"⚠ Could not train models: {e}")
        logger.info("  You can train models later with: python scripts/train_models.py")


def main():
    """Run the complete setup."""
    logger.info("=" * 60)
    logger.info("MemoryGuard Demo System Setup")
    logger.info("=" * 60)
    
    try:
        # 1. Run migrations
        run_migrations()
        
        # 2. Create demo user and data
        db = SessionLocal()
        try:
            user = create_demo_user(db)
            create_sample_health_metrics(db, user.id)
            create_sample_assessments(db, user.id)
        finally:
            db.close()
        
        # 3. Generate training data
        generate_synthetic_training_data()
        
        # 4. Train models (optional)
        logger.info("\nWould you like to train ML models now? (This may take a few minutes)")
        logger.info("You can skip this and train later with: python scripts/train_models.py")
        response = input("Train models now? (y/n): ").lower()
        if response == 'y':
            train_ml_models()
        else:
            logger.info("⊘ Skipping ML model training")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Setup Complete!")
        logger.info("=" * 60)
        logger.info("\nDemo User Credentials:")
        logger.info("  Email: demo@memoryguard.com")
        logger.info("  User ID: demo-user-123")
        logger.info("\nNext Steps:")
        logger.info("  1. Start the backend: uvicorn app.main:app --reload")
        logger.info("  2. Start the frontend: npm run dev")
        logger.info("  3. Login with the demo user")
        logger.info("\nNote: This system uses SYNTHETIC data for demonstration.")
        logger.info("Real medical data requires proper authorization and HIPAA compliance.")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise


if __name__ == "__main__":
    main()
