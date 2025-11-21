"""
Health Metrics API endpoints.
Handles CRUD operations for health metrics tracking.
Requirements: 11.1-11.6
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.health_metric import HealthMetric, MetricType, MetricSource
from app.services.health_validation import HealthMetricValidator
from app.services.health_export import HealthMetricExporter
from fastapi.responses import Response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health-metrics"])


# Request/Response models
class HealthMetricCreate(BaseModel):
    """Request model for creating a health metric"""
    type: MetricType
    name: str = Field(..., min_length=1, max_length=255)
    value: float
    unit: str = Field(..., min_length=1, max_length=50)
    source: MetricSource = MetricSource.MANUAL
    timestamp: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('value')
    def validate_value(cls, v):
        """Validate that value is a valid number"""
        if not isinstance(v, (int, float)):
            raise ValueError('Value must be a number')
        if v < 0 and v != -1:  # Allow -1 as a special "not measured" value
            raise ValueError('Value cannot be negative (except -1 for not measured)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "cognitive",
                "name": "MMSE Score",
                "value": 28.0,
                "unit": "points",
                "source": "assessment",
                "timestamp": "2025-11-16T10:30:00Z",
                "notes": "Patient was alert and cooperative"
            }
        }


class HealthMetricUpdate(BaseModel):
    """Request model for updating a health metric"""
    value: Optional[float] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('value')
    def validate_value(cls, v):
        """Validate that value is a valid number"""
        if v is not None:
            if not isinstance(v, (int, float)):
                raise ValueError('Value must be a number')
            if v < 0 and v != -1:
                raise ValueError('Value cannot be negative (except -1 for not measured)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "value": 29.0,
                "notes": "Updated after review"
            }
        }


class HealthMetricResponse(BaseModel):
    """Response model for health metric"""
    id: str
    user_id: str
    type: str
    name: str
    value: float
    unit: str
    source: str
    timestamp: str
    notes: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "type": "cognitive",
                "name": "MMSE Score",
                "value": 28.0,
                "unit": "points",
                "source": "assessment",
                "timestamp": "2025-11-16T10:30:00Z",
                "notes": "Patient was alert and cooperative",
                "created_at": "2025-11-16T10:30:00Z",
                "updated_at": "2025-11-16T10:30:00Z"
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


@router.post("/metrics", response_model=HealthMetricResponse, status_code=status.HTTP_201_CREATED)
async def create_health_metric(
    metric_data: HealthMetricCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new health metric for the current user.
    
    This endpoint allows users to add health metrics including:
    - Cognitive function scores (MMSE, MoCA, CDR)
    - Biomarker levels (Amyloid-beta, Tau, p-Tau)
    - Brain volumetric measurements
    - Lifestyle factors (sleep, activity, diet)
    - Cardiovascular metrics (BP, cholesterol, glucose)
    
    Validates metric types, values, and data completeness.
    
    Args:
        metric_data: Health metric data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created health metric
        
    Requirements: 11.1-11.6, 3.5, 11.7
    """
    try:
        # Validate the metric
        is_valid, error, warnings = HealthMetricValidator.validate_metric(
            metric_data.type,
            metric_data.name,
            metric_data.value,
            metric_data.unit
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid health metric: {error}"
            )
        
        # Log warnings if any
        if warnings:
            for warning in warnings:
                logger.warning(f"Health metric validation warning: {warning}")
        
        # Create health metric
        health_metric = HealthMetric(
            user_id=current_user.id,
            type=metric_data.type,
            name=metric_data.name,
            value=metric_data.value,
            unit=metric_data.unit,
            source=metric_data.source,
            timestamp=metric_data.timestamp or datetime.utcnow(),
            notes=metric_data.notes
        )
        
        db.add(health_metric)
        db.commit()
        db.refresh(health_metric)
        
        logger.info(f"Health metric created: {health_metric.id} for user {current_user.id}")
        
        return HealthMetricResponse(**health_metric.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating health metric: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create health metric"
        )


@router.get("/metrics/{user_id}", response_model=List[HealthMetricResponse], status_code=status.HTTP_200_OK)
async def get_user_health_metrics(
    user_id: UUID,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of metrics to return"),
    offset: int = Query(0, ge=0, description="Number of metrics to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all health metrics for a specific user.
    
    Users can only access their own metrics unless they have caregiver/provider access.
    Results are ordered by timestamp (most recent first).
    
    Args:
        user_id: User ID to get metrics for
        limit: Maximum number of metrics to return (default: 100, max: 1000)
        offset: Number of metrics to skip for pagination
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of health metrics
        
    Requirements: 11.1-11.6
    """
    try:
        # Check authorization - users can only access their own data
        # TODO: Add caregiver/provider access check in future
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's health metrics"
            )
        
        # Query health metrics
        metrics = db.query(HealthMetric).filter(
            HealthMetric.user_id == user_id
        ).order_by(
            HealthMetric.timestamp.desc()
        ).limit(limit).offset(offset).all()
        
        logger.info(f"Retrieved {len(metrics)} health metrics for user {user_id}")
        
        return [HealthMetricResponse(**metric.to_dict()) for metric in metrics]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving health metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health metrics"
        )


@router.get("/metrics/{user_id}/{metric_type}", response_model=List[HealthMetricResponse], status_code=status.HTTP_200_OK)
async def get_user_health_metrics_by_type(
    user_id: UUID,
    metric_type: MetricType,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of metrics to return"),
    offset: int = Query(0, ge=0, description="Number of metrics to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health metrics for a specific user filtered by type.
    
    Metric types:
    - cognitive: MMSE, MoCA, CDR scores
    - biomarker: Amyloid-beta, Tau, p-Tau levels
    - imaging: MRI volumetric measurements
    - lifestyle: Sleep, activity, diet, social engagement
    - cardiovascular: Blood pressure, cholesterol, glucose
    
    Args:
        user_id: User ID to get metrics for
        metric_type: Type of metrics to retrieve
        limit: Maximum number of metrics to return (default: 100, max: 1000)
        offset: Number of metrics to skip for pagination
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of health metrics of specified type
        
    Requirements: 11.1-11.6
    """
    try:
        # Check authorization
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's health metrics"
            )
        
        # Query health metrics by type
        metrics = db.query(HealthMetric).filter(
            and_(
                HealthMetric.user_id == user_id,
                HealthMetric.type == metric_type
            )
        ).order_by(
            HealthMetric.timestamp.desc()
        ).limit(limit).offset(offset).all()
        
        logger.info(f"Retrieved {len(metrics)} {metric_type} metrics for user {user_id}")
        
        return [HealthMetricResponse(**metric.to_dict()) for metric in metrics]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving health metrics by type: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health metrics"
        )


@router.put("/metrics/{metric_id}", response_model=HealthMetricResponse, status_code=status.HTTP_200_OK)
async def update_health_metric(
    metric_id: UUID,
    metric_data: HealthMetricUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing health metric.
    
    Users can only update their own metrics.
    Only value, unit, and notes can be updated.
    
    Args:
        metric_id: ID of the metric to update
        metric_data: Updated metric data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated health metric
        
    Requirements: 11.1-11.6
    """
    try:
        # Get the metric
        metric = db.query(HealthMetric).filter(HealthMetric.id == metric_id).first()
        
        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health metric not found"
            )
        
        # Check authorization
        if metric.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this health metric"
            )
        
        # Update fields
        if metric_data.value is not None:
            metric.value = metric_data.value
        if metric_data.unit is not None:
            metric.unit = metric_data.unit
        if metric_data.notes is not None:
            metric.notes = metric_data.notes
        
        db.commit()
        db.refresh(metric)
        
        logger.info(f"Health metric updated: {metric_id} by user {current_user.id}")
        
        return HealthMetricResponse(**metric.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating health metric: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update health metric"
        )


@router.delete("/metrics/{metric_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_health_metric(
    metric_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a health metric.
    
    Users can only delete their own metrics.
    This is a hard delete and cannot be undone.
    
    Args:
        metric_id: ID of the metric to delete
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Requirements: 11.1-11.6
    """
    try:
        # Get the metric
        metric = db.query(HealthMetric).filter(HealthMetric.id == metric_id).first()
        
        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health metric not found"
            )
        
        # Check authorization
        if metric.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this health metric"
            )
        
        # Delete the metric
        db.delete(metric)
        db.commit()
        
        logger.info(f"Health metric deleted: {metric_id} by user {current_user.id}")
        
        return MessageResponse(message="Health metric deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting health metric: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete health metric"
        )



@router.get("/metrics/{user_id}/completeness", status_code=status.HTTP_200_OK)
async def check_data_completeness(
    user_id: UUID,
    metric_type: MetricType = Query(..., description="Type of metrics to check completeness"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check data completeness for a specific metric type.
    
    This endpoint analyzes the user's health metrics and provides:
    - Completeness percentage
    - Missing standard metrics
    - Recommendations for additional data collection
    
    Args:
        user_id: User ID to check completeness for
        metric_type: Type of metrics to check
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Completeness analysis with recommendations
        
    Requirements: 3.5, 11.7
    """
    try:
        # Check authorization
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's health metrics"
            )
        
        # Get user's metrics of this type
        metrics = db.query(HealthMetric).filter(
            and_(
                HealthMetric.user_id == user_id,
                HealthMetric.type == metric_type
            )
        ).all()
        
        # Convert to dict format for validation
        metric_dicts = [{"name": m.name, "value": m.value, "unit": m.unit} for m in metrics]
        
        # Check completeness
        completeness = HealthMetricValidator.check_data_completeness(
            metric_type,
            metric_dicts
        )
        
        logger.info(f"Completeness check for user {user_id}, type {metric_type}: {completeness['completeness_percentage']}%")
        
        return completeness
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking data completeness: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check data completeness"
        )


@router.get("/metrics/definitions/{metric_type}", status_code=status.HTTP_200_OK)
async def get_metric_definitions(
    metric_type: MetricType,
    current_user: User = Depends(get_current_user)
):
    """
    Get all standard metric definitions for a specific type.
    
    This endpoint provides information about expected metrics including:
    - Valid value ranges
    - Expected units
    - Descriptions
    
    Useful for building data entry forms and validation on the frontend.
    
    Args:
        metric_type: Type of metrics to get definitions for
        current_user: Current authenticated user
        
    Returns:
        Dictionary of metric definitions
        
    Requirements: 3.5, 11.7
    """
    try:
        definitions = HealthMetricValidator.get_all_metrics_for_type(metric_type)
        
        if not definitions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No definitions found for metric type: {metric_type}"
            )
        
        return {
            "metric_type": metric_type.value,
            "definitions": definitions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metric definitions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metric definitions"
        )


@router.post("/metrics/validate-batch", status_code=status.HTTP_200_OK)
async def validate_metrics_batch(
    metrics: List[Dict],
    current_user: User = Depends(get_current_user)
):
    """
    Validate a batch of metrics before submission.
    
    This endpoint allows users to validate multiple metrics at once
    without actually creating them in the database. Useful for:
    - Bulk data import validation
    - Form validation before submission
    - Data quality checks
    
    Args:
        metrics: List of metric dictionaries to validate
        current_user: Current authenticated user
        
    Returns:
        Validation results with valid/invalid metrics and warnings
        
    Requirements: 3.5, 11.7
    """
    try:
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No metrics provided for validation"
            )
        
        if len(metrics) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 metrics can be validated at once"
            )
        
        # Validate batch
        results = HealthMetricValidator.validate_batch(metrics)
        
        logger.info(
            f"Batch validation for user {current_user.id}: "
            f"{len(results['valid'])} valid, {len(results['invalid'])} invalid"
        )
        
        return {
            "total": len(metrics),
            "valid_count": len(results["valid"]),
            "invalid_count": len(results["invalid"]),
            "warning_count": len(results["warnings"]),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating metrics batch: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate metrics batch"
        )



@router.get("/metrics/{user_id}/export/csv", status_code=status.HTTP_200_OK)
async def export_metrics_csv(
    user_id: UUID,
    metric_type: Optional[MetricType] = Query(None, description="Filter by metric type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export health metrics to CSV format.
    
    Downloads all or filtered health metrics as a CSV file.
    
    Args:
        user_id: User ID to export metrics for
        metric_type: Optional filter by metric type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        CSV file download
        
    Requirements: 11.9
    """
    try:
        # Check authorization
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to export this user's health metrics"
            )
        
        # Query metrics
        query = db.query(HealthMetric).filter(HealthMetric.user_id == user_id)
        
        if metric_type:
            query = query.filter(HealthMetric.type == metric_type)
        
        metrics = query.order_by(HealthMetric.timestamp.desc()).all()
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No health metrics found for export"
            )
        
        # Convert to dict format
        metric_dicts = [metric.to_dict() for metric in metrics]
        
        # Export to CSV
        csv_content = HealthMetricExporter.export_to_csv(metric_dicts)
        
        # Generate filename
        type_suffix = f"_{metric_type.value}" if metric_type else ""
        filename = f"health_metrics{type_suffix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        logger.info(f"Exported {len(metrics)} metrics to CSV for user {user_id}")
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting metrics to CSV: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export metrics to CSV"
        )


@router.get("/metrics/{user_id}/export/fhir", status_code=status.HTTP_200_OK)
async def export_metrics_fhir(
    user_id: UUID,
    metric_type: Optional[MetricType] = Query(None, description="Filter by metric type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export health metrics to FHIR R4 format (JSON).
    
    Creates a FHIR Bundle with Observation resources for interoperability
    with electronic health record systems.
    
    Args:
        user_id: User ID to export metrics for
        metric_type: Optional filter by metric type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        FHIR JSON file download
        
    Requirements: 11.9
    """
    try:
        # Check authorization
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to export this user's health metrics"
            )
        
        # Query metrics
        query = db.query(HealthMetric).filter(HealthMetric.user_id == user_id)
        
        if metric_type:
            query = query.filter(HealthMetric.type == metric_type)
        
        metrics = query.order_by(HealthMetric.timestamp.desc()).all()
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No health metrics found for export"
            )
        
        # Convert to dict format
        metric_dicts = [metric.to_dict() for metric in metrics]
        
        # Get patient info
        patient_info = {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email
        }
        
        # Export to FHIR
        fhir_content = HealthMetricExporter.export_to_fhir(metric_dicts, patient_info)
        
        # Generate filename
        type_suffix = f"_{metric_type.value}" if metric_type else ""
        filename = f"health_metrics_fhir{type_suffix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        logger.info(f"Exported {len(metrics)} metrics to FHIR for user {user_id}")
        
        return Response(
            content=fhir_content,
            media_type="application/fhir+json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting metrics to FHIR: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export metrics to FHIR"
        )


@router.get("/metrics/{user_id}/export/pdf", status_code=status.HTTP_200_OK)
async def export_metrics_pdf(
    user_id: UUID,
    metric_type: Optional[MetricType] = Query(None, description="Filter by metric type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export health metrics to PDF format (HTML).
    
    Generates an HTML document suitable for PDF conversion.
    The HTML can be converted to PDF using browser print or PDF libraries.
    
    Args:
        user_id: User ID to export metrics for
        metric_type: Optional filter by metric type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        HTML file for PDF conversion
        
    Requirements: 11.9
    """
    try:
        # Check authorization
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to export this user's health metrics"
            )
        
        # Query metrics
        query = db.query(HealthMetric).filter(HealthMetric.user_id == user_id)
        
        if metric_type:
            query = query.filter(HealthMetric.type == metric_type)
        
        metrics = query.order_by(HealthMetric.timestamp.desc()).all()
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No health metrics found for export"
            )
        
        # Convert to dict format
        metric_dicts = [metric.to_dict() for metric in metrics]
        
        # Get user info
        user_info = {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email
        }
        
        # Export to HTML
        html_content = HealthMetricExporter.export_to_pdf_html(metric_dicts, user_info)
        
        # Generate filename
        type_suffix = f"_{metric_type.value}" if metric_type else ""
        filename = f"health_metrics_report{type_suffix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        
        logger.info(f"Exported {len(metrics)} metrics to PDF/HTML for user {user_id}")
        
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting metrics to PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export metrics to PDF"
        )
