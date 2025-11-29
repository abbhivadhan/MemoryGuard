"""
Comprehensive data drift monitoring system
Integrates all monitoring components and provides database persistence
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from ml_pipeline.config.settings import settings
from ml_pipeline.data_storage.database import get_db
from ml_pipeline.data_storage.models import DataDriftReport
from ml_pipeline.monitoring.distribution_monitor import DistributionMonitor
from ml_pipeline.monitoring.drift_detector import DriftDetector
from ml_pipeline.monitoring.drift_alerting import DriftAlerter
from ml_pipeline.monitoring.performance_tracker import PerformanceTracker
from ml_pipeline.monitoring.drift_reporter import DriftReporter

logger = logging.getLogger(__name__)


class DataDriftMonitor:
    """
    Comprehensive data drift monitoring system
    Combines distribution monitoring, drift detection, alerting, and reporting
    """
    
    def __init__(
        self,
        reference_data: Optional[pd.DataFrame] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize data drift monitor
        
        Args:
            reference_data: Reference dataset for drift detection
            model_name: Name of the model being monitored
        """
        self.model_name = model_name or "default_model"
        
        # Initialize components
        self.distribution_monitor = DistributionMonitor(reference_data)
        self.drift_detector = DriftDetector(
            reference_data,
            ks_threshold=0.05,
            psi_threshold=settings.PSI_THRESHOLD
        )
        self.drift_alerter = DriftAlerter(
            alert_email=settings.PERFORMANCE_ALERT_EMAIL,
            psi_threshold=settings.PSI_THRESHOLD
        )
        self.performance_tracker = PerformanceTracker(self.model_name)
        self.drift_reporter = DriftReporter()
        
        logger.info(f"Initialized DataDriftMonitor for model: {self.model_name}")
    
    def set_reference_data(self, data: pd.DataFrame) -> None:
        """
        Set reference data for all monitoring components
        
        Args:
            data: Reference dataset
        """
        self.distribution_monitor.set_reference_data(data)
        self.drift_detector.set_reference_data(data)
        
        logger.info(f"Reference data set: {len(data)} samples")
    
    def monitor_data(
        self,
        current_data: pd.DataFrame,
        dataset_name: str = "current_data",
        save_to_db: bool = True
    ) -> Dict:
        """
        Perform comprehensive drift monitoring on current data
        
        Args:
            current_data: Current dataset to monitor
            dataset_name: Name of the dataset
            save_to_db: Whether to save results to database
            
        Returns:
            Monitoring results dictionary
        """
        logger.info(f"Starting drift monitoring for {dataset_name}")
        
        # 1. Track distributions
        logger.info("Tracking distributions...")
        current_distributions = self.distribution_monitor.track_distributions(
            current_data,
            dataset_name
        )
        
        # 2. Detect drift
        logger.info("Detecting drift...")
        drift_results = self.drift_detector.detect_drift(
            current_data,
            methods=['ks', 'psi']
        )
        
        # 3. Check for alerts
        logger.info("Checking for alerts...")
        alert_triggered = self.drift_alerter.check_and_alert(
            drift_results,
            dataset_name
        )
        
        # 4. Compile results
        monitoring_results = {
            'timestamp': datetime.now().isoformat(),
            'dataset_name': dataset_name,
            'model_name': self.model_name,
            'n_samples': len(current_data),
            'n_features': len(current_distributions),
            'drift_detected': drift_results['drift_detected'],
            'retraining_recommended': drift_results['retraining_recommended'],
            'alert_triggered': alert_triggered,
            'drift_results': drift_results,
            'current_distributions': current_distributions
        }
        
        # 5. Save to database
        if save_to_db:
            self._save_to_database(monitoring_results)
        
        logger.info(
            f"Drift monitoring complete: drift_detected={drift_results['drift_detected']}, "
            f"alert_triggered={alert_triggered}"
        )
        
        return monitoring_results
    
    def monitor_performance(
        self,
        y_true: pd.Series,
        y_pred: pd.Series,
        y_proba: Optional[pd.Series] = None,
        dataset_name: str = "recent_data"
    ) -> Dict:
        """
        Monitor model performance on recent data
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional)
            dataset_name: Name of the dataset
            
        Returns:
            Performance tracking results
        """
        logger.info(f"Monitoring performance on {dataset_name}")
        
        # Track performance
        performance_entry = self.performance_tracker.track_performance(
            y_true.values,
            y_pred.values,
            y_proba.values if y_proba is not None else None,
            dataset_name
        )
        
        # Check for degradation
        degraded, details = self.performance_tracker.detect_performance_degradation()
        
        if degraded:
            logger.warning(
                f"Performance degradation detected: {details['metric']} "
                f"dropped by {abs(details['relative_change'])*100:.2f}%"
            )
        
        return performance_entry
    
    def generate_weekly_report(
        self,
        current_data: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Generate weekly drift report
        
        Args:
            current_data: Current data for drift detection (optional)
            
        Returns:
            Report dictionary
        """
        logger.info("Generating weekly drift report...")
        
        report = self.drift_reporter.generate_weekly_report(
            distribution_monitor=self.distribution_monitor,
            drift_detector=self.drift_detector,
            performance_tracker=self.performance_tracker,
            current_data=current_data
        )
        
        return report
    
    def _save_to_database(self, monitoring_results: Dict) -> None:
        """
        Save monitoring results to database
        
        Args:
            monitoring_results: Monitoring results dictionary
        """
        try:
            db = next(get_db())
            
            # Create drift report entry
            drift_report = DataDriftReport(
                report_id=str(uuid.uuid4()),
                reference_dataset="reference_data",
                comparison_dataset=monitoring_results['dataset_name'],
                drift_detected=monitoring_results['drift_detected'],
                features_with_drift=monitoring_results['drift_results'].get('features_with_ks_drift', []),
                ks_test_results=monitoring_results['drift_results'].get('ks_test', {}),
                psi_scores=monitoring_results['drift_results'].get('psi_scores', {}),
                retraining_recommended=monitoring_results['retraining_recommended'],
                created_at=datetime.now()
            )
            
            db.add(drift_report)
            db.commit()
            
            logger.info(f"Saved drift report to database: {drift_report.report_id}")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
    
    def load_historical_statistics(
        self,
        days: int = 90
    ) -> Dict:
        """
        Load historical statistics for analysis
        
        Args:
            days: Number of days of history to load
            
        Returns:
            Historical statistics dictionary
        """
        logger.info(f"Loading historical statistics for last {days} days")
        
        # Load distribution history
        distribution_history = self.distribution_monitor.load_distribution_history()
        
        # Load performance history
        self.performance_tracker.load_performance_history(days=days)
        
        # Load alert history
        alert_history = self.drift_alerter.load_alert_history()
        
        statistics = {
            'period_days': days,
            'n_distribution_entries': len(distribution_history),
            'n_performance_entries': len(self.performance_tracker.performance_history),
            'n_alerts': len(alert_history),
            'distribution_history': distribution_history,
            'performance_history': self.performance_tracker.performance_history,
            'alert_history': alert_history
        }
        
        logger.info(
            f"Loaded historical statistics: {len(distribution_history)} distributions, "
            f"{len(alert_history)} alerts"
        )
        
        return statistics
    
    def get_drift_history_from_db(
        self,
        days: int = 30
    ) -> List[DataDriftReport]:
        """
        Get drift history from database
        
        Args:
            days: Number of days of history
            
        Returns:
            List of drift reports
        """
        try:
            db = next(get_db())
            
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            
            reports = db.query(DataDriftReport).filter(
                DataDriftReport.created_at >= cutoff_date
            ).order_by(DataDriftReport.created_at.desc()).all()
            
            logger.info(f"Retrieved {len(reports)} drift reports from database")
            
            return reports
            
        except Exception as e:
            logger.error(f"Error retrieving drift history: {e}")
            return []
        finally:
            if db:
                db.close()
    
    def get_drift_summary_df(self, days: int = 30) -> pd.DataFrame:
        """
        Get drift summary as DataFrame
        
        Args:
            days: Number of days of history
            
        Returns:
            DataFrame with drift summary
        """
        reports = self.get_drift_history_from_db(days)
        
        if not reports:
            return pd.DataFrame()
        
        data = []
        for report in reports:
            data.append({
                'report_id': report.report_id,
                'timestamp': report.created_at,
                'dataset': report.comparison_dataset,
                'drift_detected': report.drift_detected,
                'retraining_recommended': report.retraining_recommended,
                'n_features_with_drift': len(report.features_with_drift) if report.features_with_drift else 0
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('timestamp', ascending=False)
        
        return df
    
    def cleanup_old_data(self, days: int = 90) -> Dict:
        """
        Clean up old monitoring data
        
        Args:
            days: Retain data for this many days
            
        Returns:
            Cleanup summary
        """
        logger.info(f"Cleaning up data older than {days} days")
        
        summary = {
            'alerts_cleared': 0,
            'db_records_deleted': 0
        }
        
        # Clear old alerts
        summary['alerts_cleared'] = self.drift_alerter.clear_old_alerts(days)
        
        # Clear old database records
        try:
            db = next(get_db())
            
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            
            deleted = db.query(DataDriftReport).filter(
                DataDriftReport.created_at < cutoff_date
            ).delete()
            
            db.commit()
            summary['db_records_deleted'] = deleted
            
            logger.info(f"Deleted {deleted} old drift reports from database")
            
        except Exception as e:
            logger.error(f"Error cleaning up database: {e}")
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
        
        logger.info(f"Cleanup complete: {summary}")
        
        return summary
    
    def should_retrain_model(self) -> Tuple[bool, str]:
        """
        Determine if model should be retrained based on all monitoring data
        
        Returns:
            Tuple of (should_retrain, reason)
        """
        reasons = []
        
        # Check recent drift reports
        recent_reports = self.get_drift_history_from_db(days=7)
        
        if recent_reports:
            drift_count = sum(1 for r in recent_reports if r.drift_detected)
            if drift_count > 0:
                reasons.append(f"Drift detected in {drift_count} recent reports")
        
        # Check performance degradation
        degraded, details = self.performance_tracker.detect_performance_degradation()
        if degraded:
            reasons.append(
                f"Performance degraded: {details['metric']} "
                f"dropped by {abs(details['relative_change'])*100:.1f}%"
            )
        
        should_retrain = len(reasons) > 0
        reason = "; ".join(reasons) if reasons else "No retraining needed"
        
        return should_retrain, reason


# Convenience function for creating monitor instance
def create_drift_monitor(
    reference_data: pd.DataFrame,
    model_name: str = "default_model"
) -> DataDriftMonitor:
    """
    Create and initialize a data drift monitor
    
    Args:
        reference_data: Reference dataset
        model_name: Name of the model
        
    Returns:
        Initialized DataDriftMonitor instance
    """
    monitor = DataDriftMonitor(reference_data, model_name)
    return monitor
