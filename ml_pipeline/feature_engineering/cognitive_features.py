"""
Cognitive Feature Extraction

Extracts cognitive assessment scores from raw biomedical data including:
- MMSE (Mini-Mental State Examination)
- MoCA (Montreal Cognitive Assessment)
- CDR (Clinical Dementia Rating)
- ADAS-Cog (Alzheimer's Disease Assessment Scale - Cognitive)
- Individual test component scores
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CognitiveFeatureExtractor:
    """Extract and process cognitive assessment features"""
    
    def __init__(self):
        """Initialize cognitive feature extractor"""
        self.feature_columns = []
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all cognitive features from raw data
        
        Args:
            data: Raw dataframe containing cognitive assessments
            
        Returns:
            DataFrame with extracted cognitive features
        """
        logger.info("Extracting cognitive features")
        
        features = pd.DataFrame(index=data.index)
        
        # Extract MMSE scores
        mmse_features = self.extract_mmse(data)
        features = pd.concat([features, mmse_features], axis=1)
        
        # Extract MoCA scores
        moca_features = self.extract_moca(data)
        features = pd.concat([features, moca_features], axis=1)
        
        # Extract CDR scores
        cdr_features = self.extract_cdr(data)
        features = pd.concat([features, cdr_features], axis=1)
        
        # Extract ADAS-Cog scores
        adas_features = self.extract_adas_cog(data)
        features = pd.concat([features, adas_features], axis=1)
        
        # Extract component scores
        component_features = self.extract_component_scores(data)
        features = pd.concat([features, component_features], axis=1)
        
        self.feature_columns = features.columns.tolist()
        
        logger.info(f"Extracted {len(self.feature_columns)} cognitive features")
        return features
    
    def extract_mmse(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract MMSE (Mini-Mental State Examination) scores
        
        MMSE is scored 0-30, with lower scores indicating greater impairment:
        - 24-30: Normal cognition
        - 18-23: Mild cognitive impairment
        - 0-17: Severe cognitive impairment
        
        Args:
            data: Raw dataframe
            
        Returns:
            DataFrame with MMSE features
        """
        features = pd.DataFrame(index=data.index)
        
        # Total MMSE score
        if 'MMSE' in data.columns:
            features['mmse_total'] = data['MMSE']
        elif 'mmse_total' in data.columns:
            features['mmse_total'] = data['mmse_total']
        elif 'MMSCORE' in data.columns:
            features['mmse_total'] = data['MMSCORE']
        else:
            features['mmse_total'] = np.nan
            
        # Validate MMSE range (0-30)
        if 'mmse_total' in features.columns:
            features['mmse_total'] = features['mmse_total'].clip(0, 30)
            
            # Create categorical severity
            features['mmse_severity'] = pd.cut(
                features['mmse_total'],
                bins=[-1, 17, 23, 30],
                labels=[2, 1, 0]  # 2=severe, 1=mild, 0=normal
            ).astype(float)
            
            # Normalized score (0-1)
            features['mmse_normalized'] = features['mmse_total'] / 30.0
        
        return features
    
    def extract_moca(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract MoCA (Montreal Cognitive Assessment) scores
        
        MoCA is scored 0-30, with a score of 26 or above considered normal
        
        Args:
            data: Raw dataframe
            
        Returns:
            DataFrame with MoCA features
        """
        features = pd.DataFrame(index=data.index)
        
        # Total MoCA score
        if 'MoCA' in data.columns:
            features['moca_total'] = data['MoCA']
        elif 'moca_total' in data.columns:
            features['moca_total'] = data['moca_total']
        elif 'MOCA' in data.columns:
            features['moca_total'] = data['MOCA']
        else:
            features['moca_total'] = np.nan
            
        # Validate MoCA range (0-30)
        if 'moca_total' in features.columns:
            features['moca_total'] = features['moca_total'].clip(0, 30)
            
            # Binary impairment indicator (< 26 = impaired)
            features['moca_impaired'] = (features['moca_total'] < 26).astype(float)
            
            # Normalized score (0-1)
            features['moca_normalized'] = features['moca_total'] / 30.0
        
        return features
    
    def extract_cdr(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract CDR (Clinical Dementia Rating) scores
        
        CDR global score ranges from 0-3:
        - 0: No dementia
        - 0.5: Questionable dementia
        - 1: Mild dementia
        - 2: Moderate dementia
        - 3: Severe dementia
        
        Args:
            data: Raw dataframe
            
        Returns:
            DataFrame with CDR features
        """
        features = pd.DataFrame(index=data.index)
        
        # CDR global score
        if 'CDR' in data.columns:
            features['cdr_global'] = data['CDR']
        elif 'cdr_global' in data.columns:
            features['cdr_global'] = data['cdr_global']
        elif 'CDGLOBAL' in data.columns:
            features['cdr_global'] = data['CDGLOBAL']
        else:
            features['cdr_global'] = np.nan
            
        # Validate CDR range (0-3)
        if 'cdr_global' in features.columns:
            features['cdr_global'] = features['cdr_global'].clip(0, 3)
            
            # Binary dementia indicator (>= 1 = dementia)
            features['cdr_dementia'] = (features['cdr_global'] >= 1).astype(float)
            
            # CDR Sum of Boxes (if available)
            if 'CDRSB' in data.columns:
                features['cdr_sum_boxes'] = data['CDRSB'].clip(0, 18)
            elif 'cdr_sum_boxes' in data.columns:
                features['cdr_sum_boxes'] = data['cdr_sum_boxes'].clip(0, 18)
        
        return features
    
    def extract_adas_cog(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract ADAS-Cog (Alzheimer's Disease Assessment Scale - Cognitive) scores
        
        ADAS-Cog ranges from 0-70, with higher scores indicating greater impairment
        
        Args:
            data: Raw dataframe
            
        Returns:
            DataFrame with ADAS-Cog features
        """
        features = pd.DataFrame(index=data.index)
        
        # Total ADAS-Cog score
        if 'ADAS_Cog' in data.columns:
            features['adas_cog_total'] = data['ADAS_Cog']
        elif 'adas_cog_total' in data.columns:
            features['adas_cog_total'] = data['adas_cog_total']
        elif 'ADAS11' in data.columns:
            features['adas_cog_total'] = data['ADAS11']
        elif 'ADAS13' in data.columns:
            features['adas_cog_total'] = data['ADAS13']
        else:
            features['adas_cog_total'] = np.nan
            
        # Validate ADAS-Cog range (0-70)
        if 'adas_cog_total' in features.columns:
            features['adas_cog_total'] = features['adas_cog_total'].clip(0, 70)
            
            # Normalized score (0-1, inverted so higher = better)
            features['adas_cog_normalized'] = 1 - (features['adas_cog_total'] / 70.0)
        
        return features
    
    def extract_component_scores(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract individual test component scores
        
        Args:
            data: Raw dataframe
            
        Returns:
            DataFrame with component scores
        """
        features = pd.DataFrame(index=data.index)
        
        # MMSE components (if available)
        mmse_components = [
            'mmse_orientation',
            'mmse_registration',
            'mmse_attention',
            'mmse_recall',
            'mmse_language'
        ]
        
        for component in mmse_components:
            if component in data.columns:
                features[component] = data[component]
        
        # MoCA components (if available)
        moca_components = [
            'moca_visuospatial',
            'moca_naming',
            'moca_attention',
            'moca_language',
            'moca_abstraction',
            'moca_memory',
            'moca_orientation'
        ]
        
        for component in moca_components:
            if component in data.columns:
                features[component] = data[component]
        
        # CDR domain scores (if available)
        cdr_domains = [
            'cdr_memory',
            'cdr_orientation',
            'cdr_judgment',
            'cdr_community',
            'cdr_home',
            'cdr_personal_care'
        ]
        
        for domain in cdr_domains:
            if domain in data.columns:
                features[domain] = data[domain]
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get list of extracted feature names"""
        return self.feature_columns
    
    def validate_features(self, features: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate extracted features
        
        Args:
            features: DataFrame with extracted features
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Check MMSE range
        if 'mmse_total' in features.columns:
            validation['mmse_valid'] = features['mmse_total'].between(0, 30, inclusive='both').all()
        
        # Check MoCA range
        if 'moca_total' in features.columns:
            validation['moca_valid'] = features['moca_total'].between(0, 30, inclusive='both').all()
        
        # Check CDR range
        if 'cdr_global' in features.columns:
            validation['cdr_valid'] = features['cdr_global'].between(0, 3, inclusive='both').all()
        
        # Check ADAS-Cog range
        if 'adas_cog_total' in features.columns:
            validation['adas_cog_valid'] = features['adas_cog_total'].between(0, 70, inclusive='both').all()
        
        return validation
