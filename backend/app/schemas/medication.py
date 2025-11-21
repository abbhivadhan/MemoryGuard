"""
Pydantic schemas for medication endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class MedicationCreate(BaseModel):
    """Schema for creating a new medication"""
    name: str = Field(..., min_length=1, max_length=255)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=100)
    schedule: List[datetime] = Field(default_factory=list)
    instructions: Optional[str] = None
    prescriber: Optional[str] = None
    pharmacy: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class MedicationUpdate(BaseModel):
    """Schema for updating a medication"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    dosage: Optional[str] = Field(None, min_length=1, max_length=100)
    frequency: Optional[str] = Field(None, min_length=1, max_length=100)
    schedule: Optional[List[datetime]] = None
    instructions: Optional[str] = None
    prescriber: Optional[str] = None
    pharmacy: Optional[str] = None
    active: Optional[bool] = None
    end_date: Optional[datetime] = None


class AdherenceLogEntry(BaseModel):
    """Schema for a single adherence log entry"""
    scheduled_time: datetime
    taken_time: Optional[datetime] = None
    skipped: bool = False
    notes: Optional[str] = None


class MedicationLogRequest(BaseModel):
    """Schema for logging medication taken/skipped"""
    scheduled_time: datetime
    taken_time: Optional[datetime] = None
    skipped: bool = False
    notes: Optional[str] = None


class SideEffectCreate(BaseModel):
    """Schema for adding a side effect"""
    side_effect: str = Field(..., min_length=1, max_length=500)
    severity: Optional[str] = Field(None, pattern="^(mild|moderate|severe)$")
    occurred_at: Optional[datetime] = None


class AdherenceStats(BaseModel):
    """Schema for adherence statistics"""
    medication_id: UUID
    medication_name: str
    total_scheduled: int
    total_taken: int
    total_skipped: int
    adherence_rate: float
    period_days: int
    last_taken: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None


class MedicationResponse(BaseModel):
    """Schema for medication response"""
    id: UUID
    user_id: UUID
    name: str
    dosage: str
    frequency: str
    schedule: List[str]
    adherence_log: List[dict]
    side_effects: List[str]
    active: bool
    instructions: Optional[str]
    prescriber: Optional[str]
    pharmacy: Optional[str]
    start_date: str
    end_date: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class MedicationListResponse(BaseModel):
    """Schema for list of medications"""
    medications: List[MedicationResponse]
    total: int


class InteractionWarning(BaseModel):
    """Schema for drug interaction warning"""
    severity: str
    description: str
    medications: List[str]
    recommendation: str
