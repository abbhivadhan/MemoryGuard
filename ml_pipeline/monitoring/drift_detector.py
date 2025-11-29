"""
Statistical drift detection using Kolmogorov-Smirnov test and PSI
Detects changes in feature distributions that may affect model performance
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from ml_pipeline.config.settings import settings

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Detect statistical drift in feature distributions
    Uses Kolmogorov-Smirnov test and Population Stability Index
    """
    
    def __init__(
        self,
        reference_data: Optional[pd.DataFrame] = None,
        ks_threshold: float = 0.05,
        psi_threshold: float = 0.2
    ):
        """
        Initialize drift detector
        
        Args:
            reference_data: Reference dataset for comparison
            ks_threshold: P-value threshold for KS test (default: 0.05)
            psi_threshold: PSI threshold for drift detection (default: 0.2)
        """
        self.reference_data = reference_data
        self.ks_threshold = ks_threshold
        self.psi_threshold = psi_threshold
        
        logger.info(
            f"Initialized DriftDetector with KS threshold={ks_threshold}, "
            f"PSI threshold={psi_threshold}"
        )
    
    def set_reference_data(self, data: pd.DataFrame) -> None:
        """
        Set reference data for drift detection
        
        Args:
            data: Reference dataset
        """
        self.reference_data = data
        logger.info(f"Reference data set: {len(data)} samples, {len(data.columns)} features")
    
    def kolmogorov_smirnov_test(
        self,
        current_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame] = None,
        threshold: Optional[float] = None
    ) -> Dict[str, Dict]:
        """
        Perform Kolmogorov-Smirnov test for each feature
        
        The KS test detects differences between two probability distributions.
        A low p-value indicates the distributions are significantly different.
        
        Args:
            current_data: Current dataset to test
            reference_data: Reference dataset (uses stored if None)
            threshold: P-value threshold (uses stored if None)
            
        Returns:
            Dictionary with KS test results per feature
        """
        if reference_data is None:
            reference_data = self.reference_data
        
        if reference_data is None:
            raise ValueError("No reference data available for KS test")
        
        if threshold is None:
            threshold = self.ks_threshold
        
        results = {}
        
        for col in reference_data.columns:
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(reference_data[col]):
                continue
            
            if col not in current_data.columns:
                logger.warning(f"Feature {col} not in current data")
                continue
            
            # Get clean data (remove NaN)
            ref_values = reference_data[col].dropna()
            curr_values = current_data[col].dropna()
            
            if len(ref_values) == 0 or len(curr_values) == 0:
                logger.warning(f"Feature {col} has no valid data")
                continue
            
            # Perform KS test
            statistic, p_value = stats.ks_2samp(ref_values, curr_values)
            
            drift_detected = p_value < threshold
            
            results[col] = {
                'ks_statistic': float(statistic),
                'p_value': float(p_value),
                'drift_detected': drift_detected,
                'threshold': threshold,
                'reference_samples': len(ref_values),
                'current_samples': len(curr_values)
            }
            
            if drift_detected:
                logger.warning(
                    f"Drift detected in {col}: KS statistic={statistic:.4f}, "
                    f"p-value={p_value:.4f}"
                )
        
        # Summary
        n_features_tested = len(results)
        n_features_with_drift = sum(1 for r in results.values() if r['drift_detected'])
        
        logger.info(
            f"KS test complete: {n_features_with_drift}/{n_features_tested} "
            f"features with drift"
        )
        
        return results
    
    def calculate_psi(
        self,
        current_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame] = None,
        n_bins: int = 10,
        threshold: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate Population Stability Index (PSI) for each feature
        
        PSI measures the shift in population distribution:
        - PSI < 0.1: No significant change
        - 0.1 <= PSI < 0.2: Moderate change
        - PSI >= 0.2: Significant change (retraining recommended)
        
        Formula: PSI = sum((actual% - expected%) * ln(actual% / expected%))
        
        Args:
            current_data: Current dataset
            reference_data: Reference dataset (uses stored if None)
            n_bins: Number of bins for discretization
            threshold: PSI threshold (uses stored if None)
            
        Returns:
            Dictionary with PSI scores per feature
        """
        if reference_data is None:
            reference_data = self.reference_data
        
        if reference_data is None:
            raise ValueError("No reference data available for PSI calculation")
        
        if threshold is None:
            threshold = self.psi_threshold
        
        psi_scores = {}
        
        for col in reference_data.columns:
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(reference_data[col]):
                continue
            
            if col not in current_data.columns:
                logger.warning(f"Feature {col} not in current data")
                continue
            
            # Get clean data
            ref_values = reference_data[col].dropna()
            curr_values = current_data[col].dropna()
            
            if len(ref_values) == 0 or len(curr_values) == 0:
                logger.warning(f"Feature {col} has no valid data")
                continue
            
            try:
                # Create bins based on reference data
                bins = np.histogram_bin_edges(ref_values, bins=n_bins)
                
                # Ensure bins cover the range of both datasets
                min_val = min(ref_values.min(), curr_values.min())
                max_val = max(ref_values.max(), curr_values.max())
                bins[0] = min_val - 1e-10
                bins[-1] = max_val + 1e-10
                
                # Calculate histograms
                ref_counts, _ = np.histogram(ref_values, bins=bins)
                curr_counts, _ = np.histogram(curr_values, bins=bins)
                
                # Calculate proportions
                ref_props = ref_counts / len(ref_values)
                curr_props = curr_counts / len(curr_values)
                
                # Avoid division by zero and log(0)
                # Replace zeros with small value
                ref_props = np.where(ref_props == 0, 0.0001, ref_props)
                curr_props = np.where(curr_props == 0, 0.0001, curr_props)
                
                # Calculate PSI
                psi = np.sum((curr_props - ref_props) * np.log(curr_props / ref_props))
                psi_scores[col] = float(psi)
                
                if psi >= threshold:
                    logger.warning(f"High PSI detected in {col}: {psi:.4f}")
                
            except Exception as e:
                logger.error(f"Error calculating PSI for {col}: {e}")
                continue
        
        # Summary
        n_features_tested = len(psi_scores)
        n_features_high_psi = sum(1 for psi in psi_scores.values() if psi >= threshold)
        
        logger.info(
            f"PSI calculation complete: {n_features_high_psi}/{n_features_tested} "
            f"features with PSI >= {threshold}"
        )
        
        return psi_scores
    
    def detect_drift(
        self,
        current_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame] = None,
        methods: List[str] = ['ks', 'psi']
    ) -> Dict:
        """
        Comprehensive drift detection using multiple methods
        
        Args:
            current_data: Current dataset
            reference_data: Reference dataset (uses stored if None)
            methods: List of methods to use ('ks', 'psi')
            
        Returns:
            Dictionary with drift detection results
        """
        if reference_data is None:
            reference_data = self.reference_data
        
        if reference_data is None:
            raise ValueError("No reference data available")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'n_reference_samples': len(reference_data),
            'n_current_samples': len(current_data),
            'methods': methods
        }
        
        # Kolmogorov-Smirnov test
        if 'ks' in methods:
            logger.info("Running Kolmogorov-Smirnov test...")
            ks_results = self.kolmogorov_smirnov_test(current_data, reference_data)
            results['ks_test'] = ks_results
            results['features_with_ks_drift'] = [
                f for f, r in ks_results.items() if r['drift_detected']
            ]
        
        # Population Stability Index
        if 'psi' in methods:
            logger.info("Calculating Population Stability Index...")
            psi_scores = self.calculate_psi(current_data, reference_data)
            results['psi_scores'] = psi_scores
            results['features_with_high_psi'] = [
                f for f, psi in psi_scores.items() if psi >= self.psi_threshold
            ]
        
        # Overall drift detection
        drift_detected = False
        
        if 'ks' in methods:
            drift_detected = drift_detected or len(results['features_with_ks_drift']) > 0
        
        if 'psi' in methods:
            drift_detected = drift_detected or len(results['features_with_high_psi']) > 0
        
        results['drift_detected'] = drift_detected
        
        # Retraining recommendation
        results['retraining_recommended'] = self.should_retrain(results)
        
        logger.info(
            f"Drift detection complete: drift_detected={drift_detected}, "
            f"retraining_recommended={results['retraining_recommended']}"
        )
        
        return results
    
    def should_retrain(self, drift_results: Dict) -> bool:
        """
        Determine if model retraining is recommended based on drift results
        
        Args:
            drift_results: Results from detect_drift()
            
        Returns:
            True if retraining is recommended
        """
        # Check KS test results
        if 'features_with_ks_drift' in drift_results:
            n_ks_drift = len(drift_results['features_with_ks_drift'])
            if n_ks_drift > 0:
                logger.info(f"Retraining recommended: {n_ks_drift} features with KS drift")
                return True
        
        # Check PSI scores
        if 'features_with_high_psi' in drift_results:
            n_high_psi = len(drift_results['features_with_high_psi'])
            if n_high_psi > 0:
                logger.info(f"Retraining recommended: {n_high_psi} features with high PSI")
                return True
        
        return False
    
    def get_drift_summary(self, drift_results: Dict) -> pd.DataFrame:
        """
        Create a summary DataFrame of drift detection results
        
        Args:
            drift_results: Results from detect_drift()
            
        Returns:
            DataFrame with drift summary per feature
        """
        summary_data = []
        
        # Get all features
        features = set()
        if 'ks_test' in drift_results:
            features.update(drift_results['ks_test'].keys())
        if 'psi_scores' in drift_results:
            features.update(drift_results['psi_scores'].keys())
        
        for feature in sorted(features):
            row = {'feature': feature}
            
            # KS test results
            if 'ks_test' in drift_results and feature in drift_results['ks_test']:
                ks = drift_results['ks_test'][feature]
                row['ks_statistic'] = ks['ks_statistic']
                row['ks_p_value'] = ks['p_value']
                row['ks_drift'] = ks['drift_detected']
            
            # PSI scores
            if 'psi_scores' in drift_results and feature in drift_results['psi_scores']:
                row['psi_score'] = drift_results['psi_scores'][feature]
                row['psi_drift'] = row['psi_score'] >= self.psi_threshold
            
            # Overall drift
            row['drift_detected'] = row.get('ks_drift', False) or row.get('psi_drift', False)
            
            summary_data.append(row)
        
        df = pd.DataFrame(summary_data)
        
        # Sort by drift severity
        if 'psi_score' in df.columns:
            df = df.sort_values('psi_score', ascending=False)
        
        return df
