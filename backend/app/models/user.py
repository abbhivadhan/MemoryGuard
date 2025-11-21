"""
User model for authentication and user management.
"""
from sqlalchemy import Column, String, DateTime, ARRAY, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime
from typing import Optional
import enum


class APOEGenotype(str, enum.Enum):
    """APOE genotype options"""
    E2_E2 = "e2/e2"
    E2_E3 = "e2/e3"
    E2_E4 = "e2/e4"
    E3_E3 = "e3/e3"
    E3_E4 = "e3/e4"
    E4_E4 = "e4/e4"


class User(BaseModel):
    """
    User model representing application users.
    Stores authentication information and user profile data.
    """
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(String, unique=True, nullable=False, index=True)
    google_id = Column(String, unique=True, nullable=True, index=True)
    
    # Profile fields
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    
    # Genetic information
    apoe_genotype = Column(SQLEnum(APOEGenotype), nullable=True)
    
    # Relationships - stored as arrays of UUIDs
    emergency_contacts = Column(ARRAY(String), default=list, nullable=False)
    caregivers = Column(ARRAY(String), default=list, nullable=False)
    providers = Column(ARRAY(String), default=list, nullable=False)
    
    # Activity tracking
    last_active = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    exercise_performances = relationship("ExercisePerformance", back_populates="user")
    community_posts = relationship("CommunityPost", back_populates="user")
    community_replies = relationship("CommunityReply", back_populates="user")
    content_flags = relationship("ContentFlag", back_populates="reporter")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
    
    def to_dict(self):
        """Convert user to dictionary, excluding sensitive information"""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "apoe_genotype": self.apoe_genotype.value if self.apoe_genotype else None,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }
