"""
Provider and provider access models for healthcare provider portal.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime
import enum
import uuid


class ProviderType(str, enum.Enum):
    """Types of healthcare providers"""
    PHYSICIAN = "physician"
    NEUROLOGIST = "neurologist"
    PSYCHIATRIST = "psychiatrist"
    NURSE = "nurse"
    THERAPIST = "therapist"
    RESEARCHER = "researcher"
    OTHER = "other"


class AccessStatus(str, enum.Enum):
    """Status of provider access"""
    PENDING = "pending"
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class Provider(BaseModel):
    """
    Healthcare provider model.
    Represents medical professionals who can access patient data.
    """
    __tablename__ = "providers"
    
    # Authentication fields
    email = Column(String, unique=True, nullable=False, index=True)
    google_id = Column(String, unique=True, nullable=True, index=True)
    
    # Profile fields
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    provider_type = Column(SQLEnum(ProviderType), nullable=False)
    
    # Professional information
    license_number = Column(String, nullable=True)
    institution = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    
    # Account status
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Activity tracking
    last_active = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    patient_accesses = relationship("ProviderAccess", back_populates="provider")
    clinical_notes = relationship("ClinicalNote", back_populates="provider")
    
    def __repr__(self):
        return f"<Provider(id={self.id}, email={self.email}, name={self.name})>"
    
    def to_dict(self):
        """Convert provider to dictionary"""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "provider_type": self.provider_type.value if self.provider_type else None,
            "institution": self.institution,
            "specialty": self.specialty,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }


class ProviderAccess(BaseModel):
    """
    Provider access grants to patient data.
    Tracks which providers have access to which patients and audit trail.
    """
    __tablename__ = "provider_accesses"
    
    # Relationships
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False, index=True)
    
    # Access details
    status = Column(SQLEnum(AccessStatus), default=AccessStatus.PENDING, nullable=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Access scope
    can_view_assessments = Column(Boolean, default=True, nullable=False)
    can_view_health_metrics = Column(Boolean, default=True, nullable=False)
    can_view_medications = Column(Boolean, default=True, nullable=False)
    can_view_imaging = Column(Boolean, default=True, nullable=False)
    can_add_notes = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    granted_by_patient = Column(Boolean, default=True, nullable=False)
    access_reason = Column(Text, nullable=True)
    
    # Relationships
    provider = relationship("Provider", back_populates="patient_accesses")
    access_logs = relationship("ProviderAccessLog", back_populates="provider_access")
    
    def __repr__(self):
        return f"<ProviderAccess(patient_id={self.patient_id}, provider_id={self.provider_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert provider access to dictionary"""
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id),
            "provider_id": str(self.provider_id),
            "status": self.status.value,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "can_view_assessments": self.can_view_assessments,
            "can_view_health_metrics": self.can_view_health_metrics,
            "can_view_medications": self.can_view_medications,
            "can_view_imaging": self.can_view_imaging,
            "can_add_notes": self.can_add_notes,
            "access_reason": self.access_reason,
            "created_at": self.created_at.isoformat()
        }


class ProviderAccessLog(BaseModel):
    """
    Audit log for provider access to patient data.
    Tracks all provider actions for HIPAA compliance.
    """
    __tablename__ = "provider_access_logs"
    
    # Relationships
    provider_access_id = Column(UUID(as_uuid=True), ForeignKey("provider_accesses.id"), nullable=False, index=True)
    
    # Log details
    action = Column(String, nullable=False)  # e.g., "viewed_dashboard", "viewed_assessment", "added_note"
    resource_type = Column(String, nullable=True)  # e.g., "assessment", "health_metric", "medication"
    resource_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Additional context
    details = Column(Text, nullable=True)
    
    # Relationships
    provider_access = relationship("ProviderAccess", back_populates="access_logs")
    
    def __repr__(self):
        return f"<ProviderAccessLog(id={self.id}, action={self.action})>"
    
    def to_dict(self):
        """Convert access log to dictionary"""
        return {
            "id": str(self.id),
            "provider_access_id": str(self.provider_access_id),
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "details": self.details,
            "created_at": self.created_at.isoformat()
        }


class ClinicalNote(BaseModel):
    """
    Clinical notes added by healthcare providers.
    """
    __tablename__ = "clinical_notes"
    
    # Relationships
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False, index=True)
    
    # Note content
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String, nullable=True)  # e.g., "progress_note", "assessment", "treatment_plan"
    
    # Metadata
    is_private = Column(Boolean, default=False, nullable=False)  # If true, only provider can see
    
    # Relationships
    provider = relationship("Provider", back_populates="clinical_notes")
    
    def __repr__(self):
        return f"<ClinicalNote(id={self.id}, patient_id={self.patient_id}, title={self.title})>"
    
    def to_dict(self):
        """Convert clinical note to dictionary"""
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id),
            "provider_id": str(self.provider_id),
            "title": self.title,
            "content": self.content,
            "note_type": self.note_type,
            "is_private": self.is_private,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
