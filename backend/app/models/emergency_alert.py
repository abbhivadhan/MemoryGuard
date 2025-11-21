"""
Emergency Alert model for tracking emergency activations.
"""
from sqlalchemy import Column, String, Float, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class EmergencyAlert(BaseModel):
    """
    Emergency alert model for tracking SOS activations and emergency responses.
    
    Requirements: 14.1, 14.2, 14.3
    """
    __tablename__ = "emergency_alerts"
    
    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Location data
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_accuracy = Column(Float, nullable=True)
    location_address = Column(String, nullable=True)
    
    # Medical information snapshot
    medical_info = Column(JSON, nullable=True)
    
    # Alert status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    resolved_at = Column(String, nullable=True)
    resolution_notes = Column(String, nullable=True)
    
    # Notification tracking
    contacts_notified = Column(JSON, nullable=True)  # List of contact IDs notified
    notification_sent_at = Column(String, nullable=True)
    
    # Additional context
    trigger_type = Column(String, nullable=False, default="manual")  # manual, automatic
    notes = Column(String, nullable=True)
    
    # Relationship to user
    user = relationship("User", backref="emergency_alerts_list")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_emergency_alerts_user_active', 'user_id', 'is_active'),
        Index('ix_emergency_alerts_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<EmergencyAlert(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"
    
    def to_dict(self):
        """Convert emergency alert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "accuracy": self.location_accuracy,
                "address": self.location_address
            } if self.latitude and self.longitude else None,
            "medical_info": self.medical_info,
            "is_active": self.is_active,
            "resolved_at": self.resolved_at,
            "resolution_notes": self.resolution_notes,
            "contacts_notified": self.contacts_notified,
            "notification_sent_at": self.notification_sent_at,
            "trigger_type": self.trigger_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
