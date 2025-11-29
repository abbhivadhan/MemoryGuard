"""
Pydantic schemas for ML prediction endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request schema for creating a prediction."""
    user_id: Optional[str] = None  # UUID as string
    health_metrics: Optional[Dict[str, float]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "00000000-0000-0000-0000-000000000001",
                "health_metrics": {
                    "mmse_score": 24,
                    "age": 72,
                    "csf_abeta42": 450
                }
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for prediction."""
    id: str  # UUID as string
    user_id: str  # UUID as string
    risk_score: float
    risk_category: str
    confidence_interval_lower: float
    confidence_interval_upper: float
    feature_importance: Dict[str, float]
    forecast_six_month: Optional[float] = None
    forecast_twelve_month: Optional[float] = None
    forecast_twenty_four_month: Optional[float] = None
    recommendations: List[str]
    model_version: str
    model_type: str
    input_features: Dict[str, Any]
    prediction_date: datetime
    created_at: datetime
    updated_at: datetime
    
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
    prediction_id: str  # UUID as string
    top_features: List[Dict[str, Any]]
    positive_contributors: List[Dict[str, float]]
    negative_contributors: List[Dict[str, float]]
    explanation_text: str
    shap_values: Optional[Dict[str, float]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "00000000-0000-0000-0000-000000000001",
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
    user_id: Optional[str] = None  # UUID as string
    current_metrics: Dict[str, float]
    forecast_months: Optional[List[int]] = Field(default=[6, 12, 24])
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "00000000-0000-0000-0000-000000000001",
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
    user_id: str  # UUID as string
    forecasts: Dict[str, Any]
    progression_rates: Dict[str, float]
    confidence_level: float
    generated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "00000000-0000-0000-0000-000000000001",
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
