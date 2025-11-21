"""
Medication model for tracking medication schedules and adherence.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from datetime import datetime


class Medication(BaseModel):
    """
    Medication model for tracking medication schedules, adherence, and side effects.
    
    Requirements: 13.1, 13.3, 13.4
    """
    __tablename__ = "medications"
    
    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Medication details
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)  # e.g., "twice daily", "every 8 hours"
    
    # Schedule - array of datetime objects for scheduled doses
    schedule = Column(ARRAY(DateTime(timezone=True)), nullable=False, default=list)
    
    # Adherence log - stored as JSON array of log entries
    # Each entry: {"scheduled_time": ISO datetime, "taken_time": ISO datetime or null, "skipped": bool}
    adherence_log = Column(JSON, nullable=False, default=list)
    
    # Side effects - array of strings
    side_effects = Column(ARRAY(String), nullable=False, default=list)
    
    # Status
    active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Additional information
    instructions = Column(String, nullable=True)
    prescriber = Column(String, nullable=True)
    pharmacy = Column(String, nullable=True)
    
    # Start and end dates
    start_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship to user
    user = relationship("User", backref="medications")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_medications_user_active', 'user_id', 'active'),
        Index('ix_medications_user_start_date', 'user_id', 'start_date'),
    )
    
    def __repr__(self):
        return f"<Medication(id={self.id}, user_id={self.user_id}, name={self.name}, active={self.active})>"
    
    def calculate_adherence_rate(self, days: int = 7) -> float:
        """
        Calculate medication adherence rate for the last N days.
        Returns percentage (0-100).
        """
        if not self.adherence_log:
            return 0.0
        
        cutoff_time = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
        recent_logs = [
            log for log in self.adherence_log
            if datetime.fromisoformat(log.get("scheduled_time", "")).timestamp() >= cutoff_time
        ]
        
        if not recent_logs:
            return 0.0
        
        taken_count = sum(1 for log in recent_logs if not log.get("skipped", True))
        return (taken_count / len(recent_logs)) * 100
    
    def to_dict(self):
        """Convert medication to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "schedule": [dt.isoformat() for dt in self.schedule] if self.schedule else [],
            "adherence_log": self.adherence_log,
            "side_effects": self.side_effects,
            "active": self.active,
            "instructions": self.instructions,
            "prescriber": self.prescriber,
            "pharmacy": self.pharmacy,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
