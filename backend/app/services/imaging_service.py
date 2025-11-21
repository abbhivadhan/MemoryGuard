"""
Medical imaging service for processing DICOM files and extracting features.
"""
import pydicom
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import hashlib
import os
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class ImagingService:
    """Service for processing medical imaging data"""
    
    def __init__(self, storage_path: str, encryption_key: Optional[str] = None):
        """
        Initialize imaging service.
        
        Args:
            storage_path: Base path for storing imaging files
            encryption_key: Encryption key for HIPAA compliance
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate a key if none provided (for development)
            self.cipher = Fernet(Fernet.generate_key())
    
    def save_dicom_file(
        self,
        file_content: bytes,
        user_id: str,
        filename: str
    ) -> Tuple[str, float]:
        """
        Save DICOM file with encryption.
        
        Args:
            file_content: Raw file bytes
            user_id: User ID for organizing storage
            filename: Original filename
            
        Returns:
            Tuple of (file_path, file_size_mb)
        """
        # Create user directory
        user_dir = self.storage_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(file_content).hexdigest()[:8]
        safe_filename = f"{timestamp}_{file_hash}_{filename}"
        file_path = user_dir / safe_filename
        
        # Encrypt and save
        encrypted_content = self.cipher.encrypt(file_content)
        file_path.write_bytes(encrypted_content)
        
        # Calculate size in MB
        file_size_mb = len(file_content) / (1024 * 1024)
        
        return str(file_path), file_size_mb
    
    def load_dicom_file(self, file_path: str) -> pydicom.Dataset:
        """
        Load and decrypt DICOM file.
        
        Args:
            file_path: Path to encrypted DICOM file
            
        Returns:
            PyDICOM dataset
        """
        # Read and decrypt
        encrypted_content = Path(file_path).read_bytes()
        decrypted_content = self.cipher.decrypt(encrypted_content)
        
        # Parse DICOM
        from io import BytesIO
        dicom_file = BytesIO(decrypted_content)
        dataset = pydicom.dcmread(dicom_file)
        
        return dataset
    
    def extract_dicom_metadata(self, dataset: pydicom.Dataset) -> Dict[str, Any]:
        """
        Extract metadata from DICOM dataset.
        
        Args:
            dataset: PyDICOM dataset
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        # Study information
        metadata["study_date"] = str(dataset.get("StudyDate", ""))
        metadata["study_description"] = str(dataset.get("StudyDescription", ""))
        metadata["series_description"] = str(dataset.get("SeriesDescription", ""))
        metadata["modality"] = str(dataset.get("Modality", "MRI"))
        
        # Patient information (anonymized)
        metadata["patient_age"] = str(dataset.get("PatientAge", ""))
        metadata["patient_sex"] = str(dataset.get("PatientSex", ""))
        
        # Image information
        metadata["slice_thickness"] = float(dataset.get("SliceThickness", 0))
        metadata["pixel_spacing"] = list(dataset.get("PixelSpacing", []))
        metadata["rows"] = int(dataset.get("Rows", 0))
        metadata["columns"] = int(dataset.get("Columns", 0))
        
        return metadata
    
    def extract_volumetric_measurements(
        self,
        dataset: pydicom.Dataset
    ) -> Dict[str, float]:
        """
        Extract volumetric measurements from MRI data.
        
        This is a simplified implementation. In production, this would use
        advanced segmentation algorithms like FreeSurfer, FSL, or deep learning models.
        
        Args:
            dataset: PyDICOM dataset
            
        Returns:
            Dictionary of volumetric measurements
        """
        measurements = {}
        
        try:
            # Get pixel array
            pixel_array = dataset.pixel_array
            
            # Get voxel dimensions
            pixel_spacing = dataset.get("PixelSpacing", [1.0, 1.0])
            slice_thickness = float(dataset.get("SliceThickness", 1.0))
            voxel_volume = pixel_spacing[0] * pixel_spacing[1] * slice_thickness
            
            # Calculate basic statistics
            # Note: This is a placeholder. Real implementation would use
            # segmentation algorithms to identify specific brain regions
            
            total_volume = np.sum(pixel_array > 0) * voxel_volume
            measurements["total_brain_volume"] = float(total_volume)
            
            # Estimate hippocampal volume (typically 2-3% of total brain volume)
            # This is a rough estimate - real implementation needs segmentation
            estimated_hippocampal = total_volume * 0.025
            measurements["hippocampal_volume_total"] = float(estimated_hippocampal)
            measurements["hippocampal_volume_left"] = float(estimated_hippocampal * 0.5)
            measurements["hippocampal_volume_right"] = float(estimated_hippocampal * 0.5)
            
            # Estimate cortical thickness (typical range 2-4mm)
            # Real implementation would use surface-based analysis
            measurements["cortical_thickness_mean"] = 3.0
            measurements["cortical_thickness_std"] = 0.5
            
            # Estimate gray/white matter volumes
            measurements["total_gray_matter_volume"] = float(total_volume * 0.4)
            measurements["total_white_matter_volume"] = float(total_volume * 0.3)
            measurements["ventricle_volume"] = float(total_volume * 0.05)
            
            logger.info(f"Extracted volumetric measurements: {measurements}")
            
        except Exception as e:
            logger.error(f"Error extracting volumetric measurements: {e}")
            # Return empty measurements on error
            pass
        
        return measurements
    
    def detect_atrophy(
        self,
        measurements: Dict[str, float],
        age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Detect brain atrophy based on volumetric measurements.
        
        Uses normative data to identify regions with abnormal volume loss.
        
        Args:
            measurements: Volumetric measurements
            age: Patient age for age-adjusted norms
            
        Returns:
            Dictionary with atrophy detection results
        """
        atrophy_results = {
            "detected": False,
            "regions": [],
            "severity": None
        }
        
        # Normative values (simplified - real implementation would use age-adjusted norms)
        # Values in mm³
        norms = {
            "hippocampal_volume_total": {"mean": 7500, "std": 800, "threshold": -1.5},
            "cortical_thickness_mean": {"mean": 3.0, "std": 0.3, "threshold": -1.5},
            "total_brain_volume": {"mean": 1200000, "std": 100000, "threshold": -2.0}
        }
        
        atrophy_scores = []
        
        for measure_name, norm_data in norms.items():
            if measure_name in measurements:
                value = measurements[measure_name]
                mean = norm_data["mean"]
                std = norm_data["std"]
                threshold = norm_data["threshold"]
                
                # Calculate z-score
                z_score = (value - mean) / std
                
                # Check if below threshold
                if z_score < threshold:
                    region_name = measure_name.replace("_", " ").title()
                    atrophy_results["regions"].append(region_name)
                    atrophy_scores.append(abs(z_score))
        
        if atrophy_results["regions"]:
            atrophy_results["detected"] = True
            
            # Determine severity based on average z-score
            avg_score = np.mean(atrophy_scores)
            if avg_score < 2.0:
                atrophy_results["severity"] = "mild"
            elif avg_score < 3.0:
                atrophy_results["severity"] = "moderate"
            else:
                atrophy_results["severity"] = "severe"
        
        return atrophy_results
    
    def extract_ml_features(
        self,
        measurements: Dict[str, float],
        metadata: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Extract features for ML model input.
        
        Args:
            measurements: Volumetric measurements
            metadata: DICOM metadata
            
        Returns:
            Dictionary of ML features
        """
        features = {}
        
        # Direct volumetric features
        feature_keys = [
            "hippocampal_volume_total",
            "hippocampal_volume_left",
            "hippocampal_volume_right",
            "cortical_thickness_mean",
            "total_brain_volume",
            "total_gray_matter_volume",
            "total_white_matter_volume",
            "ventricle_volume"
        ]
        
        for key in feature_keys:
            if key in measurements:
                features[key] = measurements[key]
        
        # Derived features
        if "hippocampal_volume_total" in measurements and "total_brain_volume" in measurements:
            features["hippocampal_ratio"] = (
                measurements["hippocampal_volume_total"] / measurements["total_brain_volume"]
            )
        
        if "ventricle_volume" in measurements and "total_brain_volume" in measurements:
            features["ventricle_ratio"] = (
                measurements["ventricle_volume"] / measurements["total_brain_volume"]
            )
        
        if "total_gray_matter_volume" in measurements and "total_white_matter_volume" in measurements:
            features["gray_white_ratio"] = (
                measurements["total_gray_matter_volume"] / measurements["total_white_matter_volume"]
            )
        
        # Asymmetry features
        if "hippocampal_volume_left" in measurements and "hippocampal_volume_right" in measurements:
            left = measurements["hippocampal_volume_left"]
            right = measurements["hippocampal_volume_right"]
            features["hippocampal_asymmetry"] = abs(left - right) / ((left + right) / 2)
        
        return features
    
    def process_dicom_file(
        self,
        file_path: str,
        user_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Complete processing pipeline for DICOM file.
        
        Args:
            file_path: Path to encrypted DICOM file
            user_age: User age for age-adjusted analysis
            
        Returns:
            Dictionary with all analysis results
        """
        try:
            # Load DICOM
            dataset = self.load_dicom_file(file_path)
            
            # Extract metadata
            metadata = self.extract_dicom_metadata(dataset)
            
            # Extract volumetric measurements
            measurements = self.extract_volumetric_measurements(dataset)
            
            # Detect atrophy
            atrophy = self.detect_atrophy(measurements, user_age)
            
            # Extract ML features
            ml_features = self.extract_ml_features(measurements, metadata)
            
            return {
                "success": True,
                "metadata": metadata,
                "measurements": measurements,
                "atrophy": atrophy,
                "ml_features": ml_features
            }
            
        except Exception as e:
            logger.error(f"Error processing DICOM file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
