"""
Pydantic schemas for medical imaging API requests and responses.
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ImagingModalityEnum(str, Enum):
    """Medical imaging modality types"""
    MRI = "MRI"
    CT = "CT"
    PET = "PET"
    SPECT = "SPECT"


class ImagingStatusEnum(str, Enum):
    """Processing status of imaging data"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImagingUploadResponse(BaseModel):
    """Response after uploading imaging file"""
    id: UUID4
    user_id: UUID4
    modality: ImagingModalityEnum
    file_size: float
    status: ImagingStatusEnum
    created_at: datetime
    message: str = "Imaging file uploaded successfully"
    
    class Config:
        from_attributes = True


class VolumetricMeasurements(BaseModel):
    """Volumetric measurements from brain imaging"""
    hippocampal_volume_left: Optional[float] = None
    hippocampal_volume_right: Optional[float] = None
    hippocampal_volume_total: Optional[float] = None
    entorhinal_cortex_volume_left: Optional[float] = None
    entorhinal_cortex_volume_right: Optional[float] = None
    cortical_thickness_mean: Optional[float] = None
    cortical_thickness_std: Optional[float] = None
    total_brain_volume: Optional[float] = None
    total_gray_matter_volume: Optional[float] = None
    total_white_matter_volume: Optional[float] = None
    ventricle_volume: Optional[float] = None


class AtrophyDetection(BaseModel):
    """Atrophy detection results"""
    detected: bool
    regions: List[str] = []
    severity: Optional[str] = None  # mild, moderate, severe


class ImagingAnalysisResponse(BaseModel):
    """Complete imaging analysis results"""
    id: UUID4
    user_id: UUID4
    modality: ImagingModalityEnum
    study_date: Optional[str] = None
    study_description: Optional[str] = None
    series_description: Optional[str] = None
    status: ImagingStatusEnum
    processing_error: Optional[str] = None
    
    # Measurements
    volumetric_measurements: Optional[VolumetricMeasurements] = None
    atrophy_detection: Optional[AtrophyDetection] = None
    
    # Additional data
    analysis_results: Optional[Dict[str, Any]] = None
    ml_features: Optional[Dict[str, Any]] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ImagingListResponse(BaseModel):
    """List of imaging studies for a user"""
    studies: List[ImagingAnalysisResponse]
    total: int


class ImagingProcessingStatus(BaseModel):
    """Processing status check response"""
    id: UUID4
    status: ImagingStatusEnum
    progress: Optional[int] = None  # 0-100
    message: Optional[str] = None
    error: Optional[str] = None
