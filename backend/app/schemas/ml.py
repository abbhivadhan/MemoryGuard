"""
Pydantic schemas for ML prediction endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request schema for creating a prediction."""
    user_id: Optional[int] = None
    health_metrics: Optional[Dict[str, float]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "health_metrics": {
                    "mmse_score": 24,
                    "age": 72,
                    "csf_abeta42": 450
                }
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for prediction."""
    id: int
    user_id: int
    prediction: Optional[int] = None
    probability: Optional[float] = None
    confidence_score: Optional[float] = None
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    risk_level: Optional[str] = None
    model_version: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    
    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    """Response schema for list of predictions."""
    predictions: List[PredictionResponse]
    total: int
    skip: int
    limit: int


class ExplanationResponse(BaseModel):
    """Response schema for prediction explanation."""
    prediction_id: int
    top_features: List[Dict[str, Any]]
    positive_contributors: List[Dict[str, float]]
    negative_contributors: List[Dict[str, float]]
    explanation_text: str
    shap_values: Optional[Dict[str, float]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": 1,
                "top_features": [
                    {"feature": "mmse_score", "shap_value": -0.15}
                ],
                "positive_contributors": [
                    {"feature": "age", "contribution": 0.12}
                ],
                "negative_contributors": [
                    {"feature": "education_years", "contribution": 0.08}
                ],
                "explanation_text": "The model predicts high risk..."
            }
        }


class ForecastRequest(BaseModel):
    """Request schema for progression forecast."""
    user_id: Optional[int] = None
    current_metrics: Dict[str, float]
    forecast_months: Optional[List[int]] = Field(default=[6, 12, 24])
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "current_metrics": {
                    "mmse_score": 24,
                    "moca_score": 22,
                    "age": 72
                },
                "forecast_months": [6, 12, 24]
            }
        }


class ForecastResponse(BaseModel):
    """Response schema for progression forecast."""
    user_id: int
    forecasts: Dict[str, Any]
    progression_rates: Dict[str, float]
    confidence_level: float
    generated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "forecasts": {
                    "6_months": {
                        "metrics": {"mmse_score": 23.5},
                        "risk_score": 0.65
                    }
                },
                "progression_rates": {
                    "mmse_score": -2.5
                },
                "confidence_level": 0.75,
                "generated_at": "2024-01-01T00:00:00"
            }
        }
