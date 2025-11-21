"""
Health Metric model for tracking various health indicators.
"""
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from datetime import datetime
import enum


class MetricType(str, enum.Enum):
    """Types of health metrics"""
    COGNITIVE = "cognitive"
    BIOMARKER = "biomarker"
    IMAGING = "imaging"
    LIFESTYLE = "lifestyle"
    CARDIOVASCULAR = "cardiovascular"


class MetricSource(str, enum.Enum):
    """Source of health metric data"""
    MANUAL = "manual"
    ASSESSMENT = "assessment"
    DEVICE = "device"
    LAB = "lab"


class HealthMetric(BaseModel):
    """
    Health metric model for tracking cognitive, biomarker, imaging, lifestyle,
    and cardiovascular health indicators.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
    """
    __tablename__ = "health_metrics"
    
    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Metric classification
    type = Column(SQLEnum(MetricType), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    
    # Metric value and unit
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    
    # Metadata
    source = Column(SQLEnum(MetricSource), nullable=False, default=MetricSource.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Notes or additional context
    notes = Column(String, nullable=True)
    
    # Relationship to user
    user = relationship("User", backref="health_metrics")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_health_metrics_user_type', 'user_id', 'type'),
        Index('ix_health_metrics_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_health_metrics_user_type_timestamp', 'user_id', 'type', 'timestamp'),
        Index('ix_health_metrics_user_name', 'user_id', 'name'),
    )
    
    def __repr__(self):
        return f"<HealthMetric(id={self.id}, user_id={self.user_id}, type={self.type}, name={self.name}, value={self.value})>"
    
    def to_dict(self):
        """Convert health metric to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "source": self.source.value,
            "timestamp": self.timestamp.isoformat(),
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
