"""
Pydantic schemas for cognitive assessment endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class AssessmentTypeEnum(str, Enum):
    """Types of cognitive assessments"""
    MMSE = "MMSE"
    MoCA = "MoCA"
    CDR = "CDR"
    ClockDrawing = "ClockDrawing"


class AssessmentStatusEnum(str, Enum):
    """Status of assessment"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AssessmentStartRequest(BaseModel):
    """Request schema for starting a new assessment."""
    type: AssessmentTypeEnum
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "MMSE"
            }
        }


class AssessmentResponseUpdate(BaseModel):
    """Request schema for updating assessment responses."""
    responses: Dict[str, Any] = Field(..., description="Assessment responses as key-value pairs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "responses": {
                    "orientation_year": "2024",
                    "orientation_season": "winter",
                    "orientation_date": "15"
                }
            }
        }


class AssessmentCompleteRequest(BaseModel):
    """Request schema for completing an assessment."""
    duration: Optional[int] = Field(None, description="Duration in seconds")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "duration": 600,
                "notes": "Patient completed all sections"
            }
        }


class AssessmentResponse(BaseModel):
    """Response schema for assessment."""
    id: str
    user_id: str
    type: str
    status: str
    score: Optional[int] = None
    max_score: int
    responses: Dict[str, Any]
    duration: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "type": "MMSE",
                "status": "completed",
                "score": 28,
                "max_score": 30,
                "responses": {},
                "duration": 600,
                "started_at": "2024-01-01T10:00:00Z",
                "completed_at": "2024-01-01T10:10:00Z",
                "notes": None,
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:10:00Z"
            }
        }


class AssessmentListResponse(BaseModel):
    """Response schema for list of assessments."""
    assessments: List[AssessmentResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "assessments": [],
                "total": 0
            }
        }
