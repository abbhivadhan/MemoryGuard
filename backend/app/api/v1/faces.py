"""
API endpoints for face recognition management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from uuid import UUID
import numpy as np

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.face_recognition import FaceProfile
from app.schemas.face_recognition import (
    FaceProfileCreate,
    FaceProfileUpdate,
    FaceProfileResponse,
    FaceProfileWithEmbedding,
    FaceRecognitionRequest,
    FaceRecognitionMatch,
    FaceRecognitionResponse,
    FaceProfileListResponse
)

router = APIRouter()


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two face embeddings.
    Returns a value between 0 and 1, where 1 is identical.
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    # Normalize to 0-1 range
    return (similarity + 1) / 2


@router.post("/", response_model=FaceProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_face_profile(
    profile_data: FaceProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new face profile for the current user.
    """
    profile = FaceProfile(
        user_id=current_user.id,
        name=profile_data.name,
        relationship=profile_data.relationship,
        notes=profile_data.notes,
        face_embedding=profile_data.face_embedding,
        photo_url=profile_data.photo_url
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/", response_model=FaceProfileListResponse)
async def get_face_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all face profiles for the current user.
    """
    profiles = db.query(FaceProfile).filter(
        FaceProfile.user_id == current_user.id
    ).order_by(FaceProfile.name.asc()).all()
    
    return FaceProfileListResponse(
        profiles=profiles,
        total=len(profiles)
    )


@router.get("/{profile_id}", response_model=FaceProfileResponse)
async def get_face_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific face profile by ID.
    """
    profile = db.query(FaceProfile).filter(
        and_(
            FaceProfile.id == profile_id,
            FaceProfile.user_id == current_user.id
        )
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Face profile not found"
        )
    
    return profile


@router.put("/{profile_id}", response_model=FaceProfileResponse)
async def update_face_profile(
    profile_id: UUID,
    profile_data: FaceProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a face profile.
    """
    profile = db.query(FaceProfile).filter(
        and_(
            FaceProfile.id == profile_id,
            FaceProfile.user_id == current_user.id
        )
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Face profile not found"
        )
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_face_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a face profile.
    """
    profile = db.query(FaceProfile).filter(
        and_(
            FaceProfile.id == profile_id,
            FaceProfile.user_id == current_user.id
        )
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Face profile not found"
        )
    
    db.delete(profile)
    db.commit()
    
    return None


@router.post("/recognize", response_model=FaceRecognitionResponse)
async def recognize_face(
    recognition_data: FaceRecognitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recognize a face by comparing the embedding against stored profiles.
    Returns matches sorted by similarity score.
    If the model is not confident enough, returns no match.
    """
    # Get all face profiles for the user
    profiles = db.query(FaceProfile).filter(
        FaceProfile.user_id == current_user.id
    ).all()
    
    if not profiles:
        return FaceRecognitionResponse(
            matches=[],
            best_match=None
        )
    
    # Calculate similarity for each profile
    matches = []
    # Set a minimum confidence threshold - only return matches with medium or high confidence
    MINIMUM_CONFIDENCE_THRESHOLD = 0.70  # 70% similarity minimum
    
    for profile in profiles:
        similarity = cosine_similarity(
            recognition_data.face_embedding,
            profile.face_embedding
        )
        
        # Only include matches above the minimum confidence threshold
        # This ensures we don't return uncertain matches
        if similarity >= MINIMUM_CONFIDENCE_THRESHOLD:
            # Determine confidence level
            if similarity >= 0.85:
                confidence = "high"
            elif similarity >= 0.70:
                confidence = "medium"
            else:
                confidence = "low"
            
            matches.append(
                FaceRecognitionMatch(
                    profile=profile,
                    similarity=round(similarity, 4),
                    confidence=confidence
                )
            )
    
    # Sort by similarity (highest first)
    matches.sort(key=lambda x: x.similarity, reverse=True)
    
    # Get best match - only if it meets the minimum confidence threshold
    best_match = matches[0] if matches else None
    
    return FaceRecognitionResponse(
        matches=matches,
        best_match=best_match
    )
