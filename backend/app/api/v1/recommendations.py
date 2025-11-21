"""
API endpoints for personalized recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.recommendation import RecommendationCategory
from app.services.recommendation_service import RecommendationService

router = APIRouter()


# Pydantic schemas
class RecommendationResponse(BaseModel):
    """Response model for recommendation"""
    id: str
    user_id: str
    category: str
    priority: str
    title: str
    description: str
    research_citations: List[dict]
    evidence_strength: Optional[str]
    is_active: bool
    adherence_score: Optional[float]
    generated_from_risk_factors: dict
    target_metrics: List[str]
    generated_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True


class GenerateRecommendationsRequest(BaseModel):
    """Request to generate recommendations"""
    risk_factors: dict = Field(..., description="Risk factors from ML prediction")
    current_metrics: dict = Field(..., description="Current health metrics")


class TrackAdherenceRequest(BaseModel):
    """Request to track adherence"""
    recommendation_id: str
    completed: bool
    notes: Optional[str] = None
    outcome_metrics: Optional[dict] = None


class AdherenceResponse(BaseModel):
    """Response for adherence tracking"""
    id: str
    recommendation_id: str
    user_id: str
    date: datetime
    completed: bool
    notes: Optional[str]
    outcome_metrics: Optional[dict]
    
    class Config:
        from_attributes = True



@router.post("/generate", response_model=List[RecommendationResponse])
async def generate_recommendations(
    request: GenerateRecommendationsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized recommendations based on risk factors.
    
    Requirements: 15.1, 15.2, 15.3
    """
    service = RecommendationService(db)
    
    recommendations = service.generate_recommendations(
        user_id=str(current_user.id),
        risk_factors=request.risk_factors,
        current_metrics=request.current_metrics
    )
    
    return [RecommendationResponse(**rec.to_dict()) for rec in recommendations]


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    category: Optional[str] = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recommendations for the current user.
    
    Requirements: 15.1, 15.2
    """
    service = RecommendationService(db)
    
    category_enum = None
    if category:
        try:
            category_enum = RecommendationCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}"
            )
    
    recommendations = service.get_user_recommendations(
        user_id=str(current_user.id),
        category=category_enum,
        active_only=active_only
    )
    
    return [RecommendationResponse(**rec.to_dict()) for rec in recommendations]


@router.post("/adherence", response_model=AdherenceResponse)
async def track_adherence(
    request: TrackAdherenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track adherence to a recommendation.
    
    Requirements: 15.4
    """
    service = RecommendationService(db)
    
    adherence = service.track_adherence(
        recommendation_id=request.recommendation_id,
        user_id=str(current_user.id),
        completed=request.completed,
        notes=request.notes,
        outcome_metrics=request.outcome_metrics
    )
    
    return AdherenceResponse(**adherence.to_dict())


@router.get("/adherence/stats")
async def get_adherence_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get adherence statistics for the current user.
    
    Requirements: 15.4
    """
    service = RecommendationService(db)
    
    stats = service.get_adherence_stats(
        user_id=str(current_user.id),
        days=days
    )
    
    return stats


@router.post("/update", response_model=List[RecommendationResponse])
async def update_recommendations(
    new_metrics: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update recommendations based on new health metrics.
    
    Requirements: 15.5
    """
    service = RecommendationService(db)
    
    recommendations = service.update_recommendations_based_on_progress(
        user_id=str(current_user.id),
        new_metrics=new_metrics
    )
    
    return [RecommendationResponse(**rec.to_dict()) for rec in recommendations]
