"""Outlier Detection Module - Detects outliers using statistical methods"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class OutlierDetector:
    """Detect outliers using IQR and Z-score methods"""
    
    def __init__(self, iqr_multiplier: float = 1.5, z_threshold: float = 3.0):
        """
        Initialize outlier detector
        
        Args:
            iqr_multiplier: Multiplier for IQR method (default: 1.5)
            z_threshold: Threshold for Z-score method (default: 3.0)
        """
        self.iqr_multiplier = iqr_multiplier
        self.z_threshold = z_threshold
        logger.info(f"Initialized OutlierDetector (IQR={iqr_multiplier}, Z={z_threshold})")
    
    def detect_outliers_iqr(self, data: pd.Series) -> Tuple[np.ndarray, Dict]:
        """
        Detect outliers using Interquartile Range (IQR) method
        
        Args:
            data: Series to analyze
            
        Returns:
            Tuple of (boolean array of outliers, statistics dict)
        """
        # Remove NaN values for calculation
        clean_data = data.dropna()
        
        if len(clean_data) == 0:
            return np.array([]), {'error': 'No valid data'}
        
        # Calculate quartiles
        Q1 = clean_data.quantile(0.25)
        Q3 = clean_data.quantile(0.75)
        IQR = Q3 - Q1
        
        # Calculate bounds
        lower_bound = Q1 - self.iqr_multiplier * IQR
        upper_bound = Q3 + self.iqr_multiplier * IQR
        
        # Identify outliers
        outliers = (data < lower_bound) | (data > upper_bound)
        
        stats_dict = {
            'method': 'IQR',
            'Q1': float(Q1),
            'Q3': float(Q3),
            'IQR': float(IQR),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_count': int(outliers.sum()),
            'outlier_percentage': float(outliers.sum() / len(data) * 100)
        }
        
        return outliers, stats_dict
    
    def detect_outliers_zscore(self, data: pd.Series) -> Tuple[np.ndarray, Dict]:
        """
        Detect outliers using Z-score method
        
        Args:
            data: Series to analyze
            
        Returns:
            Tuple of (boolean array of outliers, statistics dict)
        """
        # Remove NaN values for calculation
        clean_data = data.dropna()
        
        if len(clean_data) == 0:
            return np.array([]), {'error': 'No valid data'}
        
        # Calculate mean and standard deviation
        mean = clean_data.mean()
        std = clean_data.std()
        
        if std == 0:
            # No variation in data
            return np.zeros(len(data), dtype=bool), {
                'method': 'Z-score',
                'mean': float(mean),
                'std': 0.0,
                'outlier_count': 0,
                'warning': 'Zero standard deviation'
            }
        
        # Calculate Z-scores
        z_scores = np.abs((data - mean) / std)
        
        # Identify outliers
        outliers = z_scores > self.z_threshold
        
        stats_dict = {
            'method': 'Z-score',
            'mean': float(mean),
            'std': float(std),
            'threshold': self.z_threshold,
            'max_z_score': float(z_scores.max()) if len(z_scores) > 0 else 0.0,
            'outlier_count': int(outliers.sum()),
            'outlier_percentage': float(outliers.sum() / len(data) * 100)
        }
        
        return outliers, stats_dict
    
    def detect_outliers_modified_zscore(self, data: pd.Series,
                                       threshold: float = 3.5) -> Tuple[np.ndarray, Dict]:
        """
        Detect outliers using Modified Z-score (using median and MAD)
        More robust to outliers than standard Z-score
        
        Args:
            data: Series to analyze
            threshold: Modified Z-score threshold (default: 3.5)
            
        Returns:
            Tuple of (boolean array of outliers, statistics dict)
        """
        clean_data = data.dropna()
        
        if len(clean_data) == 0:
            return np.array([]), {'error': 'No valid data'}
        
        # Calculate median
        median = clean_data.median()
        
        # Calculate Median Absolute Deviation (MAD)
        mad = np.median(np.abs(clean_data - median))
        
        if mad == 0:
            return np.zeros(len(data), dtype=bool), {
                'method': 'Modified Z-score',
                'median': float(median),
                'mad': 0.0,
                'outlier_count': 0,
                'warning': 'Zero MAD'
            }
        
        # Calculate modified Z-scores
        modified_z_scores = 0.6745 * (data - median) / mad
        
        # Identify outliers
        outliers = np.abs(modified_z_scores) > threshold
        
        stats_dict = {
            'method': 'Modified Z-score',
            'median': float(median),
            'mad': float(mad),
            'threshold': threshold,
            'outlier_count': int(outliers.sum()),
            'outlier_percentage': float(outliers.sum() / len(data) * 100)
        }
        
        return outliers, stats_dict
    
    def detect_outliers_dataframe(self, data: pd.DataFrame,
                                 method: str = 'both',
                                 numeric_only: bool = True) -> Dict:
        """
        Detect outliers across all numeric columns in a DataFrame
        
        Args:
            data: DataFrame to analyze
            method: 'iqr', 'zscore', or 'both' (default: 'both')
            numeric_only: Only analyze numeric columns (default: True)
            
        Returns:
            Dictionary with outlier detection results per column
        """
        logger.info(f"Detecting outliers using {method} method")
        
        if numeric_only:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
        else:
            numeric_cols = data.columns
        
        results = {}
        
        for column in numeric_cols:
            col_results = {'column': column}
            
            if method in ['iqr', 'both']:
                outliers_iqr, stats_iqr = self.detect_outliers_iqr(data[column])
                col_results['iqr'] = stats_iqr
                col_results['iqr_outlier_indices'] = data[outliers_iqr].index.tolist()
            
            if method in ['zscore', 'both']:
                outliers_z, stats_z = self.detect_outliers_zscore(data[column])
                col_results['zscore'] = stats_z
                col_results['zscore_outlier_indices'] = data[outliers_z].index.tolist()
            
            # If both methods used, find consensus outliers
            if method == 'both':
                outliers_iqr, _ = self.detect_outliers_iqr(data[column])
                outliers_z, _ = self.detect_outliers_zscore(data[column])
                consensus_outliers = outliers_iqr & outliers_z
                col_results['consensus_outliers'] = {
                    'count': int(consensus_outliers.sum()),
                    'percentage': float(consensus_outliers.sum() / len(data) * 100),
                    'indices': data[consensus_outliers].index.tolist()
                }
            
            results[column] = col_results
        
        return results
    
    def get_outlier_values(self, data: pd.Series, outlier_mask: np.ndarray) -> List:
        """
        Get the actual outlier values
        
        Args:
            data: Original series
            outlier_mask: Boolean array indicating outliers
            
        Returns:
            List of outlier values
        """
        return data[outlier_mask].tolist()
    
    def generate_outlier_report(self, data: pd.DataFrame,
                               method: str = 'both') -> Dict:
        """
        Generate comprehensive outlier detection report
        
        Args:
            data: DataFrame to analyze
            method: Detection method ('iqr', 'zscore', or 'both')
            
        Returns:
            Dictionary with complete outlier analysis
        """
        logger.info("Generating outlier detection report")
        
        # Detect outliers
        outlier_results = self.detect_outliers_dataframe(data, method=method)
        
        # Calculate summary statistics
        total_columns = len(outlier_results)
        columns_with_outliers = 0
        total_outliers_iqr = 0
        total_outliers_zscore = 0
        
        for col, results in outlier_results.items():
            if method in ['iqr', 'both']:
                if results['iqr']['outlier_count'] > 0:
                    columns_with_outliers += 1
                total_outliers_iqr += results['iqr']['outlier_count']
            
            if method in ['zscore', 'both']:
                if results['zscore']['outlier_count'] > 0:
                    columns_with_outliers += 1
                total_outliers_zscore += results['zscore']['outlier_count']
        
        # Get top columns by outlier count
        if method == 'iqr':
            sorted_cols = sorted(
                outlier_results.items(),
                key=lambda x: x[1]['iqr']['outlier_count'],
                reverse=True
            )
        elif method == 'zscore':
            sorted_cols = sorted(
                outlier_results.items(),
                key=lambda x: x[1]['zscore']['outlier_count'],
                reverse=True
            )
        else:  # both
            sorted_cols = sorted(
                outlier_results.items(),
                key=lambda x: x[1]['consensus_outliers']['count'],
                reverse=True
            )
        
        top_outlier_columns = [
            {
                'column': col,
                'outlier_count': results.get('consensus_outliers', results.get('iqr', {})).get('count', 0)
            }
            for col, results in sorted_cols[:10]
        ]
        
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'method': method,
            'dataset_info': {
                'rows': len(data),
                'columns': total_columns
            },
            'summary': {
                'columns_analyzed': total_columns,
                'columns_with_outliers': columns_with_outliers,
                'total_outliers_iqr': total_outliers_iqr if method in ['iqr', 'both'] else None,
                'total_outliers_zscore': total_outliers_zscore if method in ['zscore', 'both'] else None
            },
            'top_outlier_columns': top_outlier_columns,
            'detailed_results': outlier_results
        }
        
        return report
    
    def get_outlier_summary(self, data: pd.DataFrame, method: str = 'both') -> str:
        """
        Get human-readable outlier detection summary
        
        Args:
            data: DataFrame to analyze
            method: Detection method
            
        Returns:
            Formatted string summary
        """
        report = self.generate_outlier_report(data, method=method)
        
        summary = f"""
Outlier Detection Summary
{'='*50}
Method: {method.upper()}
Dataset: {report['dataset_info']['rows']:,} rows × {report['dataset_info']['columns']} columns

Results:
  - Columns Analyzed: {report['summary']['columns_analyzed']}
  - Columns with Outliers: {report['summary']['columns_with_outliers']}
"""
        
        if method in ['iqr', 'both']:
            summary += f"  - Total Outliers (IQR): {report['summary']['total_outliers_iqr']:,}\n"
        
        if method in ['zscore', 'both']:
            summary += f"  - Total Outliers (Z-score): {report['summary']['total_outliers_zscore']:,}\n"
        
        summary += "\nTop 5 Columns by Outlier Count:\n"
        for i, col_info in enumerate(report['top_outlier_columns'][:5], 1):
            summary += f"  {i}. {col_info['column']}: {col_info['outlier_count']} outliers\n"
        
        return summary.strip()
    
    def flag_extreme_outliers(self, data: pd.DataFrame,
                             extreme_multiplier: float = 3.0) -> Dict:
        """
        Flag extreme outliers (beyond typical outlier thresholds)
        
        Args:
            data: DataFrame to analyze
            extreme_multiplier: Multiplier for extreme outlier detection
            
        Returns:
            Dictionary with extreme outlier information
        """
        logger.info(f"Flagging extreme outliers (IQR multiplier={extreme_multiplier})")
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        extreme_outliers = {}
        
        for column in numeric_cols:
            clean_data = data[column].dropna()
            
            if len(clean_data) == 0:
                continue
            
            Q1 = clean_data.quantile(0.25)
            Q3 = clean_data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - extreme_multiplier * IQR
            upper_bound = Q3 + extreme_multiplier * IQR
            
            extreme_mask = (data[column] < lower_bound) | (data[column] > upper_bound)
            extreme_count = extreme_mask.sum()
            
            if extreme_count > 0:
                extreme_outliers[column] = {
                    'count': int(extreme_count),
                    'percentage': float(extreme_count / len(data) * 100),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'min_value': float(data[column][extreme_mask].min()),
                    'max_value': float(data[column][extreme_mask].max())
                }
        
        return extreme_outliers
