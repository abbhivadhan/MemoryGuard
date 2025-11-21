"""
Health Metrics Validation Service.
Validates metric types, values, and data completeness.
Requirements: 3.5, 11.7
"""
from typing import Dict, List, Optional, Tuple
from app.models.health_metric import MetricType
import logging

logger = logging.getLogger(__name__)


class HealthMetricValidator:
    """
    Validator for health metrics with type-specific validation rules.
    """
    
    # Define valid metric names and their expected ranges for each type
    METRIC_DEFINITIONS: Dict[MetricType, Dict[str, Dict]] = {
        MetricType.COGNITIVE: {
            "MMSE Score": {
                "min": 0,
                "max": 30,
                "unit": "points",
                "description": "Mini-Mental State Examination score"
            },
            "MoCA Score": {
                "min": 0,
                "max": 30,
                "unit": "points",
                "description": "Montreal Cognitive Assessment score"
            },
            "CDR Score": {
                "min": 0,
                "max": 3,
                "unit": "rating",
                "description": "Clinical Dementia Rating"
            },
            "Clock Drawing Score": {
                "min": 0,
                "max": 10,
                "unit": "points",
                "description": "Clock Drawing Test score"
            }
        },
        MetricType.BIOMARKER: {
            "Amyloid-beta 42": {
                "min": 0,
                "max": 2000,
                "unit": "pg/mL",
                "description": "CSF Amyloid-beta 42 level"
            },
            "Total Tau": {
                "min": 0,
                "max": 1500,
                "unit": "pg/mL",
                "description": "CSF Total Tau level"
            },
            "Phosphorylated Tau": {
                "min": 0,
                "max": 200,
                "unit": "pg/mL",
                "description": "CSF Phosphorylated Tau level"
            },
            "Tau/Aβ42 Ratio": {
                "min": 0,
                "max": 5,
                "unit": "ratio",
                "description": "Tau to Amyloid-beta 42 ratio"
            }
        },
        MetricType.IMAGING: {
            "Hippocampal Volume": {
                "min": 1000,
                "max": 8000,
                "unit": "mm³",
                "description": "Total hippocampal volume"
            },
            "Cortical Thickness": {
                "min": 1.0,
                "max": 5.0,
                "unit": "mm",
                "description": "Average cortical thickness"
            },
            "Entorhinal Cortex Volume": {
                "min": 500,
                "max": 4000,
                "unit": "mm³",
                "description": "Entorhinal cortex volume"
            },
            "Whole Brain Volume": {
                "min": 800000,
                "max": 1600000,
                "unit": "mm³",
                "description": "Total brain volume"
            }
        },
        MetricType.LIFESTYLE: {
            "Sleep Duration": {
                "min": 0,
                "max": 24,
                "unit": "hours",
                "description": "Average sleep duration per night"
            },
            "Physical Activity": {
                "min": 0,
                "max": 1440,
                "unit": "minutes",
                "description": "Physical activity minutes per day"
            },
            "Diet Quality Score": {
                "min": 0,
                "max": 100,
                "unit": "score",
                "description": "Diet quality assessment score"
            },
            "Social Engagement": {
                "min": 0,
                "max": 100,
                "unit": "score",
                "description": "Social engagement frequency score"
            },
            "Cognitive Activity": {
                "min": 0,
                "max": 100,
                "unit": "score",
                "description": "Cognitive activity engagement score"
            }
        },
        MetricType.CARDIOVASCULAR: {
            "Systolic Blood Pressure": {
                "min": 60,
                "max": 250,
                "unit": "mmHg",
                "description": "Systolic blood pressure"
            },
            "Diastolic Blood Pressure": {
                "min": 40,
                "max": 150,
                "unit": "mmHg",
                "description": "Diastolic blood pressure"
            },
            "Total Cholesterol": {
                "min": 100,
                "max": 400,
                "unit": "mg/dL",
                "description": "Total cholesterol level"
            },
            "LDL Cholesterol": {
                "min": 0,
                "max": 300,
                "unit": "mg/dL",
                "description": "Low-density lipoprotein cholesterol"
            },
            "HDL Cholesterol": {
                "min": 0,
                "max": 150,
                "unit": "mg/dL",
                "description": "High-density lipoprotein cholesterol"
            },
            "Triglycerides": {
                "min": 0,
                "max": 1000,
                "unit": "mg/dL",
                "description": "Triglyceride level"
            },
            "Fasting Glucose": {
                "min": 40,
                "max": 600,
                "unit": "mg/dL",
                "description": "Fasting blood glucose level"
            },
            "HbA1c": {
                "min": 3.0,
                "max": 15.0,
                "unit": "%",
                "description": "Hemoglobin A1c percentage"
            }
        }
    }
    
    @classmethod
    def validate_metric(
        cls,
        metric_type: MetricType,
        name: str,
        value: float,
        unit: str
    ) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """
        Validate a health metric against defined rules.
        
        Args:
            metric_type: Type of the metric
            name: Name of the metric
            value: Value of the metric
            unit: Unit of measurement
            
        Returns:
            Tuple of (is_valid, error_message, warnings)
            
        Requirements: 3.5, 11.7
        """
        warnings = []
        
        # Check if metric type has definitions
        if metric_type not in cls.METRIC_DEFINITIONS:
            return False, f"Unknown metric type: {metric_type}", None
        
        # Check if metric name is recognized
        metric_defs = cls.METRIC_DEFINITIONS[metric_type]
        if name not in metric_defs:
            # Allow custom metrics but add warning
            warnings.append(f"Metric '{name}' is not a standard metric for type '{metric_type.value}'")
            logger.warning(f"Non-standard metric: {name} for type {metric_type.value}")
            return True, None, warnings
        
        # Get metric definition
        metric_def = metric_defs[name]
        
        # Validate unit
        expected_unit = metric_def["unit"]
        if unit != expected_unit:
            warnings.append(f"Expected unit '{expected_unit}' but got '{unit}'")
        
        # Validate value range
        min_val = metric_def["min"]
        max_val = metric_def["max"]
        
        if value < min_val or value > max_val:
            # Check if it's significantly out of range (error) or just unusual (warning)
            if value < min_val * 0.5 or value > max_val * 1.5:
                return False, f"Value {value} is out of valid range [{min_val}, {max_val}] for {name}", None
            else:
                warnings.append(f"Value {value} is outside typical range [{min_val}, {max_val}] for {name}")
        
        return True, None, warnings if warnings else None
    
    @classmethod
    def check_data_completeness(
        cls,
        metric_type: MetricType,
        user_metrics: List[Dict]
    ) -> Dict[str, any]:
        """
        Check completeness of health data for a given metric type.
        
        Args:
            metric_type: Type of metrics to check
            user_metrics: List of user's metrics of this type
            
        Returns:
            Dictionary with completeness information
            
        Requirements: 3.5, 11.7
        """
        if metric_type not in cls.METRIC_DEFINITIONS:
            return {
                "complete": False,
                "error": f"Unknown metric type: {metric_type}"
            }
        
        # Get expected metrics for this type
        expected_metrics = set(cls.METRIC_DEFINITIONS[metric_type].keys())
        
        # Get user's metric names
        user_metric_names = set(m.get("name") for m in user_metrics)
        
        # Calculate completeness
        missing_metrics = expected_metrics - user_metric_names
        extra_metrics = user_metric_names - expected_metrics
        
        completeness_percentage = (
            len(user_metric_names & expected_metrics) / len(expected_metrics) * 100
            if expected_metrics else 0
        )
        
        return {
            "complete": len(missing_metrics) == 0,
            "completeness_percentage": round(completeness_percentage, 2),
            "expected_count": len(expected_metrics),
            "provided_count": len(user_metric_names & expected_metrics),
            "missing_metrics": list(missing_metrics),
            "extra_metrics": list(extra_metrics),
            "recommendations": cls._generate_recommendations(metric_type, missing_metrics)
        }
    
    @classmethod
    def _generate_recommendations(
        cls,
        metric_type: MetricType,
        missing_metrics: set
    ) -> List[str]:
        """
        Generate recommendations for missing metrics.
        
        Args:
            metric_type: Type of metrics
            missing_metrics: Set of missing metric names
            
        Returns:
            List of recommendation strings
        """
        if not missing_metrics:
            return ["All standard metrics are recorded. Great job!"]
        
        recommendations = []
        metric_defs = cls.METRIC_DEFINITIONS.get(metric_type, {})
        
        for metric_name in missing_metrics:
            if metric_name in metric_defs:
                description = metric_defs[metric_name]["description"]
                recommendations.append(f"Consider adding {metric_name}: {description}")
        
        return recommendations
    
    @classmethod
    def get_metric_info(cls, metric_type: MetricType, name: str) -> Optional[Dict]:
        """
        Get information about a specific metric.
        
        Args:
            metric_type: Type of the metric
            name: Name of the metric
            
        Returns:
            Dictionary with metric information or None if not found
        """
        if metric_type not in cls.METRIC_DEFINITIONS:
            return None
        
        metric_defs = cls.METRIC_DEFINITIONS[metric_type]
        if name not in metric_defs:
            return None
        
        return metric_defs[name]
    
    @classmethod
    def get_all_metrics_for_type(cls, metric_type: MetricType) -> Dict[str, Dict]:
        """
        Get all defined metrics for a specific type.
        
        Args:
            metric_type: Type of metrics to retrieve
            
        Returns:
            Dictionary of metric definitions
        """
        return cls.METRIC_DEFINITIONS.get(metric_type, {})
    
    @classmethod
    def validate_batch(
        cls,
        metrics: List[Dict]
    ) -> Dict[str, any]:
        """
        Validate a batch of metrics.
        
        Args:
            metrics: List of metric dictionaries with type, name, value, unit
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": [],
            "invalid": [],
            "warnings": []
        }
        
        for idx, metric in enumerate(metrics):
            try:
                metric_type = MetricType(metric.get("type"))
                name = metric.get("name")
                value = metric.get("value")
                unit = metric.get("unit")
                
                is_valid, error, warnings = cls.validate_metric(
                    metric_type, name, value, unit
                )
                
                if is_valid:
                    results["valid"].append({
                        "index": idx,
                        "metric": metric,
                        "warnings": warnings
                    })
                    if warnings:
                        results["warnings"].extend([
                            f"Metric {idx} ({name}): {w}" for w in warnings
                        ])
                else:
                    results["invalid"].append({
                        "index": idx,
                        "metric": metric,
                        "error": error
                    })
            except Exception as e:
                results["invalid"].append({
                    "index": idx,
                    "metric": metric,
                    "error": str(e)
                })
        
        return results
