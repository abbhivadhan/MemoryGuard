"""
Recommendation model for personalized health recommendations.
"""
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Index, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from datetime import datetime
import enum


class RecommendationCategory(str, enum.Enum):
    """Recommendation categories"""
    DIET = "diet"
    EXERCISE = "exercise"
    SLEEP = "sleep"
    COGNITIVE = "cognitive"
    SOCIAL = "social"


class RecommendationPriority(str, enum.Enum):
    """Recommendation priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Recommendation(BaseModel):
    """
    Recommendation model for storing personalized health recommendations.
    
    Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
    """
    __tablename__ = "recommendations"
    
    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Recommendation details
    category = Column(SQLEnum(RecommendationCategory), nullable=False, index=True)
    priority = Column(SQLEnum(RecommendationPriority), nullable=False, default=RecommendationPriority.MEDIUM)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Scientific evidence
    research_citations = Column(JSON, nullable=False, default=list)  # List of citation objects
    evidence_strength = Column(String, nullable=True)  # e.g., "strong", "moderate", "limited"
    
    # Tracking
    is_active = Column(Boolean, nullable=False, default=True)
    adherence_score = Column(Float, nullable=True)  # 0-1 scale
    
    # Metadata
    generated_from_risk_factors = Column(JSON, nullable=False, default=dict)
    target_metrics = Column(JSON, nullable=False, default=list)  # Metrics this aims to improve
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", backref="recommendations")
    
    # Composite indexes
    __table_args__ = (
        Index('ix_recommendations_user_category', 'user_id', 'category'),
        Index('ix_recommendations_user_active', 'user_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, user_id={self.user_id}, category={self.category}, title={self.title})>"
    
    def to_dict(self):
        """Convert recommendation to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "category": self.category.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "research_citations": self.research_citations,
            "evidence_strength": self.evidence_strength,
            "is_active": self.is_active,
            "adherence_score": self.adherence_score,
            "generated_from_risk_factors": self.generated_from_risk_factors,
            "target_metrics": self.target_metrics,
            "generated_at": self.generated_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class RecommendationAdherence(BaseModel):
    """
    Model for tracking user adherence to recommendations.
    
    Requirements: 15.4
    """
    __tablename__ = "recommendation_adherence"
    
    # Foreign keys
    recommendation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Adherence tracking
    date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    completed = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    
    # Outcome tracking
    outcome_metrics = Column(JSON, nullable=True)  # Metrics measured after adherence
    
    # Relationships
    recommendation = relationship("Recommendation", backref="adherence_records")
    user = relationship("User", backref="recommendation_adherence")
    
    # Composite indexes
    __table_args__ = (
        Index('ix_adherence_recommendation_date', 'recommendation_id', 'date'),
        Index('ix_adherence_user_date', 'user_id', 'date'),
    )
    
    def __repr__(self):
        return f"<RecommendationAdherence(id={self.id}, recommendation_id={self.recommendation_id}, completed={self.completed})>"
    
    def to_dict(self):
        """Convert adherence record to dictionary"""
        return {
            "id": str(self.id),
            "recommendation_id": str(self.recommendation_id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat(),
            "completed": self.completed,
            "notes": self.notes,
            "outcome_metrics": self.outcome_metrics,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
