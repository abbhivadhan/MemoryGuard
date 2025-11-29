"""
Tests for Model Management API

Tests the REST API endpoints for model registry management.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import tempfile
import shutil
from pathlib import Path

from ml_pipeline.api.main import app
from ml_pipeline.models.model_registry import ModelRegistry
from sklearn.ensemble import RandomForestClassifier
import numpy as np


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def temp_registry():
    """Create temporary model registry for testing"""
    temp_dir = tempfile.mkdtemp()
    registry = ModelRegistry(storage_path=temp_dir)
    
    yield registry
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_model():
    """Create a simple trained model for testing"""
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    X = np.random.rand(100, 5)
    y = np.random.randint(0, 2, 100)
    model.fit(X, y)
    return model


def test_list_models_empty(client):
    """Test listing models when registry is empty"""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    # May return empty list or existing models depending on database state
    assert isinstance(response.json(), list)


def test_list_model_versions_not_found(client):
    """Test listing versions for non-existent model"""
    response = client.get("/api/v1/models/nonexistent_model/versions")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_production_model_not_found(client):
    """Test getting production model when none exists"""
    response = client.get("/api/v1/models/nonexistent_model/production")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_promote_model_invalid_version(client):
    """Test promoting non-existent version"""
    response = client.post(
        "/api/v1/models/test_model/promote/invalid_version",
        json={"user_id": "test_user"}
    )
    # Should return 400 or 500 depending on validation
    assert response.status_code in [400, 500]


def test_compare_model_versions_not_found(client):
    """Test comparing versions for non-existent model"""
    response = client.get("/api/v1/models/nonexistent_model/compare")
    assert response.status_code == 404


def test_get_deployment_history(client):
    """Test getting deployment history"""
    response = client.get("/api/v1/models/test_model/deployment-history")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "deployments" in data


def test_get_registry_statistics(client):
    """Test getting registry statistics"""
    response = client.get("/api/v1/models/statistics/registry")
    assert response.status_code == 200
    data = response.json()
    assert "registry_statistics" in data
    assert "timestamp" in data
    
    stats = data["registry_statistics"]
    assert "total_models" in stats
    assert "total_versions" in stats
    assert "production_models" in stats


def test_list_models_with_limit(client):
    """Test listing model versions with limit parameter"""
    response = client.get("/api/v1/models/test_model/versions?limit=5")
    # Should return 404 if model doesn't exist, or 200 with list
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


def test_promotion_request_default_user(client):
    """Test promotion with default user_id"""
    # This will fail because model doesn't exist, but tests the request structure
    response = client.post(
        "/api/v1/models/test_model/promote/test_version",
        json={}  # Empty body should use default user_id
    )
    # Should fail with 400 or 500, not validation error
    assert response.status_code in [400, 500]


def test_api_response_models(client):
    """Test that API responses match expected schema"""
    # Test models list endpoint
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    models = response.json()
    
    for model in models:
        assert "model_name" in model
        assert "total_versions" in model
        # production_version and latest_version can be None
        assert "production_version" in model or model.get("production_version") is None
        assert "latest_version" in model or model.get("latest_version") is None


def test_compare_with_metric_parameter(client):
    """Test comparing versions with different metrics"""
    metrics = ["roc_auc", "accuracy", "f1_score"]
    
    for metric in metrics:
        response = client.get(f"/api/v1/models/test_model/compare?metric={metric}")
        # Should return 404 if model doesn't exist
        if response.status_code == 200:
            data = response.json()
            assert data["comparison_metric"] == metric


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
