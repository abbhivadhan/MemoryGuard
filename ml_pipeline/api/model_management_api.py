"""
Model Management API

REST API endpoints for managing ML models in the registry:
- List all registered models
- List versions for a specific model
- Promote models to production
- Get production model information
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ml_pipeline.models.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/models",
    tags=["Model Management"]
)

# Initialize model registry
model_registry = ModelRegistry()


# Pydantic models for request/response
class ModelInfo(BaseModel):
    """Information about a registered model"""
    model_name: str
    total_versions: int
    production_version: Optional[str] = None
    latest_version: Optional[str] = None


class VersionInfo(BaseModel):
    """Information about a model version"""
    version_id: str
    model_type: str
    created_at: Optional[str] = None
    status: str
    roc_auc: Optional[float] = None
    accuracy: Optional[float] = None
    dataset_version: Optional[str] = None


class ProductionModelInfo(BaseModel):
    """Information about the production model"""
    version_id: str
    model_name: str
    model_type: str
    deployed_at: Optional[str] = None
    metrics: Dict[str, Optional[float]]
    dataset_version: Optional[str] = None
    artifact_path: str


class PromotionRequest(BaseModel):
    """Request to promote a model to production"""
    user_id: str = Field(default="system", description="User performing the promotion")


class PromotionResponse(BaseModel):
    """Response after promoting a model"""
    success: bool
    message: str
    model_name: str
    version_id: str
    previous_production: Optional[str] = None


# API Endpoints

@router.get("", response_model=List[ModelInfo])
async def list_models():
    """
    List all registered models
    
    Returns a list of all unique model names in the registry along with
    basic information about each model.
    
    **Requirements: 8.1**
    
    Returns:
        List of ModelInfo objects containing model names and version counts
    """
    try:
        logger.info("Listing all registered models")
        
        # Get all unique model names
        model_names = model_registry.list_all_models()
        
        if not model_names:
            logger.info("No models found in registry")
            return []
        
        # Get detailed info for each model
        models_info = []
        for model_name in model_names:
            # Get all versions
            versions = model_registry.list_versions(model_name, limit=1000)
            
            # Get production version
            production_model = model_registry.get_production_model(model_name)
            production_version = production_model['version_id'] if production_model else None
            
            # Get latest version
            latest_version = versions[0]['version_id'] if versions else None
            
            models_info.append(ModelInfo(
                model_name=model_name,
                total_versions=len(versions),
                production_version=production_version,
                latest_version=latest_version
            ))
        
        logger.info(f"Found {len(models_info)} models in registry")
        return models_info
        
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list models: {str(e)}"
        )


@router.get("/{model_name}/versions", response_model=List[VersionInfo])
async def list_model_versions(
    model_name: str,
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of versions to return")
):
    """
    List all versions for a specific model
    
    Returns version history for the specified model, ordered by creation date
    (most recent first).
    
    **Requirements: 8.1, 8.7**
    
    Args:
        model_name: Name of the model
        limit: Maximum number of versions to return (default: 10, max: 100)
    
    Returns:
        List of VersionInfo objects containing version metadata
    """
    try:
        logger.info(f"Listing versions for model: {model_name} (limit: {limit})")
        
        # Get versions from registry
        versions = model_registry.list_versions(model_name, limit=limit)
        
        if not versions:
            logger.warning(f"No versions found for model: {model_name}")
            raise HTTPException(
                status_code=404,
                detail=f"Model not found: {model_name}"
            )
        
        # Convert to response model
        version_list = [VersionInfo(**v) for v in versions]
        
        logger.info(f"Found {len(version_list)} versions for {model_name}")
        return version_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing versions for {model_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list versions: {str(e)}"
        )


@router.post("/{model_name}/promote/{version_id}", response_model=PromotionResponse)
async def promote_model_to_production(
    model_name: str,
    version_id: str,
    request: PromotionRequest = PromotionRequest()
):
    """
    Promote a model version to production
    
    This endpoint promotes the specified model version to production status.
    The current production version (if any) will be automatically demoted to
    archived status.
    
    **Requirements: 8.4, 8.5**
    
    Args:
        model_name: Name of the model
        version_id: Version ID to promote
        request: Promotion request with user_id
    
    Returns:
        PromotionResponse with success status and details
    """
    try:
        logger.info(
            f"Promoting {model_name} v{version_id} to production "
            f"(user: {request.user_id})"
        )
        
        # Get current production version before promotion
        current_production = model_registry.get_production_model(model_name)
        previous_version = current_production['version_id'] if current_production else None
        
        # Promote the model
        success = model_registry.promote_to_production(
            model_name=model_name,
            version_id=version_id,
            user_id=request.user_id
        )
        
        if not success:
            logger.error(f"Failed to promote {model_name} v{version_id}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to promote model. Version may not exist or may not belong to {model_name}"
            )
        
        message = f"Successfully promoted {model_name} v{version_id} to production"
        if previous_version:
            message += f". Previous production version {previous_version} archived."
        
        logger.info(message)
        
        return PromotionResponse(
            success=True,
            message=message,
            model_name=model_name,
            version_id=version_id,
            previous_production=previous_version
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error promoting model: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to promote model: {str(e)}"
        )


@router.get("/{model_name}/production", response_model=ProductionModelInfo)
async def get_production_model(model_name: str):
    """
    Get the currently deployed production model
    
    Returns information about the model version currently deployed in production
    for the specified model name.
    
    **Requirements: 8.5**
    
    Args:
        model_name: Name of the model
    
    Returns:
        ProductionModelInfo with production model details
    """
    try:
        logger.info(f"Getting production model for: {model_name}")
        
        # Get production model from registry
        production_model = model_registry.get_production_model(model_name)
        
        if not production_model:
            logger.warning(f"No production model found for: {model_name}")
            raise HTTPException(
                status_code=404,
                detail=f"No production model found for: {model_name}"
            )
        
        logger.info(
            f"Production model for {model_name}: v{production_model['version_id']}"
        )
        
        return ProductionModelInfo(**production_model)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting production model: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get production model: {str(e)}"
        )


# Additional utility endpoints

@router.get("/{model_name}/compare")
async def compare_model_versions(
    model_name: str,
    version_ids: Optional[List[str]] = Query(None, description="Specific version IDs to compare"),
    metric: str = Query(default="roc_auc", description="Metric to sort by")
):
    """
    Compare metrics across model versions
    
    Returns a comparison of performance metrics for different versions of a model.
    
    Args:
        model_name: Name of the model
        version_ids: Optional list of specific version IDs to compare
        metric: Metric to sort by (default: roc_auc)
    
    Returns:
        List of version comparisons sorted by the specified metric
    """
    try:
        logger.info(f"Comparing versions for {model_name} by {metric}")
        
        comparisons = model_registry.compare_versions(
            model_name=model_name,
            version_ids=version_ids,
            metric=metric
        )
        
        if not comparisons:
            raise HTTPException(
                status_code=404,
                detail=f"No versions found for model: {model_name}"
            )
        
        return {
            "model_name": model_name,
            "comparison_metric": metric,
            "versions": comparisons
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing versions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare versions: {str(e)}"
        )


@router.get("/{model_name}/deployment-history")
async def get_deployment_history(
    model_name: str,
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of deployments to return")
):
    """
    Get deployment history for a model
    
    Returns the history of production deployments for the specified model.
    
    Args:
        model_name: Name of the model
        limit: Maximum number of deployments to return
    
    Returns:
        List of deployment records
    """
    try:
        logger.info(f"Getting deployment history for {model_name} (limit: {limit})")
        
        history = model_registry.get_deployment_history(model_name, limit=limit)
        
        return {
            "model_name": model_name,
            "deployment_count": len(history),
            "deployments": history
        }
        
    except Exception as e:
        logger.error(f"Error getting deployment history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get deployment history: {str(e)}"
        )


@router.get("/statistics/registry")
async def get_registry_statistics():
    """
    Get overall statistics about the model registry
    
    Returns aggregate statistics about all models in the registry.
    
    Returns:
        Dictionary with registry statistics
    """
    try:
        logger.info("Getting registry statistics")
        
        stats = model_registry.get_model_statistics()
        
        return {
            "registry_statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting registry statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get registry statistics: {str(e)}"
        )
