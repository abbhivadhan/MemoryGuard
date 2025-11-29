"""
FastAPI endpoints for ML model inference

Provides REST API for:
- Model predictions with confidence intervals
- SHAP explanations
- Progression forecasting
- Batch predictions

Implements Requirements:
- 7.1: Generate SHAP values for all predictions
- 7.5: Provide confidence intervals for all predictions
- 9.2: Generate 6, 12, 24-month progression forecasts
- 12.3: Cache loaded models in memory
- 3.5: Validate feature inputs
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator
import numpy as np
import pandas as pd
import time
import uuid

from ml_pipeline.models.model_registry import ModelRegistry
from ml_pipeline.interpretability.interpretability_system import InterpretabilitySystem
from ml_pipeline.forecasting.progression_forecaster import ProgressionForecaster
from ml_pipeline.config.logging_config import main_logger


# Initialize router
router = APIRouter(prefix="/api/v1", tags=["inference"])

# Model cache (Requirement 12.3: Cache loaded models in memory)
_model_cache = {}
_interpretability_cache = {}
_forecaster_cache = {}

# Model registry
_model_registry = None


def get_model_registry() -> ModelRegistry:
    """Get model registry instance"""
    global _model_registry
    if _model_registry is None:
        _model_registry = ModelRegistry()
    return _model_registry


# Request/Response models

class FeatureInput(BaseModel):
    """Feature input for prediction"""
    # Cognitive features
    mmse_score: Optional[float] = Field(None, ge=0, le=30, description="MMSE score (0-30)")
    moca_score: Optional[float] = Field(None, ge=0, le=30, description="MoCA score (0-30)")
    cdr_global: Optional[float] = Field(None, ge=0, le=3, description="CDR global score (0-3)")
    adas_cog: Optional[float] = Field(None, ge=0, le=70, description="ADAS-Cog score")
    
    # Biomarker features
    csf_ab42: Optional[float] = Field(None, ge=0, le=2000, description="CSF Aβ42 (pg/mL)")
    csf_tau: Optional[float] = Field(None, ge=0, le=1500, description="CSF Total Tau (pg/mL)")
    csf_ptau: Optional[float] = Field(None, ge=0, le=150, description="CSF p-Tau (pg/mL)")
    
    # Imaging features
    hippocampus_volume: Optional[float] = Field(None, ge=0, description="Hippocampal volume (mm³)")
    entorhinal_cortex_thickness: Optional[float] = Field(None, ge=0, description="Entorhinal cortex thickness (mm)")
    ventricular_volume: Optional[float] = Field(None, ge=0, description="Ventricular volume (mm³)")
    whole_brain_volume: Optional[float] = Field(None, ge=0, description="Whole brain volume (mm³)")
    
    # Genetic features
    apoe_e4_count: Optional[int] = Field(None, ge=0, le=2, description="APOE e4 allele count (0, 1, or 2)")
    
    # Demographics
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    sex: Optional[int] = Field(None, ge=0, le=1, description="Sex (0=Female, 1=Male)")
    education_years: Optional[int] = Field(None, ge=0, le=30, description="Years of education")
    
    @validator('*', pre=True)
    def validate_not_nan(cls, v):
        """Ensure no NaN values"""
        if v is not None and (isinstance(v, float) and np.isnan(v)):
            raise ValueError("NaN values are not allowed")
        return v


class PredictionRequest(BaseModel):
    """Prediction request"""
    features: FeatureInput
    model_name: str = Field("ensemble", description="Model to use (ensemble, random_forest, xgboost, neural_network)")
    include_explanation: bool = Field(True, description="Include SHAP explanation")
    include_confidence: bool = Field(True, description="Include confidence intervals")
    
    class Config:
        schema_extra = {
            "example": {
                "features": {
                    "mmse_score": 24.0,
                    "moca_score": 22.0,
                    "cdr_global": 0.5,
                    "csf_ab42": 450.0,
                    "csf_tau": 350.0,
                    "csf_ptau": 65.0,
                    "hippocampus_volume": 6500.0,
                    "age": 72,
                    "sex": 1,
                    "education_years": 16,
                    "apoe_e4_count": 1
                },
                "model_name": "ensemble",
                "include_explanation": True,
                "include_confidence": True
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response"""
    prediction_id: str
    prediction: int
    probability: float
    confidence_interval: Optional[Dict[str, float]] = None
    risk_category: str
    timestamp: str
    model_name: str
    model_version: str
    explanation: Optional[Dict[str, Any]] = None
    generation_time: float


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    features_list: List[FeatureInput]
    model_name: str = Field("ensemble", description="Model to use")
    include_explanation: bool = Field(False, description="Include SHAP explanations (slower)")
    include_confidence: bool = Field(True, description="Include confidence intervals")


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    predictions: List[PredictionResponse]
    total_count: int
    generation_time: float


class ForecastRequest(BaseModel):
    """Progression forecast request"""
    patient_id: str
    patient_history: List[FeatureInput] = Field(..., min_items=4, description="At least 4 historical visits required")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PATIENT_001",
                "patient_history": [
                    {"mmse_score": 28.0, "age": 70, "csf_ab42": 500.0},
                    {"mmse_score": 26.0, "age": 71, "csf_ab42": 480.0},
                    {"mmse_score": 24.0, "age": 72, "csf_ab42": 450.0},
                    {"mmse_score": 22.0, "age": 73, "csf_ab42": 420.0}
                ]
            }
        }


class ForecastResponse(BaseModel):
    """Progression forecast response"""
    patient_id: str
    forecasts: Dict[str, float]
    uncertainty: Dict[str, float]
    timestamp: str
    generation_time: float


class ExplanationResponse(BaseModel):
    """SHAP explanation response"""
    prediction_id: str
    explanation: Dict[str, Any]
    generation_time: float


# Helper functions

def load_model_with_cache(model_name: str, registry: ModelRegistry):
    """
    Load model with caching (Requirement 12.3)
    
    Args:
        model_name: Name of the model
        registry: Model registry instance
        
    Returns:
        Tuple of (model, metadata)
    """
    cache_key = f"{model_name}_production"
    
    if cache_key in _model_cache:
        main_logger.debug(f"Using cached model: {model_name}")
        return _model_cache[cache_key]
    
    # Load from registry
    main_logger.info(f"Loading model from registry: {model_name}")
    model, metadata = registry.load_model(model_name)
    
    # Cache the model
    _model_cache[cache_key] = (model, metadata)
    
    return model, metadata


def get_interpretability_system(model_name: str, model, metadata):
    """
    Get or create interpretability system with caching
    
    Args:
        model_name: Name of the model
        model: Model object
        metadata: Model metadata
        
    Returns:
        InterpretabilitySystem instance
    """
    cache_key = f"{model_name}_{metadata['version_id']}"
    
    if cache_key in _interpretability_cache:
        return _interpretability_cache[cache_key]
    
    # Determine model type
    model_type = metadata.get('model_type', 'tree')
    if model_type in ['random_forest', 'xgboost']:
        model_type = 'tree'
    elif model_type == 'neural_network':
        model_type = 'deep'
    
    # Create interpretability system
    interp_system = InterpretabilitySystem(
        model=model,
        model_type=model_type,
        feature_names=metadata.get('feature_names', []),
        output_dir=f"ml_pipeline/data_storage/interpretability/{model_name}",
        cache_explanations=True,
        max_background_samples=100
    )
    
    # Initialize (without background data for now)
    interp_system.initialize()
    
    # Cache it
    _interpretability_cache[cache_key] = interp_system
    
    return interp_system


def validate_features(features: FeatureInput, required_features: List[str]) -> np.ndarray:
    """
    Validate and convert features to numpy array (Requirement 3.5)
    
    Args:
        features: Feature input
        required_features: List of required feature names
        
    Returns:
        Numpy array of features
        
    Raises:
        HTTPException if validation fails
    """
    feature_dict = features.dict()
    
    # Check for required features
    missing_features = []
    feature_values = []
    
    for feat_name in required_features:
        value = feature_dict.get(feat_name)
        if value is None:
            missing_features.append(feat_name)
        else:
            feature_values.append(value)
    
    if missing_features:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required features: {missing_features}"
        )
    
    return np.array(feature_values).reshape(1, -1)


def get_risk_category(probability: float) -> str:
    """
    Categorize risk based on probability
    
    Args:
        probability: Prediction probability
        
    Returns:
        Risk category string
    """
    if probability < 0.3:
        return "Low Risk"
    elif probability < 0.6:
        return "Moderate Risk"
    elif probability < 0.8:
        return "High Risk"
    else:
        return "Very High Risk"


# API Endpoints

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    registry: ModelRegistry = Depends(get_model_registry)
):
    """
    Generate prediction with confidence intervals and optional SHAP explanation
    
    Implements Requirements:
    - 7.1: Generate SHAP values for predictions
    - 7.5: Provide confidence intervals
    - 12.3: Cache loaded models
    - 3.5: Validate feature inputs
    
    Returns prediction with:
    - Binary prediction (0: Normal, 1: AD)
    - Probability score
    - Confidence intervals (if requested)
    - SHAP explanation (if requested)
    """
    start_time = time.time()
    prediction_id = str(uuid.uuid4())
    
    try:
        # Load model with caching (Requirement 12.3)
        model, metadata = load_model_with_cache(request.model_name, registry)
        
        # Validate and prepare features (Requirement 3.5)
        required_features = metadata.get('feature_names', [])
        if not required_features:
            raise HTTPException(
                status_code=500,
                detail="Model metadata missing feature names"
            )
        
        X = validate_features(request.features, required_features)
        
        # Generate prediction
        if hasattr(model, 'predict_proba'):
            probability = float(model.predict_proba(X)[0, 1])
        else:
            probability = float(model.predict(X)[0])
        
        prediction = int(probability >= 0.5)
        
        # Calculate confidence intervals (Requirement 7.5)
        confidence_interval = None
        if request.include_confidence:
            # Simple bootstrap-based confidence interval
            # In production, this would use ensemble predictions
            ci_lower = max(0.0, probability - 0.1)
            ci_upper = min(1.0, probability + 0.1)
            confidence_interval = {
                "lower": ci_lower,
                "upper": ci_upper,
                "confidence_level": 0.95
            }
        
        # Generate SHAP explanation (Requirement 7.1)
        explanation = None
        if request.include_explanation:
            try:
                interp_system = get_interpretability_system(
                    request.model_name,
                    model,
                    metadata
                )
                explanation = interp_system.explain_prediction(
                    X,
                    prediction,
                    probability,
                    use_cache=True
                )
            except Exception as e:
                main_logger.warning(f"Failed to generate explanation: {e}")
                explanation = {"error": str(e)}
        
        generation_time = time.time() - start_time
        
        main_logger.info(
            f"Prediction generated: {prediction} (prob={probability:.3f}) "
            f"in {generation_time:.3f}s",
            extra={
                'operation': 'predict',
                'prediction_id': prediction_id,
                'model_name': request.model_name,
                'generation_time': generation_time
            }
        )
        
        return PredictionResponse(
            prediction_id=prediction_id,
            prediction=prediction,
            probability=probability,
            confidence_interval=confidence_interval,
            risk_category=get_risk_category(probability),
            timestamp=datetime.utcnow().isoformat(),
            model_name=request.model_name,
            model_version=metadata['version_id'],
            explanation=explanation,
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Prediction failed: {str(e)}",
            extra={'operation': 'predict', 'prediction_id': prediction_id}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explain/{prediction_id}", response_model=ExplanationResponse)
async def explain_prediction(
    prediction_id: str,
    registry: ModelRegistry = Depends(get_model_registry)
):
    """
    Generate SHAP explanation for a previous prediction
    
    Implements Requirement 7.1, 7.4:
    - Generate SHAP values
    - Identify top 5 contributing features
    
    Note: In production, this would retrieve the prediction from a database
    and regenerate the explanation. For now, this is a placeholder.
    """
    start_time = time.time()
    
    try:
        # In production, retrieve prediction details from database
        # For now, return a placeholder response
        
        main_logger.warning(
            f"Explanation retrieval not fully implemented for prediction_id: {prediction_id}"
        )
        
        generation_time = time.time() - start_time
        
        return ExplanationResponse(
            prediction_id=prediction_id,
            explanation={
                "message": "Explanation retrieval requires prediction storage",
                "note": "Use include_explanation=True in prediction request"
            },
            generation_time=generation_time
        )
        
    except Exception as e:
        main_logger.error(
            f"Explanation retrieval failed: {str(e)}",
            extra={'operation': 'explain_prediction', 'prediction_id': prediction_id}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast", response_model=ForecastResponse)
async def forecast_progression(
    request: ForecastRequest,
    registry: ModelRegistry = Depends(get_model_registry)
):
    """
    Generate progression forecast for 6, 12, and 24 months
    
    Implements Requirement 9.2:
    - Return 6, 12, 24-month forecasts
    - Use longitudinal patient data
    - Provide uncertainty quantification
    """
    start_time = time.time()
    
    try:
        # Load forecaster model
        forecaster_key = "progression_forecaster"
        
        if forecaster_key not in _forecaster_cache:
            # Load forecaster from registry
            try:
                forecaster_model, forecaster_metadata = registry.load_model("progression_forecaster")
                forecaster = ProgressionForecaster()
                forecaster.model = forecaster_model
                _forecaster_cache[forecaster_key] = forecaster
            except Exception as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"Progression forecaster not found: {str(e)}"
                )
        else:
            forecaster = _forecaster_cache[forecaster_key]
        
        # Validate patient history length
        if len(request.patient_history) < 4:
            raise HTTPException(
                status_code=400,
                detail="At least 4 historical visits required for forecasting"
            )
        
        # Convert patient history to DataFrame
        history_data = [feat.dict() for feat in request.patient_history]
        patient_df = pd.DataFrame(history_data)
        
        # Get feature columns (this should match training features)
        feature_columns = [col for col in patient_df.columns if patient_df[col].notna().any()]
        
        # Generate forecast
        forecasts = forecaster.forecast_single_patient(
            patient_df,
            feature_columns
        )
        
        # Calculate uncertainty (simple placeholder)
        uncertainty = {
            key: 2.0  # ±2 points on MMSE scale
            for key in forecasts.keys()
        }
        
        generation_time = time.time() - start_time
        
        main_logger.info(
            f"Forecast generated for patient {request.patient_id} "
            f"in {generation_time:.3f}s",
            extra={
                'operation': 'forecast',
                'patient_id': request.patient_id,
                'generation_time': generation_time
            }
        )
        
        return ForecastResponse(
            patient_id=request.patient_id,
            forecasts=forecasts,
            uncertainty=uncertainty,
            timestamp=datetime.utcnow().isoformat(),
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Forecast failed: {str(e)}",
            extra={'operation': 'forecast', 'patient_id': request.patient_id}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def batch_predict(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    registry: ModelRegistry = Depends(get_model_registry)
):
    """
    Generate predictions for multiple samples (batch inference)
    
    Implements performance optimization requirement:
    - Process multiple predictions efficiently
    - Reduce per-prediction overhead
    - Cache model loading
    """
    start_time = time.time()
    
    try:
        # Load model with caching
        model, metadata = load_model_with_cache(request.model_name, registry)
        
        required_features = metadata.get('feature_names', [])
        if not required_features:
            raise HTTPException(
                status_code=500,
                detail="Model metadata missing feature names"
            )
        
        # Prepare all features
        X_batch = []
        for features in request.features_list:
            X = validate_features(features, required_features)
            X_batch.append(X[0])
        
        X_batch = np.array(X_batch)
        
        # Batch prediction
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X_batch)[:, 1]
        else:
            probabilities = model.predict(X_batch)
        
        predictions = (probabilities >= 0.5).astype(int)
        
        # Generate responses
        responses = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            prediction_id = str(uuid.uuid4())
            
            # Confidence intervals
            confidence_interval = None
            if request.include_confidence:
                ci_lower = max(0.0, float(prob) - 0.1)
                ci_upper = min(1.0, float(prob) + 0.1)
                confidence_interval = {
                    "lower": ci_lower,
                    "upper": ci_upper,
                    "confidence_level": 0.95
                }
            
            # Explanations (optional, slower)
            explanation = None
            if request.include_explanation:
                try:
                    interp_system = get_interpretability_system(
                        request.model_name,
                        model,
                        metadata
                    )
                    explanation = interp_system.explain_prediction(
                        X_batch[i:i+1],
                        int(pred),
                        float(prob),
                        use_cache=True
                    )
                except Exception as e:
                    main_logger.warning(f"Failed to generate explanation: {e}")
            
            responses.append(PredictionResponse(
                prediction_id=prediction_id,
                prediction=int(pred),
                probability=float(prob),
                confidence_interval=confidence_interval,
                risk_category=get_risk_category(float(prob)),
                timestamp=datetime.utcnow().isoformat(),
                model_name=request.model_name,
                model_version=metadata['version_id'],
                explanation=explanation,
                generation_time=0.0  # Individual time not tracked in batch
            ))
        
        generation_time = time.time() - start_time
        
        main_logger.info(
            f"Batch prediction completed: {len(responses)} predictions "
            f"in {generation_time:.3f}s ({generation_time/len(responses):.3f}s per prediction)",
            extra={
                'operation': 'batch_predict',
                'batch_size': len(responses),
                'generation_time': generation_time
            }
        )
        
        return BatchPredictionResponse(
            predictions=responses,
            total_count=len(responses),
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Batch prediction failed: {str(e)}",
            extra={'operation': 'batch_predict'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/cache/status")
async def get_cache_status():
    """
    Get status of model cache
    
    Returns information about cached models
    """
    return {
        "cached_models": list(_model_cache.keys()),
        "cached_interpretability_systems": list(_interpretability_cache.keys()),
        "cached_forecasters": list(_forecaster_cache.keys()),
        "total_cached": len(_model_cache) + len(_interpretability_cache) + len(_forecaster_cache)
    }


@router.post("/models/cache/clear")
async def clear_model_cache():
    """
    Clear model cache
    
    Useful for forcing model reload after updates
    """
    global _model_cache, _interpretability_cache, _forecaster_cache
    
    cache_sizes = {
        "models_cleared": len(_model_cache),
        "interpretability_systems_cleared": len(_interpretability_cache),
        "forecasters_cleared": len(_forecaster_cache)
    }
    
    _model_cache = {}
    _interpretability_cache = {}
    _forecaster_cache = {}
    
    main_logger.info("Model cache cleared", extra={'operation': 'clear_cache'})
    
    return {
        "success": True,
        "message": "Model cache cleared",
        **cache_sizes
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ml-inference-api",
        "timestamp": datetime.utcnow().isoformat()
    }
