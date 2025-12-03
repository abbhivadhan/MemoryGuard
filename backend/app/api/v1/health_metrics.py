"""
Health Metrics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from uuid import UUID

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.health_metric import HealthMetric
from app.core.logging_config import get_logger

router = APIRouter(tags=["health-metrics"])
logger = get_logger(__name__)


@router.get("/{user_id}")
async def get_health_metrics(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all health metrics for a user"""
    # Verify permission
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    metrics = db.query(HealthMetric).filter(
        HealthMetric.user_id == user_id
    ).order_by(HealthMetric.timestamp.desc()).all()
    
    return {
        "metrics": [
            {
                "id": str(m.id),
                "userId": str(m.user_id),
                "type": m.type,
                "name": m.name,
                "value": float(m.value),
                "unit": m.unit,
                "timestamp": m.timestamp.isoformat(),
                "source": m.source
            }
            for m in metrics
        ],
        "total": len(metrics)
    }


@router.get("/{user_id}/type/{metric_type}")
async def get_health_metrics_by_type(
    user_id: UUID,
    metric_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get health metrics by type for a user"""
    # Verify permission
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    metrics = db.query(HealthMetric).filter(
        HealthMetric.user_id == user_id,
        HealthMetric.type == metric_type
    ).order_by(HealthMetric.timestamp.desc()).all()
    
    return {
        "metrics": [
            {
                "id": str(m.id),
                "userId": str(m.user_id),
                "type": m.type,
                "name": m.name,
                "value": float(m.value),
                "unit": m.unit,
                "timestamp": m.timestamp.isoformat(),
                "source": m.source
            }
            for m in metrics
        ],
        "total": len(metrics)
    }


@router.post("")
async def add_health_metric(
    metric_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new health metric"""
    try:
        user_id = UUID(metric_data.get("userId", str(current_user.id)))
        
        # Verify permission
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Parse timestamp
        timestamp_str = metric_data["timestamp"].replace('Z', '+00:00')
        timestamp = datetime.fromisoformat(timestamp_str)
        
        metric = HealthMetric(
            user_id=user_id,
            type=metric_data["type"],
            name=metric_data["name"],
            value=float(metric_data["value"]),
            unit=metric_data["unit"],
            timestamp=timestamp,
            source=metric_data.get("source", "manual"),
            notes=metric_data.get("notes")
        )
        
        db.add(metric)
        db.commit()
        db.refresh(metric)
        
        logger.info(f"Added health metric: {metric.name} = {metric.value} {metric.unit} for user {user_id}")
        
        return {
            "id": str(metric.id),
            "userId": str(metric.user_id),
            "type": metric.type,
            "name": metric.name,
            "value": float(metric.value),
            "unit": metric.unit,
            "timestamp": metric.timestamp.isoformat(),
            "source": metric.source,
            "notes": metric.notes
        }
    except KeyError as e:
        logger.error(f"Missing required field: {e}")
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
    except ValueError as e:
        logger.error(f"Invalid value: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid value: {e}")
    except Exception as e:
        logger.error(f"Error adding health metric: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding health metric: {str(e)}")


@router.put("/{metric_id}")
async def update_health_metric(
    metric_id: UUID,
    metric_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a health metric"""
    metric = db.query(HealthMetric).filter(HealthMetric.id == metric_id).first()
    
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    # Verify permission
    if metric.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    for key, value in metric_data.items():
        if key == "value":
            setattr(metric, key, float(value))
        elif key not in ["id", "userId"]:
            setattr(metric, key, value)
    
    db.commit()
    db.refresh(metric)
    
    return {
        "id": str(metric.id),
        "userId": str(metric.user_id),
        "type": metric.type,
        "name": metric.name,
        "value": float(metric.value),
        "unit": metric.unit,
        "timestamp": metric.timestamp.isoformat(),
        "source": metric.source
    }


@router.delete("/{metric_id}")
async def delete_health_metric(
    metric_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a health metric"""
    metric = db.query(HealthMetric).filter(HealthMetric.id == metric_id).first()
    
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    # Verify permission
    if metric.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(metric)
    db.commit()
    
    return {"message": "Metric deleted successfully"}
