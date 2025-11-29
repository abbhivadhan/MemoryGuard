"""
Model Interpretability Module

Provides SHAP-based explanations for ML model predictions.
"""

from ml_pipeline.interpretability.shap_explainer import (
    SHAPExplainer,
    TreeSHAPExplainer,
    DeepSHAPExplainer
)
from ml_pipeline.interpretability.feature_importance import FeatureImportanceAnalyzer
from ml_pipeline.interpretability.visualization import InterpretabilityVisualizer
from ml_pipeline.interpretability.confidence_intervals import ConfidenceIntervalCalculator

__all__ = [
    'SHAPExplainer',
    'TreeSHAPExplainer',
    'DeepSHAPExplainer',
    'FeatureImportanceAnalyzer',
    'InterpretabilityVisualizer',
    'ConfidenceIntervalCalculator'
]
