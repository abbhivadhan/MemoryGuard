"""
Pydantic schemas for face recognition endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class FaceProfileCreate(BaseModel):
    """Schema for creating a face profile"""
    name: str = Field(..., min_length=1, max_length=255)
    relationship: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    face_embedding: list[float] = Field(..., min_length=128, max_length=512)
    photo_url: Optional[str] = None  # No max_length for base64 images


class FaceProfileUpdate(BaseModel):
    """Schema for updating a face profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    relationship: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    photo_url: Optional[str] = None  # No max_length for base64 images


class FaceProfileResponse(BaseModel):
    """Schema for face profile response (without embedding)"""
    id: UUID
    user_id: UUID
    name: str
    relationship: Optional[str]
    notes: Optional[str]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FaceProfileWithEmbedding(FaceProfileResponse):
    """Schema for face profile with embedding"""
    face_embedding: list[float]


class FaceRecognitionRequest(BaseModel):
    """Schema for face recognition request"""
    face_embedding: list[float] = Field(..., min_length=128, max_length=512)
    threshold: float = Field(default=0.6, ge=0.0, le=1.0)


class FaceRecognitionMatch(BaseModel):
    """Schema for face recognition match result"""
    profile: FaceProfileResponse
    similarity: float
    confidence: str  # "high", "medium", "low"


class FaceRecognitionResponse(BaseModel):
    """Schema for face recognition response"""
    matches: list[FaceRecognitionMatch]
    best_match: Optional[FaceRecognitionMatch]


class FaceProfileListResponse(BaseModel):
    """Schema for list of face profiles"""
    profiles: list[FaceProfileResponse]
    total: int
