"""
Retraining Triggers

This module implements various triggers for automated model retraining:
- Data drift detection
- Data volume thresholds
- Performance degradation
- Manual triggers
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import get_logger
from ml_pipeline.monitoring.drift_detector import DriftDetector
from ml_pipeline.data_storage.database import get_db_session
from ml_pipeline.data_storage.models import ProcessedFeature, ModelVersion

logger = get_logger(__name__)


class RetrainingTriggers:
    """
    Manage triggers for automated model retraining
    
    Implements:
    - Drift-based triggers (Requirement 11.2)
    - Data volume triggers (Requirement 11.3)
    - Performance monitoring triggers
    """
    
    def __init__(
        self,
        drift_threshold: float = None,
        volume_threshold: int = None
    ):
        """
        Initialize retraining triggers
        
        Args:
            drift_threshold: PSI threshold for drift detection (default from settings)
            volume_threshold: Minimum new records to trigger retraining (default from settings)
        """
        self.drift_threshold = drift_threshold or settings.PSI_THRESHOLD
        self.volume_threshold = volume_threshold or 1000  # Requirement 11.3
        
        logger.info(
            f"Initialized RetrainingTriggers: "
            f"drift_threshold={self.drift_threshold}, "
            f"volume_threshold={self.volume_threshold}"
        )
    
    def check_drift(
        self,
        reference_days: int = 90,
        current_days: int = 7
    ) -> Tuple[bool, Dict]:
        """
        Check for data drift that would trigger retraining
        
        Implements Requirement 11.2: Trigger retraining when data drift is detected
        
        Args:
            reference_days: Number of days to use for reference data
            current_days: Number of days to use for current data
            
        Returns:
            Tuple of (drift_detected: bool, drift_results: Dict)
        """
        logger.info("Checking for data drift...")
        
        try:
            # Load reference data (older data)
            reference_end = datetime.now() - timedelta(days=current_days)
            reference_start = reference_end - timedelta(days=reference_days)
            
            reference_data = self._load_features_by_date_range(
                reference_start,
                reference_end
            )
            
            if reference_data is None or len(reference_data) == 0:
                logger.warning("No reference data available for drift detection")
                return False, {'error': 'No reference data'}
            
            # Load current data (recent data)
            current_start = datetime.now() - timedelta(days=current_days)
            current_end = datetime.now()
            
            current_data = self._load_features_by_date_range(
                current_start,
                current_end
            )
            
            if current_data is None or len(current_data) == 0:
                logger.warning("No current data available for drift detection")
                return False, {'error': 'No current data'}
            
            logger.info(
                f"Loaded {len(reference_data)} reference samples and "
                f"{len(current_data)} current samples"
            )
            
            # Initialize drift detector
            drift_detector = DriftDetector(
                reference_data=reference_data,
                psi_threshold=self.drift_threshold
            )
            
            # Detect drift using both KS test and PSI
            drift_results = drift_detector.detect_drift(
                current_data=current_data,
                methods=['ks', 'psi']
            )
            
            # Check if retraining is recommended
            drift_detected = drift_results.get('drift_detected', False)
            retraining_recommended = drift_results.get('retraining_recommended', False)
            
            if drift_detected:
                logger.warning(
                    f"Data drift detected! "
                    f"Features with KS drift: {len(drift_results.get('features_with_ks_drift', []))}, "
                    f"Features with high PSI: {len(drift_results.get('features_with_high_psi', []))}"
                )
            else:
                logger.info("No significant data drift detected")
            
            return retraining_recommended, drift_results
            
        except Exception as e:
            logger.error(f"Error checking drift: {e}", exc_info=True)
            return False, {'error': str(e)}
    
    def check_data_volume(
        self,
        days_since_last_training: int = 30
    ) -> Tuple[bool, int]:
        """
        Check if sufficient new data is available to trigger retraining
        
        Implements Requirement 11.3: Trigger retraining when new data > 1000 records
        
        Args:
            days_since_last_training: Number of days to look back
            
        Returns:
            Tuple of (threshold_met: bool, new_records: int)
        """
        logger.info("Checking data volume...")
        
        try:
            # Get the last training date from model registry
            last_training_date = self._get_last_training_date()
            
            if last_training_date is None:
                # No previous training, use default lookback
                cutoff_date = datetime.now() - timedelta(days=days_since_last_training)
            else:
                cutoff_date = last_training_date
            
            # Count new records since last training
            new_records = self._count_new_records(cutoff_date)
            
            threshold_met = new_records >= self.volume_threshold
            
            if threshold_met:
                logger.info(
                    f"Data volume threshold met: {new_records} new records "
                    f"(threshold: {self.volume_threshold})"
                )
            else:
                logger.info(
                    f"Data volume threshold not met: {new_records} new records "
                    f"(threshold: {self.volume_threshold})"
                )
            
            return threshold_met, new_records
            
        except Exception as e:
            logger.error(f"Error checking data volume: {e}", exc_info=True)
            return False, 0
    
    def check_performance_degradation(
        self,
        model_name: str,
        metric: str = 'roc_auc',
        threshold: float = 0.05
    ) -> Tuple[bool, Dict]:
        """
        Check if model performance has degraded significantly
        
        Args:
            model_name: Name of the model to check
            metric: Performance metric to monitor
            threshold: Degradation threshold (e.g., 0.05 = 5% drop)
            
        Returns:
            Tuple of (degradation_detected: bool, performance_info: Dict)
        """
        logger.info(f"Checking performance degradation for {model_name}...")
        
        try:
            with get_db_session() as db:
                # Get production model
                prod_model = db.query(ModelVersion).filter(
                    ModelVersion.model_name == model_name,
                    ModelVersion.status == 'production'
                ).first()
                
                if not prod_model:
                    logger.warning(f"No production model found for {model_name}")
                    return False, {'error': 'No production model'}
                
                # Get baseline performance
                baseline_performance = getattr(prod_model, metric, None)
                
                if baseline_performance is None:
                    logger.warning(f"No {metric} available for {model_name}")
                    return False, {'error': f'No {metric} metric'}
                
                # TODO: Implement real-time performance monitoring
                # For now, we'll use a placeholder
                # In production, this would query recent predictions and actual outcomes
                current_performance = baseline_performance  # Placeholder
                
                performance_drop = baseline_performance - current_performance
                degradation_detected = performance_drop > threshold
                
                performance_info = {
                    'model_name': model_name,
                    'metric': metric,
                    'baseline_performance': baseline_performance,
                    'current_performance': current_performance,
                    'performance_drop': performance_drop,
                    'threshold': threshold,
                    'degradation_detected': degradation_detected
                }
                
                if degradation_detected:
                    logger.warning(
                        f"Performance degradation detected for {model_name}: "
                        f"{metric} dropped by {performance_drop:.4f}"
                    )
                else:
                    logger.info(f"No performance degradation detected for {model_name}")
                
                return degradation_detected, performance_info
                
        except Exception as e:
            logger.error(f"Error checking performance degradation: {e}", exc_info=True)
            return False, {'error': str(e)}
    
    def should_retrain(
        self,
        check_drift: bool = True,
        check_volume: bool = True,
        check_performance: bool = False
    ) -> Tuple[bool, Dict]:
        """
        Comprehensive check to determine if retraining should be triggered
        
        Args:
            check_drift: Whether to check for data drift
            check_volume: Whether to check data volume
            check_performance: Whether to check performance degradation
            
        Returns:
            Tuple of (should_retrain: bool, trigger_info: Dict)
        """
        logger.info("Performing comprehensive retraining check...")
        
        trigger_info = {
            'timestamp': datetime.now().isoformat(),
            'checks_performed': []
        }
        
        should_retrain = False
        
        # Check drift
        if check_drift:
            drift_detected, drift_results = self.check_drift()
            trigger_info['drift_check'] = {
                'performed': True,
                'drift_detected': drift_detected,
                'results': drift_results
            }
            trigger_info['checks_performed'].append('drift')
            
            if drift_detected:
                should_retrain = True
                trigger_info['trigger_reason'] = 'data_drift'
        
        # Check volume
        if check_volume:
            volume_threshold_met, new_records = self.check_data_volume()
            trigger_info['volume_check'] = {
                'performed': True,
                'threshold_met': volume_threshold_met,
                'new_records': new_records,
                'threshold': self.volume_threshold
            }
            trigger_info['checks_performed'].append('volume')
            
            if volume_threshold_met and not should_retrain:
                should_retrain = True
                trigger_info['trigger_reason'] = 'data_volume'
        
        # Check performance
        if check_performance:
            # Check all production models
            model_names = ['random_forest', 'xgboost', 'neural_network']
            performance_issues = []
            
            for model_name in model_names:
                degradation_detected, perf_info = self.check_performance_degradation(
                    model_name
                )
                if degradation_detected:
                    performance_issues.append(perf_info)
            
            trigger_info['performance_check'] = {
                'performed': True,
                'issues_detected': len(performance_issues) > 0,
                'issues': performance_issues
            }
            trigger_info['checks_performed'].append('performance')
            
            if len(performance_issues) > 0 and not should_retrain:
                should_retrain = True
                trigger_info['trigger_reason'] = 'performance_degradation'
        
        trigger_info['should_retrain'] = should_retrain
        
        if should_retrain:
            logger.info(
                f"Retraining triggered! Reason: {trigger_info.get('trigger_reason')}"
            )
        else:
            logger.info("No retraining triggers activated")
        
        return should_retrain, trigger_info
    
    def _load_features_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Load features from database for a specific date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            DataFrame with features or None if no data
        """
        try:
            # Try loading from Parquet files first (faster)
            features_path = settings.FEATURES_PATH
            
            if features_path.exists():
                # Load all parquet files and filter by date
                parquet_files = list(features_path.glob("*.parquet"))
                
                if parquet_files:
                    dfs = []
                    for file in parquet_files:
                        df = pd.read_parquet(file)
                        if 'created_at' in df.columns:
                            df['created_at'] = pd.to_datetime(df['created_at'])
                            df = df[
                                (df['created_at'] >= start_date) &
                                (df['created_at'] <= end_date)
                            ]
                            if len(df) > 0:
                                dfs.append(df)
                    
                    if dfs:
                        combined_df = pd.concat(dfs, ignore_index=True)
                        # Drop non-feature columns
                        feature_cols = [
                            col for col in combined_df.columns
                            if col not in ['patient_id', 'visit_date', 'created_at', 
                                          'updated_at', 'diagnosis', 'data_source']
                        ]
                        return combined_df[feature_cols]
            
            # Fallback to database query
            with get_db_session() as db:
                features = db.query(ProcessedFeature).filter(
                    ProcessedFeature.created_at >= start_date,
                    ProcessedFeature.created_at <= end_date
                ).all()
                
                if not features:
                    return None
                
                # Convert to DataFrame
                data = []
                for f in features:
                    # Assuming features are stored as JSON
                    feature_dict = f.features if hasattr(f, 'features') else {}
                    data.append(feature_dict)
                
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error loading features by date range: {e}", exc_info=True)
            return None
    
    def _get_last_training_date(self) -> Optional[datetime]:
        """
        Get the date of the last model training
        
        Returns:
            Datetime of last training or None
        """
        try:
            with get_db_session() as db:
                # Get the most recent model version
                latest_model = db.query(ModelVersion).order_by(
                    ModelVersion.created_at.desc()
                ).first()
                
                if latest_model:
                    return latest_model.created_at
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting last training date: {e}", exc_info=True)
            return None
    
    def _count_new_records(self, cutoff_date: datetime) -> int:
        """
        Count new records since a cutoff date
        
        Args:
            cutoff_date: Date to count from
            
        Returns:
            Number of new records
        """
        try:
            # Try counting from Parquet files first
            features_path = settings.FEATURES_PATH
            
            if features_path.exists():
                parquet_files = list(features_path.glob("*.parquet"))
                
                if parquet_files:
                    total_count = 0
                    for file in parquet_files:
                        df = pd.read_parquet(file)
                        if 'created_at' in df.columns:
                            df['created_at'] = pd.to_datetime(df['created_at'])
                            count = len(df[df['created_at'] >= cutoff_date])
                            total_count += count
                    
                    return total_count
            
            # Fallback to database query
            with get_db_session() as db:
                count = db.query(ProcessedFeature).filter(
                    ProcessedFeature.created_at >= cutoff_date
                ).count()
                
                return count
                
        except Exception as e:
            logger.error(f"Error counting new records: {e}", exc_info=True)
            return 0
