"""Data Validation Engine - Main interface for all data validation operations"""

import pandas as pd
from typing import Dict, Optional, List
from pathlib import Path
import logging

from .phi_detector import PHIDetector
from .deidentification_verifier import DeidentificationVerifier
from .completeness_checker import CompletenessChecker
from .outlier_detector import OutlierDetector
from .range_validator import RangeValidator
from .duplicate_detector import DuplicateDetector
from .temporal_validator import TemporalValidator
from .quality_reporter import QualityReporter

logger = logging.getLogger(__name__)


class DataValidationEngine:
    """
    Main data validation engine that orchestrates all validation checks
    """
    
    def __init__(self, 
                 completeness_threshold: float = 0.70,
                 k_anonymity_threshold: int = 5):
        """
        Initialize data validation engine
        
        Args:
            completeness_threshold: Minimum acceptable completeness (default: 0.70)
            k_anonymity_threshold: Minimum k value for k-anonymity (default: 5)
        """
        self.phi_detector = PHIDetector()
        self.deidentification_verifier = DeidentificationVerifier(k_threshold=k_anonymity_threshold)
        self.completeness_checker = CompletenessChecker(completeness_threshold=completeness_threshold)
        self.outlier_detector = OutlierDetector()
        self.range_validator = RangeValidator()
        self.duplicate_detector = DuplicateDetector()
        self.temporal_validator = TemporalValidator()
        self.quality_reporter = QualityReporter()
        
        self.completeness_threshold = completeness_threshold
        self.k_anonymity_threshold = k_anonymity_threshold
        
        logger.info(f"Initialized DataValidationEngine (completeness={completeness_threshold}, k={k_anonymity_threshold})")
    
    def validate_dataset(self, 
                        data: pd.DataFrame,
                        dataset_name: str = "Unknown",
                        patient_id_col: Optional[str] = None,
                        visit_date_col: Optional[str] = None,
                        strict_mode: bool = True) -> Dict:
        """
        Perform complete validation of a dataset
        
        Args:
            data: DataFrame to validate
            dataset_name: Name of the dataset
            patient_id_col: Name of patient ID column (optional)
            visit_date_col: Name of visit date column (optional)
            strict_mode: If True, fail on any validation error
            
        Returns:
            Dictionary with validation results and quality report
        """
        logger.info(f"Starting validation for dataset: {dataset_name}")
        logger.info(f"Dataset shape: {data.shape}")
        
        # Generate comprehensive quality report
        report = self.quality_reporter.generate_comprehensive_report(
            data=data,
            dataset_name=dataset_name,
            patient_id_col=patient_id_col,
            visit_date_col=visit_date_col
        )
        
        # Determine if validation passed
        if strict_mode:
            validation_passed = (
                not report['phi_detection']['phi_detected'] and
                report['deidentification']['verification_passed'] and
                report['completeness']['validation']['validation_passed'] and
                report['range_validation']['validation_summary']['validation_passed'] and
                report['duplicates']['validation_passed']
            )
        else:
            # In non-strict mode, only fail on critical issues
            validation_passed = (
                not report['phi_detection']['phi_detected'] and
                report['completeness']['validation']['overall_completeness'] >= 0.50
            )
        
        report['validation_passed'] = validation_passed
        report['strict_mode'] = strict_mode
        
        if validation_passed:
            logger.info(f"✓ Dataset validation PASSED for {dataset_name}")
        else:
            logger.error(f"✗ Dataset validation FAILED for {dataset_name}")
        
        return report
    
    def quick_validate(self, data: pd.DataFrame) -> Dict:
        """
        Perform quick validation (PHI, completeness, duplicates only)
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Dictionary with quick validation results
        """
        logger.info("Running quick validation")
        
        results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'dataset_shape': data.shape
        }
        
        # PHI check
        phi_detected = self.phi_detector.detect_phi(data)
        results['phi_detected'] = bool(phi_detected)
        results['phi_categories'] = list(phi_detected.keys()) if phi_detected else []
        
        # Completeness check
        overall_completeness = self.completeness_checker.get_overall_completeness(data)
        results['completeness'] = overall_completeness
        results['completeness_passed'] = overall_completeness >= self.completeness_threshold
        
        # Duplicate check
        exact_duplicates = self.duplicate_detector.detect_exact_duplicates(data)
        results['duplicate_rows'] = exact_duplicates['duplicate_rows']
        results['duplicates_detected'] = exact_duplicates['duplicate_rows'] > 0
        
        # Overall quick validation
        results['quick_validation_passed'] = (
            not results['phi_detected'] and
            results['completeness_passed'] and
            not results['duplicates_detected']
        )
        
        return results
    
    def validate_and_clean(self, 
                          data: pd.DataFrame,
                          remove_duplicates: bool = True,
                          remove_incomplete_columns: bool = False,
                          incomplete_threshold: float = 0.50) -> tuple[pd.DataFrame, Dict]:
        """
        Validate dataset and perform automatic cleaning
        
        Args:
            data: DataFrame to validate and clean
            remove_duplicates: Remove duplicate rows
            remove_incomplete_columns: Remove columns below threshold
            incomplete_threshold: Threshold for removing incomplete columns
            
        Returns:
            Tuple of (cleaned DataFrame, cleaning report)
        """
        logger.info("Starting validation and cleaning")
        
        original_shape = data.shape
        cleaned_data = data.copy()
        cleaning_report = {
            'original_shape': original_shape,
            'operations': []
        }
        
        # 1. Check for PHI
        phi_detected = self.phi_detector.detect_phi(cleaned_data)
        if phi_detected:
            logger.warning("PHI detected - cannot proceed with cleaning")
            cleaning_report['error'] = "PHI detected in dataset"
            cleaning_report['phi_columns'] = phi_detected
            return data, cleaning_report
        
        # 2. Remove duplicates
        if remove_duplicates:
            cleaned_data, dup_stats = self.duplicate_detector.remove_duplicates(cleaned_data)
            if dup_stats['removed_rows'] > 0:
                cleaning_report['operations'].append({
                    'operation': 'remove_duplicates',
                    'rows_removed': dup_stats['removed_rows']
                })
                logger.info(f"Removed {dup_stats['removed_rows']} duplicate rows")
        
        # 3. Remove incomplete columns
        if remove_incomplete_columns:
            columns_to_drop = self.completeness_checker.suggest_columns_to_drop(
                cleaned_data, 
                drop_threshold=incomplete_threshold
            )
            if columns_to_drop:
                cleaned_data = cleaned_data.drop(columns=columns_to_drop)
                cleaning_report['operations'].append({
                    'operation': 'remove_incomplete_columns',
                    'columns_removed': len(columns_to_drop),
                    'column_names': columns_to_drop
                })
                logger.info(f"Removed {len(columns_to_drop)} incomplete columns")
        
        # Final report
        cleaning_report['final_shape'] = cleaned_data.shape
        cleaning_report['rows_removed'] = original_shape[0] - cleaned_data.shape[0]
        cleaning_report['columns_removed'] = original_shape[1] - cleaned_data.shape[1]
        
        logger.info(f"Cleaning complete: {original_shape} → {cleaned_data.shape}")
        
        return cleaned_data, cleaning_report
    
    def generate_report(self,
                       data: pd.DataFrame,
                       dataset_name: str = "Unknown",
                       patient_id_col: Optional[str] = None,
                       visit_date_col: Optional[str] = None,
                       output_path: Optional[Path] = None,
                       format: str = 'json') -> Dict:
        """
        Generate and optionally save quality report
        
        Args:
            data: DataFrame to analyze
            dataset_name: Name of the dataset
            patient_id_col: Name of patient ID column (optional)
            visit_date_col: Name of visit date column (optional)
            output_path: Path to save report (optional)
            format: Output format ('json' or 'html')
            
        Returns:
            Quality report dictionary
        """
        report = self.quality_reporter.generate_comprehensive_report(
            data=data,
            dataset_name=dataset_name,
            patient_id_col=patient_id_col,
            visit_date_col=visit_date_col
        )
        
        if output_path:
            self.quality_reporter.save_report(report, output_path, format=format)
        
        return report
    
    def print_summary(self, report: Dict):
        """
        Print human-readable summary of validation report
        
        Args:
            report: Quality report dictionary
        """
        summary = self.quality_reporter.get_summary_text(report)
        print(summary)
    
    def get_validation_status(self, data: pd.DataFrame) -> str:
        """
        Get simple validation status string
        
        Args:
            data: DataFrame to check
            
        Returns:
            Status string ('PASS', 'FAIL', or 'WARNING')
        """
        quick_results = self.quick_validate(data)
        
        if quick_results['quick_validation_passed']:
            return 'PASS'
        elif quick_results['phi_detected']:
            return 'FAIL'
        else:
            return 'WARNING'
    
    def validate_for_ml_training(self, data: pd.DataFrame) -> tuple[bool, List[str]]:
        """
        Check if dataset is ready for ML training
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Tuple of (is_ready, list of blocking issues)
        """
        logger.info("Checking if dataset is ready for ML training")
        
        blocking_issues = []
        
        # Critical checks
        phi_detected = self.phi_detector.detect_phi(data)
        if phi_detected:
            blocking_issues.append("PHI detected in dataset")
        
        completeness = self.completeness_checker.get_overall_completeness(data)
        if completeness < self.completeness_threshold:
            blocking_issues.append(f"Completeness below threshold: {completeness*100:.1f}% < {self.completeness_threshold*100}%")
        
        # Check for critical columns (if they exist)
        critical_numeric_cols = [col for col in data.columns 
                                if pd.api.types.is_numeric_dtype(data[col])]
        if len(critical_numeric_cols) == 0:
            blocking_issues.append("No numeric columns found for ML training")
        
        is_ready = len(blocking_issues) == 0
        
        if is_ready:
            logger.info("✓ Dataset is ready for ML training")
        else:
            logger.warning(f"✗ Dataset not ready for ML training: {len(blocking_issues)} blocking issues")
        
        return is_ready, blocking_issues
