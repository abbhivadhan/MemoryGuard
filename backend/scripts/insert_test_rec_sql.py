#!/usr/bin/env python3
"""Insert test recommendation using raw SQL."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.user import User
import uuid
from datetime import datetime
import json

db = SessionLocal()

try:
    user = db.query(User).first()
    if not user:
        print("No user found")
        sys.exit(1)
    
    print(f"Adding recommendation for user: {user.email}")
    
    rec_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    citations = json.dumps([{
        "title": "Exercise and Brain Health",
        "authors": "Smith J, et al.",
        "journal": "Neurology",
        "year": 2020,
        "doi": "10.1001/test",
        "summary": "Regular exercise improves cognitive function"
    }])
    
    risk_factors = json.dumps({"sedentary": 0.3})
    target_metrics = json.dumps(["physical_activity", "cognitive_score"])
    
    sql = f"""
    INSERT INTO recommendations (
        id, user_id, category, priority, title, description,
        research_citations, evidence_strength, is_active, adherence_score,
        generated_from_risk_factors, target_metrics, generated_at, last_updated
    ) VALUES (
        '{rec_id}'::uuid,
        '{user.id}'::uuid,
        'exercise'::recommendationcategory,
        'high'::recommendationpriority,
        'Regular Physical Activity',
        'Engage in at least 30 minutes of moderate exercise daily to support brain health.',
        '{citations}'::json,
        'strong',
        true,
        NULL,
        '{risk_factors}'::json,
        '{target_metrics}'::json,
        '{now}'::timestamp,
        '{now}'::timestamp
    )
    """
    
    from sqlalchemy import text
    db.execute(text(sql))
    db.commit()
    
    print(f"✓ Added recommendation successfully")
    print(f"  ID: {rec_id}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
