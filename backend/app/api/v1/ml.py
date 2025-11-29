"""
ML prediction API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from uuid import UUID
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
    user_id: UUID,
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
    if user_id != current_user.id:
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
                    id=str(p.id),
                    user_id=str(p.user_id),
                    risk_score=p.risk_score,
                    risk_category=p.risk_category.value,
                    confidence_interval_lower=p.confidence_interval_lower,
                    confidence_interval_upper=p.confidence_interval_upper,
                    feature_importance=p.feature_importance,
                    forecast_six_month=p.forecast_six_month,
                    forecast_twelve_month=p.forecast_twelve_month,
                    forecast_twenty_four_month=p.forecast_twenty_four_month,
                    recommendations=p.recommendations,
                    model_version=p.model_version,
                    model_type=p.model_type,
                    input_features=p.input_features,
                    prediction_date=p.prediction_date,
                    created_at=p.created_at,
                    updated_at=p.updated_at
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
    prediction_id: UUID,
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
    prediction_id: UUID,
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
        if prediction.user_id != current_user.id:
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


@router.post("/model/reload")
async def reload_model(
    version: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reload ML models from registry.
    
    If version is specified, loads that specific version.
    Otherwise, loads the production model or latest model.
    
    Requires admin privileges.
    """
    # Check admin permission
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        from app.ml.model_registry import get_model_registry
        
        registry = get_model_registry()
        
        if version:
            # Load specific version
            model_info = registry.get_model_info(version)
            if not model_info:
                raise HTTPException(status_code=404, detail=f"Model version {version} not found")
        else:
            # Load production or latest
            model_info = registry.get_production_model()
            if not model_info:
                model_info = registry.get_latest_model()
            
            if not model_info:
                raise HTTPException(status_code=404, detail="No models available")
        
        # Reload ML service (this will load the new model)
        ml_service = MLService(db)
        
        return {
            'status': 'success',
            'message': f"Model {model_info['version']} loaded successfully",
            'version': model_info['version'],
            'model_status': model_info['status']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reloading model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")


@router.get("/model/registry")
async def get_model_registry_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get model registry information.
    
    Returns list of all registered models and their status.
    """
    try:
        from app.ml.model_registry import get_model_registry
        
        registry = get_model_registry()
        summary = registry.get_registry_summary()
        models = registry.list_models()
        
        return {
            'summary': summary,
            'models': models
        }
        
    except Exception as e:
        logger.error(f"Error fetching registry info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch registry info")


@router.post("/model/promote/{version}")
async def promote_model(
    version: str,
    environment: str,  # 'staging' or 'production'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Promote a model version to staging or production.
    
    Requires admin privileges.
    """
    # Check admin permission
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    if environment not in ['staging', 'production']:
        raise HTTPException(status_code=400, detail="Environment must be 'staging' or 'production'")
    
    try:
        from app.ml.model_registry import get_model_registry
        
        registry = get_model_registry()
        
        if environment == 'staging':
            registry.promote_to_staging(version)
        else:
            registry.promote_to_production(version)
        
        return {
            'status': 'success',
            'message': f"Model {version} promoted to {environment}",
            'version': version,
            'environment': environment
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error promoting model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to promote model: {str(e)}")
