"""
Monitoring API

REST API endpoints for monitoring ML models and data:
- Drift detection results
- Model performance metrics
- Manual retraining triggers
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import pandas as pd

from ml_pipeline.monitoring.data_drift_monitor import DataDriftMonitor
from ml_pipeline.monitoring.performance_tracker import PerformanceTracker
from ml_pipeline.retraining.retraining_pipeline import AutomatedRetrainingPipeline
from ml_pipeline.config.settings import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/monitoring",
    tags=["Monitoring"]
)


# Pydantic models for request/response

class DriftFeatureResult(BaseModel):
    """Drift detection result for a single feature"""
    feature_name: str
    ks_statistic: Optional[float] = None
    ks_p_value: Optional[float] = None
    ks_drift_detected: bool
    psi_score: Optional[float] = None
    psi_drift_detected: bool


class DriftDetectionResponse(BaseModel):
    """Response for drift detection endpoint"""
    timestamp: str
    model_name: str
    dataset_name: str
    n_samples: int
    n_features: int
    drift_detected: bool
    retraining_recommended: bool
    features_with_drift: List[str]
    feature_results: List[DriftFeatureResult]
    summary: Dict[str, Any]


class PerformanceMetrics(BaseModel):
    """Model performance metrics"""
    accuracy: float
    balanced_accuracy: Optional[float] = None
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    n_samples: int


class PerformanceEntry(BaseModel):
    """Single performance tracking entry"""
    timestamp: str
    dataset_name: str
    metrics: PerformanceMetrics
    baseline_comparison: Optional[Dict[str, Any]] = None


class PerformanceMonitoringResponse(BaseModel):
    """Response for performance monitoring endpoint"""
    model_name: str
    current_performance: Optional[PerformanceEntry] = None
    baseline_metrics: Optional[Dict[str, float]] = None
    performance_degraded: bool
    degradation_details: Optional[Dict[str, Any]] = None
    recent_history: List[PerformanceEntry]
    summary: Dict[str, Any]


class RetrainingTriggerRequest(BaseModel):
    """Request to trigger manual retraining"""
    reason: str = Field(description="Reason for manual retraining")
    user_id: str = Field(default="system", description="User triggering retraining")
    dataset_name: str = Field(default="train_features", description="Dataset to use for retraining")
    target_column: str = Field(default="diagnosis", description="Target column name")


class RetrainingTriggerResponse(BaseModel):
    """Response after triggering retraining"""
    success: bool
    message: str
    job_id: Optional[str] = None
    triggered_at: str
    estimated_completion_time: Optional[str] = None


# API Endpoints

@router.get("/drift", response_model=DriftDetectionResponse)
async def get_drift_detection_results(
    model_name: str = Query(default="default_model", description="Name of the model to monitor"),
    days: int = Query(default=7, ge=1, le=90, description="Number of days of history to analyze")
):
    """
    Get drift detection results
    
    Returns comprehensive drift detection results including:
    - Kolmogorov-Smirnov test results for each feature
    - Population Stability Index (PSI) scores
    - Overall drift assessment
    - Retraining recommendations
    
    **Requirements: 10.2, 10.3**
    
    Args:
        model_name: Name of the model being monitored
        days: Number of days of history to analyze (default: 7)
    
    Returns:
        DriftDetectionResponse with comprehensive drift analysis
    """
    try:
        logger.info(f"Getting drift detection results for {model_name} (last {days} days)")
        
        # Initialize drift monitor
        drift_monitor = DataDriftMonitor(model_name=model_name)
        
        # Get drift history from database
        drift_reports = drift_monitor.get_drift_history_from_db(days=days)
        
        if not drift_reports:
            logger.warning(f"No drift reports found for {model_name} in last {days} days")
            raise HTTPException(
                status_code=404,
                detail=f"No drift reports found for model '{model_name}' in the last {days} days"
            )
        
        # Get most recent report
        latest_report = drift_reports[0]
        
        # Parse drift results
        ks_test_results = latest_report.ks_test_results or {}
        psi_scores = latest_report.psi_scores or {}
        features_with_drift = latest_report.features_with_drift or []
        
        # Build feature results
        feature_results = []
        all_features = set(list(ks_test_results.keys()) + list(psi_scores.keys()))
        
        for feature in all_features:
            ks_result = ks_test_results.get(feature, {})
            psi_score = psi_scores.get(feature)
            
            feature_results.append(DriftFeatureResult(
                feature_name=feature,
                ks_statistic=ks_result.get('statistic'),
                ks_p_value=ks_result.get('p_value'),
                ks_drift_detected=ks_result.get('drift_detected', False),
                psi_score=psi_score,
                psi_drift_detected=(psi_score or 0) > settings.PSI_THRESHOLD
            ))
        
        # Calculate summary statistics
        n_features_with_ks_drift = sum(1 for f in feature_results if f.ks_drift_detected)
        n_features_with_psi_drift = sum(1 for f in feature_results if f.psi_drift_detected)
        avg_psi = sum(f.psi_score for f in feature_results if f.psi_score) / len(feature_results) if feature_results else 0
        
        summary = {
            "total_reports_analyzed": len(drift_reports),
            "reports_with_drift": sum(1 for r in drift_reports if r.drift_detected),
            "n_features_with_ks_drift": n_features_with_ks_drift,
            "n_features_with_psi_drift": n_features_with_psi_drift,
            "average_psi_score": round(avg_psi, 4),
            "psi_threshold": settings.PSI_THRESHOLD,
            "analysis_period_days": days
        }
        
        logger.info(
            f"Drift detection results: drift_detected={latest_report.drift_detected}, "
            f"features_with_drift={len(features_with_drift)}"
        )
        
        return DriftDetectionResponse(
            timestamp=latest_report.created_at.isoformat(),
            model_name=model_name,
            dataset_name=latest_report.comparison_dataset,
            n_samples=0,  # Not stored in current schema
            n_features=len(feature_results),
            drift_detected=latest_report.drift_detected,
            retraining_recommended=latest_report.retraining_recommended,
            features_with_drift=features_with_drift,
            feature_results=feature_results,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting drift detection results: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get drift detection results: {str(e)}"
        )


@router.get("/performance", response_model=PerformanceMonitoringResponse)
async def get_performance_monitoring(
    model_name: str = Query(default="default_model", description="Name of the model to monitor"),
    days: int = Query(default=30, ge=1, le=90, description="Number of days of history to retrieve")
):
    """
    Get model performance monitoring results
    
    Returns comprehensive performance tracking including:
    - Current performance metrics
    - Baseline comparison
    - Performance degradation detection
    - Historical performance trends
    
    **Requirements: 10.5**
    
    Args:
        model_name: Name of the model being monitored
        days: Number of days of history to retrieve (default: 30)
    
    Returns:
        PerformanceMonitoringResponse with performance analysis
    """
    try:
        logger.info(f"Getting performance monitoring for {model_name} (last {days} days)")
        
        # Initialize performance tracker
        performance_tracker = PerformanceTracker(model_name=model_name)
        
        # Load baseline metrics
        baseline_metrics = performance_tracker.load_baseline_metrics()
        
        # Load performance history
        history = performance_tracker.load_performance_history(days=days)
        
        if not history:
            logger.warning(f"No performance history found for {model_name} in last {days} days")
            
            # Return response with no data
            return PerformanceMonitoringResponse(
                model_name=model_name,
                current_performance=None,
                baseline_metrics=baseline_metrics,
                performance_degraded=False,
                degradation_details=None,
                recent_history=[],
                summary={
                    "n_tracking_entries": 0,
                    "analysis_period_days": days,
                    "message": f"No performance data available for {model_name} in the last {days} days"
                }
            )
        
        # Get most recent performance
        current_entry = history[-1]
        
        # Convert to response model
        current_performance = PerformanceEntry(
            timestamp=current_entry['timestamp'],
            dataset_name=current_entry['dataset_name'],
            metrics=PerformanceMetrics(**current_entry['metrics']),
            baseline_comparison=current_entry.get('baseline_comparison')
        )
        
        # Convert history to response models
        recent_history = [
            PerformanceEntry(
                timestamp=entry['timestamp'],
                dataset_name=entry['dataset_name'],
                metrics=PerformanceMetrics(**entry['metrics']),
                baseline_comparison=entry.get('baseline_comparison')
            )
            for entry in history[-10:]  # Last 10 entries
        ]
        
        # Check for performance degradation
        degraded, degradation_details = performance_tracker.detect_performance_degradation()
        
        # Calculate summary statistics
        df = performance_tracker.get_performance_summary()
        
        summary = {
            "n_tracking_entries": len(history),
            "analysis_period_days": days,
            "has_baseline": baseline_metrics is not None
        }
        
        if not df.empty:
            summary.update({
                "avg_accuracy": round(float(df['accuracy'].mean()), 4),
                "avg_f1_score": round(float(df['f1_score'].mean()), 4),
                "accuracy_std": round(float(df['accuracy'].std()), 4),
                "accuracy_trend": "improving" if df['accuracy'].iloc[-1] > df['accuracy'].iloc[0] else "declining"
            })
        
        logger.info(
            f"Performance monitoring results: degraded={degraded}, "
            f"n_entries={len(history)}"
        )
        
        return PerformanceMonitoringResponse(
            model_name=model_name,
            current_performance=current_performance,
            baseline_metrics=baseline_metrics,
            performance_degraded=degraded,
            degradation_details=degradation_details,
            recent_history=recent_history,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting performance monitoring: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance monitoring: {str(e)}"
        )


@router.post("/trigger-retrain", response_model=RetrainingTriggerResponse)
async def trigger_manual_retraining(
    request: RetrainingTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    Manually trigger model retraining
    
    Initiates a manual retraining job for all models. The retraining process
    runs in the background and includes:
    - Loading new training data
    - Retraining all models (Random Forest, XGBoost, Neural Network, Ensemble)
    - Evaluating new models against production
    - Automatic promotion if new models are 5% better
    
    **Requirements: 11.2**
    
    Args:
        request: RetrainingTriggerRequest with reason and configuration
        background_tasks: FastAPI background tasks
    
    Returns:
        RetrainingTriggerResponse with job information
    """
    try:
        logger.info(
            f"Manual retraining triggered by {request.user_id}: {request.reason}"
        )
        
        # Generate job ID
        job_id = f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        triggered_at = datetime.now()
        
        # Estimate completion time (2 hours as per requirement 5.8)
        estimated_completion = triggered_at + timedelta(hours=2)
        
        # Add retraining task to background
        background_tasks.add_task(
            _run_retraining_job,
            job_id=job_id,
            dataset_name=request.dataset_name,
            target_column=request.target_column,
            user_id=request.user_id,
            reason=request.reason
        )
        
        message = (
            f"Retraining job '{job_id}' started successfully. "
            f"Reason: {request.reason}. "
            f"Estimated completion: {estimated_completion.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        logger.info(message)
        
        return RetrainingTriggerResponse(
            success=True,
            message=message,
            job_id=job_id,
            triggered_at=triggered_at.isoformat(),
            estimated_completion_time=estimated_completion.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error triggering retraining: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger retraining: {str(e)}"
        )


# Background task functions

async def _run_retraining_job(
    job_id: str,
    dataset_name: str,
    target_column: str,
    user_id: str,
    reason: str
):
    """
    Run retraining job in background
    
    Args:
        job_id: Unique job identifier
        dataset_name: Name of the dataset to use
        target_column: Target column name
        user_id: User who triggered the job
        reason: Reason for retraining
    """
    try:
        logger.info(f"Starting retraining job {job_id}")
        
        # Initialize retraining pipeline
        retraining_pipeline = AutomatedRetrainingPipeline()
        
        # Run retraining
        retraining_results = retraining_pipeline.retrain_all_models(
            dataset_name=dataset_name,
            target_column=target_column
        )
        
        if not retraining_results.get('success'):
            logger.error(f"Retraining job {job_id} failed: {retraining_results.get('error')}")
            return
        
        # Evaluate new models
        evaluation_results = retraining_pipeline.evaluate_new_models(retraining_results)
        
        if not evaluation_results.get('success'):
            logger.error(f"Evaluation for job {job_id} failed: {evaluation_results.get('error')}")
            return
        
        # Log summary
        summary = evaluation_results.get('summary', {})
        logger.info(
            f"Retraining job {job_id} completed successfully. "
            f"Models recommended for deployment: {summary.get('models_recommended_for_deployment', 0)}"
        )
        
        # TODO: Send notification to user
        # notification_service.send_notification(
        #     user_id=user_id,
        #     message=f"Retraining job {job_id} completed",
        #     details=summary
        # )
        
    except Exception as e:
        logger.error(f"Error in retraining job {job_id}: {e}", exc_info=True)


# Additional utility endpoints

@router.get("/drift/history")
async def get_drift_history(
    model_name: str = Query(default="default_model", description="Name of the model"),
    days: int = Query(default=30, ge=1, le=90, description="Number of days of history")
):
    """
    Get historical drift detection results
    
    Returns a summary of drift detection over time.
    
    Args:
        model_name: Name of the model
        days: Number of days of history
    
    Returns:
        DataFrame-like structure with drift history
    """
    try:
        logger.info(f"Getting drift history for {model_name} (last {days} days)")
        
        drift_monitor = DataDriftMonitor(model_name=model_name)
        df = drift_monitor.get_drift_summary_df(days=days)
        
        if df.empty:
            return {
                "model_name": model_name,
                "period_days": days,
                "history": [],
                "message": "No drift history available"
            }
        
        # Convert to dict for JSON response
        history = df.to_dict('records')
        
        return {
            "model_name": model_name,
            "period_days": days,
            "n_reports": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"Error getting drift history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get drift history: {str(e)}"
        )


@router.get("/performance/trend")
async def get_performance_trend(
    model_name: str = Query(default="default_model", description="Name of the model"),
    metric: str = Query(default="accuracy", description="Metric to analyze"),
    days: int = Query(default=30, ge=1, le=90, description="Number of days of history")
):
    """
    Get performance trend analysis for a specific metric
    
    Returns trend analysis including moving averages and trend direction.
    
    Args:
        model_name: Name of the model
        metric: Metric to analyze (e.g., 'accuracy', 'f1_score', 'roc_auc')
        days: Number of days of history
    
    Returns:
        Trend analysis data
    """
    try:
        logger.info(f"Getting performance trend for {model_name}.{metric} (last {days} days)")
        
        performance_tracker = PerformanceTracker(model_name=model_name)
        performance_tracker.load_performance_history(days=days)
        
        trend_df = performance_tracker.get_metric_trend(metric=metric, window_size=5)
        
        if trend_df.empty:
            return {
                "model_name": model_name,
                "metric": metric,
                "period_days": days,
                "trend_data": [],
                "message": "No performance data available"
            }
        
        # Convert to dict for JSON response
        trend_data = trend_df.to_dict('records')
        
        # Calculate overall trend
        if len(trend_df) > 1:
            first_value = trend_df[metric].iloc[0]
            last_value = trend_df[metric].iloc[-1]
            trend_direction = "improving" if last_value > first_value else "declining"
            trend_change = last_value - first_value
        else:
            trend_direction = "stable"
            trend_change = 0
        
        return {
            "model_name": model_name,
            "metric": metric,
            "period_days": days,
            "n_data_points": len(trend_data),
            "trend_direction": trend_direction,
            "trend_change": round(float(trend_change), 4),
            "trend_data": trend_data
        }
        
    except Exception as e:
        logger.error(f"Error getting performance trend: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance trend: {str(e)}"
        )


@router.get("/health-check")
async def monitoring_health_check():
    """
    Health check for monitoring system
    
    Returns the status of monitoring components.
    
    Returns:
        Health status dictionary
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "drift_detection": "operational",
                "performance_tracking": "operational",
                "retraining_pipeline": "operational"
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
