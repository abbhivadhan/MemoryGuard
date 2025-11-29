"""
Tests for Monitoring API

Tests all monitoring endpoints:
- Drift detection endpoint (GET /api/v1/monitoring/drift)
- Performance monitoring endpoint (GET /api/v1/monitoring/performance)
- Manual retraining trigger (POST /api/v1/monitoring/trigger-retrain)
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import uuid

from ml_pipeline.api.main import app
from ml_pipeline.data_storage.models import DataDriftReport

# Create test client
client = TestClient(app)


class TestDriftDetectionEndpoint:
    """Test drift detection endpoint (Requirement 10.2, 10.3)"""
    
    def test_drift_detection_success(self):
        """Test successful drift detection retrieval"""
        # Mock drift report
        mock_report = Mock(spec=DataDriftReport)
        mock_report.report_id = str(uuid.uuid4())
        mock_report.created_at = datetime.now()
        mock_report.comparison_dataset = "test_dataset"
        mock_report.drift_detected = True
        mock_report.retraining_recommended = True
        mock_report.features_with_drift = ["feature1", "feature2"]
        mock_report.ks_test_results = {
            "feature1": {"statistic": 0.15, "p_value": 0.01, "drift_detected": True},
            "feature2": {"statistic": 0.12, "p_value": 0.03, "drift_detected": True}
        }
        mock_report.psi_scores = {
            "feature1": 0.25,
            "feature2": 0.22
        }
        
        with patch('ml_pipeline.api.monitoring_api.DataDriftMonitor') as mock_monitor:
            mock_instance = mock_monitor.return_value
            mock_instance.get_drift_history_from_db.return_value = [mock_report]
            
            response = client.get("/api/v1/monitoring/drift?model_name=test_model&days=7")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "timestamp" in data
            assert data["model_name"] == "test_model"
            assert data["drift_detected"] is True
            assert data["retraining_recommended"] is True
            assert len(data["features_with_drift"]) == 2
            assert len(data["feature_results"]) == 2
            assert "summary" in data
    
    def test_drift_detection_no_reports(self):
        """Test drift detection when no reports exist"""
        with patch('ml_pipeline.api.monitoring_api.DataDriftMonitor') as mock_monitor:
            mock_instance = mock_monitor.return_value
            mock_instance.get_drift_history_from_db.return_value = []
            
            response = client.get("/api/v1/monitoring/drift?model_name=test_model&days=7")
            
            assert response.status_code == 404
            assert "No drift reports found" in response.json()["detail"]
    
    def test_drift_detection_with_parameters(self):
        """Test drift detection with different parameters"""
        mock_report = Mock(spec=DataDriftReport)
        mock_report.report_id = str(uuid.uuid4())
        mock_report.created_at = datetime.now()
        mock_report.comparison_dataset = "test_dataset"
        mock_report.drift_detected = False
        mock_report.retraining_recommended = False
        mock_report.features_with_drift = []
        mock_report.ks_test_results = {}
        mock_report.psi_scores = {}
        
        with patch('ml_pipeline.api.monitoring_api.DataDriftMonitor') as mock_monitor:
            mock_instance = mock_monitor.return_value
            mock_instance.get_drift_history_from_db.return_value = [mock_report]
            
            response = client.get("/api/v1/monitoring/drift?model_name=custom_model&days=30")
            
            assert response.status_code == 200
            data = response.json()
            assert data["drift_detected"] is False
            assert data["retraining_recommended"] is False
    
    def test_drift_detection_error_handling(self):
        """Test error handling in drift detection"""
        with patch('ml_pipeline.api.monitoring_api.DataDriftMonitor') as mock_monitor:
            mock_instance = mock_monitor.return_value
            mock_instance.get_drift_history_from_db.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/monitoring/drift?model_name=test_model")
            
            assert response.status_code == 500
            assert "Failed to get drift detection results" in response.json()["detail"]


class TestPerformanceMonitoringEndpoint:
    """Test performance monitoring endpoint (Requirement 10.5)"""
    
    def test_performance_monitoring_success(self):
        """Test successful performance monitoring retrieval"""
        # Mock performance history
        mock_history = [
            {
                "timestamp": datetime.now().isoformat(),
                "dataset_name": "test_data",
                "metrics": {
                    "accuracy": 0.85,
                    "balanced_accuracy": 0.84,
                    "precision": 0.86,
                    "recall": 0.83,
                    "f1_score": 0.84,
                    "roc_auc": 0.88,
                    "n_samples": 1000
                },
                "baseline_comparison": {
                    "accuracy": {
                        "baseline": 0.82,
                        "current": 0.85,
                        "absolute_change": 0.03,
                        "relative_change": 0.0366,
                        "degraded": False
                    }
                }
            }
        ]
        
        mock_baseline = {
            "accuracy": 0.82,
            "f1_score": 0.80,
            "roc_auc": 0.85
        }
        
        with patch('ml_pipeline.api.monitoring_api.PerformanceTracker') as mock_tracker:
            mock_instance = mock_tracker.return_value
            mock_instance.load_baseline_metrics.return_value = mock_baseline
            mock_instance.load_performance_history.return_value = mock_history
            mock_instance.detect_performance_degradation.return_value = (False, None)
            
            # Mock DataFrame
            mock_df = pd.DataFrame({
                'accuracy': [0.85],
                'f1_score': [0.84]
            })
            mock_instance.get_performance_summary.return_value = mock_df
            
            response = client.get("/api/v1/monitoring/performance?model_name=test_model&days=30")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert data["model_name"] == "test_model"
            assert data["current_performance"] is not None
            assert data["baseline_metrics"] == mock_baseline
            assert data["performance_degraded"] is False
            assert len(data["recent_history"]) > 0
            assert "summary" in data
    
    def test_performance_monitoring_no_data(self):
        """Test performance monitoring when no data exists"""
        with patch('ml_pipeline.api.monitoring_api.PerformanceTracker') as mock_tracker:
            mock_instance = mock_tracker.return_value
            mock_instance.load_baseline_metrics.return_value = None
            mock_instance.load_performance_history.return_value = []
            
            response = client.get("/api/v1/monitoring/performance?model_name=test_model&days=30")
            
            assert response.status_code == 200
            data = response.json()
            assert data["current_performance"] is None
            assert len(data["recent_history"]) == 0
            assert "No performance data available" in data["summary"]["message"]
    
    def test_performance_monitoring_with_degradation(self):
        """Test performance monitoring when degradation is detected"""
        mock_history = [
            {
                "timestamp": datetime.now().isoformat(),
                "dataset_name": "test_data",
                "metrics": {
                    "accuracy": 0.75,
                    "precision": 0.76,
                    "recall": 0.74,
                    "f1_score": 0.75,
                    "n_samples": 1000
                }
            }
        ]
        
        mock_degradation_details = {
            "metric": "accuracy",
            "baseline_value": 0.85,
            "recent_average": 0.75,
            "relative_change": -0.1176,
            "threshold": 0.05,
            "degraded": True
        }
        
        with patch('ml_pipeline.api.monitoring_api.PerformanceTracker') as mock_tracker:
            mock_instance = mock_tracker.return_value
            mock_instance.load_baseline_metrics.return_value = {"accuracy": 0.85}
            mock_instance.load_performance_history.return_value = mock_history
            mock_instance.detect_performance_degradation.return_value = (True, mock_degradation_details)
            mock_instance.get_performance_summary.return_value = pd.DataFrame()
            
            response = client.get("/api/v1/monitoring/performance?model_name=test_model")
            
            assert response.status_code == 200
            data = response.json()
            assert data["performance_degraded"] is True
            assert data["degradation_details"] is not None
            assert data["degradation_details"]["degraded"] is True
    
    def test_performance_monitoring_error_handling(self):
        """Test error handling in performance monitoring"""
        with patch('ml_pipeline.api.monitoring_api.PerformanceTracker') as mock_tracker:
            mock_instance = mock_tracker.return_value
            mock_instance.load_baseline_metrics.side_effect = Exception("Storage error")
            
            response = client.get("/api/v1/monitoring/performance?model_name=test_model")
            
            assert response.status_code == 500
            assert "Failed to get performance monitoring" in response.json()["detail"]


class TestManualRetrainingTrigger:
    """Test manual retraining trigger endpoint (Requirement 11.2)"""
    
    def test_trigger_retraining_success(self):
        """Test successful manual retraining trigger"""
        request_data = {
            "reason": "Manual trigger for testing",
            "user_id": "test_user",
            "dataset_name": "train_features",
            "target_column": "diagnosis"
        }
        
        with patch('ml_pipeline.api.monitoring_api._run_retraining_job') as mock_job:
            response = client.post("/api/v1/monitoring/trigger-retrain", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert data["success"] is True
            assert "job_id" in data
            assert data["job_id"].startswith("retrain_")
            assert "triggered_at" in data
            assert "estimated_completion_time" in data
            assert "Manual trigger for testing" in data["message"]
    
    def test_trigger_retraining_with_defaults(self):
        """Test retraining trigger with default values"""
        request_data = {
            "reason": "Scheduled retraining"
        }
        
        with patch('ml_pipeline.api.monitoring_api._run_retraining_job') as mock_job:
            response = client.post("/api/v1/monitoring/trigger-retrain", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "job_id" in data
    
    def test_trigger_retraining_validation(self):
        """Test request validation for retraining trigger"""
        # Missing required field
        request_data = {}
        
        response = client.post("/api/v1/monitoring/trigger-retrain", json=request_data)
        
        # Should fail validation
        assert response.status_code == 422
    
    def test_trigger_retraining_error_handling(self):
        """Test error handling in retraining trigger"""
        request_data = {
            "reason": "Test error handling"
        }
        
        with patch('ml_pipeline.api.monitoring_api.datetime') as mock_datetime:
            mock_datetime.now.side_effect = Exception("System error")
            
            response = client.post("/api/v1/monitoring/trigger-retrain", json=request_data)
            
            assert response.status_code == 500
            assert "Failed to trigger retraining" in response.json()["detail"]


class TestAdditionalMonitoringEndpoints:
    """Test additional utility endpoints"""
    
    def test_drift_history_endpoint(self):
        """Test drift history endpoint"""
        mock_df = pd.DataFrame({
            'report_id': ['id1', 'id2'],
            'timestamp': [datetime.now(), datetime.now() - timedelta(days=1)],
            'dataset': ['dataset1', 'dataset2'],
            'drift_detected': [True, False],
            'retraining_recommended': [True, False],
            'n_features_with_drift': [3, 0]
        })
        
        with patch('ml_pipeline.api.monitoring_api.DataDriftMonitor') as mock_monitor:
            mock_instance = mock_monitor.return_value
            mock_instance.get_drift_summary_df.return_value = mock_df
            
            response = client.get("/api/v1/monitoring/drift/history?model_name=test_model&days=30")
            
            assert response.status_code == 200
            data = response.json()
            assert data["model_name"] == "test_model"
            assert data["n_reports"] == 2
            assert len(data["history"]) == 2
    
    def test_performance_trend_endpoint(self):
        """Test performance trend endpoint"""
        mock_df = pd.DataFrame({
            'timestamp': [datetime.now() - timedelta(days=i) for i in range(5)],
            'accuracy': [0.85, 0.84, 0.86, 0.85, 0.87],
            'accuracy_ma': [0.85, 0.845, 0.85, 0.85, 0.854],
            'trend_slope': [0.005] * 5
        })
        
        with patch('ml_pipeline.api.monitoring_api.PerformanceTracker') as mock_tracker:
            mock_instance = mock_tracker.return_value
            mock_instance.load_performance_history.return_value = []
            mock_instance.get_metric_trend.return_value = mock_df
            
            response = client.get(
                "/api/v1/monitoring/performance/trend"
                "?model_name=test_model&metric=accuracy&days=30"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["model_name"] == "test_model"
            assert data["metric"] == "accuracy"
            assert data["n_data_points"] == 5
            assert "trend_direction" in data
            assert "trend_data" in data
    
    def test_health_check_endpoint(self):
        """Test monitoring health check endpoint"""
        response = client.get("/api/v1/monitoring/health-check")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "components" in data
        assert data["components"]["drift_detection"] == "operational"
        assert data["components"]["performance_tracking"] == "operational"
        assert data["components"]["retraining_pipeline"] == "operational"


class TestEndToEndMonitoring:
    """End-to-end integration tests"""
    
    def test_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        # 1. Check drift detection
        mock_report = Mock(spec=DataDriftReport)
        mock_report.report_id = str(uuid.uuid4())
        mock_report.created_at = datetime.now()
        mock_report.comparison_dataset = "test_dataset"
        mock_report.drift_detected = True
        mock_report.retraining_recommended = True
        mock_report.features_with_drift = ["feature1"]
        mock_report.ks_test_results = {
            "feature1": {"statistic": 0.15, "p_value": 0.01, "drift_detected": True}
        }
        mock_report.psi_scores = {"feature1": 0.25}
        
        with patch('ml_pipeline.api.monitoring_api.DataDriftMonitor') as mock_monitor:
            mock_instance = mock_monitor.return_value
            mock_instance.get_drift_history_from_db.return_value = [mock_report]
            
            drift_response = client.get("/api/v1/monitoring/drift?model_name=test_model")
            assert drift_response.status_code == 200
            assert drift_response.json()["retraining_recommended"] is True
        
        # 2. Check performance
        mock_history = [{
            "timestamp": datetime.now().isoformat(),
            "dataset_name": "test_data",
            "metrics": {
                "accuracy": 0.85,
                "precision": 0.86,
                "recall": 0.84,
                "f1_score": 0.85,
                "n_samples": 1000
            }
        }]
        
        with patch('ml_pipeline.api.monitoring_api.PerformanceTracker') as mock_tracker:
            mock_instance = mock_tracker.return_value
            mock_instance.load_baseline_metrics.return_value = {"accuracy": 0.82}
            mock_instance.load_performance_history.return_value = mock_history
            mock_instance.detect_performance_degradation.return_value = (False, None)
            mock_instance.get_performance_summary.return_value = pd.DataFrame()
            
            perf_response = client.get("/api/v1/monitoring/performance?model_name=test_model")
            assert perf_response.status_code == 200
        
        # 3. Trigger retraining based on drift
        request_data = {
            "reason": "Drift detected in monitoring workflow"
        }
        
        with patch('ml_pipeline.api.monitoring_api._run_retraining_job'):
            retrain_response = client.post("/api/v1/monitoring/trigger-retrain", json=request_data)
            assert retrain_response.status_code == 200
            assert retrain_response.json()["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
