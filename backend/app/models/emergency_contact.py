"""
Emergency Contact and relationship models.
"""
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from app.core.encryption import EncryptedString
import enum


class RelationshipType(str, enum.Enum):
    """Types of relationships"""
    FAMILY = "family"
    FRIEND = "friend"
    CAREGIVER = "caregiver"
    HEALTHCARE_PROVIDER = "healthcare_provider"
    OTHER = "other"


class EmergencyContact(BaseModel):
    """
    Emergency contact model for storing emergency contact information.
    
    Requirements: 14.3
    """
    __tablename__ = "emergency_contacts"
    
    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Contact information
    name = Column(EncryptedString(length=255), nullable=False)
    phone = Column(EncryptedString(length=255), nullable=False)
    email = Column(EncryptedString(length=255), nullable=True)
    
    # Relationship type
    relationship_type = Column(SQLEnum(RelationshipType), nullable=False)
    relationship_description = Column(EncryptedString(length=512), nullable=True)  # Additional details
    
    # Priority (1 = primary contact)
    priority = Column(String, nullable=False, default="1")
    
    # Status
    active = Column(Boolean, nullable=False, default=True)
    
    # Additional information
    address = Column(EncryptedString(length=512), nullable=True)
    notes = Column(EncryptedString(length=1024), nullable=True)
    
    # Relationship to user
    user = relationship("User", backref="emergency_contacts_list")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_emergency_contacts_user_active', 'user_id', 'active'),
        Index('ix_emergency_contacts_user_priority', 'user_id', 'priority'),
    )
    
    def __repr__(self):
        return (
            f"<EmergencyContact(id={self.id}, user_id={self.user_id}, "
            f"name={self.name}, relationship={self.relationship_type})>"
        )
    
    def to_dict(self):
        """Convert emergency contact to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "relationship": self.relationship_type.value,
            "relationship_description": self.relationship_description,
            "priority": self.priority,
            "active": self.active,
            "address": self.address,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class CaregiverRelationship(BaseModel):
    """
    Caregiver relationship model for managing caregiver access and permissions.
    
    Requirements: 6.1
    """
    __tablename__ = "caregiver_relationships"
    
    # Patient user ID
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Caregiver user ID
    caregiver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationship details
    relationship_type = Column(SQLEnum(RelationshipType), nullable=False)
    relationship_description = Column(String, nullable=True)
    
    # Permissions
    can_view_health_data = Column(Boolean, nullable=False, default=True)
    can_view_assessments = Column(Boolean, nullable=False, default=True)
    can_view_medications = Column(Boolean, nullable=False, default=True)
    can_manage_reminders = Column(Boolean, nullable=False, default=True)
    can_receive_alerts = Column(Boolean, nullable=False, default=True)
    
    # Status
    active = Column(Boolean, nullable=False, default=True, index=True)
    approved = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="caregivers_list")
    caregiver = relationship("User", foreign_keys=[caregiver_id], backref="patients_list")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_caregiver_relationships_patient_active', 'patient_id', 'active'),
        Index('ix_caregiver_relationships_caregiver_active', 'caregiver_id', 'active'),
        Index('ix_caregiver_relationships_unique', 'patient_id', 'caregiver_id', unique=True),
    )
    
    def __repr__(self):
        return f"<CaregiverRelationship(id={self.id}, patient_id={self.patient_id}, caregiver_id={self.caregiver_id})>"
    
    def to_dict(self):
        """Convert caregiver relationship to dictionary"""
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id),
            "caregiver_id": str(self.caregiver_id),
            "relationship_type": self.relationship_type.value,
            "relationship_description": self.relationship_description,
            "permissions": {
                "can_view_health_data": self.can_view_health_data,
                "can_view_assessments": self.can_view_assessments,
                "can_view_medications": self.can_view_medications,
                "can_manage_reminders": self.can_manage_reminders,
                "can_receive_alerts": self.can_receive_alerts
            },
            "active": self.active,
            "approved": self.approved,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class ProviderRelationship(BaseModel):
    """
    Healthcare provider relationship model for managing provider access.
    
    Requirements: 6.1
    """
    __tablename__ = "provider_relationships"
    
    # Patient user ID
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Provider user ID
    provider_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Provider details
    provider_type = Column(String, nullable=True)  # e.g., "neurologist", "primary care"
    specialty = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    
    # Permissions
    can_view_all_data = Column(Boolean, nullable=False, default=True)
    can_add_notes = Column(Boolean, nullable=False, default=True)
    can_view_predictions = Column(Boolean, nullable=False, default=True)
    
    # Status
    active = Column(Boolean, nullable=False, default=True, index=True)
    approved = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="providers_list")
    provider = relationship("User", foreign_keys=[provider_id], backref="provider_patients_list")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_provider_relationships_patient_active', 'patient_id', 'active'),
        Index('ix_provider_relationships_provider_active', 'provider_id', 'active'),
        Index('ix_provider_relationships_unique', 'patient_id', 'provider_id', unique=True),
    )
    
    def __repr__(self):
        return f"<ProviderRelationship(id={self.id}, patient_id={self.patient_id}, provider_id={self.provider_id})>"
    
    def to_dict(self):
        """Convert provider relationship to dictionary"""
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id),
            "provider_id": str(self.provider_id),
            "provider_type": self.provider_type,
            "specialty": self.specialty,
            "organization": self.organization,
            "permissions": {
                "can_view_all_data": self.can_view_all_data,
                "can_add_notes": self.can_add_notes,
                "can_view_predictions": self.can_view_predictions
            },
            "active": self.active,
            "approved": self.approved,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
