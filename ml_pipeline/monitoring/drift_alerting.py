"""
Drift alerting system
Triggers alerts when drift is detected and sends notifications
"""
import json
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from ml_pipeline.config.settings import settings

logger = logging.getLogger(__name__)


class DriftAlerter:
    """
    Alert system for data drift detection
    Sends notifications when drift exceeds thresholds
    """
    
    def __init__(
        self,
        alert_email: Optional[str] = None,
        psi_threshold: float = 0.2,
        alert_storage_path: Optional[Path] = None
    ):
        """
        Initialize drift alerter
        
        Args:
            alert_email: Email address for alerts
            psi_threshold: PSI threshold for triggering alerts
            alert_storage_path: Path to store alert history
        """
        self.alert_email = alert_email or settings.PERFORMANCE_ALERT_EMAIL
        self.psi_threshold = psi_threshold
        
        # Storage for alert history
        if alert_storage_path is None:
            alert_storage_path = settings.METADATA_PATH / "alerts"
        self.alert_storage_path = alert_storage_path
        self.alert_storage_path.mkdir(parents=True, exist_ok=True)
        
        self.alert_history = []
        
        logger.info(f"Initialized DriftAlerter with email={self.alert_email}")
    
    def check_and_alert(
        self,
        drift_results: Dict,
        dataset_name: str = "unknown"
    ) -> bool:
        """
        Check drift results and trigger alerts if necessary
        
        Args:
            drift_results: Results from DriftDetector.detect_drift()
            dataset_name: Name of the dataset being monitored
            
        Returns:
            True if alert was triggered
        """
        alert_triggered = False
        
        # Check if drift was detected
        if not drift_results.get('drift_detected', False):
            logger.info("No drift detected, no alert needed")
            return False
        
        # Check PSI scores
        high_psi_features = drift_results.get('features_with_high_psi', [])
        ks_drift_features = drift_results.get('features_with_ks_drift', [])
        
        if high_psi_features or ks_drift_features:
            alert_triggered = True
            
            # Create alert
            alert = self._create_alert(
                drift_results=drift_results,
                dataset_name=dataset_name,
                high_psi_features=high_psi_features,
                ks_drift_features=ks_drift_features
            )
            
            # Store alert
            self._store_alert(alert)
            
            # Send notification
            if self.alert_email:
                self._send_email_alert(alert)
            else:
                logger.warning("No alert email configured, skipping email notification")
            
            # Log alert
            logger.warning(
                f"DRIFT ALERT: {len(high_psi_features)} features with high PSI, "
                f"{len(ks_drift_features)} features with KS drift"
            )
        
        return alert_triggered
    
    def _create_alert(
        self,
        drift_results: Dict,
        dataset_name: str,
        high_psi_features: List[str],
        ks_drift_features: List[str]
    ) -> Dict:
        """
        Create alert object
        
        Args:
            drift_results: Drift detection results
            dataset_name: Dataset name
            high_psi_features: Features with high PSI
            ks_drift_features: Features with KS drift
            
        Returns:
            Alert dictionary
        """
        alert = {
            'alert_id': f"drift_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'dataset_name': dataset_name,
            'alert_type': 'data_drift',
            'severity': self._determine_severity(high_psi_features, ks_drift_features),
            'drift_detected': True,
            'retraining_recommended': drift_results.get('retraining_recommended', False),
            'n_reference_samples': drift_results.get('n_reference_samples', 0),
            'n_current_samples': drift_results.get('n_current_samples', 0),
            'features_with_high_psi': high_psi_features,
            'features_with_ks_drift': ks_drift_features,
            'psi_scores': drift_results.get('psi_scores', {}),
            'ks_test_results': drift_results.get('ks_test', {})
        }
        
        return alert
    
    def _determine_severity(
        self,
        high_psi_features: List[str],
        ks_drift_features: List[str]
    ) -> str:
        """
        Determine alert severity based on number of drifted features
        
        Args:
            high_psi_features: Features with high PSI
            ks_drift_features: Features with KS drift
            
        Returns:
            Severity level: 'low', 'medium', 'high', 'critical'
        """
        total_drift_features = len(set(high_psi_features + ks_drift_features))
        
        if total_drift_features >= 10:
            return 'critical'
        elif total_drift_features >= 5:
            return 'high'
        elif total_drift_features >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _store_alert(self, alert: Dict) -> None:
        """
        Store alert to disk
        
        Args:
            alert: Alert dictionary
        """
        # Add to history
        self.alert_history.append(alert)
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_to_native(obj):
            """Convert numpy types to native Python types"""
            import numpy as np
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            return obj
        
        # Save to file
        filepath = self.alert_storage_path / f"{alert['alert_id']}.json"
        with open(filepath, 'w') as f:
            json.dump(convert_to_native(alert), f, indent=2)
        
        logger.info(f"Alert stored: {filepath}")
    
    def _send_email_alert(self, alert: Dict) -> None:
        """
        Send email alert
        
        Args:
            alert: Alert dictionary
        """
        try:
            # Create email message
            subject = f"[{alert['severity'].upper()}] Data Drift Alert - {alert['dataset_name']}"
            body = self._format_alert_email(alert)
            
            # For now, just log the email content
            # In production, this would use SMTP to send actual emails
            logger.info(f"Email alert would be sent to {self.alert_email}")
            logger.info(f"Subject: {subject}")
            logger.debug(f"Body:\n{body}")
            
            # Store email content
            email_file = self.alert_storage_path / f"{alert['alert_id']}_email.txt"
            with open(email_file, 'w') as f:
                f.write(f"To: {self.alert_email}\n")
                f.write(f"Subject: {subject}\n\n")
                f.write(body)
            
            logger.info(f"Alert email content saved to {email_file}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _format_alert_email(self, alert: Dict) -> str:
        """
        Format alert as email body
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Formatted email body
        """
        body = f"""
Data Drift Alert
================

Alert ID: {alert['alert_id']}
Timestamp: {alert['timestamp']}
Dataset: {alert['dataset_name']}
Severity: {alert['severity'].upper()}

Summary
-------
Drift Detected: {alert['drift_detected']}
Retraining Recommended: {alert['retraining_recommended']}

Reference Samples: {alert['n_reference_samples']}
Current Samples: {alert['n_current_samples']}

Features with High PSI (>= {self.psi_threshold})
-------------------------------------------------
"""
        
        if alert['features_with_high_psi']:
            for feature in alert['features_with_high_psi']:
                psi_score = alert['psi_scores'].get(feature, 'N/A')
                body += f"  - {feature}: PSI = {psi_score:.4f}\n"
        else:
            body += "  None\n"
        
        body += "\nFeatures with KS Drift\n"
        body += "----------------------\n"
        
        if alert['features_with_ks_drift']:
            for feature in alert['features_with_ks_drift']:
                ks_result = alert['ks_test_results'].get(feature, {})
                p_value = ks_result.get('p_value', 'N/A')
                body += f"  - {feature}: p-value = {p_value}\n"
        else:
            body += "  None\n"
        
        body += "\nRecommended Actions\n"
        body += "-------------------\n"
        
        if alert['retraining_recommended']:
            body += "1. Review drift analysis results\n"
            body += "2. Investigate root causes of distribution changes\n"
            body += "3. Consider retraining models with recent data\n"
            body += "4. Update reference distributions if changes are expected\n"
        else:
            body += "Monitor the situation. Retraining may not be necessary yet.\n"
        
        body += f"\nThis alert was generated automatically by the ML Pipeline monitoring system.\n"
        
        return body
    
    def load_alert_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Load alert history from storage
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        for filepath in sorted(self.alert_storage_path.glob("drift_alert_*.json")):
            with open(filepath, 'r') as f:
                alert = json.load(f)
            
            alert_time = datetime.fromisoformat(alert['timestamp'])
            
            # Filter by date range
            if start_date and alert_time < start_date:
                continue
            if end_date and alert_time > end_date:
                continue
            
            alerts.append(alert)
        
        self.alert_history = alerts
        logger.info(f"Loaded {len(alerts)} alerts from history")
        
        return alerts
    
    def get_alert_summary(self) -> pd.DataFrame:
        """
        Get summary of alert history
        
        Returns:
            DataFrame with alert summary
        """
        if not self.alert_history:
            logger.warning("No alert history available")
            return pd.DataFrame()
        
        summary_data = []
        
        for alert in self.alert_history:
            summary_data.append({
                'alert_id': alert['alert_id'],
                'timestamp': alert['timestamp'],
                'dataset_name': alert['dataset_name'],
                'severity': alert['severity'],
                'n_high_psi_features': len(alert['features_with_high_psi']),
                'n_ks_drift_features': len(alert['features_with_ks_drift']),
                'retraining_recommended': alert['retraining_recommended']
            })
        
        df = pd.DataFrame(summary_data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
        
        return df
    
    def clear_old_alerts(self, days: int = 90) -> int:
        """
        Clear alerts older than specified days
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of alerts cleared
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        cleared_count = 0
        
        for filepath in self.alert_storage_path.glob("drift_alert_*.json"):
            if filepath.stat().st_mtime < cutoff_date:
                filepath.unlink()
                cleared_count += 1
        
        logger.info(f"Cleared {cleared_count} alerts older than {days} days")
        
        return cleared_count
