"""
Assessment model for cognitive test results.
"""
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from datetime import datetime
import enum


class AssessmentType(str, enum.Enum):
    """Types of cognitive assessments"""
    MMSE = "MMSE"
    MOCA = "MoCA"
    CDR = "CDR"
    CLOCK_DRAWING = "ClockDrawing"


class AssessmentStatus(str, enum.Enum):
    """Status of assessment"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Assessment(BaseModel):
    """
    Assessment model for storing cognitive test results.
    Supports MMSE, MoCA, CDR, and Clock Drawing tests.
    
    Requirements: 12.1, 12.4
    """
    __tablename__ = "assessments"
    
    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Assessment details
    type = Column(SQLEnum(AssessmentType), nullable=False, index=True)
    status = Column(SQLEnum(AssessmentStatus), nullable=False, default=AssessmentStatus.IN_PROGRESS)
    
    # Scoring
    score = Column(Integer, nullable=True)  # Null until completed
    max_score = Column(Integer, nullable=False)
    
    # Test responses stored as JSON
    responses = Column(JSON, nullable=False, default=dict)
    
    # Timing information
    duration = Column(Integer, nullable=True)  # Duration in seconds
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Additional notes
    notes = Column(String, nullable=True)
    
    # Relationship to user
    user = relationship("User", backref="assessments")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_assessments_user_type', 'user_id', 'type'),
        Index('ix_assessments_user_completed', 'user_id', 'completed_at'),
        Index('ix_assessments_user_type_completed', 'user_id', 'type', 'completed_at'),
    )
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, user_id={self.user_id}, type={self.type}, score={self.score}/{self.max_score})>"
    
    def to_dict(self):
        """Convert assessment to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "status": self.status.value,
            "score": self.score,
            "max_score": self.max_score,
            "responses": self.responses,
            "duration": self.duration,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
