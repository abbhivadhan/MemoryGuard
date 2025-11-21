"""
Pydantic schemas for provider portal.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProviderType(str, Enum):
    """Types of healthcare providers"""
    PHYSICIAN = "physician"
    NEUROLOGIST = "neurologist"
    PSYCHIATRIST = "psychiatrist"
    NURSE = "nurse"
    THERAPIST = "therapist"
    RESEARCHER = "researcher"
    OTHER = "other"


class AccessStatus(str, Enum):
    """Status of provider access"""
    PENDING = "pending"
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


# Provider Schemas
class ProviderBase(BaseModel):
    """Base provider schema"""
    email: EmailStr
    name: str
    provider_type: ProviderType
    license_number: Optional[str] = None
    institution: Optional[str] = None
    specialty: Optional[str] = None


class ProviderCreate(ProviderBase):
    """Schema for creating a provider"""
    google_id: Optional[str] = None


class ProviderUpdate(BaseModel):
    """Schema for updating a provider"""
    name: Optional[str] = None
    provider_type: Optional[ProviderType] = None
    license_number: Optional[str] = None
    institution: Optional[str] = None
    specialty: Optional[str] = None
    is_active: Optional[bool] = None


class ProviderResponse(ProviderBase):
    """Schema for provider response"""
    id: str
    picture: Optional[str] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True


# Provider Access Schemas
class ProviderAccessBase(BaseModel):
    """Base provider access schema"""
    can_view_assessments: bool = True
    can_view_health_metrics: bool = True
    can_view_medications: bool = True
    can_view_imaging: bool = True
    can_add_notes: bool = True
    access_reason: Optional[str] = None


class ProviderAccessGrant(ProviderAccessBase):
    """Schema for granting provider access"""
    provider_email: EmailStr
    expires_at: Optional[datetime] = None


class ProviderAccessUpdate(BaseModel):
    """Schema for updating provider access"""
    status: Optional[AccessStatus] = None
    can_view_assessments: Optional[bool] = None
    can_view_health_metrics: Optional[bool] = None
    can_view_medications: Optional[bool] = None
    can_view_imaging: Optional[bool] = None
    can_add_notes: Optional[bool] = None
    expires_at: Optional[datetime] = None


class ProviderAccessResponse(ProviderAccessBase):
    """Schema for provider access response"""
    id: str
    patient_id: str
    provider_id: str
    status: AccessStatus
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProviderAccessWithProvider(ProviderAccessResponse):
    """Schema for provider access with provider details"""
    provider: ProviderResponse


# Access Log Schemas
class ProviderAccessLogCreate(BaseModel):
    """Schema for creating an access log"""
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None


class ProviderAccessLogResponse(BaseModel):
    """Schema for access log response"""
    id: str
    provider_access_id: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Clinical Note Schemas
class ClinicalNoteBase(BaseModel):
    """Base clinical note schema"""
    title: str
    content: str
    note_type: Optional[str] = None
    is_private: bool = False


class ClinicalNoteCreate(ClinicalNoteBase):
    """Schema for creating a clinical note"""
    patient_id: str


class ClinicalNoteUpdate(BaseModel):
    """Schema for updating a clinical note"""
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[str] = None
    is_private: Optional[bool] = None


class ClinicalNoteResponse(ClinicalNoteBase):
    """Schema for clinical note response"""
    id: str
    patient_id: str
    provider_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClinicalNoteWithProvider(ClinicalNoteResponse):
    """Schema for clinical note with provider details"""
    provider: ProviderResponse


# Patient Data Schemas for Provider Portal
class PatientSummary(BaseModel):
    """Summary of patient data for provider dashboard"""
    id: str
    name: str
    email: str
    date_of_birth: Optional[datetime] = None
    apoe_genotype: Optional[str] = None
    last_active: datetime


class PatientHealthOverview(BaseModel):
    """Overview of patient health metrics"""
    latest_mmse_score: Optional[float] = None
    latest_moca_score: Optional[float] = None
    latest_risk_score: Optional[float] = None
    medication_adherence_rate: Optional[float] = None
    last_assessment_date: Optional[datetime] = None
    last_prediction_date: Optional[datetime] = None


class PatientDashboardData(BaseModel):
    """Complete patient data for provider dashboard"""
    patient: PatientSummary
    health_overview: PatientHealthOverview
    recent_assessments: List[dict] = []
    recent_health_metrics: List[dict] = []
    active_medications: List[dict] = []
    recent_predictions: List[dict] = []
    clinical_notes: List[ClinicalNoteResponse] = []
