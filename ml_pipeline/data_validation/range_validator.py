"""Range Validator Module - Validates data against expected ranges"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RangeValidator:
    """Validate data against expected ranges for biomarkers and cognitive scores"""
    
    def __init__(self):
        """Initialize range validator with predefined ranges"""
        self.ranges = self._define_valid_ranges()
        logger.info("Initialized RangeValidator with predefined ranges")
    
    def _define_valid_ranges(self) -> Dict[str, Dict]:
        """
        Define valid ranges for biomarkers and cognitive scores
        
        Returns:
            Dictionary mapping field names to their valid ranges
        """
        ranges = {
            # Cognitive Assessment Scores
            'MMSE': {'min': 0, 'max': 30, 'unit': 'points', 'type': 'cognitive'},
            'mmse_score': {'min': 0, 'max': 30, 'unit': 'points', 'type': 'cognitive'},
            'MoCA': {'min': 0, 'max': 30, 'unit': 'points', 'type': 'cognitive'},
            'moca_score': {'min': 0, 'max': 30, 'unit': 'points', 'type': 'cognitive'},
            'CDR': {'min': 0, 'max': 3, 'unit': 'score', 'type': 'cognitive'},
            'CDR_GLOBAL': {'min': 0, 'max': 3, 'unit': 'score', 'type': 'cognitive'},
            'cdr_global': {'min': 0, 'max': 3, 'unit': 'score', 'type': 'cognitive'},
            'ADAS_Cog': {'min': 0, 'max': 70, 'unit': 'points', 'type': 'cognitive'},
            'adas_cog': {'min': 0, 'max': 70, 'unit': 'points', 'type': 'cognitive'},
            
            # CSF Biomarkers (pg/mL)
            'CSF_AB42': {'min': 0, 'max': 2000, 'unit': 'pg/mL', 'type': 'biomarker'},
            'csf_ab42': {'min': 0, 'max': 2000, 'unit': 'pg/mL', 'type': 'biomarker'},
            'CSF_TAU': {'min': 0, 'max': 1500, 'unit': 'pg/mL', 'type': 'biomarker'},
            'csf_tau': {'min': 0, 'max': 1500, 'unit': 'pg/mL', 'type': 'biomarker'},
            'CSF_PTAU': {'min': 0, 'max': 150, 'unit': 'pg/mL', 'type': 'biomarker'},
            'csf_ptau': {'min': 0, 'max': 150, 'unit': 'pg/mL', 'type': 'biomarker'},
            
            # Biomarker Ratios
            'ab42_tau_ratio': {'min': 0, 'max': 10, 'unit': 'ratio', 'type': 'biomarker'},
            'ptau_tau_ratio': {'min': 0, 'max': 1, 'unit': 'ratio', 'type': 'biomarker'},
            
            # Brain Volumes (cm³)
            'hippocampus_volume': {'min': 1.0, 'max': 10.0, 'unit': 'cm³', 'type': 'imaging'},
            'hippocampus_left': {'min': 0.5, 'max': 6.0, 'unit': 'cm³', 'type': 'imaging'},
            'hippocampus_right': {'min': 0.5, 'max': 6.0, 'unit': 'cm³', 'type': 'imaging'},
            'entorhinal_cortex': {'min': 0.5, 'max': 5.0, 'unit': 'cm³', 'type': 'imaging'},
            'entorhinal_cortex_thickness': {'min': 1.0, 'max': 5.0, 'unit': 'mm', 'type': 'imaging'},
            'ventricular_volume': {'min': 10, 'max': 200, 'unit': 'cm³', 'type': 'imaging'},
            'whole_brain_volume': {'min': 800, 'max': 1800, 'unit': 'cm³', 'type': 'imaging'},
            'intracranial_volume': {'min': 1000, 'max': 2000, 'unit': 'cm³', 'type': 'imaging'},
            
            # Cortical Thickness (mm)
            'cortical_thickness': {'min': 1.0, 'max': 5.0, 'unit': 'mm', 'type': 'imaging'},
            
            # Demographics
            'age': {'min': 18, 'max': 120, 'unit': 'years', 'type': 'demographic'},
            'education_years': {'min': 0, 'max': 30, 'unit': 'years', 'type': 'demographic'},
            'education': {'min': 0, 'max': 30, 'unit': 'years', 'type': 'demographic'},
            
            # Genetic
            'apoe_e4_count': {'min': 0, 'max': 2, 'unit': 'alleles', 'type': 'genetic'},
            
            # Vital Signs
            'bmi': {'min': 10, 'max': 60, 'unit': 'kg/m²', 'type': 'vital'},
            'systolic_bp': {'min': 60, 'max': 250, 'unit': 'mmHg', 'type': 'vital'},
            'diastolic_bp': {'min': 40, 'max': 150, 'unit': 'mmHg', 'type': 'vital'},
            'heart_rate': {'min': 30, 'max': 200, 'unit': 'bpm', 'type': 'vital'},
        }
        
        return ranges
    
    def add_custom_range(self, field_name: str, min_val: float, max_val: float,
                        unit: str = '', field_type: str = 'custom'):
        """
        Add a custom range definition
        
        Args:
            field_name: Name of the field
            min_val: Minimum valid value
            max_val: Maximum valid value
            unit: Unit of measurement
            field_type: Type of field
        """
        self.ranges[field_name] = {
            'min': min_val,
            'max': max_val,
            'unit': unit,
            'type': field_type
        }
        logger.info(f"Added custom range for {field_name}: [{min_val}, {max_val}] {unit}")
    
    def validate_value(self, field_name: str, value: float) -> Tuple[bool, Optional[str]]:
        """
        Validate a single value against its expected range
        
        Args:
            field_name: Name of the field
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if pd.isna(value):
            return True, None  # NaN values are handled separately
        
        if field_name not in self.ranges:
            return True, None  # No range defined, assume valid
        
        range_def = self.ranges[field_name]
        min_val = range_def['min']
        max_val = range_def['max']
        
        if value < min_val or value > max_val:
            error_msg = f"Value {value} outside valid range [{min_val}, {max_val}] {range_def['unit']}"
            return False, error_msg
        
        return True, None
    
    def validate_column(self, data: pd.Series, field_name: str) -> Dict:
        """
        Validate all values in a column
        
        Args:
            data: Series to validate
            field_name: Name of the field
            
        Returns:
            Dictionary with validation results
        """
        if field_name not in self.ranges:
            return {
                'field': field_name,
                'validated': False,
                'reason': 'No range definition available'
            }
        
        range_def = self.ranges[field_name]
        min_val = range_def['min']
        max_val = range_def['max']
        
        # Remove NaN values for validation
        clean_data = data.dropna()
        
        if len(clean_data) == 0:
            return {
                'field': field_name,
                'validated': True,
                'violations': 0,
                'note': 'All values are NaN'
            }
        
        # Check for violations
        below_min = clean_data < min_val
        above_max = clean_data > max_val
        violations = below_min | above_max
        
        violation_count = violations.sum()
        
        result = {
            'field': field_name,
            'validated': violation_count == 0,
            'range': {'min': min_val, 'max': max_val, 'unit': range_def['unit']},
            'violations': int(violation_count),
            'violation_percentage': float(violation_count / len(clean_data) * 100),
            'below_min_count': int(below_min.sum()),
            'above_max_count': int(above_max.sum()),
            'actual_min': float(clean_data.min()),
            'actual_max': float(clean_data.max()),
            'total_values': len(clean_data)
        }
        
        if violation_count > 0:
            # Get examples of violations
            violation_examples = clean_data[violations].head(5).tolist()
            result['violation_examples'] = violation_examples
        
        return result
    
    def validate_dataframe(self, data: pd.DataFrame) -> Dict:
        """
        Validate all applicable columns in a DataFrame
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Dictionary with validation results for all columns
        """
        logger.info(f"Validating {len(data.columns)} columns against defined ranges")
        
        results = {}
        validated_count = 0
        violation_count = 0
        
        for column in data.columns:
            # Check if column matches any defined range (case-insensitive)
            matching_range = None
            for range_key in self.ranges.keys():
                if column.lower() == range_key.lower() or \
                   column.lower().replace('_', '') == range_key.lower().replace('_', ''):
                    matching_range = range_key
                    break
            
            if matching_range:
                result = self.validate_column(data[column], matching_range)
                results[column] = result
                validated_count += 1
                
                if not result['validated']:
                    violation_count += 1
        
        summary = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_columns': len(data.columns),
            'validated_columns': validated_count,
            'columns_with_violations': violation_count,
            'validation_passed': violation_count == 0,
            'column_results': results
        }
        
        if violation_count > 0:
            logger.warning(f"Range validation found violations in {violation_count} columns")
        else:
            logger.info(f"Range validation passed for all {validated_count} validated columns")
        
        return summary
    
    def get_violations_summary(self, data: pd.DataFrame) -> List[Dict]:
        """
        Get summary of all range violations
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            List of dictionaries with violation details
        """
        validation_results = self.validate_dataframe(data)
        
        violations = []
        
        for column, result in validation_results['column_results'].items():
            if not result['validated'] and result['violations'] > 0:
                violations.append({
                    'column': column,
                    'violations': result['violations'],
                    'percentage': result['violation_percentage'],
                    'expected_range': f"[{result['range']['min']}, {result['range']['max']}] {result['range']['unit']}",
                    'actual_range': f"[{result['actual_min']:.2f}, {result['actual_max']:.2f}]",
                    'below_min': result['below_min_count'],
                    'above_max': result['above_max_count']
                })
        
        # Sort by violation count
        violations.sort(key=lambda x: x['violations'], reverse=True)
        
        return violations
    
    def generate_range_report(self, data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive range validation report
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary with complete range validation analysis
        """
        logger.info("Generating range validation report")
        
        validation_results = self.validate_dataframe(data)
        violations_summary = self.get_violations_summary(data)
        
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'dataset_info': {
                'rows': len(data),
                'columns': len(data.columns)
            },
            'validation_summary': {
                'total_columns': validation_results['total_columns'],
                'validated_columns': validation_results['validated_columns'],
                'columns_with_violations': validation_results['columns_with_violations'],
                'validation_passed': validation_results['validation_passed']
            },
            'violations': violations_summary,
            'detailed_results': validation_results['column_results']
        }
        
        return report
    
    def get_range_summary(self, data: pd.DataFrame) -> str:
        """
        Get human-readable range validation summary
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Formatted string summary
        """
        report = self.generate_range_report(data)
        
        summary = f"""
Range Validation Summary
{'='*50}
Dataset: {report['dataset_info']['rows']:,} rows × {report['dataset_info']['columns']} columns

Validation Results:
  - Columns Validated: {report['validation_summary']['validated_columns']}
  - Columns with Violations: {report['validation_summary']['columns_with_violations']}
  - Status: {'✓ PASSED' if report['validation_summary']['validation_passed'] else '✗ FAILED'}
"""
        
        if report['violations']:
            summary += "\nTop Violations:\n"
            for i, violation in enumerate(report['violations'][:5], 1):
                summary += f"  {i}. {violation['column']}: {violation['violations']} violations ({violation['percentage']:.1f}%)\n"
                summary += f"     Expected: {violation['expected_range']}, Actual: {violation['actual_range']}\n"
        
        return summary.strip()
    
    def get_available_ranges(self) -> pd.DataFrame:
        """
        Get DataFrame of all available range definitions
        
        Returns:
            DataFrame with range definitions
        """
        ranges_list = []
        
        for field, range_def in self.ranges.items():
            ranges_list.append({
                'field': field,
                'min': range_def['min'],
                'max': range_def['max'],
                'unit': range_def['unit'],
                'type': range_def['type']
            })
        
        return pd.DataFrame(ranges_list).sort_values('type')
