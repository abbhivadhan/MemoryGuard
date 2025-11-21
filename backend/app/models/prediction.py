"""
Prediction model for ML risk assessment results.
"""
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Index, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from datetime import datetime
import enum


class RiskCategory(str, enum.Enum):
    """Risk assessment categories"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class Prediction(BaseModel):
    """
    Prediction model for storing ML-based Alzheimer's risk assessment results.
    Includes SHAP values for interpretability and progression forecasts.
    
    Requirements: 3.3, 3.4, 4.1
    """
    __tablename__ = "predictions"
    
    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Risk assessment results
    risk_score = Column(Float, nullable=False)  # 0-1 scale
    risk_category = Column(SQLEnum(RiskCategory), nullable=False, index=True)
    
    # Confidence interval [lower, upper]
    confidence_interval_lower = Column(Float, nullable=False)
    confidence_interval_upper = Column(Float, nullable=False)
    
    # Feature importance (SHAP values) - stored as JSON
    # Format: {"feature_name": importance_value, ...}
    feature_importance = Column(JSON, nullable=False, default=dict)
    
    # Progression forecasts
    forecast_six_month = Column(Float, nullable=True)
    forecast_twelve_month = Column(Float, nullable=True)
    forecast_twenty_four_month = Column(Float, nullable=True)
    
    # Recommendations - array of strings
    recommendations = Column(ARRAY(String), nullable=False, default=list)
    
    # Model metadata
    model_version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # e.g., "ensemble", "random_forest"
    
    # Input features used for prediction (for reproducibility)
    input_features = Column(JSON, nullable=False, default=dict)
    
    # Timestamp of prediction
    prediction_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship to user
    user = relationship("User", backref="predictions")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_predictions_user_date', 'user_id', 'prediction_date'),
        Index('ix_predictions_user_risk', 'user_id', 'risk_category'),
    )
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, user_id={self.user_id}, risk_score={self.risk_score}, risk_category={self.risk_category})>"
    
    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "risk_score": self.risk_score,
            "risk_category": self.risk_category.value,
            "confidence_interval": [
                self.confidence_interval_lower,
                self.confidence_interval_upper
            ],
            "feature_importance": self.feature_importance,
            "progression_forecast": {
                "six_month": self.forecast_six_month,
                "twelve_month": self.forecast_twelve_month,
                "twenty_four_month": self.forecast_twenty_four_month
            },
            "recommendations": self.recommendations,
            "model_version": self.model_version,
            "model_type": self.model_type,
            "input_features": self.input_features,
            "prediction_date": self.prediction_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
