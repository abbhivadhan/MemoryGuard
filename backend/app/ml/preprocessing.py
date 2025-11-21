"""
Feature preprocessing pipeline for Alzheimer's ML models.
Handles feature extraction, missing data imputation, and normalization.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer, KNNImputer
import logging

logger = logging.getLogger(__name__)


class FeaturePreprocessor:
    """
    Preprocesses health metrics data for ML model input.
    Handles feature extraction, missing data imputation, and scaling.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = KNNImputer(n_neighbors=5)
        self.feature_names: List[str] = []
        self.is_fitted = False
        
        # Define expected feature categories
        self.cognitive_features = [
            'mmse_score',  # 0-30
            'moca_score',  # 0-30
            'cdr_score',   # 0-3
        ]
        
        self.biomarker_features = [
            'csf_abeta42',      # pg/mL
            'csf_tau',          # pg/mL
            'csf_ptau',         # pg/mL
            'tau_abeta_ratio',  # Calculated
        ]
        
        self.imaging_features = [
            'hippocampal_volume',    # mm³
            'entorhinal_thickness',  # mm
            'cortical_thickness',    # mm
            'ventricular_volume',    # mm³
        ]
        
        self.demographic_features = [
            'age',              # years
            'education_years',  # years
            'apoe4_alleles',    # 0, 1, or 2
        ]
        
        self.lifestyle_features = [
            'physical_activity_minutes',  # minutes/week
            'sleep_hours',                # hours/day
            'social_engagement_score',    # 0-10
            'diet_quality_score',         # 0-10
        ]
        
        self.cardiovascular_features = [
            'systolic_bp',      # mmHg
            'diastolic_bp',     # mmHg
            'total_cholesterol', # mg/dL
            'hdl_cholesterol',   # mg/dL
            'ldl_cholesterol',   # mg/dL
            'glucose',           # mg/dL
            'bmi',               # kg/m²
        ]
        
        # Combine all features
        self.all_features = (
            self.cognitive_features +
            self.biomarker_features +
            self.imaging_features +
            self.demographic_features +
            self.lifestyle_features +
            self.cardiovascular_features
        )
    
    def extract_features_from_metrics(
        self, 
        health_metrics: List[Dict]
    ) -> Dict[str, float]:
        """
        Extract features from health metrics data.
        
        Args:
            health_metrics: List of health metric dictionaries
            
        Returns:
            Dictionary of feature names to values
        """
        features = {}
        
        # Group metrics by type
        metrics_by_name = {}
        for metric in health_metrics:
            name = metric.get('name', '').lower().replace(' ', '_')
            value = metric.get('value')
            if name and value is not None:
                metrics_by_name[name] = float(value)
        
        # Extract cognitive features
        features['mmse_score'] = metrics_by_name.get('mmse_score', np.nan)
        features['moca_score'] = metrics_by_name.get('moca_score', np.nan)
        features['cdr_score'] = metrics_by_name.get('cdr_score', np.nan)
        
        # Extract biomarker features
        features['csf_abeta42'] = metrics_by_name.get('csf_abeta42', np.nan)
        features['csf_tau'] = metrics_by_name.get('csf_tau', np.nan)
        features['csf_ptau'] = metrics_by_name.get('csf_ptau', np.nan)
        
        # Calculate tau/abeta ratio if both available
        if not np.isnan(features['csf_tau']) and not np.isnan(features['csf_abeta42']):
            features['tau_abeta_ratio'] = features['csf_tau'] / features['csf_abeta42']
        else:
            features['tau_abeta_ratio'] = np.nan
        
        # Extract imaging features
        features['hippocampal_volume'] = metrics_by_name.get('hippocampal_volume', np.nan)
        features['entorhinal_thickness'] = metrics_by_name.get('entorhinal_thickness', np.nan)
        features['cortical_thickness'] = metrics_by_name.get('cortical_thickness', np.nan)
        features['ventricular_volume'] = metrics_by_name.get('ventricular_volume', np.nan)
        
        # Extract demographic features
        features['age'] = metrics_by_name.get('age', np.nan)
        features['education_years'] = metrics_by_name.get('education_years', np.nan)
        features['apoe4_alleles'] = metrics_by_name.get('apoe4_alleles', np.nan)
        
        # Extract lifestyle features
        features['physical_activity_minutes'] = metrics_by_name.get('physical_activity_minutes', np.nan)
        features['sleep_hours'] = metrics_by_name.get('sleep_hours', np.nan)
        features['social_engagement_score'] = metrics_by_name.get('social_engagement_score', np.nan)
        features['diet_quality_score'] = metrics_by_name.get('diet_quality_score', np.nan)
        
        # Extract cardiovascular features
        features['systolic_bp'] = metrics_by_name.get('systolic_bp', np.nan)
        features['diastolic_bp'] = metrics_by_name.get('diastolic_bp', np.nan)
        features['total_cholesterol'] = metrics_by_name.get('total_cholesterol', np.nan)
        features['hdl_cholesterol'] = metrics_by_name.get('hdl_cholesterol', np.nan)
        features['ldl_cholesterol'] = metrics_by_name.get('ldl_cholesterol', np.nan)
        features['glucose'] = metrics_by_name.get('glucose', np.nan)
        features['bmi'] = metrics_by_name.get('bmi', np.nan)
        
        return features
    
    def validate_features(self, features: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validate that features meet minimum requirements.
        
        Args:
            features: Dictionary of feature names to values
            
        Returns:
            Tuple of (is_valid, list of missing critical features)
        """
        # Critical features that must be present
        critical_features = [
            'age',
            'mmse_score',
        ]
        
        missing_critical = []
        for feature in critical_features:
            if feature not in features or np.isnan(features[feature]):
                missing_critical.append(feature)
        
        is_valid = len(missing_critical) == 0
        
        # Check for minimum data completeness (at least 50% of features)
        total_features = len(self.all_features)
        present_features = sum(
            1 for f in self.all_features 
            if f in features and not np.isnan(features[f])
        )
        
        completeness = present_features / total_features
        if completeness < 0.5:
            is_valid = False
            missing_critical.append(f"Insufficient data: only {completeness:.1%} complete")
        
        return is_valid, missing_critical
    
    def impute_missing_values(
        self, 
        features_df: pd.DataFrame,
        method: str = 'knn'
    ) -> pd.DataFrame:
        """
        Impute missing values in features.
        
        Args:
            features_df: DataFrame with features
            method: Imputation method ('knn', 'mean', 'median')
            
        Returns:
            DataFrame with imputed values
        """
        if method == 'knn':
            imputer = KNNImputer(n_neighbors=5, weights='distance')
        elif method == 'mean':
            imputer = SimpleImputer(strategy='mean')
        elif method == 'median':
            imputer = SimpleImputer(strategy='median')
        else:
            raise ValueError(f"Unknown imputation method: {method}")
        
        # Impute missing values
        imputed_values = imputer.fit_transform(features_df)
        imputed_df = pd.DataFrame(
            imputed_values,
            columns=features_df.columns,
            index=features_df.index
        )
        
        return imputed_df
    
    def normalize_features(
        self, 
        features_df: pd.DataFrame,
        method: str = 'standard'
    ) -> pd.DataFrame:
        """
        Normalize/scale features.
        
        Args:
            features_df: DataFrame with features
            method: Scaling method ('standard', 'minmax')
            
        Returns:
            DataFrame with normalized values
        """
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
        
        # Scale features
        scaled_values = scaler.fit_transform(features_df)
        scaled_df = pd.DataFrame(
            scaled_values,
            columns=features_df.columns,
            index=features_df.index
        )
        
        return scaled_df
    
    def fit(self, features_list: List[Dict[str, float]]) -> 'FeaturePreprocessor':
        """
        Fit the preprocessor on training data.
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            Self for chaining
        """
        # Convert to DataFrame
        df = pd.DataFrame(features_list)
        
        # Ensure all expected features are present
        for feature in self.all_features:
            if feature not in df.columns:
                df[feature] = np.nan
        
        # Reorder columns
        df = df[self.all_features]
        
        # Fit imputer
        self.imputer.fit(df)
        
        # Impute for fitting scaler
        imputed_df = pd.DataFrame(
            self.imputer.transform(df),
            columns=df.columns
        )
        
        # Fit scaler
        self.scaler.fit(imputed_df)
        
        self.feature_names = self.all_features
        self.is_fitted = True
        
        logger.info(f"Preprocessor fitted on {len(features_list)} samples")
        
        return self
    
    def transform(self, features: Dict[str, float]) -> np.ndarray:
        """
        Transform features for model input.
        
        Args:
            features: Dictionary of feature names to values
            
        Returns:
            Numpy array of preprocessed features
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        # Create DataFrame with single row
        df = pd.DataFrame([features])
        
        # Ensure all expected features are present
        for feature in self.all_features:
            if feature not in df.columns:
                df[feature] = np.nan
        
        # Reorder columns
        df = df[self.all_features]
        
        # Impute missing values
        imputed_df = pd.DataFrame(
            self.imputer.transform(df),
            columns=df.columns
        )
        
        # Scale features
        scaled_values = self.scaler.transform(imputed_df)
        
        return scaled_values[0]
    
    def fit_transform(
        self, 
        features_list: List[Dict[str, float]]
    ) -> np.ndarray:
        """
        Fit preprocessor and transform features in one step.
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            Numpy array of preprocessed features
        """
        self.fit(features_list)
        
        # Transform all features
        df = pd.DataFrame(features_list)
        
        # Ensure all expected features are present
        for feature in self.all_features:
            if feature not in df.columns:
                df[feature] = np.nan
        
        # Reorder columns
        df = df[self.all_features]
        
        # Impute missing values
        imputed_df = pd.DataFrame(
            self.imputer.transform(df),
            columns=df.columns
        )
        
        # Scale features
        scaled_values = self.scaler.transform(imputed_df)
        
        return scaled_values
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names in order."""
        return self.feature_names.copy()
    
    def get_feature_importance_map(
        self, 
        importance_values: np.ndarray
    ) -> Dict[str, float]:
        """
        Map feature importance values to feature names.
        
        Args:
            importance_values: Array of importance values
            
        Returns:
            Dictionary mapping feature names to importance
        """
        if len(importance_values) != len(self.feature_names):
            raise ValueError(
                f"Importance values length {len(importance_values)} "
                f"doesn't match features length {len(self.feature_names)}"
            )
        
        return dict(zip(self.feature_names, importance_values))
