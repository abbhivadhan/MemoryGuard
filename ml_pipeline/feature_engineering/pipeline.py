"""
Feature Engineering Pipeline

Main pipeline that orchestrates all feature engineering steps:
1. Cognitive feature extraction
2. Biomarker feature processing
3. Imaging feature extraction
4. Genetic feature encoding
5. Demographic feature processing
6. Missing data imputation
7. Feature normalization
8. Temporal feature engineering
9. Feature report generation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import logging

from .cognitive_features import CognitiveFeatureExtractor
from .biomarker_features import BiomarkerFeatureProcessor
from .imaging_features import ImagingFeatureExtractor
from .genetic_features import GeneticFeatureEncoder
from .demographic_features import DemographicFeatureProcessor
from .imputation import MissingDataImputer
from .normalization import FeatureNormalizer
from .temporal_features import TemporalFeatureEngineer
from .feature_report import FeatureReportGenerator

logger = logging.getLogger(__name__)


class FeatureEngineeringPipeline:
    """Complete feature engineering pipeline for biomedical data"""
    
    def __init__(
        self,
        imputation_strategy: str = 'iterative',
        normalization_method: str = 'standard',
        include_temporal: bool = True
    ):
        """
        Initialize feature engineering pipeline
        
        Args:
            imputation_strategy: Strategy for missing data imputation
            normalization_method: Method for feature normalization
            include_temporal: Whether to include temporal features
        """
        self.imputation_strategy = imputation_strategy
        self.normalization_method = normalization_method
        self.include_temporal = include_temporal
        
        # Initialize extractors
        self.cognitive_extractor = CognitiveFeatureExtractor()
        self.biomarker_processor = BiomarkerFeatureProcessor()
        self.imaging_extractor = ImagingFeatureExtractor()
        self.genetic_encoder = GeneticFeatureEncoder()
        self.demographic_processor = DemographicFeatureProcessor()
        self.temporal_engineer = TemporalFeatureEngineer()
        
        # Initialize transformers
        self.imputer = MissingDataImputer(strategy=imputation_strategy)
        self.normalizer = FeatureNormalizer(method=normalization_method)
        
        # Initialize reporter
        self.reporter = FeatureReportGenerator()
        
        self.is_fitted = False
        
    def fit_transform(
        self,
        data: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        visit_date_col: str = 'visit_date'
    ) -> pd.DataFrame:
        """
        Fit pipeline and transform data
        
        Args:
            data: Raw biomedical data
            patient_id_col: Name of patient ID column
            visit_date_col: Name of visit date column
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Starting feature engineering pipeline")
        
        # Step 1: Extract cognitive features
        logger.info("Step 1/9: Extracting cognitive features")
        cognitive_features = self.cognitive_extractor.extract_features(data)
        
        # Step 2: Process biomarker features
        logger.info("Step 2/9: Processing biomarker features")
        biomarker_features = self.biomarker_processor.extract_features(data)
        
        # Step 3: Extract imaging features
        logger.info("Step 3/9: Extracting imaging features")
        imaging_features = self.imaging_extractor.extract_features(data)
        
        # Step 4: Encode genetic features
        logger.info("Step 4/9: Encoding genetic features")
        genetic_features = self.genetic_encoder.extract_features(data)
        
        # Step 5: Process demographic features
        logger.info("Step 5/9: Processing demographic features")
        demographic_features = self.demographic_processor.extract_features(data)
        
        # Combine all features
        all_features = pd.concat([
            cognitive_features,
            biomarker_features,
            imaging_features,
            genetic_features,
            demographic_features
        ], axis=1)
        
        # Step 6: Impute missing data
        logger.info("Step 6/9: Imputing missing data")
        imputed_features = self.imputer.fit_transform(all_features)
        
        # Step 7: Normalize features
        logger.info("Step 7/9: Normalizing features")
        normalized_features = self.normalizer.fit_transform(imputed_features)
        
        # Step 8: Add temporal features (if requested and data is longitudinal)
        if self.include_temporal and patient_id_col in data.columns:
            logger.info("Step 8/9: Engineering temporal features")
            temporal_features = self.temporal_engineer.extract_features(
                data, patient_id_col, visit_date_col
            )
            
            # Normalize temporal features
            temporal_normalized = self.normalizer.transform(temporal_features)
            
            # Combine with other features
            normalized_features = pd.concat([
                normalized_features,
                temporal_normalized
            ], axis=1)
        else:
            logger.info("Step 8/9: Skipping temporal features")
        
        # Step 9: Generate feature report
        logger.info("Step 9/9: Generating feature report")
        self.feature_report = self.reporter.generate_report(normalized_features)
        
        self.is_fitted = True
        
        logger.info(f"Feature engineering complete. Total features: {len(normalized_features.columns)}")
        return normalized_features
    
    def transform(
        self,
        data: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        visit_date_col: str = 'visit_date'
    ) -> pd.DataFrame:
        """
        Transform new data using fitted pipeline
        
        Args:
            data: Raw biomedical data
            patient_id_col: Name of patient ID column
            visit_date_col: Name of visit date column
            
        Returns:
            DataFrame with engineered features
        """
        if not self.is_fitted:
            raise ValueError("Pipeline not fitted. Call fit_transform first.")
        
        logger.info("Transforming new data")
        
        # Extract features
        cognitive_features = self.cognitive_extractor.extract_features(data)
        biomarker_features = self.biomarker_processor.extract_features(data)
        imaging_features = self.imaging_extractor.extract_features(data)
        genetic_features = self.genetic_encoder.extract_features(data)
        demographic_features = self.demographic_processor.extract_features(data)
        
        # Combine features
        all_features = pd.concat([
            cognitive_features,
            biomarker_features,
            imaging_features,
            genetic_features,
            demographic_features
        ], axis=1)
        
        # Impute and normalize
        imputed_features = self.imputer.transform(all_features)
        normalized_features = self.normalizer.transform(imputed_features)
        
        # Add temporal features if requested
        if self.include_temporal and patient_id_col in data.columns:
            temporal_features = self.temporal_engineer.extract_features(
                data, patient_id_col, visit_date_col
            )
            temporal_normalized = self.normalizer.transform(temporal_features)
            normalized_features = pd.concat([
                normalized_features,
                temporal_normalized
            ], axis=1)
        
        return normalized_features
    
    def get_feature_names(self) -> List[str]:
        """
        Get list of all feature names
        
        Returns:
            List of feature names
        """
        if not self.is_fitted:
            raise ValueError("Pipeline not fitted. Call fit_transform first.")
        
        feature_names = []
        feature_names.extend(self.cognitive_extractor.get_feature_names())
        feature_names.extend(self.biomarker_processor.get_feature_names())
        feature_names.extend(self.imaging_extractor.get_feature_names())
        feature_names.extend(self.genetic_encoder.get_feature_names())
        feature_names.extend(self.demographic_processor.get_feature_names())
        
        if self.include_temporal:
            feature_names.extend(self.temporal_engineer.get_feature_names())
        
        return feature_names
    
    def get_feature_report(self) -> Dict:
        """
        Get feature engineering report
        
        Returns:
            Dictionary with feature report
        """
        if not self.is_fitted:
            raise ValueError("Pipeline not fitted. Call fit_transform first.")
        
        return self.feature_report
    
    def save_feature_documentation(self, output_path: Path) -> None:
        """
        Save feature documentation to file
        
        Args:
            output_path: Path to save documentation
        """
        if not self.is_fitted:
            raise ValueError("Pipeline not fitted. Call fit_transform first.")
        
        # Get all features (need to reconstruct from report)
        logger.info(f"Saving feature documentation to {output_path}")
        
        # Save report
        self.reporter.save_report(self.feature_report, output_path)
    
    def validate_pipeline(self, data: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate pipeline on data
        
        Args:
            data: DataFrame with features
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Validate each component
        validation['cognitive'] = self.cognitive_extractor.validate_features(data)
        validation['biomarker'] = self.biomarker_processor.validate_features(data)
        validation['imaging'] = self.imaging_extractor.validate_features(data)
        validation['genetic'] = self.genetic_encoder.validate_features(data)
        validation['demographic'] = self.demographic_processor.validate_features(data)
        
        if self.include_temporal:
            validation['temporal'] = self.temporal_engineer.validate_features(data)
        
        return validation
