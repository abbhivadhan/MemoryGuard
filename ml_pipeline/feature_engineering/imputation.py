"""
Missing Data Imputation

Handles missing values in biomedical data using multiple imputation techniques:
- Simple imputation (mean, median, mode)
- Multiple imputation (MICE - Multivariate Imputation by Chained Equations)
- K-Nearest Neighbors imputation
- Indicator variables for missingness patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MissingDataImputer:
    """Handle missing data using multiple imputation techniques"""
    
    def __init__(self, strategy: str = 'iterative', add_indicators: bool = True):
        """
        Initialize missing data imputer
        
        Args:
            strategy: Imputation strategy ('mean', 'median', 'iterative', 'knn')
            add_indicators: Whether to add binary indicators for missing values
        """
        self.strategy = strategy
        self.add_indicators = add_indicators
        self.imputer = None
        self.missing_indicators = {}
        
    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Fit imputer and transform data
        
        Args:
            data: DataFrame with missing values
            
        Returns:
            DataFrame with imputed values
        """
        logger.info(f"Imputing missing data using {self.strategy} strategy")
        
        # Analyze missingness patterns
        self._analyze_missingness(data)
        
        # Add missingness indicators if requested
        if self.add_indicators:
            indicator_features = self._create_missing_indicators(data)
        
        # Perform imputation
        imputed_data = self._impute(data)
        
        # Add indicators back
        if self.add_indicators:
            imputed_data = pd.concat([imputed_data, indicator_features], axis=1)
        
        logger.info("Missing data imputation complete")
        return imputed_data
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted imputer
        
        Args:
            data: DataFrame with missing values
            
        Returns:
            DataFrame with imputed values
        """
        if self.imputer is None:
            raise ValueError("Imputer not fitted. Call fit_transform first.")
        
        # Add missingness indicators if requested
        if self.add_indicators:
            indicator_features = self._create_missing_indicators(data)
        
        # Perform imputation
        imputed_data = self._impute(data)
        
        # Add indicators back
        if self.add_indicators:
            imputed_data = pd.concat([imputed_data, indicator_features], axis=1)
        
        return imputed_data
    
    def _analyze_missingness(self, data: pd.DataFrame) -> None:
        """
        Analyze missingness patterns in the data
        
        Args:
            data: DataFrame to analyze
        """
        missing_counts = data.isnull().sum()
        missing_pct = (missing_counts / len(data)) * 100
        
        logger.info("Missingness analysis:")
        for col in missing_pct[missing_pct > 0].index:
            logger.info(f"  {col}: {missing_pct[col]:.2f}% missing")
        
        # Store columns with missing data
        self.missing_indicators = {
            col: True for col in missing_pct[missing_pct > 0].index
        }
    
    def _create_missing_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create binary indicators for missing values
        
        These indicators can be informative features themselves, as
        missingness patterns may be related to the outcome.
        
        Args:
            data: DataFrame with potential missing values
            
        Returns:
            DataFrame with missing indicators
        """
        indicators = pd.DataFrame(index=data.index)
        
        for col in data.columns:
            if data[col].isnull().any():
                indicators[f'{col}_missing'] = data[col].isnull().astype(float)
        
        return indicators
    
    def _impute(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform imputation based on selected strategy
        
        Args:
            data: DataFrame with missing values
            
        Returns:
            DataFrame with imputed values
        """
        if self.strategy == 'mean':
            return self._impute_mean(data)
        elif self.strategy == 'median':
            return self._impute_median(data)
        elif self.strategy == 'iterative':
            return self._impute_iterative(data)
        elif self.strategy == 'knn':
            return self._impute_knn(data)
        else:
            raise ValueError(f"Unknown imputation strategy: {self.strategy}")
    
    def _impute_mean(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing values with column means
        
        Args:
            data: DataFrame with missing values
            
        Returns:
            DataFrame with imputed values
        """
        from sklearn.impute import SimpleImputer
        
        if self.imputer is None:
            self.imputer = SimpleImputer(strategy='mean')
            imputed_array = self.imputer.fit_transform(data)
        else:
            imputed_array = self.imputer.transform(data)
        
        return pd.DataFrame(
            imputed_array,
            columns=data.columns,
            index=data.index
        )
    
    def _impute_median(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing values with column medians
        
        Args:
            data: DataFrame with missing values
            
        Returns:
            DataFrame with imputed values
        """
        from sklearn.impute import SimpleImputer
        
        if self.imputer is None:
            self.imputer = SimpleImputer(strategy='median')
            imputed_array = self.imputer.fit_transform(data)
        else:
            imputed_array = self.imputer.transform(data)
        
        return pd.DataFrame(
            imputed_array,
            columns=data.columns,
            index=data.index
        )
    
    def _impute_iterative(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing values using MICE (Multivariate Imputation by Chained Equations)
        
        This method models each feature with missing values as a function of other features
        in a round-robin fashion. It's more sophisticated than simple imputation and can
        capture relationships between features.
        
        Args:
            data: DataFrame with missing values
            
        Returns:
            DataFrame with imputed values
        """
        try:
            from sklearn.experimental import enable_iterative_imputer
            from sklearn.impute import IterativeImputer
        except ImportError:
            logger.warning("IterativeImputer not available, falling back to mean imputation")
            return self._impute_mean(data)
        
        if self.imputer is None:
            self.imputer = IterativeImputer(
                max_iter=10,
                random_state=42,
                verbose=0
            )
            imputed_array = self.imputer.fit_transform(data)
        else:
            imputed_array = self.imputer.transform(data)
        
        return pd.DataFrame(
            imputed_array,
            columns=data.columns,
            index=data.index
        )
    
    def _impute_knn(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing values using K-Nearest Neighbors
        
        This method finds k similar samples and uses their values to impute missing data.
        
        Args:
            data: DataFrame with missing values
            
        Returns:
            DataFrame with imputed values
        """
        from sklearn.impute import KNNImputer
        
        if self.imputer is None:
            self.imputer = KNNImputer(n_neighbors=5)
            imputed_array = self.imputer.fit_transform(data)
        else:
            imputed_array = self.imputer.transform(data)
        
        return pd.DataFrame(
            imputed_array,
            columns=data.columns,
            index=data.index
        )
    
    def get_missingness_report(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate a report on missing data patterns
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            DataFrame with missingness statistics
        """
        report = pd.DataFrame({
            'column': data.columns,
            'missing_count': data.isnull().sum().values,
            'missing_pct': (data.isnull().sum() / len(data) * 100).values,
            'dtype': data.dtypes.values
        })
        
        report = report[report['missing_count'] > 0].sort_values(
            'missing_pct',
            ascending=False
        )
        
        return report
    
    def validate_imputation(
        self,
        original: pd.DataFrame,
        imputed: pd.DataFrame
    ) -> Dict[str, bool]:
        """
        Validate that imputation was successful
        
        Args:
            original: Original DataFrame with missing values
            imputed: Imputed DataFrame
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Check that no missing values remain
        validation['no_missing'] = not imputed.isnull().any().any()
        
        # Check that non-missing values weren't changed
        mask = original.notna()
        validation['original_preserved'] = np.allclose(
            original[mask].values,
            imputed[mask].values,
            equal_nan=True
        )
        
        # Check that imputed values are within reasonable ranges
        for col in original.columns:
            if original[col].isnull().any():
                original_min = original[col].min()
                original_max = original[col].max()
                imputed_min = imputed[col].min()
                imputed_max = imputed[col].max()
                
                # Imputed values should be within original range (with some tolerance)
                validation[f'{col}_range_valid'] = (
                    imputed_min >= original_min * 0.9 and
                    imputed_max <= original_max * 1.1
                )
        
        return validation
