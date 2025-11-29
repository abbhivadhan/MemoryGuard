"""
FastAPI endpoints for feature store operations
Provides REST API for feature retrieval with caching
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
import pandas as pd

from ml_pipeline.data_storage.feature_store import FeatureStore
from ml_pipeline.config.logging_config import main_logger


# Initialize router
router = APIRouter(prefix="/api/v1/features", tags=["features"])

# Initialize feature store (singleton)
_feature_store = None


def get_feature_store() -> FeatureStore:
    """Get feature store instance"""
    global _feature_store
    if _feature_store is None:
        _feature_store = FeatureStore()
    return _feature_store


# Request/Response models
class FeatureQuery(BaseModel):
    """Feature query parameters"""
    patient_ids: Optional[List[str]] = Field(None, description="List of patient IDs")
    cohorts: Optional[List[str]] = Field(None, description="Cohorts to include (ADNI, OASIS, NACC)")
    start_date: Optional[date] = Field(None, description="Start date for filtering")
    end_date: Optional[date] = Field(None, description="End date for filtering")
    columns: Optional[List[str]] = Field(None, description="Specific columns to retrieve")
    use_cache: bool = Field(True, description="Whether to use Redis cache")


class FeatureResponse(BaseModel):
    """Feature retrieval response"""
    success: bool
    record_count: int
    features: List[dict]
    message: Optional[str] = None


class FeatureStatistics(BaseModel):
    """Feature statistics response"""
    success: bool
    statistics: dict
    message: Optional[str] = None


class StorageInfo(BaseModel):
    """Storage information response"""
    success: bool
    storage_info: dict
    message: Optional[str] = None


class IndexStatistics(BaseModel):
    """Index statistics response"""
    success: bool
    statistics: dict
    message: Optional[str] = None


class CompressionStatistics(BaseModel):
    """Compression statistics response"""
    success: bool
    statistics: dict
    message: Optional[str] = None


class TrainingDataResponse(BaseModel):
    """Training data response"""
    success: bool
    n_samples: int
    n_features: int
    feature_names: List[str]
    label_distribution: dict
    message: Optional[str] = None


# API Endpoints

@router.post("/query", response_model=FeatureResponse)
async def query_features(
    query: FeatureQuery,
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Query features with filtering
    
    Supports filtering by:
    - Patient IDs
    - Cohorts (ADNI, OASIS, NACC)
    - Date range
    - Specific columns
    
    Uses Redis caching for frequently accessed features
    """
    try:
        date_range = None
        if query.start_date and query.end_date:
            date_range = (query.start_date, query.end_date)
        elif query.start_date:
            date_range = (query.start_date, query.start_date)
        
        df = feature_store.read_features(
            patient_ids=query.patient_ids,
            cohorts=query.cohorts,
            date_range=date_range,
            columns=query.columns,
            use_cache=query.use_cache
        )
        
        # Convert DataFrame to list of dicts
        features = df.to_dict('records')
        
        # Convert datetime objects to strings for JSON serialization
        for feature in features:
            for key, value in feature.items():
                if isinstance(value, (datetime, date)):
                    feature[key] = value.isoformat()
                elif pd.isna(value):
                    feature[key] = None
        
        main_logger.info(
            f"Feature query returned {len(features)} records",
            extra={
                'operation': 'query_features',
                'user_id': 'api',
                'record_count': len(features)
            }
        )
        
        return FeatureResponse(
            success=True,
            record_count=len(features),
            features=features,
            message=f"Retrieved {len(features)} feature records"
        )
        
    except Exception as e:
        main_logger.error(
            f"Feature query failed: {str(e)}",
            extra={'operation': 'query_features', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patient/{patient_id}", response_model=FeatureResponse)
async def get_patient_features(
    patient_id: str,
    use_cache: bool = Query(True, description="Use Redis cache"),
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Get all features for a specific patient
    
    Returns all visits and features for the patient.
    Results are cached in Redis for fast subsequent access.
    """
    try:
        df = feature_store.get_patient_features(
            patient_id=patient_id,
            use_cache=use_cache
        )
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No features found for patient {patient_id}"
            )
        
        features = df.to_dict('records')
        
        # Convert datetime objects to strings
        for feature in features:
            for key, value in feature.items():
                if isinstance(value, (datetime, date)):
                    feature[key] = value.isoformat()
                elif pd.isna(value):
                    feature[key] = None
        
        return FeatureResponse(
            success=True,
            record_count=len(features),
            features=features,
            message=f"Retrieved {len(features)} records for patient {patient_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Failed to get patient features: {str(e)}",
            extra={'operation': 'get_patient_features', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patient/{patient_id}/latest", response_model=dict)
async def get_latest_patient_features(
    patient_id: str,
    use_cache: bool = Query(True, description="Use Redis cache"),
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Get most recent features for a patient
    
    Returns the latest visit features for the patient.
    Useful for real-time predictions.
    """
    try:
        latest = feature_store.get_latest_features(
            patient_id=patient_id,
            use_cache=use_cache
        )
        
        if latest is None:
            raise HTTPException(
                status_code=404,
                detail=f"No features found for patient {patient_id}"
            )
        
        # Convert to dict and handle datetime/NaN
        features = latest.to_dict()
        for key, value in features.items():
            if isinstance(value, (datetime, date)):
                features[key] = value.isoformat()
            elif pd.isna(value):
                features[key] = None
        
        return {
            "success": True,
            "patient_id": patient_id,
            "features": features,
            "message": f"Retrieved latest features for patient {patient_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Failed to get latest patient features: {str(e)}",
            extra={'operation': 'get_latest_patient_features', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=FeatureStatistics)
async def get_feature_statistics(
    cohorts: Optional[List[str]] = Query(None, description="Cohorts to include"),
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Get statistics for all features
    
    Returns descriptive statistics including:
    - Count, mean, std, min, max
    - Quartiles
    - Completeness percentage
    """
    try:
        stats_df = feature_store.get_feature_statistics(cohorts=cohorts)
        
        if stats_df.empty:
            return FeatureStatistics(
                success=True,
                statistics={},
                message="No features found"
            )
        
        # Convert to dict
        statistics = stats_df.to_dict('index')
        
        return FeatureStatistics(
            success=True,
            statistics=statistics,
            message=f"Retrieved statistics for {len(statistics)} features"
        )
        
    except Exception as e:
        main_logger.error(
            f"Failed to get feature statistics: {str(e)}",
            extra={'operation': 'get_feature_statistics', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/storage/info", response_model=StorageInfo)
async def get_storage_info(
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Get storage information
    
    Returns:
    - Total storage size
    - Number of files
    - Number of partitions
    """
    try:
        info = feature_store.get_storage_info()
        
        return StorageInfo(
            success=True,
            storage_info=info,
            message="Storage information retrieved"
        )
        
    except Exception as e:
        main_logger.error(
            f"Failed to get storage info: {str(e)}",
            extra={'operation': 'get_storage_info', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index/statistics", response_model=IndexStatistics)
async def get_index_statistics(
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Get index statistics
    
    Returns information about the feature index including:
    - Total records indexed
    - Total patients
    - Date range
    - Cohort distribution
    """
    try:
        stats = feature_store.get_index_statistics()
        
        # Convert date objects to strings
        if 'date_range' in stats and stats['date_range'][0]:
            stats['date_range'] = (
                stats['date_range'][0].isoformat(),
                stats['date_range'][1].isoformat()
            )
        
        if 'last_updated' in stats and stats['last_updated']:
            stats['last_updated'] = stats['last_updated'].isoformat()
        
        return IndexStatistics(
            success=True,
            statistics=stats,
            message="Index statistics retrieved"
        )
        
    except Exception as e:
        main_logger.error(
            f"Failed to get index statistics: {str(e)}",
            extra={'operation': 'get_index_statistics', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/rebuild")
async def rebuild_index(
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Rebuild feature index
    
    Scans all Parquet files and rebuilds the index.
    Use this after bulk data imports or if index is corrupted.
    """
    try:
        feature_store.rebuild_index()
        
        stats = feature_store.get_index_statistics()
        
        return {
            "success": True,
            "message": "Index rebuilt successfully",
            "statistics": stats
        }
        
    except Exception as e:
        main_logger.error(
            f"Failed to rebuild index: {str(e)}",
            extra={'operation': 'rebuild_index', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compression/statistics", response_model=CompressionStatistics)
async def get_compression_statistics(
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Get compression statistics
    
    Returns:
    - Compression ratio
    - Storage savings percentage
    - Whether 50% target is met
    """
    try:
        stats = feature_store.get_compression_statistics()
        
        return CompressionStatistics(
            success=True,
            statistics=stats,
            message="Compression statistics retrieved"
        )
        
    except Exception as e:
        main_logger.error(
            f"Failed to get compression statistics: {str(e)}",
            extra={'operation': 'get_compression_statistics', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training-data", response_model=TrainingDataResponse)
async def get_training_data(
    cohorts: Optional[List[str]] = Query(None, description="Cohorts to include"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    min_completeness: float = Query(0.7, description="Minimum completeness threshold"),
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Get training data with features and labels
    
    Returns processed features ready for ML training:
    - Features DataFrame
    - Labels Series
    - Feature names
    - Label distribution
    
    Note: This endpoint returns metadata only. Use the download endpoint for actual data.
    """
    try:
        date_range = None
        if start_date and end_date:
            date_range = (start_date, end_date)
        
        features, labels = feature_store.get_training_data(
            cohorts=cohorts,
            date_range=date_range,
            min_completeness=min_completeness
        )
        
        # Get label distribution
        label_dist = labels.value_counts().to_dict()
        label_dist = {str(k): int(v) for k, v in label_dist.items()}
        
        return TrainingDataResponse(
            success=True,
            n_samples=len(features),
            n_features=len(features.columns),
            feature_names=features.columns.tolist(),
            label_distribution=label_dist,
            message=f"Training data ready: {len(features)} samples, {len(features.columns)} features"
        )
        
    except Exception as e:
        main_logger.error(
            f"Failed to get training data: {str(e)}",
            extra={'operation': 'get_training_data', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/clear")
async def clear_cache(
    patient_id: Optional[str] = Query(None, description="Specific patient ID to clear"),
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Clear feature cache
    
    Clears Redis cache for:
    - Specific patient (if patient_id provided)
    - All patients (if no patient_id)
    """
    try:
        feature_store.clear_cache(patient_id=patient_id)
        
        message = (
            f"Cache cleared for patient {patient_id}"
            if patient_id
            else "Cache cleared for all patients"
        )
        
        return {
            "success": True,
            "message": message
        }
        
    except Exception as e:
        main_logger.error(
            f"Failed to clear cache: {str(e)}",
            extra={'operation': 'clear_cache', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_storage(
    feature_store: FeatureStore = Depends(get_feature_store)
):
    """
    Optimize storage by compacting files
    
    Combines small files within partitions and removes duplicates.
    This can improve query performance and reduce storage overhead.
    """
    try:
        stats = feature_store.optimize_storage()
        
        return {
            "success": True,
            "message": "Storage optimized",
            "statistics": stats
        }
        
    except Exception as e:
        main_logger.error(
            f"Failed to optimize storage: {str(e)}",
            extra={'operation': 'optimize_storage', 'user_id': 'api'}
        )
        raise HTTPException(status_code=500, detail=str(e))
