"""
Main FastAPI application for ML Pipeline API

Integrates all API routers:
- Feature Store API
- Inference API (predictions, explanations, forecasting)
- Model Management API (future)
- Monitoring API (future)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from ml_pipeline.api.feature_api import router as feature_router
from ml_pipeline.api.inference_api import router as inference_router
from ml_pipeline.api.data_ingestion_api import router as data_ingestion_router
from ml_pipeline.api.model_management_api import router as model_management_router
from ml_pipeline.api.monitoring_api import router as monitoring_router
from ml_pipeline.config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ML Pipeline API",
    description="REST API for biomedical ML pipeline - data ingestion, predictions, explanations, and forecasting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data_ingestion_router)
app.include_router(feature_router)
app.include_router(inference_router)
app.include_router(model_management_router)
app.include_router(monitoring_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ML Pipeline API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "data_ingestion": "/api/v1/data/ingest",
            "data_sources": "/api/v1/data/sources",
            "quality_reports": "/api/v1/data/quality/{dataset_id}",
            "feature_extraction": "/api/v1/data/features/extract",
            "patient_features": "/api/v1/data/features/{patient_id}",
            "feature_statistics": "/api/v1/data/features/statistics",
            "features": "/api/v1/features",
            "predictions": "/api/v1/predict",
            "forecasts": "/api/v1/forecast",
            "batch_predictions": "/api/v1/predict/batch",
            "models": "/api/v1/models",
            "model_versions": "/api/v1/models/{model_name}/versions",
            "promote_model": "/api/v1/models/{model_name}/promote/{version_id}",
            "production_model": "/api/v1/models/{model_name}/production"
        }
    }

# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ml-pipeline-api"
    }

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ml_pipeline.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
