"""
Uncertainty Quantifier

Provides uncertainty quantification for progression forecasts using
Monte Carlo Dropout and prediction intervals.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from scipy import stats

logger = logging.getLogger(__name__)


class UncertaintyQuantifier:
    """
    Quantifies uncertainty in progression forecasts.
    
    Methods:
    - Monte Carlo Dropout for epistemic uncertainty
    - Prediction intervals based on historical errors
    - Confidence intervals for forecasts
    """
    
    def __init__(
        self,
        n_mc_samples: int = 100,
        confidence_level: float = 0.95
    ):
        """
        Initialize the uncertainty quantifier.
        
        Args:
            n_mc_samples: Number of Monte Carlo samples for dropout
            confidence_level: Confidence level for intervals (e.g., 0.95 for 95%)
        """
        self.n_mc_samples = n_mc_samples
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
        
        # Store historical errors for calibration
        self.historical_errors = {}
        
        logger.info(
            f"Initialized UncertaintyQuantifier with n_mc_samples={n_mc_samples}, "
            f"confidence_level={confidence_level}"
        )
    
    def monte_carlo_dropout_prediction(
        self,
        model,
        X: np.ndarray,
        n_samples: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate predictions using Monte Carlo Dropout.
        
        Performs multiple forward passes with dropout enabled to estimate
        epistemic uncertainty.
        
        Args:
            model: Keras model with dropout layers
            X: Input sequences (n_samples, sequence_length, n_features)
            n_samples: Number of MC samples (uses self.n_mc_samples if None)
            
        Returns:
            Tuple of (mean_predictions, std_predictions)
        """
        n_samples = n_samples or self.n_mc_samples
        
        logger.info(f"Generating {n_samples} MC dropout predictions for {len(X)} samples")
        
        # Store predictions from multiple forward passes
        predictions = []
        
        # Enable dropout during inference
        for _ in range(n_samples):
            # Forward pass with dropout enabled (training=True)
            pred = model(X, training=True).numpy()
            predictions.append(pred)
        
        # Stack predictions
        predictions = np.array(predictions)  # Shape: (n_mc_samples, n_samples, n_horizons)
        
        # Calculate mean and std across MC samples
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        logger.info(f"MC dropout complete. Mean std: {np.mean(std_pred):.3f}")
        
        return mean_pred, std_pred
    
    def calculate_prediction_intervals(
        self,
        predictions: np.ndarray,
        std_predictions: np.ndarray,
        method: str = 'gaussian'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate prediction intervals for forecasts.
        
        Args:
            predictions: Point predictions (n_samples, n_horizons)
            std_predictions: Standard deviations (n_samples, n_horizons)
            method: Method for interval calculation ('gaussian' or 'quantile')
            
        Returns:
            Tuple of (lower_bounds, upper_bounds)
        """
        if method == 'gaussian':
            # Use Gaussian approximation
            z_score = stats.norm.ppf(1 - self.alpha / 2)
            
            lower_bounds = predictions - z_score * std_predictions
            upper_bounds = predictions + z_score * std_predictions
        
        elif method == 'quantile':
            # Use quantile-based intervals (requires historical data)
            if not self.historical_errors:
                logger.warning("No historical errors available. Using Gaussian method.")
                return self.calculate_prediction_intervals(
                    predictions, std_predictions, method='gaussian'
                )
            
            # Calculate intervals based on historical error distribution
            lower_bounds = np.zeros_like(predictions)
            upper_bounds = np.zeros_like(predictions)
            
            for horizon_idx in range(predictions.shape[1]):
                if horizon_idx in self.historical_errors:
                    errors = self.historical_errors[horizon_idx]
                    lower_q = np.percentile(errors, self.alpha / 2 * 100)
                    upper_q = np.percentile(errors, (1 - self.alpha / 2) * 100)
                    
                    lower_bounds[:, horizon_idx] = predictions[:, horizon_idx] + lower_q
                    upper_bounds[:, horizon_idx] = predictions[:, horizon_idx] + upper_q
                else:
                    # Fall back to Gaussian
                    z_score = stats.norm.ppf(1 - self.alpha / 2)
                    lower_bounds[:, horizon_idx] = predictions[:, horizon_idx] - z_score * std_predictions[:, horizon_idx]
                    upper_bounds[:, horizon_idx] = predictions[:, horizon_idx] + z_score * std_predictions[:, horizon_idx]
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return lower_bounds, upper_bounds
    
    def calibrate_intervals(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        forecast_horizons: List[int]
    ):
        """
        Calibrate prediction intervals using historical errors.
        
        Args:
            y_true: True values (n_samples, n_horizons)
            y_pred: Predicted values (n_samples, n_horizons)
            forecast_horizons: List of forecast horizons
        """
        logger.info("Calibrating prediction intervals with historical data")
        
        for i, horizon in enumerate(forecast_horizons):
            errors = y_true[:, i] - y_pred[:, i]
            self.historical_errors[i] = errors
        
        logger.info(f"Calibration complete for {len(forecast_horizons)} horizons")
    
    def predict_with_uncertainty(
        self,
        model,
        X: np.ndarray,
        forecast_horizons: List[int],
        return_intervals: bool = True
    ) -> Dict:
        """
        Generate predictions with uncertainty quantification.
        
        Args:
            model: Trained Keras model
            X: Input sequences
            forecast_horizons: List of forecast horizons (e.g., [6, 12, 24])
            return_intervals: Whether to return prediction intervals
            
        Returns:
            Dictionary with predictions, uncertainties, and intervals
        """
        # Generate MC dropout predictions
        mean_pred, std_pred = self.monte_carlo_dropout_prediction(model, X)
        
        result = {
            'predictions': mean_pred,
            'std': std_pred
        }
        
        # Calculate prediction intervals
        if return_intervals:
            lower_bounds, upper_bounds = self.calculate_prediction_intervals(
                mean_pred,
                std_pred,
                method='quantile' if self.historical_errors else 'gaussian'
            )
            
            result['lower_bounds'] = lower_bounds
            result['upper_bounds'] = upper_bounds
        
        # Format by horizon
        result_by_horizon = {}
        for i, horizon in enumerate(forecast_horizons):
            result_by_horizon[f'{horizon}_month'] = {
                'prediction': mean_pred[:, i],
                'std': std_pred[:, i]
            }
            
            if return_intervals:
                result_by_horizon[f'{horizon}_month']['lower_bound'] = lower_bounds[:, i]
                result_by_horizon[f'{horizon}_month']['upper_bound'] = upper_bounds[:, i]
        
        result['by_horizon'] = result_by_horizon
        
        return result
    
    def predict_single_with_uncertainty(
        self,
        model,
        X: np.ndarray,
        forecast_horizons: List[int]
    ) -> Dict[str, Dict[str, float]]:
        """
        Generate prediction with uncertainty for a single patient.
        
        Args:
            model: Trained Keras model
            X: Single input sequence (1, sequence_length, n_features)
            forecast_horizons: List of forecast horizons
            
        Returns:
            Dictionary with predictions and uncertainty for each horizon
        """
        result = self.predict_with_uncertainty(
            model,
            X,
            forecast_horizons,
            return_intervals=True
        )
        
        # Extract single patient results
        single_result = {}
        for horizon in forecast_horizons:
            horizon_key = f'{horizon}_month'
            single_result[horizon_key] = {
                'prediction': float(result['by_horizon'][horizon_key]['prediction'][0]),
                'std': float(result['by_horizon'][horizon_key]['std'][0]),
                'lower_bound': float(result['by_horizon'][horizon_key]['lower_bound'][0]),
                'upper_bound': float(result['by_horizon'][horizon_key]['upper_bound'][0]),
                'confidence_level': self.confidence_level
            }
        
        return single_result
    
    def calculate_coverage(
        self,
        y_true: np.ndarray,
        lower_bounds: np.ndarray,
        upper_bounds: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate empirical coverage of prediction intervals.
        
        Args:
            y_true: True values
            lower_bounds: Lower bounds of intervals
            upper_bounds: Upper bounds of intervals
            
        Returns:
            Dictionary with coverage statistics
        """
        # Check if true values fall within intervals
        within_interval = (y_true >= lower_bounds) & (y_true <= upper_bounds)
        
        # Calculate coverage for each horizon
        coverage = {}
        n_horizons = y_true.shape[1]
        
        for i in range(n_horizons):
            coverage[f'horizon_{i}'] = float(np.mean(within_interval[:, i]))
        
        # Overall coverage
        coverage['overall'] = float(np.mean(within_interval))
        
        logger.info(f"Empirical coverage: {coverage['overall']:.3f} (target: {self.confidence_level})")
        
        return coverage
    
    def evaluate_uncertainty_quality(
        self,
        y_true: np.ndarray,
        predictions: np.ndarray,
        std_predictions: np.ndarray,
        lower_bounds: np.ndarray,
        upper_bounds: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate the quality of uncertainty estimates.
        
        Args:
            y_true: True values
            predictions: Point predictions
            std_predictions: Standard deviations
            lower_bounds: Lower bounds of intervals
            upper_bounds: Upper bounds of intervals
            
        Returns:
            Dictionary with uncertainty quality metrics
        """
        metrics = {}
        
        # Coverage
        coverage = self.calculate_coverage(y_true, lower_bounds, upper_bounds)
        metrics['coverage'] = coverage['overall']
        
        # Interval width
        interval_widths = upper_bounds - lower_bounds
        metrics['mean_interval_width'] = float(np.mean(interval_widths))
        metrics['median_interval_width'] = float(np.median(interval_widths))
        
        # Calibration: correlation between std and absolute error
        abs_errors = np.abs(y_true - predictions)
        
        # Flatten for correlation
        std_flat = std_predictions.flatten()
        errors_flat = abs_errors.flatten()
        
        if len(std_flat) > 1:
            correlation = np.corrcoef(std_flat, errors_flat)[0, 1]
            metrics['std_error_correlation'] = float(correlation)
        
        # Sharpness: average std (lower is better, but must maintain coverage)
        metrics['mean_std'] = float(np.mean(std_predictions))
        
        logger.info(f"Uncertainty quality metrics: {metrics}")
        
        return metrics
    
    def get_confidence_description(self, std: float) -> str:
        """
        Get human-readable confidence description.
        
        Args:
            std: Standard deviation of prediction
            
        Returns:
            String describing confidence level
        """
        # Thresholds based on MMSE scale (0-30)
        if std < 1.0:
            return "Very High Confidence"
        elif std < 2.0:
            return "High Confidence"
        elif std < 3.0:
            return "Moderate Confidence"
        elif std < 4.0:
            return "Low Confidence"
        else:
            return "Very Low Confidence"
