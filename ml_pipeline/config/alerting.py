"""
Alerting system for ML pipeline
Sends alerts on processing failures and threshold violations
"""
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import json

from ml_pipeline.config.logging_config import main_logger
from ml_pipeline.config.settings import settings


class AlertManager:
    """Manage alerts for pipeline failures and issues"""
    
    def __init__(self):
        self.alert_history: List[Dict[str, Any]] = []
        self.alert_cooldown: Dict[str, float] = {}
        self.cooldown_period = 300  # 5 minutes between duplicate alerts
        self.alert_file = settings.LOGS_PATH / "alerts.json"
        self._load_alert_history()
    
    def _load_alert_history(self):
        """Load alert history from file"""
        if self.alert_file.exists():
            try:
                with open(self.alert_file, 'r') as f:
                    self.alert_history = json.load(f)
            except Exception as e:
                main_logger.error(f"Failed to load alert history: {e}")
    
    def _save_alert_history(self):
        """Save alert history to file"""
        try:
            self.alert_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.alert_file, 'w') as f:
                json.dump(self.alert_history[-1000:], f, indent=2)  # Keep last 1000
        except Exception as e:
            main_logger.error(f"Failed to save alert history: {e}")
    
    def _should_send_alert(self, alert_key: str) -> bool:
        """
        Check if alert should be sent based on cooldown
        
        Args:
            alert_key: Unique key for the alert type
            
        Returns:
            True if alert should be sent
        """
        current_time = time.time()
        
        if alert_key in self.alert_cooldown:
            last_alert_time = self.alert_cooldown[alert_key]
            if current_time - last_alert_time < self.cooldown_period:
                return False
        
        self.alert_cooldown[alert_key] = current_time
        return True
    
    def send_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Send an alert
        
        Args:
            alert_type: Type of alert (processing_failure, resource_threshold, etc.)
            severity: Severity level (info, warning, error, critical)
            message: Alert message
            details: Additional details
        """
        alert_key = f"{alert_type}_{severity}"
        
        # Check cooldown
        if not self._should_send_alert(alert_key):
            main_logger.debug(f"Alert suppressed due to cooldown: {alert_key}")
            return
        
        # Create alert record
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'details': details or {}
        }
        
        # Add to history
        self.alert_history.append(alert)
        self._save_alert_history()
        
        # Log alert
        log_method = getattr(main_logger, severity.lower(), main_logger.error)
        log_method(
            f"ALERT [{severity.upper()}] {alert_type}: {message}",
            extra={'operation': 'alert', 'user_id': 'system'}
        )
        
        # Send email if configured
        if settings.PERFORMANCE_ALERT_EMAIL:
            self._send_email_alert(alert)
        
        # Send to external systems (Prometheus, PagerDuty, etc.)
        self._send_to_external_systems(alert)
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """
        Send alert via email
        
        Args:
            alert: Alert dictionary
        """
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = 'ml-pipeline@example.com'
            msg['To'] = settings.PERFORMANCE_ALERT_EMAIL
            msg['Subject'] = f"[{alert['severity'].upper()}] ML Pipeline Alert: {alert['alert_type']}"
            
            # Email body
            body = f"""
ML Pipeline Alert

Timestamp: {alert['timestamp']}
Alert Type: {alert['alert_type']}
Severity: {alert['severity']}
Message: {alert['message']}

Details:
{json.dumps(alert['details'], indent=2)}

---
This is an automated alert from the ML Pipeline monitoring system.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email (would need SMTP configuration)
            # For now, just log that we would send
            main_logger.info(
                f"Email alert prepared for {settings.PERFORMANCE_ALERT_EMAIL}",
                extra={'operation': 'alert_email', 'user_id': 'system'}
            )
            
        except Exception as e:
            main_logger.error(f"Failed to send email alert: {e}")
    
    def _send_to_external_systems(self, alert: Dict[str, Any]):
        """
        Send alert to external monitoring systems
        
        Args:
            alert: Alert dictionary
        """
        # Placeholder for integration with external systems
        # Could integrate with:
        # - Prometheus Alertmanager
        # - PagerDuty
        # - Slack
        # - Microsoft Teams
        pass
    
    def alert_processing_failure(
        self,
        operation: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Alert on processing failure
        
        Args:
            operation: Operation that failed
            error: Error message
            details: Additional details
        """
        self.send_alert(
            alert_type='processing_failure',
            severity='error',
            message=f"Processing failure in {operation}: {error}",
            details={
                'operation': operation,
                'error': error,
                **(details or {})
            }
        )
    
    def alert_resource_threshold(
        self,
        resource: str,
        current_value: float,
        threshold: float,
        unit: str = ''
    ):
        """
        Alert on resource threshold violation
        
        Args:
            resource: Resource name (cpu, memory, disk)
            current_value: Current value
            threshold: Threshold value
            unit: Unit of measurement
        """
        self.send_alert(
            alert_type='resource_threshold',
            severity='warning',
            message=f"{resource} threshold exceeded: {current_value}{unit} > {threshold}{unit}",
            details={
                'resource': resource,
                'current_value': current_value,
                'threshold': threshold,
                'unit': unit
            }
        )
    
    def alert_data_quality_issue(
        self,
        dataset: str,
        issue_type: str,
        details: Dict[str, Any]
    ):
        """
        Alert on data quality issues
        
        Args:
            dataset: Dataset name
            issue_type: Type of issue
            details: Issue details
        """
        self.send_alert(
            alert_type='data_quality',
            severity='warning',
            message=f"Data quality issue in {dataset}: {issue_type}",
            details={
                'dataset': dataset,
                'issue_type': issue_type,
                **details
            }
        )
    
    def alert_model_performance_degradation(
        self,
        model_name: str,
        metric: str,
        current_value: float,
        baseline_value: float
    ):
        """
        Alert on model performance degradation
        
        Args:
            model_name: Model name
            metric: Performance metric
            current_value: Current metric value
            baseline_value: Baseline metric value
        """
        degradation_percent = ((baseline_value - current_value) / baseline_value) * 100
        
        self.send_alert(
            alert_type='model_performance',
            severity='warning',
            message=f"Model performance degradation: {model_name} - "
                   f"{metric} decreased by {degradation_percent:.1f}%",
            details={
                'model_name': model_name,
                'metric': metric,
                'current_value': current_value,
                'baseline_value': baseline_value,
                'degradation_percent': degradation_percent
            }
        )
    
    def alert_data_drift(
        self,
        feature: str,
        psi_value: float,
        threshold: float
    ):
        """
        Alert on data drift detection
        
        Args:
            feature: Feature name
            psi_value: PSI value
            threshold: PSI threshold
        """
        self.send_alert(
            alert_type='data_drift',
            severity='warning',
            message=f"Data drift detected in feature {feature}: PSI={psi_value:.3f}",
            details={
                'feature': feature,
                'psi_value': psi_value,
                'threshold': threshold
            }
        )
    
    def get_recent_alerts(
        self,
        hours: int = 24,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts
        
        Args:
            hours: Number of hours to look back
            severity: Filter by severity (optional)
            
        Returns:
            List of alerts
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
        ]
        
        if severity:
            recent_alerts = [
                alert for alert in recent_alerts
                if alert['severity'] == severity
            ]
        
        return recent_alerts
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, int]:
        """
        Get summary of alerts
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with alert counts by type and severity
        """
        recent_alerts = self.get_recent_alerts(hours)
        
        summary = {
            'total': len(recent_alerts),
            'by_severity': {},
            'by_type': {}
        }
        
        for alert in recent_alerts:
            # Count by severity
            severity = alert['severity']
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Count by type
            alert_type = alert['alert_type']
            summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
        
        return summary


# Global alert manager instance
alert_manager = AlertManager()


class AlertThresholds:
    """Define alert thresholds"""
    
    # Resource thresholds
    CPU_THRESHOLD = 90.0  # percent
    MEMORY_THRESHOLD = 90.0  # percent
    DISK_THRESHOLD = 10.0  # GB free
    
    # Processing time thresholds (seconds)
    DATA_INGESTION_THRESHOLD = 3600  # 1 hour
    TRAINING_THRESHOLD = 7200  # 2 hours
    FEATURE_EXTRACTION_THRESHOLD = 60  # 1 minute per scan
    
    # Data quality thresholds
    COMPLETENESS_THRESHOLD = 0.70
    OUTLIER_THRESHOLD = 0.05  # 5% outliers
    
    # Model performance thresholds
    MIN_AUC_ROC = 0.80
    PERFORMANCE_DEGRADATION_THRESHOLD = 0.05  # 5% degradation
    
    # Drift thresholds
    PSI_THRESHOLD = 0.2


def check_and_alert_on_failure(operation: str):
    """
    Decorator to automatically alert on operation failures
    
    Args:
        operation: Operation name
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Send alert
                alert_manager.alert_processing_failure(
                    operation=operation,
                    error=str(e),
                    details={
                        'function': func.__name__,
                        'args': str(args)[:200],  # Truncate for safety
                        'kwargs': str(kwargs)[:200]
                    }
                )
                raise
        
        return wrapper
    return decorator
