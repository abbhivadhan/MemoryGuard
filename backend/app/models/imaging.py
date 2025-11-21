"""
Medical imaging model for storing MRI and other brain imaging data.
"""
from sqlalchemy import Column, String, Float, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class ImagingModality(str, enum.Enum):
    """Medical imaging modality types"""
    MRI = "MRI"
    CT = "CT"
    PET = "PET"
    SPECT = "SPECT"


class ImagingStatus(str, enum.Enum):
    """Processing status of imaging data"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MedicalImaging(BaseModel):
    """
    Medical imaging model for storing brain scan data and analysis results.
    Supports DICOM files and extracted volumetric measurements.
    """
    __tablename__ = "medical_imaging"
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Imaging metadata
    modality = Column(SQLEnum(ImagingModality), nullable=False)
    study_date = Column(String, nullable=True)
    study_description = Column(String, nullable=True)
    series_description = Column(String, nullable=True)
    
    # File storage
    file_path = Column(String, nullable=False)  # Encrypted storage path
    file_size = Column(Float, nullable=False)  # Size in MB
    
    # Processing status
    status = Column(SQLEnum(ImagingStatus), default=ImagingStatus.UPLOADED, nullable=False)
    processing_error = Column(String, nullable=True)
    
    # Volumetric measurements (in mm³)
    hippocampal_volume_left = Column(Float, nullable=True)
    hippocampal_volume_right = Column(Float, nullable=True)
    hippocampal_volume_total = Column(Float, nullable=True)
    
    entorhinal_cortex_volume_left = Column(Float, nullable=True)
    entorhinal_cortex_volume_right = Column(Float, nullable=True)
    
    cortical_thickness_mean = Column(Float, nullable=True)  # in mm
    cortical_thickness_std = Column(Float, nullable=True)
    
    total_brain_volume = Column(Float, nullable=True)
    total_gray_matter_volume = Column(Float, nullable=True)
    total_white_matter_volume = Column(Float, nullable=True)
    
    ventricle_volume = Column(Float, nullable=True)
    
    # Atrophy detection
    atrophy_detected = Column(JSON, nullable=True)  # List of regions with atrophy
    atrophy_severity = Column(String, nullable=True)  # mild, moderate, severe
    
    # Additional analysis results
    analysis_results = Column(JSON, nullable=True)
    
    # ML feature extraction
    ml_features = Column(JSON, nullable=True)  # Features for ML model input
    
    def __repr__(self):
        return f"<MedicalImaging(id={self.id}, user_id={self.user_id}, modality={self.modality}, status={self.status})>"
    
    def to_dict(self):
        """Convert imaging to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "modality": self.modality.value,
            "study_date": self.study_date,
            "study_description": self.study_description,
            "series_description": self.series_description,
            "file_size": self.file_size,
            "status": self.status.value,
            "processing_error": self.processing_error,
            "hippocampal_volume_left": self.hippocampal_volume_left,
            "hippocampal_volume_right": self.hippocampal_volume_right,
            "hippocampal_volume_total": self.hippocampal_volume_total,
            "entorhinal_cortex_volume_left": self.entorhinal_cortex_volume_left,
            "entorhinal_cortex_volume_right": self.entorhinal_cortex_volume_right,
            "cortical_thickness_mean": self.cortical_thickness_mean,
            "cortical_thickness_std": self.cortical_thickness_std,
            "total_brain_volume": self.total_brain_volume,
            "total_gray_matter_volume": self.total_gray_matter_volume,
            "total_white_matter_volume": self.total_white_matter_volume,
            "ventricle_volume": self.ventricle_volume,
            "atrophy_detected": self.atrophy_detected,
            "atrophy_severity": self.atrophy_severity,
            "analysis_results": self.analysis_results,
            "ml_features": self.ml_features,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
