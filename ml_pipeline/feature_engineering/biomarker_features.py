"""
Biomarker Feature Processing

Processes CSF (Cerebrospinal Fluid) biomarker data including:
- Amyloid-beta 42 (Aβ42)
- Total Tau (t-Tau)
- Phosphorylated Tau (p-Tau)
- Biomarker ratios
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class BiomarkerFeatureProcessor:
    """Process CSF biomarker features"""
    
    def __init__(self):
        """Initialize biomarker feature processor"""
        self.feature_columns = []
        
        # Reference ranges for biomarkers (pg/mL)
        self.reference_ranges = {
            'csf_ab42': (0, 2000),
            'csf_tau': (0, 1500),
            'csf_ptau': (0, 150)
        }
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all biomarker features from raw data
        
        Args:
            data: Raw dataframe containing CSF biomarker measurements
            
        Returns:
            DataFrame with extracted biomarker features
        """
        logger.info("Extracting biomarker features")
        
        features = pd.DataFrame(index=data.index)
        
        # Extract individual biomarkers
        features['csf_ab42'] = self.extract_ab42(data)
        features['csf_tau'] = self.extract_tau(data)
        features['csf_ptau'] = self.extract_ptau(data)
        
        # Calculate ratios
        ratio_features = self.calculate_ratios(features)
        features = pd.concat([features, ratio_features], axis=1)
        
        # Create biomarker profile indicators
        profile_features = self.create_biomarker_profiles(features)
        features = pd.concat([features, profile_features], axis=1)
        
        self.feature_columns = features.columns.tolist()
        
        logger.info(f"Extracted {len(self.feature_columns)} biomarker features")
        return features
    
    def extract_ab42(self, data: pd.DataFrame) -> pd.Series:
        """
        Extract CSF Amyloid-beta 42 levels
        
        Aβ42 is a key biomarker for Alzheimer's disease. Lower levels
        indicate amyloid plaque accumulation in the brain.
        
        Normal range: typically > 550 pg/mL
        AD range: typically < 500 pg/mL
        
        Args:
            data: Raw dataframe
            
        Returns:
            Series with Aβ42 values
        """
        # Try different column name variations
        ab42_columns = ['CSF_AB42', 'csf_ab42', 'ABETA42', 'AB42', 'Abeta42']
        
        for col in ab42_columns:
            if col in data.columns:
                values = data[col].copy()
                # Validate range
                values = values.clip(
                    self.reference_ranges['csf_ab42'][0],
                    self.reference_ranges['csf_ab42'][1]
                )
                return values
        
        return pd.Series(np.nan, index=data.index)
    
    def extract_tau(self, data: pd.DataFrame) -> pd.Series:
        """
        Extract CSF Total Tau levels
        
        Total Tau is elevated in neurodegeneration. Higher levels
        indicate neuronal damage.
        
        Normal range: typically < 300 pg/mL
        AD range: typically > 400 pg/mL
        
        Args:
            data: Raw dataframe
            
        Returns:
            Series with Total Tau values
        """
        # Try different column name variations
        tau_columns = ['CSF_TAU', 'csf_tau', 'TAU', 'TTAU', 'TotalTau']
        
        for col in tau_columns:
            if col in data.columns:
                values = data[col].copy()
                # Validate range
                values = values.clip(
                    self.reference_ranges['csf_tau'][0],
                    self.reference_ranges['csf_tau'][1]
                )
                return values
        
        return pd.Series(np.nan, index=data.index)
    
    def extract_ptau(self, data: pd.DataFrame) -> pd.Series:
        """
        Extract CSF Phosphorylated Tau levels
        
        p-Tau is specifically elevated in Alzheimer's disease and
        correlates with tangle pathology.
        
        Normal range: typically < 60 pg/mL
        AD range: typically > 80 pg/mL
        
        Args:
            data: Raw dataframe
            
        Returns:
            Series with p-Tau values
        """
        # Try different column name variations
        ptau_columns = ['CSF_PTAU', 'csf_ptau', 'PTAU', 'PTau181', 'pTau']
        
        for col in ptau_columns:
            if col in data.columns:
                values = data[col].copy()
                # Validate range
                values = values.clip(
                    self.reference_ranges['csf_ptau'][0],
                    self.reference_ranges['csf_ptau'][1]
                )
                return values
        
        return pd.Series(np.nan, index=data.index)
    
    def calculate_ratios(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate biomarker ratios
        
        Ratios are often more informative than absolute values:
        - Aβ42/Tau ratio: Lower in AD
        - p-Tau/Tau ratio: Indicates proportion of phosphorylated tau
        - Tau/Aβ42 ratio: Higher in AD (inverse of Aβ42/Tau)
        
        Args:
            features: DataFrame with individual biomarker values
            
        Returns:
            DataFrame with calculated ratios
        """
        ratios = pd.DataFrame(index=features.index)
        
        # Aβ42/Tau ratio
        if 'csf_ab42' in features.columns and 'csf_tau' in features.columns:
            # Avoid division by zero
            tau_safe = features['csf_tau'].replace(0, np.nan)
            ratios['ab42_tau_ratio'] = features['csf_ab42'] / tau_safe
            
            # Also calculate inverse (Tau/Aβ42)
            ab42_safe = features['csf_ab42'].replace(0, np.nan)
            ratios['tau_ab42_ratio'] = features['csf_tau'] / ab42_safe
        
        # p-Tau/Tau ratio
        if 'csf_ptau' in features.columns and 'csf_tau' in features.columns:
            tau_safe = features['csf_tau'].replace(0, np.nan)
            ratios['ptau_tau_ratio'] = features['csf_ptau'] / tau_safe
        
        # Aβ42/p-Tau ratio
        if 'csf_ab42' in features.columns and 'csf_ptau' in features.columns:
            ptau_safe = features['csf_ptau'].replace(0, np.nan)
            ratios['ab42_ptau_ratio'] = features['csf_ab42'] / ptau_safe
        
        return ratios
    
    def create_biomarker_profiles(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Create biomarker profile indicators
        
        Classify biomarker patterns based on established cutoffs:
        - AD profile: Low Aβ42, High Tau, High p-Tau
        - Normal profile: Normal levels of all biomarkers
        
        Args:
            features: DataFrame with biomarker values and ratios
            
        Returns:
            DataFrame with profile indicators
        """
        profiles = pd.DataFrame(index=features.index)
        
        # Amyloid positivity (low Aβ42)
        if 'csf_ab42' in features.columns:
            profiles['amyloid_positive'] = (features['csf_ab42'] < 500).astype(float)
        
        # Tau positivity (high Tau)
        if 'csf_tau' in features.columns:
            profiles['tau_positive'] = (features['csf_tau'] > 400).astype(float)
        
        # p-Tau positivity (high p-Tau)
        if 'csf_ptau' in features.columns:
            profiles['ptau_positive'] = (features['csf_ptau'] > 80).astype(float)
        
        # AD biomarker profile (A+T+)
        if all(col in profiles.columns for col in ['amyloid_positive', 'tau_positive']):
            profiles['ad_biomarker_profile'] = (
                (profiles['amyloid_positive'] == 1) & 
                (profiles['tau_positive'] == 1)
            ).astype(float)
        
        # Ratio-based indicators
        if 'ab42_tau_ratio' in features.columns:
            # Low ratio indicates AD
            profiles['ab42_tau_ratio_abnormal'] = (features['ab42_tau_ratio'] < 1.0).astype(float)
        
        return profiles
    
    def get_feature_names(self) -> List[str]:
        """Get list of extracted feature names"""
        return self.feature_columns
    
    def validate_features(self, features: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate extracted biomarker features
        
        Args:
            features: DataFrame with extracted features
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Check Aβ42 range
        if 'csf_ab42' in features.columns:
            validation['ab42_valid'] = features['csf_ab42'].between(
                self.reference_ranges['csf_ab42'][0],
                self.reference_ranges['csf_ab42'][1],
                inclusive='both'
            ).all()
        
        # Check Tau range
        if 'csf_tau' in features.columns:
            validation['tau_valid'] = features['csf_tau'].between(
                self.reference_ranges['csf_tau'][0],
                self.reference_ranges['csf_tau'][1],
                inclusive='both'
            ).all()
        
        # Check p-Tau range
        if 'csf_ptau' in features.columns:
            validation['ptau_valid'] = features['csf_ptau'].between(
                self.reference_ranges['csf_ptau'][0],
                self.reference_ranges['csf_ptau'][1],
                inclusive='both'
            ).all()
        
        # Check ratios are positive
        if 'ab42_tau_ratio' in features.columns:
            validation['ab42_tau_ratio_positive'] = (features['ab42_tau_ratio'] >= 0).all()
        
        if 'ptau_tau_ratio' in features.columns:
            validation['ptau_tau_ratio_positive'] = (features['ptau_tau_ratio'] >= 0).all()
        
        return validation
