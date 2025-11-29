"""
Imaging Feature Extraction

Extracts volumetric and morphometric features from MRI DICOM files including:
- Hippocampal volume (left, right, total)
- Entorhinal cortex thickness
- Ventricular volume
- Whole brain volume
- Cortical thickness for multiple regions
- Normalized volumes by intracranial volume
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImagingFeatureExtractor:
    """Extract volumetric and morphometric features from MRI data"""
    
    def __init__(self):
        """Initialize imaging feature extractor"""
        self.feature_columns = []
        
        # Brain regions of interest for Alzheimer's disease
        self.roi_regions = [
            'hippocampus_left',
            'hippocampus_right',
            'entorhinal_cortex_left',
            'entorhinal_cortex_right',
            'amygdala_left',
            'amygdala_right',
            'temporal_lobe_left',
            'temporal_lobe_right',
            'parietal_lobe_left',
            'parietal_lobe_right',
            'frontal_lobe_left',
            'frontal_lobe_right',
            'ventricles',
            'whole_brain',
            'intracranial_volume'
        ]
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all imaging features from raw data
        
        Args:
            data: Raw dataframe containing imaging measurements or paths to DICOM files
            
        Returns:
            DataFrame with extracted imaging features
        """
        logger.info("Extracting imaging features")
        
        features = pd.DataFrame(index=data.index)
        
        # Extract volumetric measurements
        volume_features = self.extract_volumes(data)
        features = pd.concat([features, volume_features], axis=1)
        
        # Extract cortical thickness
        thickness_features = self.extract_cortical_thickness(data)
        features = pd.concat([features, thickness_features], axis=1)
        
        # Normalize by intracranial volume
        normalized_features = self.normalize_by_icv(features)
        features = pd.concat([features, normalized_features], axis=1)
        
        # Calculate derived features
        derived_features = self.calculate_derived_features(features)
        features = pd.concat([features, derived_features], axis=1)
        
        self.feature_columns = features.columns.tolist()
        
        logger.info(f"Extracted {len(self.feature_columns)} imaging features")
        return features
    
    def extract_volumes(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract volumetric measurements from MRI data
        
        Args:
            data: Raw dataframe with volume measurements
            
        Returns:
            DataFrame with volume features
        """
        volumes = pd.DataFrame(index=data.index)
        
        # Hippocampal volumes (mm³)
        volumes['hippocampus_left'] = self._extract_column(
            data, ['hippocampus_left', 'Left_Hippocampus', 'HIPP_LEFT']
        )
        volumes['hippocampus_right'] = self._extract_column(
            data, ['hippocampus_right', 'Right_Hippocampus', 'HIPP_RIGHT']
        )
        
        # Calculate total hippocampal volume
        if 'hippocampus_left' in volumes.columns and 'hippocampus_right' in volumes.columns:
            volumes['hippocampus_total'] = (
                volumes['hippocampus_left'].fillna(0) + 
                volumes['hippocampus_right'].fillna(0)
            )
            volumes.loc[
                volumes['hippocampus_left'].isna() & volumes['hippocampus_right'].isna(),
                'hippocampus_total'
            ] = np.nan
        
        # Entorhinal cortex volumes (mm³)
        volumes['entorhinal_cortex_left'] = self._extract_column(
            data, ['entorhinal_cortex_left', 'Left_Entorhinal', 'EC_LEFT']
        )
        volumes['entorhinal_cortex_right'] = self._extract_column(
            data, ['entorhinal_cortex_right', 'Right_Entorhinal', 'EC_RIGHT']
        )
        
        # Amygdala volumes (mm³)
        volumes['amygdala_left'] = self._extract_column(
            data, ['amygdala_left', 'Left_Amygdala', 'AMYG_LEFT']
        )
        volumes['amygdala_right'] = self._extract_column(
            data, ['amygdala_right', 'Right_Amygdala', 'AMYG_RIGHT']
        )
        
        # Ventricular volume (mm³)
        volumes['ventricles'] = self._extract_column(
            data, ['ventricles', 'Ventricles', 'VENT_VOLUME', 'ventricular_volume']
        )
        
        # Whole brain volume (mm³)
        volumes['whole_brain'] = self._extract_column(
            data, ['whole_brain', 'WholeBrain', 'BRAIN_VOLUME', 'total_brain_volume']
        )
        
        # Intracranial volume (mm³)
        volumes['intracranial_volume'] = self._extract_column(
            data, ['intracranial_volume', 'ICV', 'TIV', 'total_intracranial_volume']
        )
        
        # Temporal lobe volumes
        volumes['temporal_lobe_left'] = self._extract_column(
            data, ['temporal_lobe_left', 'Left_Temporal', 'TEMP_LEFT']
        )
        volumes['temporal_lobe_right'] = self._extract_column(
            data, ['temporal_lobe_right', 'Right_Temporal', 'TEMP_RIGHT']
        )
        
        # Parietal lobe volumes
        volumes['parietal_lobe_left'] = self._extract_column(
            data, ['parietal_lobe_left', 'Left_Parietal', 'PAR_LEFT']
        )
        volumes['parietal_lobe_right'] = self._extract_column(
            data, ['parietal_lobe_right', 'Right_Parietal', 'PAR_RIGHT']
        )
        
        # Frontal lobe volumes
        volumes['frontal_lobe_left'] = self._extract_column(
            data, ['frontal_lobe_left', 'Left_Frontal', 'FRONT_LEFT']
        )
        volumes['frontal_lobe_right'] = self._extract_column(
            data, ['frontal_lobe_right', 'Right_Frontal', 'FRONT_RIGHT']
        )
        
        return volumes
    
    def extract_cortical_thickness(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract cortical thickness measurements
        
        Args:
            data: Raw dataframe with thickness measurements
            
        Returns:
            DataFrame with cortical thickness features
        """
        thickness = pd.DataFrame(index=data.index)
        
        # Entorhinal cortex thickness (mm)
        thickness['entorhinal_thickness_left'] = self._extract_column(
            data, ['entorhinal_thickness_left', 'Left_EC_Thickness', 'EC_THICK_LEFT']
        )
        thickness['entorhinal_thickness_right'] = self._extract_column(
            data, ['entorhinal_thickness_right', 'Right_EC_Thickness', 'EC_THICK_RIGHT']
        )
        
        # Mean entorhinal thickness
        if 'entorhinal_thickness_left' in thickness.columns and 'entorhinal_thickness_right' in thickness.columns:
            thickness['entorhinal_thickness_mean'] = thickness[[
                'entorhinal_thickness_left', 
                'entorhinal_thickness_right'
            ]].mean(axis=1)
        
        # Temporal cortex thickness
        thickness['temporal_thickness_left'] = self._extract_column(
            data, ['temporal_thickness_left', 'Left_Temporal_Thickness', 'TEMP_THICK_LEFT']
        )
        thickness['temporal_thickness_right'] = self._extract_column(
            data, ['temporal_thickness_right', 'Right_Temporal_Thickness', 'TEMP_THICK_RIGHT']
        )
        
        # Parietal cortex thickness
        thickness['parietal_thickness_left'] = self._extract_column(
            data, ['parietal_thickness_left', 'Left_Parietal_Thickness', 'PAR_THICK_LEFT']
        )
        thickness['parietal_thickness_right'] = self._extract_column(
            data, ['parietal_thickness_right', 'Right_Parietal_Thickness', 'PAR_THICK_RIGHT']
        )
        
        # Mean cortical thickness
        thickness_cols = [col for col in thickness.columns if 'thickness' in col and 'mean' not in col]
        if thickness_cols:
            thickness['mean_cortical_thickness'] = thickness[thickness_cols].mean(axis=1)
        
        return thickness
    
    def normalize_by_icv(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize volumetric features by intracranial volume
        
        This accounts for individual differences in head size
        
        Args:
            features: DataFrame with volume features
            
        Returns:
            DataFrame with normalized volume features
        """
        normalized = pd.DataFrame(index=features.index)
        
        if 'intracranial_volume' not in features.columns:
            logger.warning("Intracranial volume not available, skipping normalization")
            return normalized
        
        # Avoid division by zero
        icv_safe = features['intracranial_volume'].replace(0, np.nan)
        
        # Normalize all volume features
        volume_features = [
            'hippocampus_left', 'hippocampus_right', 'hippocampus_total',
            'entorhinal_cortex_left', 'entorhinal_cortex_right',
            'amygdala_left', 'amygdala_right',
            'ventricles', 'whole_brain',
            'temporal_lobe_left', 'temporal_lobe_right',
            'parietal_lobe_left', 'parietal_lobe_right',
            'frontal_lobe_left', 'frontal_lobe_right'
        ]
        
        for vol_feature in volume_features:
            if vol_feature in features.columns:
                normalized[f'{vol_feature}_norm'] = features[vol_feature] / icv_safe
        
        return normalized
    
    def calculate_derived_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived imaging features
        
        Args:
            features: DataFrame with base imaging features
            
        Returns:
            DataFrame with derived features
        """
        derived = pd.DataFrame(index=features.index)
        
        # Hippocampal asymmetry
        if 'hippocampus_left' in features.columns and 'hippocampus_right' in features.columns:
            left = features['hippocampus_left']
            right = features['hippocampus_right']
            total = left + right
            total_safe = total.replace(0, np.nan)
            derived['hippocampus_asymmetry'] = (left - right) / total_safe
        
        # Brain atrophy index (ventricle-to-brain ratio)
        if 'ventricles' in features.columns and 'whole_brain' in features.columns:
            brain_safe = features['whole_brain'].replace(0, np.nan)
            derived['ventricle_brain_ratio'] = features['ventricles'] / brain_safe
        
        # Medial temporal lobe atrophy score
        if 'hippocampus_total' in features.columns and 'entorhinal_cortex_left' in features.columns:
            # Simplified atrophy score (lower values = more atrophy)
            derived['mtl_atrophy_score'] = (
                features['hippocampus_total'].fillna(0) + 
                features['entorhinal_cortex_left'].fillna(0) +
                features['entorhinal_cortex_right'].fillna(0)
            )
        
        return derived
    
    def parse_dicom_file(self, dicom_path: Path) -> Dict[str, float]:
        """
        Parse DICOM file and extract volumetric measurements
        
        Note: This is a placeholder for actual DICOM processing.
        In production, this would use PyDICOM and FreeSurfer/FSL for segmentation.
        
        Args:
            dicom_path: Path to DICOM file
            
        Returns:
            Dictionary of extracted volumes
        """
        try:
            import pydicom
            
            # Read DICOM file
            dcm = pydicom.dcmread(dicom_path)
            
            # In production, this would:
            # 1. Load the MRI scan
            # 2. Run segmentation (FreeSurfer, FSL, or deep learning model)
            # 3. Calculate volumes for each region
            # 4. Return measurements
            
            logger.warning("DICOM parsing not fully implemented - returning placeholder values")
            return {}
            
        except ImportError:
            logger.error("PyDICOM not installed. Install with: pip install pydicom")
            return {}
        except Exception as e:
            logger.error(f"Error parsing DICOM file {dicom_path}: {e}")
            return {}
    
    def _extract_column(self, data: pd.DataFrame, column_names: List[str]) -> pd.Series:
        """
        Extract column trying multiple possible names
        
        Args:
            data: DataFrame to search
            column_names: List of possible column names
            
        Returns:
            Series with extracted values or NaN
        """
        for col in column_names:
            if col in data.columns:
                return data[col]
        
        return pd.Series(np.nan, index=data.index)
    
    def get_feature_names(self) -> List[str]:
        """Get list of extracted feature names"""
        return self.feature_columns
    
    def validate_features(self, features: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate extracted imaging features
        
        Args:
            features: DataFrame with extracted features
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Check that volumes are positive
        volume_features = [col for col in features.columns if 'volume' in col.lower() or 'hippocampus' in col]
        for vol_feature in volume_features:
            if vol_feature in features.columns:
                validation[f'{vol_feature}_positive'] = (features[vol_feature] >= 0).all()
        
        # Check that thickness values are reasonable (0-10 mm)
        thickness_features = [col for col in features.columns if 'thickness' in col]
        for thick_feature in thickness_features:
            if thick_feature in features.columns:
                validation[f'{thick_feature}_valid'] = features[thick_feature].between(0, 10, inclusive='both').all()
        
        # Check that normalized values are between 0 and 1
        norm_features = [col for col in features.columns if '_norm' in col]
        for norm_feature in norm_features:
            if norm_feature in features.columns:
                validation[f'{norm_feature}_valid'] = features[norm_feature].between(0, 1, inclusive='both').all()
        
        return validation
