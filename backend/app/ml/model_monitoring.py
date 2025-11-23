"""
Model monitoring system for tracking prediction accuracy and data drift.

This module provides functionality for:
- Tracking prediction accuracy over time
- Detecting data drift
- Monitoring model performance degradation
- Triggering retraining alerts
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats
import json
import logging

logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Monitors ML model performance and data distribution.
    """
    
    def __init__(self, monitoring_dir: str = "models/monitoring"):
        """
        Initialize model monitor.
        
        Args:
            monitoring_dir: Directory to store monitoring data
        """
        self.monitoring_dir = Path(monitoring_dir)
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.monitoring_dir / 'metrics.jsonl'
        self.drift_file = self.monitoring_dir / 'drift_reports.jsonl'
    
    def log_prediction(
        self,
        prediction_id: int,
        features: Dict[str, float],
        prediction: int,
        probability: float,
        confidence: float,
        model_version: str,
        actual_outcome: Optional[int] = None
    ) -> None:
        """
        Log a prediction for monitoring.
        
        Args:
            prediction_id: Prediction ID
            features: Input features
            prediction: Model prediction
            probability: Prediction probability
            confidence: Confidence score
            model_version: Model version used
            actual_outcome: Actual outcome if available
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'prediction_id': prediction_id,
            'model_version': model_version,
            'prediction': prediction,
            'probability': probability,
            'confidence': confidence,
            'actual_outcome': actual_outcome,
            'features': features
        }
        
        # Append to metrics file
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def update_actual_outcome(
        self,
        prediction_id: int,
        actual_outcome: int
    ) -> None:
        """
        Update a prediction with actual outcome.
        
        Args:
            prediction_id: Prediction ID
            actual_outcome: Actual outcome
        """
        # Read all entries
        entries = []
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                entries = [json.loads(line) for line in f]
        
        # Update matching entry
        updated = False
        for entry in entries:
            if entry['prediction_id'] == prediction_id:
                entry['actual_outcome'] = actual_outcome
                entry['outcome_updated_at'] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            # Rewrite file
            with open(self.metrics_file, 'w') as f:
                for entry in entries:
                    f.write(json.dumps(entry) + '\n')
            
            logger.info(f"Updated actual outcome for prediction {prediction_id}")
        else:
            logger.warning(f"Prediction {prediction_id} not found in monitoring logs")
    
    def calculate_accuracy_over_time(
        self,
        window_days: int = 30,
        model_version: Optional[str] = None
    ) -> Dict:
        """
        Calculate prediction accuracy over time.
        
        Args:
            window_days: Time window in days
            model_version: Optional model version filter
            
        Returns:
            Dictionary with accuracy metrics
        """
        if not self.metrics_file.exists():
            return {'error': 'No monitoring data available'}
        
        # Load predictions
        predictions = []
        with open(self.metrics_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                
                # Filter by model version if specified
                if model_version and entry.get('model_version') != model_version:
                    continue
                
                # Only include predictions with actual outcomes
                if entry.get('actual_outcome') is not None:
                    predictions.append(entry)
        
        if not predictions:
            return {'error': 'No predictions with actual outcomes'}
        
        # Convert to DataFrame
        df = pd.DataFrame(predictions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter by time window
        cutoff_date = datetime.now() - timedelta(days=window_days)
        df = df[df['timestamp'] >= cutoff_date]
        
        if len(df) == 0:
            return {'error': f'No predictions in last {window_days} days'}
        
        # Calculate metrics
        correct = (df['prediction'] == df['actual_outcome']).sum()
        total = len(df)
        accuracy = correct / total if total > 0 else 0
        
        # Calculate by time buckets
        df['date'] = df['timestamp'].dt.date
        daily_accuracy = df.groupby('date').apply(
            lambda x: (x['prediction'] == x['actual_outcome']).mean()
        ).to_dict()
        
        # Convert date keys to strings
        daily_accuracy = {str(k): v for k, v in daily_accuracy.items()}
        
        # Calculate confidence calibration
        df['confidence_bucket'] = pd.cut(
            df['confidence'],
            bins=[0, 0.5, 0.7, 0.9, 1.0],
            labels=['low', 'medium', 'high', 'very_high']
        )
        
        calibration = df.groupby('confidence_bucket').apply(
            lambda x: {
                'accuracy': (x['prediction'] == x['actual_outcome']).mean(),
                'count': len(x),
                'mean_confidence': x['confidence'].mean()
            }
        ).to_dict()
        
        return {
            'window_days': window_days,
            'total_predictions': total,
            'correct_predictions': int(correct),
            'overall_accuracy': float(accuracy),
            'daily_accuracy': daily_accuracy,
            'confidence_calibration': {
                str(k): v for k, v in calibration.items()
            },
            'model_version': model_version
        }
    
    def detect_data_drift(
        self,
        reference_features: pd.DataFrame,
        current_features: pd.DataFrame,
        threshold: float = 0.05
    ) -> Dict:
        """
        Detect data drift using statistical tests.
        
        Args:
            reference_features: Reference (training) feature distribution
            current_features: Current feature distribution
            threshold: P-value threshold for drift detection
            
        Returns:
            Dictionary with drift detection results
        """
        drift_results = {
            'timestamp': datetime.now().isoformat(),
            'features_analyzed': [],
            'drifted_features': [],
            'drift_scores': {},
            'overall_drift_detected': False
        }
        
        # Analyze each feature
        for feature in reference_features.columns:
            if feature not in current_features.columns:
                continue
            
            ref_values = reference_features[feature].dropna()
            curr_values = current_features[feature].dropna()
            
            if len(ref_values) == 0 or len(curr_values) == 0:
                continue
            
            # Perform Kolmogorov-Smirnov test
            statistic, p_value = stats.ks_2samp(ref_values, curr_values)
            
            drift_results['features_analyzed'].append(feature)
            drift_results['drift_scores'][feature] = {
                'ks_statistic': float(statistic),
                'p_value': float(p_value),
                'drifted': p_value < threshold
            }
            
            if p_value < threshold:
                drift_results['drifted_features'].append(feature)
        
        # Overall drift detection
        drift_results['overall_drift_detected'] = len(drift_results['drifted_features']) > 0
        drift_results['drift_percentage'] = (
            len(drift_results['drifted_features']) / 
            len(drift_results['features_analyzed'])
            if drift_results['features_analyzed'] else 0
        )
        
        # Log drift report
        with open(self.drift_file, 'a') as f:
            f.write(json.dumps(drift_results) + '\n')
        
        logger.info(
            f"Drift detection: {len(drift_results['drifted_features'])} / "
            f"{len(drift_results['features_analyzed'])} features drifted"
        )
        
        return drift_results
    
    def check_performance_degradation(
        self,
        baseline_accuracy: float,
        current_window_days: int = 30,
        degradation_threshold: float = 0.05
    ) -> Dict:
        """
        Check if model performance has degraded.
        
        Args:
            baseline_accuracy: Baseline accuracy from training
            current_window_days: Window for current accuracy calculation
            degradation_threshold: Threshold for degradation alert
            
        Returns:
            Dictionary with degradation check results
        """
        current_metrics = self.calculate_accuracy_over_time(
            window_days=current_window_days
        )
        
        if 'error' in current_metrics:
            return {
                'degradation_detected': False,
                'reason': current_metrics['error']
            }
        
        current_accuracy = current_metrics['overall_accuracy']
        accuracy_drop = baseline_accuracy - current_accuracy
        
        degradation_detected = accuracy_drop > degradation_threshold
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'baseline_accuracy': baseline_accuracy,
            'current_accuracy': current_accuracy,
            'accuracy_drop': accuracy_drop,
            'degradation_threshold': degradation_threshold,
            'degradation_detected': degradation_detected,
            'window_days': current_window_days,
            'total_predictions': current_metrics['total_predictions']
        }
        
        if degradation_detected:
            logger.warning(
                f"Performance degradation detected: "
                f"accuracy dropped from {baseline_accuracy:.3f} to {current_accuracy:.3f}"
            )
        
        return result
    
    def should_retrain(
        self,
        baseline_accuracy: float,
        min_predictions: int = 100,
        accuracy_threshold: float = 0.05,
        drift_threshold: float = 0.3
    ) -> Tuple[bool, str]:
        """
        Determine if model should be retrained.
        
        Args:
            baseline_accuracy: Baseline accuracy from training
            min_predictions: Minimum predictions needed for decision
            accuracy_threshold: Accuracy drop threshold
            drift_threshold: Percentage of features drifted threshold
            
        Returns:
            Tuple of (should_retrain, reason)
        """
        # Check if we have enough predictions
        metrics = self.calculate_accuracy_over_time(window_days=90)
        
        if 'error' in metrics:
            return False, "Insufficient data for retraining decision"
        
        if metrics['total_predictions'] < min_predictions:
            return False, f"Need at least {min_predictions} predictions with outcomes"
        
        # Check performance degradation
        degradation = self.check_performance_degradation(
            baseline_accuracy=baseline_accuracy,
            degradation_threshold=accuracy_threshold
        )
        
        if degradation['degradation_detected']:
            return True, (
                f"Performance degraded: accuracy dropped by "
                f"{degradation['accuracy_drop']:.3f}"
            )
        
        # Check data drift (would need reference data)
        # This is a placeholder - in production, you'd load reference data
        # and compare with recent predictions
        
        return False, "No retraining needed"
    
    def get_monitoring_summary(self) -> Dict:
        """
        Get summary of monitoring data.
        
        Returns:
            Dictionary with monitoring summary
        """
        summary = {
            'total_predictions': 0,
            'predictions_with_outcomes': 0,
            'recent_accuracy': None,
            'drift_reports': 0
        }
        
        # Count predictions
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    summary['total_predictions'] += 1
                    if entry.get('actual_outcome') is not None:
                        summary['predictions_with_outcomes'] += 1
        
        # Get recent accuracy
        recent_metrics = self.calculate_accuracy_over_time(window_days=30)
        if 'overall_accuracy' in recent_metrics:
            summary['recent_accuracy'] = recent_metrics['overall_accuracy']
        
        # Count drift reports
        if self.drift_file.exists():
            with open(self.drift_file, 'r') as f:
                summary['drift_reports'] = sum(1 for _ in f)
        
        return summary


def get_model_monitor(monitoring_dir: str = "models/monitoring") -> ModelMonitor:
    """
    Get the global model monitor instance.
    
    Args:
        monitoring_dir: Directory for monitoring data
        
    Returns:
        ModelMonitor instance
    """
    return ModelMonitor(monitoring_dir)
