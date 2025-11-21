"""
Medical imaging API endpoints for uploading and analyzing brain scans.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.imaging import MedicalImaging, ImagingModality, ImagingStatus
from app.schemas.imaging import (
    ImagingUploadResponse,
    ImagingAnalysisResponse,
    ImagingListResponse,
    ImagingProcessingStatus,
    VolumetricMeasurements,
    AtrophyDetection
)
from app.services.imaging_service import ImagingService
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize imaging service
imaging_service = ImagingService(
    storage_path=getattr(settings, "IMAGING_STORAGE_PATH", "./data/imaging"),
    encryption_key=getattr(settings, "IMAGING_ENCRYPTION_KEY", None)
)


def process_imaging_background(imaging_id: str, file_path: str, user_age: int = None):
    """
    Background task to process imaging file.
    
    Args:
        imaging_id: ID of the imaging record
        file_path: Path to the encrypted DICOM file
        user_age: User age for age-adjusted analysis
    """
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get imaging record
        imaging = db.query(MedicalImaging).filter(
            MedicalImaging.id == imaging_id
        ).first()
        
        if not imaging:
            logger.error(f"Imaging record {imaging_id} not found")
            return
        
        # Update status to processing
        imaging.status = ImagingStatus.PROCESSING
        db.commit()
        
        # Process DICOM file
        results = imaging_service.process_dicom_file(file_path, user_age)
        
        if results["success"]:
            # Update imaging record with results
            measurements = results.get("measurements", {})
            imaging.hippocampal_volume_left = measurements.get("hippocampal_volume_left")
            imaging.hippocampal_volume_right = measurements.get("hippocampal_volume_right")
            imaging.hippocampal_volume_total = measurements.get("hippocampal_volume_total")
            imaging.entorhinal_cortex_volume_left = measurements.get("entorhinal_cortex_volume_left")
            imaging.entorhinal_cortex_volume_right = measurements.get("entorhinal_cortex_volume_right")
            imaging.cortical_thickness_mean = measurements.get("cortical_thickness_mean")
            imaging.cortical_thickness_std = measurements.get("cortical_thickness_std")
            imaging.total_brain_volume = measurements.get("total_brain_volume")
            imaging.total_gray_matter_volume = measurements.get("total_gray_matter_volume")
            imaging.total_white_matter_volume = measurements.get("total_white_matter_volume")
            imaging.ventricle_volume = measurements.get("ventricle_volume")
            
            # Atrophy detection
            atrophy = results.get("atrophy", {})
            imaging.atrophy_detected = atrophy.get("regions", [])
            imaging.atrophy_severity = atrophy.get("severity")
            
            # Store additional results
            imaging.analysis_results = results.get("metadata", {})
            imaging.ml_features = results.get("ml_features", {})
            
            # Update metadata
            metadata = results.get("metadata", {})
            imaging.study_date = metadata.get("study_date")
            imaging.study_description = metadata.get("study_description")
            imaging.series_description = metadata.get("series_description")
            
            imaging.status = ImagingStatus.COMPLETED
            logger.info(f"Successfully processed imaging {imaging_id}")
        else:
            imaging.status = ImagingStatus.FAILED
            imaging.processing_error = results.get("error", "Unknown error")
            logger.error(f"Failed to process imaging {imaging_id}: {imaging.processing_error}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error in background processing: {e}")
        if imaging:
            imaging.status = ImagingStatus.FAILED
            imaging.processing_error = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=ImagingUploadResponse)
async def upload_imaging(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload medical imaging file (DICOM format).
    
    The file will be encrypted and stored securely. Processing happens
    in the background and results can be retrieved via the analysis endpoint.
    """
    # Validate file type
    if not file.filename.lower().endswith(('.dcm', '.dicom')):
        raise HTTPException(
            status_code=400,
            detail="Only DICOM files (.dcm, .dicom) are supported"
        )
    
    # Check file size (limit to 100MB)
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 100MB limit"
        )
    
    try:
        # Save encrypted file
        file_path, file_size_mb = imaging_service.save_dicom_file(
            file_content=content,
            user_id=str(current_user.id),
            filename=file.filename
        )
        
        # Create database record
        imaging = MedicalImaging(
            user_id=current_user.id,
            modality=ImagingModality.MRI,  # Default to MRI, will be updated after processing
            file_path=file_path,
            file_size=file_size_mb,
            status=ImagingStatus.UPLOADED
        )
        
        db.add(imaging)
        db.commit()
        db.refresh(imaging)
        
        # Schedule background processing
        user_age = None
        if current_user.date_of_birth:
            from datetime import datetime
            age = datetime.utcnow().year - current_user.date_of_birth.year
            user_age = age
        
        background_tasks.add_task(
            process_imaging_background,
            str(imaging.id),
            file_path,
            user_age
        )
        
        logger.info(f"Uploaded imaging file for user {current_user.id}: {imaging.id}")
        
        return ImagingUploadResponse(
            id=imaging.id,
            user_id=imaging.user_id,
            modality=imaging.modality,
            file_size=imaging.file_size,
            status=imaging.status,
            created_at=imaging.created_at,
            message="Imaging file uploaded successfully. Processing in background."
        )
        
    except Exception as e:
        logger.error(f"Error uploading imaging file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload imaging file: {str(e)}"
        )


@router.get("/{imaging_id}/analysis", response_model=ImagingAnalysisResponse)
async def get_imaging_analysis(
    imaging_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analysis results for a specific imaging study.
    """
    imaging = db.query(MedicalImaging).filter(
        MedicalImaging.id == imaging_id,
        MedicalImaging.user_id == current_user.id
    ).first()
    
    if not imaging:
        raise HTTPException(status_code=404, detail="Imaging study not found")
    
    # Build volumetric measurements
    volumetric = None
    if imaging.status == ImagingStatus.COMPLETED:
        volumetric = VolumetricMeasurements(
            hippocampal_volume_left=imaging.hippocampal_volume_left,
            hippocampal_volume_right=imaging.hippocampal_volume_right,
            hippocampal_volume_total=imaging.hippocampal_volume_total,
            entorhinal_cortex_volume_left=imaging.entorhinal_cortex_volume_left,
            entorhinal_cortex_volume_right=imaging.entorhinal_cortex_volume_right,
            cortical_thickness_mean=imaging.cortical_thickness_mean,
            cortical_thickness_std=imaging.cortical_thickness_std,
            total_brain_volume=imaging.total_brain_volume,
            total_gray_matter_volume=imaging.total_gray_matter_volume,
            total_white_matter_volume=imaging.total_white_matter_volume,
            ventricle_volume=imaging.ventricle_volume
        )
    
    # Build atrophy detection
    atrophy = None
    if imaging.atrophy_detected:
        atrophy = AtrophyDetection(
            detected=len(imaging.atrophy_detected) > 0,
            regions=imaging.atrophy_detected,
            severity=imaging.atrophy_severity
        )
    
    return ImagingAnalysisResponse(
        id=imaging.id,
        user_id=imaging.user_id,
        modality=imaging.modality,
        study_date=imaging.study_date,
        study_description=imaging.study_description,
        series_description=imaging.series_description,
        status=imaging.status,
        processing_error=imaging.processing_error,
        volumetric_measurements=volumetric,
        atrophy_detection=atrophy,
        analysis_results=imaging.analysis_results,
        ml_features=imaging.ml_features,
        created_at=imaging.created_at,
        updated_at=imaging.updated_at
    )


@router.get("/{imaging_id}/status", response_model=ImagingProcessingStatus)
async def get_imaging_status(
    imaging_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check processing status of an imaging study.
    """
    imaging = db.query(MedicalImaging).filter(
        MedicalImaging.id == imaging_id,
        MedicalImaging.user_id == current_user.id
    ).first()
    
    if not imaging:
        raise HTTPException(status_code=404, detail="Imaging study not found")
    
    # Calculate progress
    progress = None
    message = None
    
    if imaging.status == ImagingStatus.UPLOADED:
        progress = 0
        message = "Waiting to start processing"
    elif imaging.status == ImagingStatus.PROCESSING:
        progress = 50
        message = "Processing DICOM file and extracting measurements"
    elif imaging.status == ImagingStatus.COMPLETED:
        progress = 100
        message = "Processing completed successfully"
    elif imaging.status == ImagingStatus.FAILED:
        progress = 0
        message = "Processing failed"
    
    return ImagingProcessingStatus(
        id=imaging.id,
        status=imaging.status,
        progress=progress,
        message=message,
        error=imaging.processing_error
    )


@router.get("/user/{user_id}", response_model=ImagingListResponse)
async def get_user_imaging_studies(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all imaging studies for a user.
    
    Users can only access their own studies unless they are a caregiver/provider.
    """
    # Check authorization
    if str(current_user.id) != str(user_id):
        # Check if current user is a caregiver for this user
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user or str(current_user.id) not in target_user.caregivers:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this user's imaging studies"
            )
    
    # Get all imaging studies
    studies = db.query(MedicalImaging).filter(
        MedicalImaging.user_id == user_id
    ).order_by(MedicalImaging.created_at.desc()).all()
    
    # Build response
    study_responses = []
    for imaging in studies:
        volumetric = None
        if imaging.status == ImagingStatus.COMPLETED:
            volumetric = VolumetricMeasurements(
                hippocampal_volume_left=imaging.hippocampal_volume_left,
                hippocampal_volume_right=imaging.hippocampal_volume_right,
                hippocampal_volume_total=imaging.hippocampal_volume_total,
                entorhinal_cortex_volume_left=imaging.entorhinal_cortex_volume_left,
                entorhinal_cortex_volume_right=imaging.entorhinal_cortex_volume_right,
                cortical_thickness_mean=imaging.cortical_thickness_mean,
                cortical_thickness_std=imaging.cortical_thickness_std,
                total_brain_volume=imaging.total_brain_volume,
                total_gray_matter_volume=imaging.total_gray_matter_volume,
                total_white_matter_volume=imaging.total_white_matter_volume,
                ventricle_volume=imaging.ventricle_volume
            )
        
        atrophy = None
        if imaging.atrophy_detected:
            atrophy = AtrophyDetection(
                detected=len(imaging.atrophy_detected) > 0,
                regions=imaging.atrophy_detected,
                severity=imaging.atrophy_severity
            )
        
        study_responses.append(
            ImagingAnalysisResponse(
                id=imaging.id,
                user_id=imaging.user_id,
                modality=imaging.modality,
                study_date=imaging.study_date,
                study_description=imaging.study_description,
                series_description=imaging.series_description,
                status=imaging.status,
                processing_error=imaging.processing_error,
                volumetric_measurements=volumetric,
                atrophy_detection=atrophy,
                analysis_results=imaging.analysis_results,
                ml_features=imaging.ml_features,
                created_at=imaging.created_at,
                updated_at=imaging.updated_at
            )
        )
    
    return ImagingListResponse(
        studies=study_responses,
        total=len(study_responses)
    )
