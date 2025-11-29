"""
Feature Engineering Module

This module provides comprehensive feature engineering capabilities for biomedical data,
transforming raw data from ADNI, OASIS, and NACC into ML-ready features.
"""

from .cognitive_features import CognitiveFeatureExtractor
from .biomarker_features import BiomarkerFeatureProcessor
from .imaging_features import ImagingFeatureExtractor
from .genetic_features import GeneticFeatureEncoder
from .demographic_features import DemographicFeatureProcessor
from .imputation import MissingDataImputer
from .normalization import FeatureNormalizer
from .temporal_features import TemporalFeatureEngineer
from .feature_report import FeatureReportGenerator
from .pipeline import FeatureEngineeringPipeline

__all__ = [
    'CognitiveFeatureExtractor',
    'BiomarkerFeatureProcessor',
    'ImagingFeatureExtractor',
    'GeneticFeatureEncoder',
    'DemographicFeatureProcessor',
    'MissingDataImputer',
    'FeatureNormalizer',
    'TemporalFeatureEngineer',
    'FeatureReportGenerator',
    'FeatureEngineeringPipeline'
]
