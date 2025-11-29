"""Duplicate Detection Module - Detects duplicate patient records and visits"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Detect duplicate patient records and visits"""
    
    def __init__(self):
        """Initialize duplicate detector"""
        logger.info("Initialized DuplicateDetector")
    
    def detect_exact_duplicates(self, data: pd.DataFrame,
                               subset: Optional[List[str]] = None) -> Dict:
        """
        Detect exact duplicate rows
        
        Args:
            data: DataFrame to analyze
            subset: Columns to consider for duplicates (None = all columns)
            
        Returns:
            Dictionary with duplicate detection results
        """
        logger.info("Detecting exact duplicate rows")
        
        # Find duplicates
        if subset:
            duplicates = data.duplicated(subset=subset, keep=False)
        else:
            duplicates = data.duplicated(keep=False)
        
        duplicate_count = duplicates.sum()
        
        result = {
            'method': 'exact',
            'duplicate_rows': int(duplicate_count),
            'duplicate_percentage': float(duplicate_count / len(data) * 100),
            'unique_rows': int(len(data) - duplicate_count),
            'total_rows': len(data),
            'columns_checked': subset if subset else list(data.columns)
        }
        
        if duplicate_count > 0:
            # Get indices of duplicate rows
            duplicate_indices = data[duplicates].index.tolist()
            result['duplicate_indices'] = duplicate_indices
            logger.warning(f"Found {duplicate_count} exact duplicate rows")
        else:
            logger.info("No exact duplicates found")
        
        return result
    
    def detect_patient_duplicates(self, data: pd.DataFrame,
                                  patient_id_col: str = 'patient_id') -> Dict:
        """
        Detect duplicate patient records (same patient appearing multiple times)
        
        Args:
            data: DataFrame to analyze
            patient_id_col: Name of patient ID column
            
        Returns:
            Dictionary with patient duplicate analysis
        """
        logger.info(f"Detecting duplicate patients using column: {patient_id_col}")
        
        if patient_id_col not in data.columns:
            return {
                'error': f"Column '{patient_id_col}' not found in dataset",
                'available_columns': list(data.columns)
            }
        
        # Count occurrences of each patient ID
        patient_counts = data[patient_id_col].value_counts()
        
        # Find patients with multiple records
        duplicate_patients = patient_counts[patient_counts > 1]
        
        result = {
            'patient_id_column': patient_id_col,
            'total_records': len(data),
            'unique_patients': len(patient_counts),
            'duplicate_patients': len(duplicate_patients),
            'duplicate_patient_percentage': float(len(duplicate_patients) / len(patient_counts) * 100) if len(patient_counts) > 0 else 0.0,
            'records_from_duplicate_patients': int(duplicate_patients.sum()),
            'max_records_per_patient': int(patient_counts.max()),
            'mean_records_per_patient': float(patient_counts.mean())
        }
        
        if len(duplicate_patients) > 0:
            # Get top duplicate patients
            top_duplicates = duplicate_patients.head(10).to_dict()
            result['top_duplicate_patients'] = top_duplicates
            logger.warning(f"Found {len(duplicate_patients)} patients with multiple records")
        else:
            logger.info("No duplicate patients found")
        
        return result
    
    def detect_visit_duplicates(self, data: pd.DataFrame,
                               patient_id_col: str = 'patient_id',
                               visit_date_col: str = 'visit_date') -> Dict:
        """
        Detect duplicate visits (same patient on same date)
        
        Args:
            data: DataFrame to analyze
            patient_id_col: Name of patient ID column
            visit_date_col: Name of visit date column
            
        Returns:
            Dictionary with visit duplicate analysis
        """
        logger.info(f"Detecting duplicate visits using {patient_id_col} and {visit_date_col}")
        
        # Check if required columns exist
        missing_cols = []
        if patient_id_col not in data.columns:
            missing_cols.append(patient_id_col)
        if visit_date_col not in data.columns:
            missing_cols.append(visit_date_col)
        
        if missing_cols:
            return {
                'error': f"Required columns not found: {missing_cols}",
                'available_columns': list(data.columns)
            }
        
        # Find duplicate patient-date combinations
        duplicates = data.duplicated(subset=[patient_id_col, visit_date_col], keep=False)
        duplicate_count = duplicates.sum()
        
        result = {
            'patient_id_column': patient_id_col,
            'visit_date_column': visit_date_col,
            'total_visits': len(data),
            'duplicate_visits': int(duplicate_count),
            'duplicate_visit_percentage': float(duplicate_count / len(data) * 100),
            'unique_visits': int(len(data) - duplicate_count)
        }
        
        if duplicate_count > 0:
            # Get examples of duplicate visits
            duplicate_data = data[duplicates][[patient_id_col, visit_date_col]]
            duplicate_examples = duplicate_data.drop_duplicates().head(10).to_dict('records')
            result['duplicate_examples'] = duplicate_examples
            result['duplicate_indices'] = data[duplicates].index.tolist()
            logger.warning(f"Found {duplicate_count} duplicate visits")
        else:
            logger.info("No duplicate visits found")
        
        return result
    
    def detect_fuzzy_duplicates(self, data: pd.DataFrame,
                               columns: List[str],
                               threshold: float = 0.95) -> Dict:
        """
        Detect fuzzy/near duplicates based on similarity threshold
        
        Args:
            data: DataFrame to analyze
            columns: Columns to compare for similarity
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            Dictionary with fuzzy duplicate results
        """
        logger.info(f"Detecting fuzzy duplicates with threshold={threshold}")
        
        # Check if columns exist
        missing_cols = [col for col in columns if col not in data.columns]
        if missing_cols:
            return {
                'error': f"Columns not found: {missing_cols}",
                'available_columns': list(data.columns)
            }
        
        # For numeric columns, calculate similarity based on normalized differences
        numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(data[col])]
        
        if not numeric_cols:
            return {
                'error': 'No numeric columns provided for fuzzy matching',
                'provided_columns': columns
            }
        
        # Normalize numeric columns
        normalized_data = data[numeric_cols].copy()
        for col in numeric_cols:
            col_min = normalized_data[col].min()
            col_max = normalized_data[col].max()
            if col_max > col_min:
                normalized_data[col] = (normalized_data[col] - col_min) / (col_max - col_min)
        
        # Find similar pairs (simplified approach for demonstration)
        # In production, use more sophisticated methods like LSH or clustering
        similar_pairs = []
        
        # Sample for performance (compare first 1000 rows)
        sample_size = min(1000, len(data))
        sample_indices = data.index[:sample_size]
        
        for i in range(len(sample_indices)):
            for j in range(i + 1, len(sample_indices)):
                idx_i = sample_indices[i]
                idx_j = sample_indices[j]
                
                # Calculate similarity (1 - normalized distance)
                diff = np.abs(normalized_data.loc[idx_i] - normalized_data.loc[idx_j])
                similarity = 1 - diff.mean()
                
                if similarity >= threshold:
                    similar_pairs.append({
                        'index_1': int(idx_i),
                        'index_2': int(idx_j),
                        'similarity': float(similarity)
                    })
        
        result = {
            'method': 'fuzzy',
            'threshold': threshold,
            'columns_compared': numeric_cols,
            'rows_analyzed': sample_size,
            'similar_pairs_found': len(similar_pairs),
            'similar_pairs': similar_pairs[:20]  # Return top 20
        }
        
        if similar_pairs:
            logger.warning(f"Found {len(similar_pairs)} fuzzy duplicate pairs")
        else:
            logger.info("No fuzzy duplicates found")
        
        return result
    
    def remove_duplicates(self, data: pd.DataFrame,
                         subset: Optional[List[str]] = None,
                         keep: str = 'first') -> Tuple[pd.DataFrame, Dict]:
        """
        Remove duplicate rows from DataFrame
        
        Args:
            data: DataFrame to clean
            subset: Columns to consider for duplicates
            keep: Which duplicates to keep ('first', 'last', False)
            
        Returns:
            Tuple of (cleaned DataFrame, removal statistics)
        """
        logger.info(f"Removing duplicates (keep={keep})")
        
        original_count = len(data)
        
        # Remove duplicates
        cleaned_data = data.drop_duplicates(subset=subset, keep=keep)
        
        removed_count = original_count - len(cleaned_data)
        
        stats = {
            'original_rows': original_count,
            'removed_rows': removed_count,
            'remaining_rows': len(cleaned_data),
            'removal_percentage': float(removed_count / original_count * 100) if original_count > 0 else 0.0,
            'keep_strategy': keep,
            'columns_checked': subset if subset else 'all'
        }
        
        logger.info(f"Removed {removed_count} duplicate rows ({stats['removal_percentage']:.2f}%)")
        
        return cleaned_data, stats
    
    def comprehensive_duplicate_check(self, data: pd.DataFrame,
                                     patient_id_col: Optional[str] = None,
                                     visit_date_col: Optional[str] = None) -> Dict:
        """
        Perform comprehensive duplicate detection
        
        Args:
            data: DataFrame to analyze
            patient_id_col: Name of patient ID column (optional)
            visit_date_col: Name of visit date column (optional)
            
        Returns:
            Dictionary with all duplicate detection results
        """
        logger.info("Starting comprehensive duplicate detection")
        
        results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'dataset_info': {
                'rows': len(data),
                'columns': len(data.columns)
            }
        }
        
        # Check exact duplicates
        exact_duplicates = self.detect_exact_duplicates(data)
        results['exact_duplicates'] = exact_duplicates
        
        # Check patient duplicates if column provided
        if patient_id_col:
            patient_duplicates = self.detect_patient_duplicates(data, patient_id_col)
            results['patient_duplicates'] = patient_duplicates
        
        # Check visit duplicates if both columns provided
        if patient_id_col and visit_date_col:
            visit_duplicates = self.detect_visit_duplicates(data, patient_id_col, visit_date_col)
            results['visit_duplicates'] = visit_duplicates
        
        # Overall assessment
        has_duplicates = (
            exact_duplicates.get('duplicate_rows', 0) > 0 or
            (patient_duplicates and patient_duplicates.get('duplicate_patients', 0) > 0) or
            (visit_duplicates and visit_duplicates.get('duplicate_visits', 0) > 0)
        )
        
        results['has_duplicates'] = has_duplicates
        results['validation_passed'] = not has_duplicates
        
        if has_duplicates:
            logger.warning("Duplicate detection found issues")
        else:
            logger.info("✓ No duplicates detected")
        
        return results
    
    def generate_duplicate_report(self, data: pd.DataFrame,
                                 patient_id_col: Optional[str] = None,
                                 visit_date_col: Optional[str] = None) -> Dict:
        """
        Generate comprehensive duplicate detection report
        
        Args:
            data: DataFrame to analyze
            patient_id_col: Name of patient ID column (optional)
            visit_date_col: Name of visit date column (optional)
            
        Returns:
            Dictionary with complete duplicate analysis
        """
        logger.info("Generating duplicate detection report")
        
        return self.comprehensive_duplicate_check(data, patient_id_col, visit_date_col)
    
    def get_duplicate_summary(self, data: pd.DataFrame,
                             patient_id_col: Optional[str] = None,
                             visit_date_col: Optional[str] = None) -> str:
        """
        Get human-readable duplicate detection summary
        
        Args:
            data: DataFrame to analyze
            patient_id_col: Name of patient ID column (optional)
            visit_date_col: Name of visit date column (optional)
            
        Returns:
            Formatted string summary
        """
        report = self.generate_duplicate_report(data, patient_id_col, visit_date_col)
        
        summary = f"""
Duplicate Detection Summary
{'='*50}
Dataset: {report['dataset_info']['rows']:,} rows × {report['dataset_info']['columns']} columns
Status: {'✓ PASSED' if report['validation_passed'] else '✗ FAILED'}

Exact Duplicates:
  - Duplicate Rows: {report['exact_duplicates']['duplicate_rows']:,}
  - Percentage: {report['exact_duplicates']['duplicate_percentage']:.2f}%
"""
        
        if 'patient_duplicates' in report:
            pd_result = report['patient_duplicates']
            if 'error' not in pd_result:
                summary += f"""
Patient Duplicates:
  - Unique Patients: {pd_result['unique_patients']:,}
  - Patients with Multiple Records: {pd_result['duplicate_patients']:,}
  - Max Records per Patient: {pd_result['max_records_per_patient']}
"""
        
        if 'visit_duplicates' in report:
            vd_result = report['visit_duplicates']
            if 'error' not in vd_result:
                summary += f"""
Visit Duplicates:
  - Duplicate Visits: {vd_result['duplicate_visits']:,}
  - Percentage: {vd_result['duplicate_visit_percentage']:.2f}%
"""
        
        return summary.strip()
