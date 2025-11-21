"""
API endpoints for cognitive assessments.
Requirements: 12.4
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime
import uuid

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.assessment import Assessment, AssessmentType, AssessmentStatus
from app.schemas.assessment import (
    AssessmentStartRequest,
    AssessmentResponseUpdate,
    AssessmentCompleteRequest,
    AssessmentResponse,
    AssessmentListResponse
)
from app.services.assessment_service import AssessmentScoringService

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/start", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def start_assessment(
    request: AssessmentStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new cognitive assessment.
    
    Requirements: 12.4
    """
    # Get max score for assessment type
    max_score = AssessmentScoringService.get_max_score(request.type.value)
    
    # Create new assessment
    assessment = Assessment(
        id=uuid.uuid4(),
        user_id=current_user.id,
        type=AssessmentType[request.type.value],
        status=AssessmentStatus.IN_PROGRESS,
        max_score=max_score,
        responses={},
        started_at=datetime.utcnow()
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return assessment.to_dict()


@router.put("/{assessment_id}/response", response_model=AssessmentResponse)
async def update_assessment_response(
    assessment_id: str,
    request: AssessmentResponseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update assessment responses.
    
    Requirements: 12.4
    """
    # Get assessment
    try:
        assessment_uuid = uuid.UUID(assessment_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment ID format"
        )
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_uuid,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if assessment.status != AssessmentStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update completed or abandoned assessment"
        )
    
    # Update responses (merge with existing)
    current_responses = assessment.responses or {}
    current_responses.update(request.responses)
    assessment.responses = current_responses
    assessment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(assessment)
    
    return assessment.to_dict()


@router.post("/{assessment_id}/complete", response_model=AssessmentResponse)
async def complete_assessment(
    assessment_id: str,
    request: AssessmentCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete an assessment and calculate score.
    
    Requirements: 12.3, 12.4
    """
    # Get assessment
    try:
        assessment_uuid = uuid.UUID(assessment_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment ID format"
        )
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_uuid,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if assessment.status != AssessmentStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment is not in progress"
        )
    
    # Calculate score
    score = AssessmentScoringService.score_assessment(
        assessment.type.value,
        assessment.responses
    )
    
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to calculate score. Please ensure all required responses are provided."
        )
    
    # Update assessment
    assessment.status = AssessmentStatus.COMPLETED
    assessment.score = score
    assessment.completed_at = datetime.utcnow()
    assessment.updated_at = datetime.utcnow()
    
    if request.duration:
        assessment.duration = request.duration
    
    if request.notes:
        assessment.notes = request.notes
    
    db.commit()
    db.refresh(assessment)
    
    return assessment.to_dict()


@router.get("/{user_id}", response_model=AssessmentListResponse)
async def get_user_assessments(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all assessments for a user.
    
    Requirements: 12.4, 12.7
    """
    # Verify user can access this data (must be own data or caregiver)
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    if str(current_user.id) != user_id:
        # TODO: Add caregiver permission check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's assessments"
        )
    
    # Get assessments ordered by completion date (most recent first)
    assessments = db.query(Assessment).filter(
        Assessment.user_id == user_uuid
    ).order_by(desc(Assessment.completed_at), desc(Assessment.started_at)).all()
    
    return {
        "assessments": [assessment.to_dict() for assessment in assessments],
        "total": len(assessments)
    }


@router.get("/{user_id}/latest/{assessment_type}", response_model=AssessmentResponse)
async def get_latest_assessment(
    user_id: str,
    assessment_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the latest assessment of a specific type for a user.
    
    Requirements: 12.4
    """
    # Verify user can access this data
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's assessments"
        )
    
    # Validate assessment type
    try:
        assessment_type_enum = AssessmentType[assessment_type]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid assessment type: {assessment_type}"
        )
    
    # Get latest completed assessment
    assessment = db.query(Assessment).filter(
        Assessment.user_id == user_uuid,
        Assessment.type == assessment_type_enum,
        Assessment.status == AssessmentStatus.COMPLETED
    ).order_by(desc(Assessment.completed_at)).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No completed {assessment_type} assessment found"
        )
    
    return assessment.to_dict()
