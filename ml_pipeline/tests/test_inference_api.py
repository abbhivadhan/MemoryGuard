"""
Tests for Inference API

Tests the API endpoints for predictions, explanations, and forecasting.
"""
import pytest
from fastapi.testclient import TestClient
import numpy as np

# Note: These are basic structure tests. Full integration tests would require
# trained models in the model registry.


def test_api_imports():
    """Test that API modules can be imported"""
    try:
        from ml_pipeline.api.main import app
        from ml_pipeline.api.inference_api import router
        from ml_pipeline.api.feature_api import router as feature_router
        assert app is not None
        assert router is not None
        assert feature_router is not None
    except ImportError as e:
        pytest.fail(f"Failed to import API modules: {e}")


def test_api_structure():
    """Test that the API has the expected structure"""
    from ml_pipeline.api.main import app
    
    # Check that app is a FastAPI instance
    assert hasattr(app, 'routes')
    assert hasattr(app, 'router')
    
    # Get all route paths
    routes = [route.path for route in app.routes]
    
    # Check for expected endpoints
    expected_endpoints = [
        '/',
        '/health',
        '/api/v1/predict',
        '/api/v1/predict/batch',
        '/api/v1/forecast',
        '/api/v1/explain/{prediction_id}',
        '/api/v1/models/cache/status',
        '/api/v1/models/cache/clear'
    ]
    
    for endpoint in expected_endpoints:
        assert any(endpoint in route for route in routes), f"Missing endpoint: {endpoint}"


def test_request_models():
    """Test that request models are properly defined"""
    from ml_pipeline.api.inference_api import (
        FeatureInput,
        PredictionRequest,
        BatchPredictionRequest,
        ForecastRequest
    )
    
    # Test FeatureInput validation
    features = FeatureInput(
        mmse_score=24.0,
        age=72,
        csf_ab42=450.0
    )
    assert features.mmse_score == 24.0
    assert features.age == 72
    
    # Test PredictionRequest
    request = PredictionRequest(
        features=features,
        model_name="ensemble",
        include_explanation=True
    )
    assert request.model_name == "ensemble"
    assert request.include_explanation is True
    
    # Test BatchPredictionRequest
    batch_request = BatchPredictionRequest(
        features_list=[features, features],
        model_name="ensemble"
    )
    assert len(batch_request.features_list) == 2
    
    # Test ForecastRequest
    forecast_request = ForecastRequest(
        patient_id="TEST_001",
        patient_history=[features, features, features, features]
    )
    assert forecast_request.patient_id == "TEST_001"
    assert len(forecast_request.patient_history) == 4


def test_feature_validation():
    """Test feature input validation"""
    from ml_pipeline.api.inference_api import FeatureInput
    from pydantic import ValidationError
    
    # Valid features
    valid_features = FeatureInput(
        mmse_score=24.0,
        age=72
    )
    assert valid_features.mmse_score == 24.0
    
    # Test range validation for MMSE
    with pytest.raises(ValidationError):
        FeatureInput(mmse_score=35.0)  # Out of range (0-30)
    
    with pytest.raises(ValidationError):
        FeatureInput(mmse_score=-5.0)  # Negative
    
    # Test range validation for age
    with pytest.raises(ValidationError):
        FeatureInput(age=150)  # Out of range (0-120)
    
    # Test APOE e4 count validation
    with pytest.raises(ValidationError):
        FeatureInput(apoe_e4_count=3)  # Out of range (0-2)


def test_response_models():
    """Test that response models are properly defined"""
    from ml_pipeline.api.inference_api import (
        PredictionResponse,
        BatchPredictionResponse,
        ForecastResponse,
        ExplanationResponse
    )
    
    # Test PredictionResponse
    pred_response = PredictionResponse(
        prediction_id="test-123",
        prediction=1,
        probability=0.75,
        risk_category="High Risk",
        timestamp="2025-01-26T12:00:00",
        model_name="ensemble",
        model_version="v123",
        generation_time=0.5
    )
    assert pred_response.prediction == 1
    assert pred_response.probability == 0.75
    
    # Test BatchPredictionResponse
    batch_response = BatchPredictionResponse(
        predictions=[pred_response],
        total_count=1,
        generation_time=0.5
    )
    assert batch_response.total_count == 1
    
    # Test ForecastResponse
    forecast_response = ForecastResponse(
        patient_id="TEST_001",
        forecasts={"6_month_mmse": 20.5},
        uncertainty={"6_month_mmse": 2.0},
        timestamp="2025-01-26T12:00:00",
        generation_time=0.4
    )
    assert forecast_response.patient_id == "TEST_001"
    
    # Test ExplanationResponse
    explanation_response = ExplanationResponse(
        prediction_id="test-123",
        explanation={"top_features": []},
        generation_time=0.1
    )
    assert explanation_response.prediction_id == "test-123"


def test_helper_functions():
    """Test helper functions"""
    from ml_pipeline.api.inference_api import get_risk_category
    
    # Test risk categorization
    assert get_risk_category(0.2) == "Low Risk"
    assert get_risk_category(0.4) == "Moderate Risk"
    assert get_risk_category(0.7) == "High Risk"
    assert get_risk_category(0.9) == "Very High Risk"


def test_health_endpoint():
    """Test health check endpoint"""
    from ml_pipeline.api.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    from ml_pipeline.api.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "endpoints" in data


def test_cache_status_endpoint():
    """Test cache status endpoint"""
    from ml_pipeline.api.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/api/v1/models/cache/status")
    
    assert response.status_code == 200
    data = response.json()
    assert "cached_models" in data
    assert "total_cached" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
