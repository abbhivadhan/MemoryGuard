"""
API module for ML pipeline

Provides REST API endpoints for:
- Feature store operations
- Model inference (predictions, explanations, forecasting)
- Model management
- Monitoring
"""
from ml_pipeline.api.feature_api import router as feature_router
from ml_pipeline.api.inference_api import router as inference_router

__all__ = ['feature_router', 'inference_router']
