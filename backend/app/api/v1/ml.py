"""
ML prediction API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.health_metric import HealthMetric
from app.schemas.ml import (
    PredictionRequest,
    PredictionResponse,
    PredictionListResponse,
    ExplanationResponse,
    ForecastRequest,
    ForecastResponse
)
from app.services.ml_service import MLService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new Alzheimer's disease risk prediction.
    
    This endpoint processes health metrics and generates a prediction using
    the ensemble ML model. The prediction is processed asynchronously.
    """
    try:
        ml_service = MLService(db)
        
        # Get user's health metrics
        user_id = request.user_id if request.user_id else current_user.id
        
        # Verify user has permission
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to create predictions for other users"
            )
        
        # Queue prediction task
        prediction = await ml_service.create_prediction_async(
            user_id=user_id,
            health_metrics=request.health_metrics,
            background_tasks=background_tasks
        )
        
        return PredictionResponse(
            id=prediction.id,
            user_id=prediction.user_id,
            status='processing',
            created_at=prediction.created_at,
            message="Prediction is being processed"
        )
        
    except ValueError as e:
        logger.error(f"Validation error in prediction: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create prediction")


@router.get("/predictions/{user_id}", response_model=PredictionListResponse)
async def get_user_predictions(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all predictions for a specific user.
    
    Returns a paginated list of predictions ordered by creation date.
    """
    # Verify user has permission
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view predictions for other users"
        )
    
    try:
        ml_service = MLService(db)
        predictions = ml_service.get_user_predictions(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        total = ml_service.count_user_predictions(user_id)
        
        return PredictionListResponse(
            predictions=[
                PredictionResponse(
                    id=p.id,
                    user_id=p.user_id,
                    prediction=p.prediction,
                    probability=p.probability,
                    confidence_score=p.confidence_score,
                    risk_level=p.risk_level,
                    status=p.status,
                    created_at=p.created_at,
                    completed_at=p.completed_at
                )
                for p in predictions
            ],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching predictions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch predictions")


@router.get("/predictions/{prediction_id}/detail", response_model=PredictionResponse)
async def get_prediction_detail(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific prediction.
    """
    try:
        ml_service = MLService(db)
        prediction = ml_service.get_prediction_by_id(prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Verify user has permission
        if prediction.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this prediction"
            )
        
        return PredictionResponse(
            id=prediction.id,
            user_id=prediction.user_id,
            prediction=prediction.prediction,
            probability=prediction.probability,
            confidence_score=prediction.confidence_score,
            confidence_interval_lower=prediction.confidence_interval_lower,
            confidence_interval_upper=prediction.confidence_interval_upper,
            risk_level=prediction.risk_level,
            model_version=prediction.model_version,
            status=prediction.status,
            created_at=prediction.created_at,
            completed_at=prediction.completed_at,
            metadata=prediction.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prediction detail: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch prediction")


@router.get("/explain/{prediction_id}", response_model=ExplanationResponse)
async def explain_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get SHAP-based explanation for a prediction.
    
    Returns feature importance and contribution analysis.
    """
    try:
        ml_service = MLService(db)
        prediction = ml_service.get_prediction_by_id(prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Verify user has permission
        if prediction.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this explanation"
            )
        
        # Generate explanation
        explanation = ml_service.generate_explanation(prediction_id)
        
        return ExplanationResponse(
            prediction_id=prediction_id,
            top_features=explanation['top_features'],
            positive_contributors=explanation['positive_contributors'],
            negative_contributors=explanation['negative_contributors'],
            explanation_text=explanation['explanation_text'],
            shap_values=explanation.get('shap_values', {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate explanation")


@router.post("/forecast", response_model=ForecastResponse)
async def create_forecast(
    request: ForecastRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate disease progression forecast.
    
    Creates forecasts for 6, 12, and 24 months based on current and historical data.
    """
    try:
        ml_service = MLService(db)
        
        # Verify user has permission
        user_id = request.user_id if request.user_id else current_user.id
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to create forecasts for other users"
            )
        
        # Generate forecast
        forecast = ml_service.generate_forecast(
            user_id=user_id,
            current_metrics=request.current_metrics,
            forecast_months=request.forecast_months or [6, 12, 24]
        )
        
        return ForecastResponse(
            user_id=user_id,
            forecasts=forecast['forecasts'],
            progression_rates=forecast['progression_rates'],
            confidence_level=forecast['confidence_level'],
            generated_at=datetime.utcnow()
        )
        
    except ValueError as e:
        logger.error(f"Validation error in forecast: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating forecast: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create forecast")


@router.get("/model/info")
async def get_model_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the ML models.
    
    Returns model versions, architecture details, and performance metrics.
    """
    try:
        ml_service = MLService(db)
        model_info = ml_service.get_model_info()
        
        return {
            'model_version': model_info.get('version', '1.0.0'),
            'ensemble_info': model_info.get('ensemble_info', {}),
            'last_trained': model_info.get('last_trained'),
            'performance_metrics': model_info.get('performance_metrics', {})
        }
        
    except Exception as e:
        logger.error(f"Error fetching model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch model info")


@router.get("/health")
async def ml_health_check():
    """
    Health check endpoint for ML service.
    """
    try:
        # Check if models are loaded
        ml_service = MLService(None)
        status = ml_service.check_health()
        
        return {
            'status': 'healthy' if status else 'unhealthy',
            'models_loaded': status,
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"ML health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow()
        }
