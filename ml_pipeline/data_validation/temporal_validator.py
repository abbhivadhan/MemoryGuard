"""Temporal Consistency Validator - Validates temporal ordering in longitudinal data"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TemporalValidator:
    """Validate temporal consistency in longitudinal data"""
    
    def __init__(self):
        """Initialize temporal validator"""
        logger.info("Initialized TemporalValidator")
    
    def validate_date_sequences(self, data: pd.DataFrame,
                                patient_id_col: str = 'patient_id',
                                date_col: str = 'visit_date') -> Dict:
        """
        Validate that dates are in chronological order for each patient
        
        Args:
            data: DataFrame to validate
            patient_id_col: Name of patient ID column
            date_col: Name of date column
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating date sequences for {patient_id_col} and {date_col}")
        
        # Check if required columns exist
        missing_cols = []
        if patient_id_col not in data.columns:
            missing_cols.append(patient_id_col)
        if date_col not in data.columns:
            missing_cols.append(date_col)
        
        if missing_cols:
            return {
                'error': f"Required columns not found: {missing_cols}",
                'available_columns': list(data.columns)
            }
        
        # Convert date column to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(data[date_col]):
            try:
                dates = pd.to_datetime(data[date_col])
            except Exception as e:
                return {
                    'error': f"Could not convert {date_col} to datetime: {str(e)}"
                }
        else:
            dates = data[date_col]
        
        # Check for chronological order within each patient
        violations = []
        patients_checked = 0
        
        for patient_id in data[patient_id_col].unique():
            patient_data = data[data[patient_id_col] == patient_id].copy()
            patient_dates = dates[data[patient_id_col] == patient_id]
            
            if len(patient_data) < 2:
                continue  # Skip patients with single visit
            
            patients_checked += 1
            
            # Check if dates are sorted
            sorted_dates = patient_dates.sort_values()
            
            if not patient_dates.equals(sorted_dates):
                violations.append({
                    'patient_id': patient_id,
                    'visit_count': len(patient_data),
                    'dates': patient_dates.dt.strftime('%Y-%m-%d').tolist() if pd.api.types.is_datetime64_any_dtype(patient_dates) else patient_dates.tolist()
                })
        
        result = {
            'patient_id_column': patient_id_col,
            'date_column': date_col,
            'total_patients': len(data[patient_id_col].unique()),
            'patients_with_multiple_visits': patients_checked,
            'patients_with_violations': len(violations),
            'validation_passed': len(violations) == 0
        }
        
        if violations:
            result['violations'] = violations[:10]  # Return first 10
            logger.warning(f"Found {len(violations)} patients with non-chronological dates")
        else:
            logger.info("✓ All date sequences are chronological")
        
        return result
    
    def validate_date_ranges(self, data: pd.DataFrame,
                            date_col: str,
                            min_date: Optional[datetime] = None,
                            max_date: Optional[datetime] = None) -> Dict:
        """
        Validate that dates fall within expected range
        
        Args:
            data: DataFrame to validate
            date_col: Name of date column
            min_date: Minimum valid date (optional)
            max_date: Maximum valid date (optional)
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating date ranges for {date_col}")
        
        if date_col not in data.columns:
            return {
                'error': f"Column '{date_col}' not found",
                'available_columns': list(data.columns)
            }
        
        # Convert to datetime
        if not pd.api.types.is_datetime64_any_dtype(data[date_col]):
            try:
                dates = pd.to_datetime(data[date_col])
            except Exception as e:
                return {
                    'error': f"Could not convert {date_col} to datetime: {str(e)}"
                }
        else:
            dates = data[date_col]
        
        # Remove NaN dates
        valid_dates = dates.dropna()
        
        if len(valid_dates) == 0:
            return {
                'error': 'All dates are NaN',
                'date_column': date_col
            }
        
        # Check ranges
        actual_min = valid_dates.min()
        actual_max = valid_dates.max()
        
        violations = []
        
        if min_date:
            below_min = valid_dates < min_date
            if below_min.any():
                violations.append({
                    'type': 'below_minimum',
                    'count': int(below_min.sum()),
                    'min_allowed': min_date.strftime('%Y-%m-%d'),
                    'actual_min': actual_min.strftime('%Y-%m-%d')
                })
        
        if max_date:
            above_max = valid_dates > max_date
            if above_max.any():
                violations.append({
                    'type': 'above_maximum',
                    'count': int(above_max.sum()),
                    'max_allowed': max_date.strftime('%Y-%m-%d'),
                    'actual_max': actual_max.strftime('%Y-%m-%d')
                })
        
        result = {
            'date_column': date_col,
            'total_dates': len(dates),
            'valid_dates': len(valid_dates),
            'actual_min_date': actual_min.strftime('%Y-%m-%d'),
            'actual_max_date': actual_max.strftime('%Y-%m-%d'),
            'date_range_days': (actual_max - actual_min).days,
            'violations': violations,
            'validation_passed': len(violations) == 0
        }
        
        if violations:
            logger.warning(f"Found date range violations in {date_col}")
        else:
            logger.info(f"✓ All dates in {date_col} are within valid range")
        
        return result
    
    def validate_visit_intervals(self, data: pd.DataFrame,
                                patient_id_col: str = 'patient_id',
                                date_col: str = 'visit_date',
                                min_interval_days: int = 1,
                                max_interval_days: int = 730) -> Dict:
        """
        Validate that visit intervals are reasonable
        
        Args:
            data: DataFrame to validate
            patient_id_col: Name of patient ID column
            date_col: Name of date column
            min_interval_days: Minimum days between visits
            max_interval_days: Maximum days between visits
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating visit intervals ({min_interval_days}-{max_interval_days} days)")
        
        # Check if required columns exist
        if patient_id_col not in data.columns or date_col not in data.columns:
            return {
                'error': f"Required columns not found",
                'available_columns': list(data.columns)
            }
        
        # Convert to datetime
        if not pd.api.types.is_datetime64_any_dtype(data[date_col]):
            try:
                dates = pd.to_datetime(data[date_col])
            except Exception as e:
                return {
                    'error': f"Could not convert {date_col} to datetime: {str(e)}"
                }
        else:
            dates = data[date_col]
        
        # Calculate intervals for each patient
        violations = []
        all_intervals = []
        
        for patient_id in data[patient_id_col].unique():
            patient_dates = dates[data[patient_id_col] == patient_id].sort_values()
            
            if len(patient_dates) < 2:
                continue
            
            # Calculate intervals between consecutive visits
            intervals = patient_dates.diff().dt.days.dropna()
            all_intervals.extend(intervals.tolist())
            
            # Check for violations
            too_short = intervals < min_interval_days
            too_long = intervals > max_interval_days
            
            if too_short.any() or too_long.any():
                violations.append({
                    'patient_id': patient_id,
                    'visit_count': len(patient_dates),
                    'intervals_too_short': int(too_short.sum()),
                    'intervals_too_long': int(too_long.sum()),
                    'min_interval': float(intervals.min()),
                    'max_interval': float(intervals.max())
                })
        
        result = {
            'patient_id_column': patient_id_col,
            'date_column': date_col,
            'min_interval_days': min_interval_days,
            'max_interval_days': max_interval_days,
            'patients_with_violations': len(violations),
            'validation_passed': len(violations) == 0
        }
        
        if all_intervals:
            result['interval_statistics'] = {
                'mean_interval_days': float(np.mean(all_intervals)),
                'median_interval_days': float(np.median(all_intervals)),
                'min_interval_days': float(np.min(all_intervals)),
                'max_interval_days': float(np.max(all_intervals)),
                'std_interval_days': float(np.std(all_intervals))
            }
        
        if violations:
            result['violations'] = violations[:10]
            logger.warning(f"Found {len(violations)} patients with invalid visit intervals")
        else:
            logger.info("✓ All visit intervals are within valid range")
        
        return result
    
    def validate_temporal_ordering(self, data: pd.DataFrame,
                                   patient_id_col: str = 'patient_id',
                                   date_col: str = 'visit_date',
                                   value_col: str = None,
                                   should_increase: bool = None) -> Dict:
        """
        Validate that a value changes logically over time
        
        Args:
            data: DataFrame to validate
            patient_id_col: Name of patient ID column
            date_col: Name of date column
            value_col: Name of value column to check
            should_increase: True if value should increase, False if decrease, None for no check
            
        Returns:
            Dictionary with validation results
        """
        if value_col is None:
            return {'error': 'value_col must be specified'}
        
        logger.info(f"Validating temporal ordering for {value_col}")
        
        # Check if required columns exist
        required_cols = [patient_id_col, date_col, value_col]
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            return {
                'error': f"Required columns not found: {missing_cols}",
                'available_columns': list(data.columns)
            }
        
        # Convert to datetime
        if not pd.api.types.is_datetime64_any_dtype(data[date_col]):
            try:
                dates = pd.to_datetime(data[date_col])
            except Exception as e:
                return {
                    'error': f"Could not convert {date_col} to datetime: {str(e)}"
                }
        else:
            dates = data[date_col]
        
        violations = []
        
        for patient_id in data[patient_id_col].unique():
            patient_mask = data[patient_id_col] == patient_id
            patient_data = data[patient_mask].copy()
            patient_data['_date'] = dates[patient_mask]
            
            # Sort by date
            patient_data = patient_data.sort_values('_date')
            
            if len(patient_data) < 2:
                continue
            
            values = patient_data[value_col].dropna()
            
            if len(values) < 2:
                continue
            
            # Check ordering if specified
            if should_increase is not None:
                if should_increase:
                    # Check if values generally increase
                    decreases = (values.diff() < 0).sum()
                    if decreases > len(values) * 0.3:  # More than 30% decreases
                        violations.append({
                            'patient_id': patient_id,
                            'expected': 'increasing',
                            'decreases_found': int(decreases),
                            'total_transitions': len(values) - 1
                        })
                else:
                    # Check if values generally decrease
                    increases = (values.diff() > 0).sum()
                    if increases > len(values) * 0.3:  # More than 30% increases
                        violations.append({
                            'patient_id': patient_id,
                            'expected': 'decreasing',
                            'increases_found': int(increases),
                            'total_transitions': len(values) - 1
                        })
        
        result = {
            'patient_id_column': patient_id_col,
            'date_column': date_col,
            'value_column': value_col,
            'expected_trend': 'increasing' if should_increase else 'decreasing' if should_increase is False else 'none',
            'patients_with_violations': len(violations),
            'validation_passed': len(violations) == 0
        }
        
        if violations:
            result['violations'] = violations[:10]
            logger.warning(f"Found {len(violations)} patients with unexpected temporal trends")
        else:
            logger.info(f"✓ Temporal ordering validated for {value_col}")
        
        return result
    
    def comprehensive_temporal_validation(self, data: pd.DataFrame,
                                         patient_id_col: str = 'patient_id',
                                         date_col: str = 'visit_date') -> Dict:
        """
        Perform comprehensive temporal validation
        
        Args:
            data: DataFrame to validate
            patient_id_col: Name of patient ID column
            date_col: Name of date column
            
        Returns:
            Dictionary with all temporal validation results
        """
        logger.info("Starting comprehensive temporal validation")
        
        results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'dataset_info': {
                'rows': len(data),
                'columns': len(data.columns)
            }
        }
        
        # Validate date sequences
        date_sequences = self.validate_date_sequences(data, patient_id_col, date_col)
        results['date_sequences'] = date_sequences
        
        # Validate date ranges (reasonable dates)
        min_reasonable_date = datetime(1900, 1, 1)
        max_reasonable_date = datetime.now() + timedelta(days=365)
        date_ranges = self.validate_date_ranges(data, date_col, min_reasonable_date, max_reasonable_date)
        results['date_ranges'] = date_ranges
        
        # Validate visit intervals
        visit_intervals = self.validate_visit_intervals(data, patient_id_col, date_col)
        results['visit_intervals'] = visit_intervals
        
        # Overall validation
        all_passed = (
            date_sequences.get('validation_passed', False) and
            date_ranges.get('validation_passed', False) and
            visit_intervals.get('validation_passed', False)
        )
        
        results['validation_passed'] = all_passed
        
        if all_passed:
            logger.info("✓ All temporal validation checks passed")
        else:
            logger.warning("✗ Temporal validation found issues")
        
        return results
    
    def get_temporal_summary(self, data: pd.DataFrame,
                            patient_id_col: str = 'patient_id',
                            date_col: str = 'visit_date') -> str:
        """
        Get human-readable temporal validation summary
        
        Args:
            data: DataFrame to analyze
            patient_id_col: Name of patient ID column
            date_col: Name of date column
            
        Returns:
            Formatted string summary
        """
        report = self.comprehensive_temporal_validation(data, patient_id_col, date_col)
        
        summary = f"""
Temporal Consistency Summary
{'='*50}
Dataset: {report['dataset_info']['rows']:,} rows × {report['dataset_info']['columns']} columns
Status: {'✓ PASSED' if report['validation_passed'] else '✗ FAILED'}

Date Sequences:
  - Patients Checked: {report['date_sequences'].get('patients_with_multiple_visits', 0):,}
  - Violations: {report['date_sequences'].get('patients_with_violations', 0):,}
  - Status: {'✓ PASSED' if report['date_sequences'].get('validation_passed') else '✗ FAILED'}

Date Ranges:
  - Date Range: {report['date_ranges'].get('actual_min_date', 'N/A')} to {report['date_ranges'].get('actual_max_date', 'N/A')}
  - Span: {report['date_ranges'].get('date_range_days', 0):,} days
  - Status: {'✓ PASSED' if report['date_ranges'].get('validation_passed') else '✗ FAILED'}

Visit Intervals:
  - Patients with Violations: {report['visit_intervals'].get('patients_with_violations', 0):,}
  - Status: {'✓ PASSED' if report['visit_intervals'].get('validation_passed') else '✗ FAILED'}
"""
        
        if 'interval_statistics' in report['visit_intervals']:
            stats = report['visit_intervals']['interval_statistics']
            summary += f"""
Interval Statistics:
  - Mean: {stats['mean_interval_days']:.1f} days
  - Median: {stats['median_interval_days']:.1f} days
  - Range: {stats['min_interval_days']:.1f} - {stats['max_interval_days']:.1f} days
"""
        
        return summary.strip()
