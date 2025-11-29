"""
Feature Normalization

Normalizes continuous features using various techniques:
- Standardization (z-score normalization)
- Min-Max scaling
- Robust scaling (using median and IQR)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureNormalizer:
    """Normalize continuous features for machine learning"""
    
    def __init__(self, method: str = 'standard', exclude_binary: bool = True):
        """
        Initialize feature normalizer
        
        Args:
            method: Normalization method ('standard', 'minmax', 'robust')
            exclude_binary: Whether to exclude binary features from normalization
        """
        self.method = method
        self.exclude_binary = exclude_binary
        self.scaler = None
        self.feature_columns = []
        self.binary_columns = []
        
    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Fit normalizer and transform data
        
        Args:
            data: DataFrame with features to normalize
            
        Returns:
            DataFrame with normalized features
        """
        logger.info(f"Normalizing features using {self.method} method")
        
        # Identify binary features to exclude
        if self.exclude_binary:
            self.binary_columns = self._identify_binary_features(data)
            logger.info(f"Excluding {len(self.binary_columns)} binary features from normalization")
        
        # Separate features to normalize
        features_to_normalize = [
            col for col in data.columns 
            if col not in self.binary_columns
        ]
        self.feature_columns = features_to_normalize
        
        # Normalize
        normalized_data = data.copy()
        
        if features_to_normalize:
            if self.method == 'standard':
                normalized_data[features_to_normalize] = self._standardize(
                    data[features_to_normalize]
                )
            elif self.method == 'minmax':
                normalized_data[features_to_normalize] = self._minmax_scale(
                    data[features_to_normalize]
                )
            elif self.method == 'robust':
                normalized_data[features_to_normalize] = self._robust_scale(
                    data[features_to_normalize]
                )
            else:
                raise ValueError(f"Unknown normalization method: {self.method}")
        
        logger.info("Feature normalization complete")
        return normalized_data
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted normalizer
        
        Args:
            data: DataFrame with features to normalize
            
        Returns:
            DataFrame with normalized features
        """
        if self.scaler is None:
            raise ValueError("Normalizer not fitted. Call fit_transform first.")
        
        normalized_data = data.copy()
        
        if self.feature_columns:
            normalized_array = self.scaler.transform(data[self.feature_columns])
            normalized_data[self.feature_columns] = normalized_array
        
        return normalized_data
    
    def _identify_binary_features(self, data: pd.DataFrame) -> List[str]:
        """
        Identify binary features (only contain 0 and 1)
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            List of binary feature column names
        """
        binary_cols = []
        
        for col in data.columns:
            unique_values = data[col].dropna().unique()
            
            # Check if only contains 0 and 1
            if len(unique_values) <= 2 and set(unique_values).issubset({0, 1, 0.0, 1.0}):
                binary_cols.append(col)
        
        return binary_cols
    
    def _standardize(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize features using z-score normalization
        
        Formula: z = (x - mean) / std
        
        This transforms features to have mean=0 and std=1
        
        Args:
            data: DataFrame with features to standardize
            
        Returns:
            DataFrame with standardized features
        """
        from sklearn.preprocessing import StandardScaler
        
        if self.scaler is None:
            self.scaler = StandardScaler()
            standardized_array = self.scaler.fit_transform(data)
        else:
            standardized_array = self.scaler.transform(data)
        
        return pd.DataFrame(
            standardized_array,
            columns=data.columns,
            index=data.index
        )
    
    def _minmax_scale(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Scale features to [0, 1] range using min-max scaling
        
        Formula: x_scaled = (x - min) / (max - min)
        
        Args:
            data: DataFrame with features to scale
            
        Returns:
            DataFrame with scaled features
        """
        from sklearn.preprocessing import MinMaxScaler
        
        if self.scaler is None:
            self.scaler = MinMaxScaler()
            scaled_array = self.scaler.fit_transform(data)
        else:
            scaled_array = self.scaler.transform(data)
        
        return pd.DataFrame(
            scaled_array,
            columns=data.columns,
            index=data.index
        )
    
    def _robust_scale(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Scale features using median and IQR (robust to outliers)
        
        Formula: x_scaled = (x - median) / IQR
        
        This method is more robust to outliers than standard scaling
        
        Args:
            data: DataFrame with features to scale
            
        Returns:
            DataFrame with scaled features
        """
        from sklearn.preprocessing import RobustScaler
        
        if self.scaler is None:
            self.scaler = RobustScaler()
            scaled_array = self.scaler.fit_transform(data)
        else:
            scaled_array = self.scaler.transform(data)
        
        return pd.DataFrame(
            scaled_array,
            columns=data.columns,
            index=data.index
        )
    
    def get_scaling_parameters(self) -> Dict[str, Dict[str, float]]:
        """
        Get scaling parameters for each feature
        
        Returns:
            Dictionary with scaling parameters
        """
        if self.scaler is None:
            raise ValueError("Normalizer not fitted")
        
        params = {}
        
        if self.method == 'standard':
            for i, col in enumerate(self.feature_columns):
                params[col] = {
                    'mean': self.scaler.mean_[i],
                    'std': self.scaler.scale_[i]
                }
        
        elif self.method == 'minmax':
            for i, col in enumerate(self.feature_columns):
                params[col] = {
                    'min': self.scaler.data_min_[i],
                    'max': self.scaler.data_max_[i],
                    'scale': self.scaler.scale_[i]
                }
        
        elif self.method == 'robust':
            for i, col in enumerate(self.feature_columns):
                params[col] = {
                    'median': self.scaler.center_[i],
                    'iqr': self.scaler.scale_[i]
                }
        
        return params
    
    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform normalized features back to original scale
        
        Args:
            data: DataFrame with normalized features
            
        Returns:
            DataFrame with features in original scale
        """
        if self.scaler is None:
            raise ValueError("Normalizer not fitted")
        
        original_data = data.copy()
        
        if self.feature_columns:
            original_array = self.scaler.inverse_transform(data[self.feature_columns])
            original_data[self.feature_columns] = original_array
        
        return original_data
    
    def validate_normalization(
        self,
        original: pd.DataFrame,
        normalized: pd.DataFrame
    ) -> Dict[str, bool]:
        """
        Validate that normalization was successful
        
        Args:
            original: Original DataFrame
            normalized: Normalized DataFrame
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Check that binary features weren't normalized
        for col in self.binary_columns:
            if col in normalized.columns:
                validation[f'{col}_unchanged'] = original[col].equals(normalized[col])
        
        # Check that normalized features have expected properties
        for col in self.feature_columns:
            if col in normalized.columns:
                if self.method == 'standard':
                    # Should have mean ≈ 0 and std ≈ 1
                    mean = normalized[col].mean()
                    std = normalized[col].std()
                    validation[f'{col}_mean_zero'] = abs(mean) < 0.1
                    validation[f'{col}_std_one'] = abs(std - 1.0) < 0.1
                
                elif self.method == 'minmax':
                    # Should be in [0, 1] range
                    validation[f'{col}_in_range'] = (
                        normalized[col].min() >= 0 and
                        normalized[col].max() <= 1
                    )
                
                elif self.method == 'robust':
                    # Median should be ≈ 0
                    median = normalized[col].median()
                    validation[f'{col}_median_zero'] = abs(median) < 0.1
        
        return validation
    
    def get_feature_statistics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Get statistics for all features before and after normalization
        
        Args:
            data: DataFrame with features
            
        Returns:
            DataFrame with feature statistics
        """
        stats = pd.DataFrame({
            'feature': data.columns,
            'mean': data.mean().values,
            'std': data.std().values,
            'min': data.min().values,
            'max': data.max().values,
            'median': data.median().values,
            'is_binary': [col in self.binary_columns for col in data.columns]
        })
        
        return stats
