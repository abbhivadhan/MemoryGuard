"""
Forecast Evaluator

Validates forecast accuracy and ensures MAE is below 3 points on MMSE scale.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import matplotlib.pyplot as plt
from pathlib import Path

logger = logging.getLogger(__name__)


class ForecastEvaluator:
    """
    Evaluates progression forecast accuracy.
    
    Validates that forecasts meet accuracy requirements:
    - MAE below 3 points on MMSE scale
    - Consistent performance across horizons
    - Calibrated uncertainty estimates
    """
    
    def __init__(
        self,
        mae_threshold: float = 3.0,
        forecast_horizons: List[int] = [6, 12, 24]
    ):
        """
        Initialize the evaluator.
        
        Args:
            mae_threshold: Maximum acceptable MAE (default: 3.0 for MMSE)
            forecast_horizons: List of forecast horizons in months
        """
        self.mae_threshold = mae_threshold
        self.forecast_horizons = forecast_horizons
        
        logger.info(f"Initialized ForecastEvaluator with MAE threshold={mae_threshold}")
    
    def evaluate_accuracy(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        detailed: bool = True
    ) -> Dict[str, float]:
        """
        Evaluate forecast accuracy with comprehensive metrics.
        
        Args:
            y_true: True MMSE scores (n_samples, n_horizons)
            y_pred: Predicted MMSE scores (n_samples, n_horizons)
            detailed: Whether to include detailed per-horizon metrics
            
        Returns:
            Dictionary with accuracy metrics
        """
        logger.info(f"Evaluating forecast accuracy on {len(y_true)} samples")
        
        metrics = {}
        
        # Calculate metrics for each horizon
        for i, horizon in enumerate(self.forecast_horizons):
            y_true_h = y_true[:, i]
            y_pred_h = y_pred[:, i]
            
            # Mean Absolute Error
            mae = np.mean(np.abs(y_true_h - y_pred_h))
            
            # Mean Squared Error
            mse = np.mean((y_true_h - y_pred_h) ** 2)
            
            # Root Mean Squared Error
            rmse = np.sqrt(mse)
            
            # Mean Absolute Percentage Error
            # Avoid division by zero
            mask = y_true_h != 0
            if np.any(mask):
                mape = np.mean(np.abs((y_true_h[mask] - y_pred_h[mask]) / y_true_h[mask])) * 100
            else:
                mape = np.nan
            
            # R-squared
            ss_res = np.sum((y_true_h - y_pred_h) ** 2)
            ss_tot = np.sum((y_true_h - np.mean(y_true_h)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Median Absolute Error
            median_ae = np.median(np.abs(y_true_h - y_pred_h))
            
            # 90th percentile error
            p90_error = np.percentile(np.abs(y_true_h - y_pred_h), 90)
            
            if detailed:
                metrics[f'{horizon}_month_mae'] = float(mae)
                metrics[f'{horizon}_month_mse'] = float(mse)
                metrics[f'{horizon}_month_rmse'] = float(rmse)
                metrics[f'{horizon}_month_mape'] = float(mape) if not np.isnan(mape) else None
                metrics[f'{horizon}_month_r2'] = float(r2)
                metrics[f'{horizon}_month_median_ae'] = float(median_ae)
                metrics[f'{horizon}_month_p90_error'] = float(p90_error)
            
            # Check if meets threshold
            meets_threshold = mae < self.mae_threshold
            metrics[f'{horizon}_month_meets_threshold'] = meets_threshold
            
            logger.info(
                f"{horizon}-month forecast: MAE={mae:.3f}, "
                f"RMSE={rmse:.3f}, R²={r2:.3f}, "
                f"Meets threshold: {meets_threshold}"
            )
        
        # Overall metrics
        overall_mae = np.mean([metrics[f'{h}_month_mae'] for h in self.forecast_horizons])
        overall_rmse = np.mean([metrics[f'{h}_month_rmse'] for h in self.forecast_horizons])
        overall_r2 = np.mean([metrics[f'{h}_month_r2'] for h in self.forecast_horizons])
        
        metrics['overall_mae'] = float(overall_mae)
        metrics['overall_rmse'] = float(overall_rmse)
        metrics['overall_r2'] = float(overall_r2)
        metrics['overall_meets_threshold'] = overall_mae < self.mae_threshold
        
        # Check if all horizons meet threshold
        all_meet_threshold = all(
            metrics[f'{h}_month_meets_threshold'] for h in self.forecast_horizons
        )
        metrics['all_horizons_meet_threshold'] = all_meet_threshold
        
        logger.info(
            f"Overall: MAE={overall_mae:.3f}, RMSE={overall_rmse:.3f}, R²={overall_r2:.3f}"
        )
        logger.info(f"Meets accuracy requirement (MAE < {self.mae_threshold}): {all_meet_threshold}")
        
        return metrics
    
    def validate_requirements(
        self,
        metrics: Dict[str, float]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that forecast meets all requirements.
        
        Args:
            metrics: Dictionary with evaluation metrics
            
        Returns:
            Tuple of (passes_validation, list_of_issues)
        """
        issues = []
        
        # Check overall MAE
        if metrics['overall_mae'] >= self.mae_threshold:
            issues.append(
                f"Overall MAE ({metrics['overall_mae']:.3f}) exceeds threshold ({self.mae_threshold})"
            )
        
        # Check each horizon
        for horizon in self.forecast_horizons:
            mae = metrics.get(f'{horizon}_month_mae')
            if mae and mae >= self.mae_threshold:
                issues.append(
                    f"{horizon}-month MAE ({mae:.3f}) exceeds threshold ({self.mae_threshold})"
                )
        
        # Check R-squared (should be positive)
        if metrics['overall_r2'] < 0:
            issues.append(
                f"Overall R² ({metrics['overall_r2']:.3f}) is negative (worse than mean baseline)"
            )
        
        passes = len(issues) == 0
        
        if passes:
            logger.info("✓ All validation requirements met")
        else:
            logger.warning(f"✗ Validation failed with {len(issues)} issues:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        
        return passes, issues
    
    def analyze_errors_by_baseline(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        baseline_scores: np.ndarray
    ) -> Dict:
        """
        Analyze forecast errors stratified by baseline MMSE score.
        
        Args:
            y_true: True values
            y_pred: Predictions
            baseline_scores: Baseline MMSE scores for each sample
            
        Returns:
            Dictionary with stratified error analysis
        """
        # Define MMSE ranges
        ranges = [
            (24, 30, 'Normal (24-30)'),
            (18, 23, 'Mild (18-23)'),
            (10, 17, 'Moderate (10-17)'),
            (0, 9, 'Severe (0-9)')
        ]
        
        results = {}
        
        for low, high, label in ranges:
            mask = (baseline_scores >= low) & (baseline_scores <= high)
            
            if not np.any(mask):
                continue
            
            y_true_range = y_true[mask]
            y_pred_range = y_pred[mask]
            
            mae_by_horizon = []
            for i in range(y_true.shape[1]):
                mae = np.mean(np.abs(y_true_range[:, i] - y_pred_range[:, i]))
                mae_by_horizon.append(mae)
            
            results[label] = {
                'n_samples': int(np.sum(mask)),
                'mae_by_horizon': [float(m) for m in mae_by_horizon],
                'overall_mae': float(np.mean(mae_by_horizon))
            }
        
        logger.info("Error analysis by baseline MMSE:")
        for label, data in results.items():
            logger.info(f"  {label}: MAE={data['overall_mae']:.3f} (n={data['n_samples']})")
        
        return results
    
    def plot_predictions_vs_actual(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        output_path: Optional[Path] = None
    ):
        """
        Create scatter plots of predictions vs actual values.
        
        Args:
            y_true: True values
            y_pred: Predictions
            output_path: Path to save plot
        """
        n_horizons = len(self.forecast_horizons)
        
        fig, axes = plt.subplots(1, n_horizons, figsize=(5 * n_horizons, 5))
        
        if n_horizons == 1:
            axes = [axes]
        
        for i, (ax, horizon) in enumerate(zip(axes, self.forecast_horizons)):
            y_true_h = y_true[:, i]
            y_pred_h = y_pred[:, i]
            
            # Scatter plot
            ax.scatter(y_true_h, y_pred_h, alpha=0.5, s=20)
            
            # Perfect prediction line
            min_val = min(y_true_h.min(), y_pred_h.min())
            max_val = max(y_true_h.max(), y_pred_h.max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect prediction')
            
            # MAE threshold lines
            ax.plot([min_val, max_val], [min_val + self.mae_threshold, max_val + self.mae_threshold],
                   'g--', alpha=0.5, label=f'±{self.mae_threshold} MAE')
            ax.plot([min_val, max_val], [min_val - self.mae_threshold, max_val - self.mae_threshold],
                   'g--', alpha=0.5)
            
            ax.set_xlabel('Actual MMSE Score')
            ax.set_ylabel('Predicted MMSE Score')
            ax.set_title(f'{horizon}-Month Forecast')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {output_path}")
        
        plt.close()
    
    def plot_error_distribution(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        output_path: Optional[Path] = None
    ):
        """
        Plot distribution of prediction errors.
        
        Args:
            y_true: True values
            y_pred: Predictions
            output_path: Path to save plot
        """
        n_horizons = len(self.forecast_horizons)
        
        fig, axes = plt.subplots(1, n_horizons, figsize=(5 * n_horizons, 4))
        
        if n_horizons == 1:
            axes = [axes]
        
        for i, (ax, horizon) in enumerate(zip(axes, self.forecast_horizons)):
            errors = y_true[:, i] - y_pred[:, i]
            
            # Histogram
            ax.hist(errors, bins=30, alpha=0.7, edgecolor='black')
            
            # Add vertical lines for mean and threshold
            ax.axvline(0, color='r', linestyle='--', linewidth=2, label='Zero error')
            ax.axvline(errors.mean(), color='g', linestyle='--', linewidth=2, label=f'Mean: {errors.mean():.2f}')
            ax.axvline(-self.mae_threshold, color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
            ax.axvline(self.mae_threshold, color='orange', linestyle=':', linewidth=1.5, alpha=0.7,
                      label=f'±{self.mae_threshold} threshold')
            
            ax.set_xlabel('Prediction Error (True - Predicted)')
            ax.set_ylabel('Frequency')
            ax.set_title(f'{horizon}-Month Forecast Errors')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {output_path}")
        
        plt.close()
    
    def generate_evaluation_report(
        self,
        metrics: Dict[str, float],
        output_path: Path
    ):
        """
        Generate a comprehensive evaluation report.
        
        Args:
            metrics: Dictionary with evaluation metrics
            output_path: Path to save report
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("# Progression Forecasting Evaluation Report\n\n")
            
            # Overall metrics
            f.write("## Overall Performance\n\n")
            f.write(f"- **Overall MAE**: {metrics['overall_mae']:.3f}\n")
            f.write(f"- **Overall RMSE**: {metrics['overall_rmse']:.3f}\n")
            f.write(f"- **Overall R²**: {metrics['overall_r2']:.3f}\n")
            f.write(f"- **Meets Threshold (MAE < {self.mae_threshold})**: ")
            f.write("✓ Yes\n\n" if metrics['overall_meets_threshold'] else "✗ No\n\n")
            
            # Per-horizon metrics
            f.write("## Performance by Forecast Horizon\n\n")
            f.write("| Horizon | MAE | RMSE | R² | Median AE | 90th %ile | Meets Threshold |\n")
            f.write("|---------|-----|------|----|-----------|-----------|-----------------|\n")
            
            for horizon in self.forecast_horizons:
                mae = metrics[f'{horizon}_month_mae']
                rmse = metrics[f'{horizon}_month_rmse']
                r2 = metrics[f'{horizon}_month_r2']
                median_ae = metrics[f'{horizon}_month_median_ae']
                p90 = metrics[f'{horizon}_month_p90_error']
                meets = "✓" if metrics[f'{horizon}_month_meets_threshold'] else "✗"
                
                f.write(f"| {horizon} months | {mae:.3f} | {rmse:.3f} | {r2:.3f} | ")
                f.write(f"{median_ae:.3f} | {p90:.3f} | {meets} |\n")
            
            f.write("\n")
            
            # Validation status
            passes, issues = self.validate_requirements(metrics)
            
            f.write("## Validation Status\n\n")
            if passes:
                f.write("✓ **All requirements met**\n\n")
            else:
                f.write("✗ **Validation failed**\n\n")
                f.write("Issues:\n")
                for issue in issues:
                    f.write(f"- {issue}\n")
                f.write("\n")
        
        logger.info(f"Evaluation report saved to {output_path}")
