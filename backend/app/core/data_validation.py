"""
Data Validation Utilities
Validates data to ensure no placeholder or demo data is used
Requirements: 21.8
"""

import re
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Common placeholder patterns
PLACEHOLDER_PATTERNS = [
    r'demo',
    r'test.*data',
    r'placeholder',
    r'sample',
    r'fake',
    r'mock',
    r'example',
    r'lorem.*ipsum',
    r'xxx+',
    r'\[.*\]',  # [placeholder]
    r'\{.*\}',  # {placeholder}
]

# Common demo values
DEMO_VALUES = [
    'demo',
    'test',
    'sample',
    'placeholder',
    'example',
    'fake',
    'mock',
    'n/a',
    'tbd',
    'todo',
]

# Common placeholder numbers
PLACEHOLDER_NUMBERS = [
    0,
    -1,
    999,
    9999,
    99999,
    123,
    12345,
    111111,
    123456789,
]


def is_placeholder_string(value: str) -> bool:
    """
    Check if a string value appears to be placeholder/demo data
    
    Args:
        value: String to check
        
    Returns:
        True if value appears to be placeholder data
    """
    if not value or not isinstance(value, str):
        return False
    
    normalized = value.strip().lower()
    
    # Check against demo values
    if normalized in DEMO_VALUES:
        return True
    
    # Check against patterns
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
    
    return False


def is_placeholder_number(value: float) -> bool:
    """
    Check if a number appears to be a placeholder value
    
    Args:
        value: Number to check
        
    Returns:
        True if value appears to be placeholder data
    """
    return value in PLACEHOLDER_NUMBERS


def validate_health_metric(metric_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate health metric data
    
    Args:
        metric_data: Dictionary containing metric information
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    if 'name' not in metric_data:
        errors.append('Metric name is required')
    elif is_placeholder_string(metric_data['name']):
        errors.append(f"Metric name '{metric_data['name']}' appears to be placeholder data")
    
    if 'value' not in metric_data:
        errors.append('Metric value is required')
    elif not isinstance(metric_data['value'], (int, float)):
        errors.append('Metric value must be a number')
    elif is_placeholder_number(metric_data['value']):
        errors.append(f"Metric value {metric_data['value']} appears to be placeholder data")
    
    if 'type' not in metric_data:
        errors.append('Metric type is required')
    elif metric_data['type'] not in ['cognitive', 'biomarker', 'imaging', 'lifestyle', 'cardiovascular']:
        errors.append(f"Invalid metric type: {metric_data['type']}")
    
    # Type-specific validation
    if 'type' in metric_data and 'name' in metric_data and 'value' in metric_data:
        metric_type = metric_data['type']
        metric_name = metric_data['name'].lower()
        metric_value = metric_data['value']
        
        if metric_type == 'cognitive':
            if 'mmse' in metric_name and not (0 <= metric_value <= 30):
                errors.append('MMSE score must be between 0 and 30')
            elif 'moca' in metric_name and not (0 <= metric_value <= 30):
                errors.append('MoCA score must be between 0 and 30')
            elif 'cdr' in metric_name and not (0 <= metric_value <= 3):
                errors.append('CDR score must be between 0 and 3')
        
        elif metric_type == 'biomarker':
            if metric_value < 0:
                errors.append('Biomarker values cannot be negative')
        
        elif metric_type == 'imaging':
            if metric_value < 0:
                errors.append('Imaging measurements cannot be negative')
    
    return len(errors) == 0, errors


def validate_medication(medication_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate medication data
    
    Args:
        medication_data: Dictionary containing medication information
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    if 'name' not in medication_data:
        errors.append('Medication name is required')
    elif not medication_data['name'] or not medication_data['name'].strip():
        errors.append('Medication name cannot be empty')
    elif is_placeholder_string(medication_data['name']):
        errors.append(f"Medication name '{medication_data['name']}' appears to be placeholder data")
    
    if 'dosage' not in medication_data:
        errors.append('Dosage is required')
    elif not medication_data['dosage'] or not medication_data['dosage'].strip():
        errors.append('Dosage cannot be empty')
    elif is_placeholder_string(medication_data['dosage']):
        errors.append(f"Dosage '{medication_data['dosage']}' appears to be placeholder data")
    
    if 'frequency' not in medication_data:
        errors.append('Frequency is required')
    elif is_placeholder_string(medication_data['frequency']):
        errors.append(f"Frequency '{medication_data['frequency']}' appears to be placeholder data")
    
    return len(errors) == 0, errors


def validate_assessment(assessment_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate assessment data
    
    Args:
        assessment_data: Dictionary containing assessment information
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    if 'type' not in assessment_data:
        errors.append('Assessment type is required')
    elif assessment_data['type'] not in ['MMSE', 'MoCA', 'CDR', 'ClockDrawing']:
        errors.append(f"Invalid assessment type: {assessment_data['type']}")
    
    if 'score' in assessment_data:
        score = assessment_data['score']
        
        if not isinstance(score, (int, float)):
            errors.append('Score must be a number')
        elif is_placeholder_number(score):
            errors.append(f"Score {score} appears to be placeholder data")
        
        # Check score range
        if 'max_score' in assessment_data:
            max_score = assessment_data['max_score']
            if not (0 <= score <= max_score):
                errors.append(f"Score must be between 0 and {max_score}")
    
    return len(errors) == 0, errors


def log_validation_warning(data_type: str, data: Dict[str, Any], errors: List[str]) -> None:
    """
    Log validation warnings
    
    Args:
        data_type: Type of data being validated
        data: The data that failed validation
        errors: List of validation errors
    """
    logger.warning(
        f"Data validation failed for {data_type}",
        extra={
            'data_type': data_type,
            'data': data,
            'errors': errors,
        }
    )


def validate_and_log(
    data_type: str,
    data: Dict[str, Any],
    validator_func
) -> Tuple[bool, List[str]]:
    """
    Validate data and log if validation fails
    
    Args:
        data_type: Type of data being validated
        data: The data to validate
        validator_func: Validation function to use
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    is_valid, errors = validator_func(data)
    
    if not is_valid:
        log_validation_warning(data_type, data, errors)
    
    return is_valid, errors
