#!/usr/bin/env python3
"""Quick script to add a single test recommendation."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.recommendation import Recommendation, RecommendationCategory, RecommendationPriority
import uuid
from datetime import datetime

db = SessionLocal()

try:
    user = db.query(User).first()
    if not user:
        print("No user found")
        sys.exit(1)
    
    print(f"Adding recommendation for user: {user.email}")
    
    # Create a simple recommendation
    rec = Recommendation()
    rec.id = uuid.uuid4()
    rec.user_id = user.id
    rec.category = RecommendationCategory.EXERCISE
    rec.priority = RecommendationPriority.HIGH
    rec.title = "Regular Physical Activity"
    rec.description = "Engage in at least 30 minutes of moderate exercise daily to support brain health."
    rec.research_citations = [{
        "title": "Exercise and Brain Health",
        "authors": "Smith J, et al.",
        "journal": "Neurology",
        "year": 2020,
        "doi": "10.1001/test",
        "summary": "Regular exercise improves cognitive function"
    }]
    rec.evidence_strength = "strong"
    rec.is_active = True
    rec.adherence_score = None
    rec.generated_from_risk_factors = {"sedentary": 0.3}
    rec.target_metrics = ["physical_activity", "cognitive_score"]
    rec.generated_at = datetime.utcnow()
    rec.last_updated = datetime.utcnow()
    
    db.add(rec)
    db.commit()
    
    print(f"✓ Added recommendation: {rec.title}")
    print(f"  ID: {rec.id}")
    print(f"  Category: {rec.category.value}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
