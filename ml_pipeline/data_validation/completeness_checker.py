"""Completeness Checker Module - Validates data completeness and quality"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class CompletenessChecker:
    """Check data completeness and reject datasets below threshold"""
    
    def __init__(self, completeness_threshold: float = 0.70):
        """
        Initialize completeness checker
        
        Args:
            completeness_threshold: Minimum acceptable completeness (default: 0.70 = 70%)
        """
        self.completeness_threshold = completeness_threshold
        logger.info(f"Initialized CompletenessChecker with threshold={completeness_threshold*100}%")
    
    def calculate_completeness(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate percentage of non-null values per column
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary mapping column names to completeness percentages
        """
        logger.info(f"Calculating completeness for {len(data.columns)} columns")
        
        completeness = {}
        
        for column in data.columns:
            non_null_count = data[column].notna().sum()
            total_count = len(data)
            completeness_pct = non_null_count / total_count if total_count > 0 else 0.0
            completeness[column] = completeness_pct
        
        return completeness
    
    def get_overall_completeness(self, data: pd.DataFrame) -> float:
        """
        Calculate overall dataset completeness
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Overall completeness percentage (0.0 to 1.0)
        """
        total_cells = data.size
        non_null_cells = data.notna().sum().sum()
        
        overall = non_null_cells / total_cells if total_cells > 0 else 0.0
        
        logger.info(f"Overall completeness: {overall*100:.2f}%")
        return overall
    
    def identify_incomplete_columns(self, data: pd.DataFrame,
                                   threshold: float = None) -> List[str]:
        """
        Identify columns below completeness threshold
        
        Args:
            data: DataFrame to analyze
            threshold: Completeness threshold (uses instance threshold if None)
            
        Returns:
            List of column names below threshold
        """
        if threshold is None:
            threshold = self.completeness_threshold
        
        completeness = self.calculate_completeness(data)
        
        incomplete_columns = [
            col for col, pct in completeness.items()
            if pct < threshold
        ]
        
        if incomplete_columns:
            logger.warning(f"Found {len(incomplete_columns)} columns below {threshold*100}% completeness")
        else:
            logger.info(f"All columns meet {threshold*100}% completeness threshold")
        
        return incomplete_columns
    
    def validate_dataset_completeness(self, data: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Validate that dataset meets completeness requirements
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Tuple of (validation_passed, details_dict)
        """
        logger.info("Validating dataset completeness")
        
        # Calculate completeness metrics
        column_completeness = self.calculate_completeness(data)
        overall_completeness = self.get_overall_completeness(data)
        incomplete_columns = self.identify_incomplete_columns(data)
        
        # Check if dataset passes
        passes_validation = overall_completeness >= self.completeness_threshold
        
        details = {
            'overall_completeness': overall_completeness,
            'threshold': self.completeness_threshold,
            'validation_passed': passes_validation,
            'total_columns': len(data.columns),
            'total_rows': len(data),
            'incomplete_columns': incomplete_columns,
            'incomplete_columns_count': len(incomplete_columns),
            'column_completeness': column_completeness
        }
        
        if passes_validation:
            logger.info(f"✓ Dataset completeness validation passed: {overall_completeness*100:.2f}% >= {self.completeness_threshold*100}%")
        else:
            logger.error(f"✗ Dataset completeness validation failed: {overall_completeness*100:.2f}% < {self.completeness_threshold*100}%")
        
        return passes_validation, details
    
    def get_missing_value_patterns(self, data: pd.DataFrame) -> Dict:
        """
        Analyze missing value patterns in the dataset
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary with missing value pattern analysis
        """
        logger.info("Analyzing missing value patterns")
        
        # Count missing values per column
        missing_counts = data.isnull().sum()
        missing_percentages = (missing_counts / len(data) * 100).round(2)
        
        # Identify columns with no missing values
        complete_columns = missing_counts[missing_counts == 0].index.tolist()
        
        # Identify columns with all missing values
        empty_columns = missing_counts[missing_counts == len(data)].index.tolist()
        
        # Count rows with any missing values
        rows_with_missing = data.isnull().any(axis=1).sum()
        
        # Count completely empty rows
        completely_empty_rows = data.isnull().all(axis=1).sum()
        
        patterns = {
            'total_missing_values': int(missing_counts.sum()),
            'total_cells': data.size,
            'missing_percentage': float(missing_counts.sum() / data.size * 100),
            'columns_with_missing': int((missing_counts > 0).sum()),
            'complete_columns': complete_columns,
            'complete_columns_count': len(complete_columns),
            'empty_columns': empty_columns,
            'empty_columns_count': len(empty_columns),
            'rows_with_missing': int(rows_with_missing),
            'rows_with_missing_percentage': float(rows_with_missing / len(data) * 100),
            'completely_empty_rows': int(completely_empty_rows),
            'missing_by_column': missing_percentages.to_dict()
        }
        
        return patterns
    
    def generate_completeness_report(self, data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive completeness report
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary with complete analysis
        """
        logger.info("Generating completeness report")
        
        # Validate completeness
        validation_passed, validation_details = self.validate_dataset_completeness(data)
        
        # Get missing value patterns
        patterns = self.get_missing_value_patterns(data)
        
        # Get top incomplete columns
        column_completeness = self.calculate_completeness(data)
        sorted_completeness = sorted(column_completeness.items(), key=lambda x: x[1])
        top_incomplete = [
            {'column': col, 'completeness': pct}
            for col, pct in sorted_completeness[:10]
        ]
        
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'dataset_info': {
                'rows': len(data),
                'columns': len(data.columns),
                'total_cells': data.size
            },
            'validation': validation_details,
            'missing_patterns': patterns,
            'top_incomplete_columns': top_incomplete,
            'recommendation': self._get_recommendation(validation_passed, patterns)
        }
        
        return report
    
    def _get_recommendation(self, validation_passed: bool, patterns: Dict) -> str:
        """Generate recommendation based on completeness analysis"""
        if validation_passed:
            return "Dataset meets completeness requirements and can proceed to next stage."
        
        if patterns['empty_columns_count'] > 0:
            return f"Dataset has {patterns['empty_columns_count']} completely empty columns. Consider removing these columns and re-validating."
        
        if patterns['missing_percentage'] > 50:
            return "Dataset has excessive missing values (>50%). Consider data collection improvements or alternative data sources."
        
        return f"Dataset completeness ({patterns['missing_percentage']:.1f}% missing) is below threshold. Consider imputation strategies or additional data collection."
    
    def suggest_columns_to_drop(self, data: pd.DataFrame,
                               drop_threshold: float = 0.50) -> List[str]:
        """
        Suggest columns that should be dropped due to low completeness
        
        Args:
            data: DataFrame to analyze
            drop_threshold: Threshold below which columns should be dropped
            
        Returns:
            List of column names to consider dropping
        """
        completeness = self.calculate_completeness(data)
        
        columns_to_drop = [
            col for col, pct in completeness.items()
            if pct < drop_threshold
        ]
        
        if columns_to_drop:
            logger.info(f"Suggesting {len(columns_to_drop)} columns for removal (completeness < {drop_threshold*100}%)")
        
        return columns_to_drop
    
    def get_completeness_summary(self, data: pd.DataFrame) -> str:
        """
        Get human-readable completeness summary
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Formatted string summary
        """
        validation_passed, details = self.validate_dataset_completeness(data)
        patterns = self.get_missing_value_patterns(data)
        
        summary = f"""
Completeness Summary
{'='*50}
Overall Completeness: {details['overall_completeness']*100:.2f}%
Threshold: {self.completeness_threshold*100:.2f}%
Status: {'✓ PASSED' if validation_passed else '✗ FAILED'}

Dataset Size: {details['total_rows']:,} rows × {details['total_columns']} columns
Total Missing Values: {patterns['total_missing_values']:,} ({patterns['missing_percentage']:.2f}%)

Columns:
  - Complete: {patterns['complete_columns_count']}
  - Incomplete: {details['incomplete_columns_count']}
  - Empty: {patterns['empty_columns_count']}

Rows:
  - With Missing Values: {patterns['rows_with_missing']:,} ({patterns['rows_with_missing_percentage']:.2f}%)
  - Completely Empty: {patterns['completely_empty_rows']:,}
"""
        
        return summary.strip()
