"""
Confidence Interval Calculator Module

Calculates confidence intervals for predictions and SHAP values.

Implements Requirement 7.5:
- Calculate prediction confidence intervals
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy import stats
import pandas as pd

logger = logging.getLogger(__name__)


class ConfidenceIntervalCalculator:
    """
    Calculates confidence intervals for predictions and explanations.
    
    Provides uncertainty quantification for model predictions
    and SHAP value estimates.
    """
    
    def __init__(
        self,
        confidence_level: float = 0.95
    ):
        """
        Initialize confidence interval calculator.
        
        Args:
            confidence_level: Confidence level (default 0.95 for 95% CI)
        """
        self.confidence_level = confidence_level
        self.z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        logger.info(
            f"Initialized ConfidenceIntervalCalculator "
            f"with {confidence_level*100}% confidence level"
        )
    
    def calculate_prediction_confidence_interval(
        self,
        predictions: np.ndarray,
        method: str = 'bootstrap',
        n_bootstrap: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate confidence intervals for predictions.
        
        Implements Requirement 7.5: Calculate prediction confidence intervals
        
        Args:
            predictions: Array of predictions from multiple models or bootstrap samples
            method: Method for CI calculation ('bootstrap', 'normal')
            n_bootstrap: Number of bootstrap samples (if using bootstrap)
            
        Returns:
            Tuple of (lower_bounds, upper_bounds)
        """
        logger.info(f"Calculating prediction confidence intervals using {method} method")
        
        if method == 'bootstrap':
            # Bootstrap confidence intervals
            lower_bounds, upper_bounds = self._bootstrap_ci(predictions, n_bootstrap)
        elif method == 'normal':
            # Normal approximation
            mean = np.mean(predictions, axis=0)
            std = np.std(predictions, axis=0)
            margin = self.z_score * std / np.sqrt(len(predictions))
            lower_bounds = mean - margin
            upper_bounds = mean + margin
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Clip to [0, 1] for probabilities
        lower_bounds = np.clip(lower_bounds, 0, 1)
        upper_bounds = np.clip(upper_bounds, 0, 1)
        
        logger.info(f"Confidence intervals calculated")
        
        return lower_bounds, upper_bounds
    
    def _bootstrap_ci(
        self,
        data: np.ndarray,
        n_bootstrap: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate bootstrap confidence intervals.
        
        Args:
            data: Data array
            n_bootstrap: Number of bootstrap samples
            
        Returns:
            Tuple of (lower_bounds, upper_bounds)
        """
        bootstrap_samples = []
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            indices = np.random.choice(len(data), size=len(data), replace=True)
            sample = data[indices]
            bootstrap_samples.append(np.mean(sample, axis=0))
        
        bootstrap_samples = np.array(bootstrap_samples)
        
        # Calculate percentiles
        alpha = 1 - self.confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bounds = np.percentile(bootstrap_samples, lower_percentile, axis=0)
        upper_bounds = np.percentile(bootstrap_samples, upper_percentile, axis=0)
        
        return lower_bounds, upper_bounds
    
    def calculate_ensemble_prediction_ci(
        self,
        model_predictions: Dict[str, np.ndarray],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate confidence intervals for ensemble predictions.
        
        Args:
            model_predictions: Dictionary mapping model names to predictions
            weights: Optional weights for each model
            
        Returns:
            Dictionary with ensemble prediction and confidence intervals
        """
        logger.info("Calculating ensemble prediction confidence intervals")
        
        # Stack predictions
        predictions_array = np.array(list(model_predictions.values()))
        
        # Calculate weighted average if weights provided
        if weights is not None:
            weight_array = np.array([weights[name] for name in model_predictions.keys()])
            weight_array = weight_array / np.sum(weight_array)  # Normalize
            ensemble_pred = np.average(predictions_array, axis=0, weights=weight_array)
        else:
            ensemble_pred = np.mean(predictions_array, axis=0)
        
        # Calculate standard error
        std_error = np.std(predictions_array, axis=0) / np.sqrt(len(predictions_array))
        
        # Calculate confidence intervals
        margin = self.z_score * std_error
        lower_bound = np.clip(ensemble_pred - margin, 0, 1)
        upper_bound = np.clip(ensemble_pred + margin, 0, 1)
        
        # Calculate prediction variance (disagreement between models)
        variance = np.var(predictions_array, axis=0)
        
        result = {
            'ensemble_prediction': ensemble_pred,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence_interval_width': upper_bound - lower_bound,
            'standard_error': std_error,
            'variance': variance,
            'confidence_level': self.confidence_level
        }
        
        logger.info(
            f"Ensemble prediction: {ensemble_pred:.3f} "
            f"[{lower_bound:.3f}, {upper_bound:.3f}]"
        )
        
        return result
    
    def calculate_shap_confidence_intervals(
        self,
        shap_values_list: List[np.ndarray],
        feature_names: List[str]
    ) -> pd.DataFrame:
        """
        Calculate confidence intervals for SHAP values.
        
        Useful when SHAP values are computed multiple times
        (e.g., with different random seeds or subsamples).
        
        Args:
            shap_values_list: List of SHAP value arrays
            feature_names: List of feature names
            
        Returns:
            DataFrame with SHAP value confidence intervals
        """
        logger.info("Calculating SHAP value confidence intervals")
        
        # Stack SHAP values
        shap_array = np.array(shap_values_list)  # (n_runs, n_samples, n_features)
        
        # Calculate mean and confidence intervals for each feature
        results = []
        
        for i, feature in enumerate(feature_names):
            feature_shap = shap_array[:, :, i]  # All runs, all samples, this feature
            
            # Flatten across runs and samples
            flat_shap = feature_shap.flatten()
            
            mean_shap = np.mean(flat_shap)
            std_shap = np.std(flat_shap)
            
            # Calculate CI
            margin = self.z_score * std_shap / np.sqrt(len(flat_shap))
            lower_bound = mean_shap - margin
            upper_bound = mean_shap + margin
            
            results.append({
                'feature': feature,
                'mean_shap': mean_shap,
                'std_shap': std_shap,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'ci_width': upper_bound - lower_bound
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('mean_shap', key=abs, ascending=False)
        
        logger.info(f"Calculated CI for {len(df)} features")
        
        return df
    
    def assess_prediction_uncertainty(
        self,
        prediction: float,
        lower_bound: float,
        upper_bound: float
    ) -> Dict[str, Any]:
        """
        Assess the uncertainty of a prediction.
        
        Args:
            prediction: Point prediction
            lower_bound: Lower confidence bound
            upper_bound: Upper confidence bound
            
        Returns:
            Dictionary with uncertainty assessment
        """
        ci_width = upper_bound - lower_bound
        
        # Categorize uncertainty
        if ci_width < 0.1:
            uncertainty_level = 'low'
        elif ci_width < 0.2:
            uncertainty_level = 'moderate'
        elif ci_width < 0.3:
            uncertainty_level = 'high'
        else:
            uncertainty_level = 'very_high'
        
        # Check if CI crosses decision boundary (0.5)
        crosses_boundary = (lower_bound < 0.5 < upper_bound)
        
        assessment = {
            'prediction': float(prediction),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'ci_width': float(ci_width),
            'uncertainty_level': uncertainty_level,
            'crosses_decision_boundary': crosses_boundary,
            'confidence_level': self.confidence_level
        }
        
        return assessment
    
    def calculate_calibrated_confidence(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        n_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate calibrated confidence scores.
        
        Adjusts confidence based on model calibration.
        
        Args:
            predictions: Model predictions (probabilities)
            true_labels: True labels
            n_bins: Number of bins for calibration
            
        Returns:
            Dictionary with calibration information
        """
        logger.info("Calculating calibrated confidence")
        
        # Create bins
        bin_edges = np.linspace(0, 1, n_bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Calculate accuracy in each bin
        bin_accuracies = []
        bin_confidences = []
        bin_counts = []
        
        for i in range(n_bins):
            lower = bin_edges[i]
            upper = bin_edges[i + 1]
            
            # Find predictions in this bin
            in_bin = (predictions >= lower) & (predictions < upper)
            
            if i == n_bins - 1:  # Include upper bound in last bin
                in_bin = (predictions >= lower) & (predictions <= upper)
            
            if np.sum(in_bin) > 0:
                bin_accuracy = np.mean(true_labels[in_bin])
                bin_confidence = np.mean(predictions[in_bin])
                bin_count = np.sum(in_bin)
                
                bin_accuracies.append(bin_accuracy)
                bin_confidences.append(bin_confidence)
                bin_counts.append(bin_count)
            else:
                bin_accuracies.append(np.nan)
                bin_confidences.append(np.nan)
                bin_counts.append(0)
        
        # Calculate Expected Calibration Error (ECE)
        ece = 0.0
        total_samples = len(predictions)
        
        for accuracy, confidence, count in zip(bin_accuracies, bin_confidences, bin_counts):
            if not np.isnan(accuracy):
                ece += (count / total_samples) * abs(accuracy - confidence)
        
        calibration_info = {
            'expected_calibration_error': ece,
            'bin_edges': bin_edges.tolist(),
            'bin_centers': bin_centers.tolist(),
            'bin_accuracies': [float(x) if not np.isnan(x) else None for x in bin_accuracies],
            'bin_confidences': [float(x) if not np.isnan(x) else None for x in bin_confidences],
            'bin_counts': [int(x) for x in bin_counts]
        }
        
        logger.info(f"Expected Calibration Error: {ece:.4f}")
        
        return calibration_info
    
    def generate_confidence_report(
        self,
        prediction: float,
        lower_bound: float,
        upper_bound: float,
        model_predictions: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Generate human-readable confidence report.
        
        Args:
            prediction: Point prediction
            lower_bound: Lower confidence bound
            upper_bound: Upper confidence bound
            model_predictions: Optional individual model predictions
            
        Returns:
            Formatted confidence report string
        """
        assessment = self.assess_prediction_uncertainty(
            prediction, lower_bound, upper_bound
        )
        
        report = "PREDICTION CONFIDENCE REPORT\n"
        report += "=" * 60 + "\n\n"
        
        report += f"Prediction: {prediction:.3f}\n"
        report += f"{self.confidence_level*100:.0f}% Confidence Interval: "
        report += f"[{lower_bound:.3f}, {upper_bound:.3f}]\n"
        report += f"Interval Width: {assessment['ci_width']:.3f}\n"
        report += f"Uncertainty Level: {assessment['uncertainty_level'].replace('_', ' ').title()}\n\n"
        
        if assessment['crosses_decision_boundary']:
            report += "⚠️  Note: Confidence interval crosses decision boundary (0.5)\n"
            report += "   Prediction uncertainty is high for classification.\n\n"
        
        if model_predictions:
            report += "Individual Model Predictions:\n"
            for model_name, pred in model_predictions.items():
                report += f"  {model_name}: {pred:.3f}\n"
            
            variance = np.var(list(model_predictions.values()))
            report += f"\nModel Agreement (Variance): {variance:.4f}\n"
        
        report += "\n" + "=" * 60 + "\n"
        
        return report
