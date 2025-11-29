"""
Model performance tracking on recent data
Monitors prediction accuracy and model degradation over time
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    balanced_accuracy_score
)

from ml_pipeline.config.settings import settings

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Track model performance on recent data
    Monitors for performance degradation that may indicate drift
    """
    
    def __init__(
        self,
        model_name: str,
        storage_path: Optional[Path] = None
    ):
        """
        Initialize performance tracker
        
        Args:
            model_name: Name of the model to track
            storage_path: Path to store performance history
        """
        self.model_name = model_name
        
        if storage_path is None:
            storage_path = settings.METADATA_PATH / "performance"
        self.storage_path = storage_path / model_name
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.performance_history = []
        self.baseline_metrics = None
        
        logger.info(f"Initialized PerformanceTracker for model: {model_name}")
    
    def set_baseline_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Set baseline performance metrics
        
        Args:
            metrics: Dictionary of baseline metrics
        """
        self.baseline_metrics = metrics
        
        # Save baseline
        filepath = self.storage_path / "baseline_metrics.json"
        with open(filepath, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics
            }, f, indent=2)
        
        logger.info(f"Baseline metrics set: {metrics}")
    
    def load_baseline_metrics(self) -> Optional[Dict[str, float]]:
        """
        Load baseline metrics from storage
        
        Returns:
            Baseline metrics dictionary or None
        """
        filepath = self.storage_path / "baseline_metrics.json"
        
        if not filepath.exists():
            logger.warning("No baseline metrics found")
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.baseline_metrics = data['metrics']
        
        logger.info(f"Loaded baseline metrics: {self.baseline_metrics}")
        return self.baseline_metrics
    
    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Calculate performance metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional)
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_true, y_pred, average='weighted', zero_division=0),
            'n_samples': len(y_true)
        }
        
        # Add AUC if probabilities provided
        if y_proba is not None:
            try:
                # Handle binary and multiclass
                if len(np.unique(y_true)) == 2:
                    metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
                else:
                    metrics['roc_auc'] = roc_auc_score(
                        y_true, y_proba, multi_class='ovr', average='weighted'
                    )
            except Exception as e:
                logger.warning(f"Could not calculate ROC AUC: {e}")
        
        return metrics
    
    def track_performance(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        dataset_name: str = "recent_data",
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Track performance on a dataset
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional)
            dataset_name: Name of the dataset
            timestamp: Timestamp for tracking (defaults to now)
            
        Returns:
            Performance tracking entry
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Calculate metrics
        metrics = self.calculate_metrics(y_true, y_pred, y_proba)
        
        # Create tracking entry
        entry = {
            'timestamp': timestamp.isoformat(),
            'dataset_name': dataset_name,
            'model_name': self.model_name,
            'metrics': metrics
        }
        
        # Compare with baseline if available
        if self.baseline_metrics:
            entry['baseline_comparison'] = self._compare_with_baseline(metrics)
        
        # Add to history
        self.performance_history.append(entry)
        
        # Save to disk
        self._save_performance_entry(entry)
        
        logger.info(
            f"Tracked performance for {dataset_name}: "
            f"accuracy={metrics['accuracy']:.4f}, "
            f"f1={metrics['f1_score']:.4f}"
        )
        
        return entry
    
    def _compare_with_baseline(self, current_metrics: Dict[str, float]) -> Dict:
        """
        Compare current metrics with baseline
        
        Args:
            current_metrics: Current performance metrics
            
        Returns:
            Comparison results
        """
        comparison = {}
        
        for metric_name, baseline_value in self.baseline_metrics.items():
            if metric_name in current_metrics:
                current_value = current_metrics[metric_name]
                
                # Calculate absolute and relative change
                absolute_change = current_value - baseline_value
                relative_change = (absolute_change / baseline_value) if baseline_value != 0 else 0
                
                comparison[metric_name] = {
                    'baseline': baseline_value,
                    'current': current_value,
                    'absolute_change': absolute_change,
                    'relative_change': relative_change,
                    'degraded': absolute_change < -0.05  # 5% degradation threshold
                }
        
        return comparison
    
    def _save_performance_entry(self, entry: Dict) -> None:
        """
        Save performance entry to storage
        
        Args:
            entry: Performance tracking entry
        """
        timestamp_str = entry['timestamp'].replace(':', '-').replace('.', '-')
        filepath = self.storage_path / f"performance_{timestamp_str}.json"
        
        with open(filepath, 'w') as f:
            json.dump(entry, f, indent=2)
    
    def load_performance_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: Optional[int] = None
    ) -> List[Dict]:
        """
        Load performance history from storage
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            days: Load last N days (alternative to date range)
            
        Returns:
            List of performance entries
        """
        if days is not None:
            start_date = datetime.now() - timedelta(days=days)
        
        history = []
        
        for filepath in sorted(self.storage_path.glob("performance_*.json")):
            with open(filepath, 'r') as f:
                entry = json.load(f)
            
            entry_time = datetime.fromisoformat(entry['timestamp'])
            
            # Filter by date range
            if start_date and entry_time < start_date:
                continue
            if end_date and entry_time > end_date:
                continue
            
            history.append(entry)
        
        self.performance_history = history
        logger.info(f"Loaded {len(history)} performance entries")
        
        return history
    
    def get_performance_summary(self) -> pd.DataFrame:
        """
        Get summary of performance history
        
        Returns:
            DataFrame with performance metrics over time
        """
        if not self.performance_history:
            logger.warning("No performance history available")
            return pd.DataFrame()
        
        summary_data = []
        
        for entry in self.performance_history:
            row = {
                'timestamp': entry['timestamp'],
                'dataset_name': entry['dataset_name'],
                **entry['metrics']
            }
            
            # Add baseline comparison if available
            if 'baseline_comparison' in entry:
                for metric, comp in entry['baseline_comparison'].items():
                    row[f'{metric}_change'] = comp['relative_change']
                    row[f'{metric}_degraded'] = comp['degraded']
            
            summary_data.append(row)
        
        df = pd.DataFrame(summary_data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        return df
    
    def detect_performance_degradation(
        self,
        threshold: float = 0.05,
        metric: str = 'accuracy'
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Detect if performance has degraded significantly
        
        Args:
            threshold: Degradation threshold (default: 5%)
            metric: Metric to check (default: 'accuracy')
            
        Returns:
            Tuple of (degraded, details)
        """
        if not self.baseline_metrics:
            logger.warning("No baseline metrics available")
            return False, None
        
        if not self.performance_history:
            logger.warning("No performance history available")
            return False, None
        
        # Get recent performance
        recent_entries = self.performance_history[-5:]  # Last 5 entries
        
        if not recent_entries:
            return False, None
        
        # Calculate average recent performance
        recent_values = [
            entry['metrics'].get(metric, 0)
            for entry in recent_entries
        ]
        avg_recent = np.mean(recent_values)
        
        # Compare with baseline
        baseline_value = self.baseline_metrics.get(metric, 0)
        
        if baseline_value == 0:
            return False, None
        
        relative_change = (avg_recent - baseline_value) / baseline_value
        degraded = relative_change < -threshold
        
        details = {
            'metric': metric,
            'baseline_value': baseline_value,
            'recent_average': avg_recent,
            'relative_change': relative_change,
            'threshold': threshold,
            'degraded': degraded,
            'n_recent_samples': len(recent_entries)
        }
        
        if degraded:
            logger.warning(
                f"Performance degradation detected: {metric} dropped by "
                f"{abs(relative_change)*100:.2f}% (threshold: {threshold*100}%)"
            )
        
        return degraded, details
    
    def get_metric_trend(
        self,
        metric: str = 'accuracy',
        window_size: int = 5
    ) -> pd.DataFrame:
        """
        Get trend analysis for a specific metric
        
        Args:
            metric: Metric to analyze
            window_size: Window size for moving average
            
        Returns:
            DataFrame with metric trend
        """
        df = self.get_performance_summary()
        
        if df.empty or metric not in df.columns:
            return pd.DataFrame()
        
        # Calculate moving average
        df[f'{metric}_ma'] = df[metric].rolling(window=window_size, min_periods=1).mean()
        
        # Calculate trend (simple linear regression slope)
        if len(df) > 1:
            x = np.arange(len(df))
            y = df[metric].values
            slope = np.polyfit(x, y, 1)[0]
            df['trend_slope'] = slope
        
        return df[['timestamp', metric, f'{metric}_ma', 'trend_slope']]
    
    def generate_performance_report(self) -> Dict:
        """
        Generate comprehensive performance report
        
        Returns:
            Performance report dictionary
        """
        report = {
            'model_name': self.model_name,
            'generated_at': datetime.now().isoformat(),
            'baseline_metrics': self.baseline_metrics,
            'n_tracking_entries': len(self.performance_history)
        }
        
        if self.performance_history:
            # Recent performance
            recent_entry = self.performance_history[-1]
            report['most_recent'] = {
                'timestamp': recent_entry['timestamp'],
                'metrics': recent_entry['metrics']
            }
            
            # Performance degradation check
            degraded, details = self.detect_performance_degradation()
            report['degradation_detected'] = degraded
            report['degradation_details'] = details
            
            # Summary statistics
            df = self.get_performance_summary()
            if not df.empty:
                report['summary_statistics'] = {
                    'accuracy': {
                        'mean': float(df['accuracy'].mean()),
                        'std': float(df['accuracy'].std()),
                        'min': float(df['accuracy'].min()),
                        'max': float(df['accuracy'].max())
                    }
                }
        
        return report
