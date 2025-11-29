"""
Notification Service

This module handles sending notifications about retraining events including:
- Retraining completion
- Model promotion
- Performance alerts
- Drift detection
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import get_logger

logger = get_logger(__name__)


class NotificationService:
    """
    Handle notifications for automated retraining events
    
    Implements:
    - Send notifications before model updates (Requirement 11.6)
    - Alert on retraining completion
    - Alert on model promotion
    - Alert on drift detection
    """
    
    def __init__(
        self,
        email_recipients: List[str] = None,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_username: str = None,
        smtp_password: str = None
    ):
        """
        Initialize notification service
        
        Args:
            email_recipients: List of email addresses to notify
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_username: SMTP username
            smtp_password: SMTP password
        """
        self.email_recipients = email_recipients or (
            [settings.PERFORMANCE_ALERT_EMAIL] if settings.PERFORMANCE_ALERT_EMAIL else []
        )
        
        # SMTP configuration (would typically come from environment variables)
        self.smtp_host = smtp_host or "localhost"
        self.smtp_port = smtp_port or 587
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        
        logger.info(
            f"Initialized NotificationService with {len(self.email_recipients)} recipients"
        )
    
    def send_retraining_summary(
        self,
        drift_detected: bool,
        volume_threshold_met: bool,
        deployment_results: Dict[str, Any]
    ) -> bool:
        """
        Send summary notification about retraining results
        
        Implements Requirement 11.6: Send notifications before model updates
        
        Args:
            drift_detected: Whether drift was detected
            volume_threshold_met: Whether volume threshold was met
            deployment_results: Results from model promotion
            
        Returns:
            True if notification sent successfully
        """
        logger.info("Sending retraining summary notification...")
        
        try:
            # Build notification content
            subject = self._build_retraining_subject(deployment_results)
            body = self._build_retraining_body(
                drift_detected,
                volume_threshold_met,
                deployment_results
            )
            
            # Send email
            success = self._send_email(subject, body)
            
            if success:
                logger.info("Retraining summary notification sent successfully")
            else:
                logger.warning("Failed to send retraining summary notification")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending retraining summary: {e}", exc_info=True)
            return False
    
    def send_drift_alert(
        self,
        drift_results: Dict[str, Any]
    ) -> bool:
        """
        Send alert when data drift is detected
        
        Args:
            drift_results: Results from drift detection
            
        Returns:
            True if notification sent successfully
        """
        logger.info("Sending drift alert notification...")
        
        try:
            subject = "⚠️ Data Drift Detected - Retraining Recommended"
            
            body = f"""
Data Drift Alert
================

Data drift has been detected in the ML pipeline.

Timestamp: {drift_results.get('timestamp', 'N/A')}

Drift Detection Results:
- Features with KS drift: {len(drift_results.get('features_with_ks_drift', []))}
- Features with high PSI: {len(drift_results.get('features_with_high_psi', []))}

Features with KS Drift:
{self._format_list(drift_results.get('features_with_ks_drift', []))}

Features with High PSI:
{self._format_list(drift_results.get('features_with_high_psi', []))}

Retraining Recommended: {drift_results.get('retraining_recommended', False)}

Action Required:
- Review drift detection results
- Consider triggering manual retraining if not already scheduled
- Investigate potential causes of drift

---
This is an automated notification from the ML Pipeline Monitoring System.
"""
            
            success = self._send_email(subject, body)
            
            if success:
                logger.info("Drift alert notification sent successfully")
            else:
                logger.warning("Failed to send drift alert notification")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending drift alert: {e}", exc_info=True)
            return False
    
    def send_promotion_notification(
        self,
        model_name: str,
        version_id: str,
        improvement_percent: float,
        new_metrics: Dict[str, float],
        scheduled_deployment_time: Optional[datetime] = None
    ) -> bool:
        """
        Send notification before promoting a model to production
        
        Implements Requirement 11.6: Send notifications before model updates
        
        Args:
            model_name: Name of the model
            version_id: Version ID being promoted
            improvement_percent: Performance improvement percentage
            new_metrics: Metrics of the new model
            scheduled_deployment_time: When deployment is scheduled
            
        Returns:
            True if notification sent successfully
        """
        logger.info(f"Sending promotion notification for {model_name}...")
        
        try:
            subject = f"🚀 Model Promotion: {model_name} v{version_id}"
            
            deployment_time_str = (
                scheduled_deployment_time.strftime("%Y-%m-%d %H:%M:%S UTC")
                if scheduled_deployment_time
                else "Immediately"
            )
            
            body = f"""
Model Promotion Notification
============================

A new model version is being promoted to production.

Model: {model_name}
Version: {version_id}
Improvement: {improvement_percent:.2f}%
Scheduled Deployment: {deployment_time_str}

New Model Metrics:
{self._format_metrics(new_metrics)}

Action Required:
- Review the new model performance
- Verify deployment schedule
- Monitor model performance after deployment

To cancel this deployment, please contact the ML team immediately.

---
This is an automated notification from the ML Pipeline Monitoring System.
"""
            
            success = self._send_email(subject, body)
            
            if success:
                logger.info("Promotion notification sent successfully")
            else:
                logger.warning("Failed to send promotion notification")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending promotion notification: {e}", exc_info=True)
            return False
    
    def send_retraining_started_notification(
        self,
        trigger_reason: str,
        trigger_details: Dict[str, Any]
    ) -> bool:
        """
        Send notification when retraining starts
        
        Args:
            trigger_reason: Reason for retraining (drift, volume, manual)
            trigger_details: Additional details about the trigger
            
        Returns:
            True if notification sent successfully
        """
        logger.info("Sending retraining started notification...")
        
        try:
            subject = f"🔄 Model Retraining Started - Trigger: {trigger_reason}"
            
            body = f"""
Model Retraining Started
========================

Automated model retraining has been initiated.

Trigger Reason: {trigger_reason}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

Trigger Details:
{json.dumps(trigger_details, indent=2)}

Expected Duration: ~2 hours

You will receive another notification when retraining is complete.

---
This is an automated notification from the ML Pipeline Monitoring System.
"""
            
            success = self._send_email(subject, body)
            
            if success:
                logger.info("Retraining started notification sent successfully")
            else:
                logger.warning("Failed to send retraining started notification")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending retraining started notification: {e}", exc_info=True)
            return False
    
    def send_retraining_failed_notification(
        self,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification when retraining fails
        
        Args:
            error_message: Error message
            error_details: Additional error details
            
        Returns:
            True if notification sent successfully
        """
        logger.info("Sending retraining failed notification...")
        
        try:
            subject = "❌ Model Retraining Failed - Action Required"
            
            body = f"""
Model Retraining Failed
=======================

Automated model retraining has failed.

Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

Error Message:
{error_message}

Error Details:
{json.dumps(error_details or {}, indent=2)}

Action Required:
- Review error logs
- Check data pipeline status
- Investigate root cause
- Consider manual intervention

---
This is an automated notification from the ML Pipeline Monitoring System.
"""
            
            success = self._send_email(subject, body)
            
            if success:
                logger.info("Retraining failed notification sent successfully")
            else:
                logger.warning("Failed to send retraining failed notification")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending retraining failed notification: {e}", exc_info=True)
            return False
    
    def _build_retraining_subject(
        self,
        deployment_results: Dict[str, Any]
    ) -> str:
        """Build email subject for retraining summary"""
        summary = deployment_results.get('summary', {})
        models_promoted = summary.get('models_promoted', 0)
        
        if models_promoted > 0:
            return f"✅ Model Retraining Complete - {models_promoted} Model(s) Promoted"
        else:
            return "ℹ️ Model Retraining Complete - No Promotions"
    
    def _build_retraining_body(
        self,
        drift_detected: bool,
        volume_threshold_met: bool,
        deployment_results: Dict[str, Any]
    ) -> str:
        """Build email body for retraining summary"""
        summary = deployment_results.get('summary', {})
        promotion_results = deployment_results.get('promotion_results', {})
        
        # Build trigger section
        triggers = []
        if drift_detected:
            triggers.append("Data Drift Detected")
        if volume_threshold_met:
            triggers.append("Data Volume Threshold Met")
        
        trigger_text = ", ".join(triggers) if triggers else "Scheduled Retraining"
        
        # Build promotion section
        promoted_models = []
        for model_name, result in promotion_results.items():
            if result.get('promoted'):
                improvement = result.get('improvement_percent', 0)
                version = result.get('version_id', 'N/A')
                promoted_models.append(
                    f"  - {model_name} v{version} (+{improvement:.2f}%)"
                )
        
        promoted_text = "\n".join(promoted_models) if promoted_models else "  None"
        
        # Build review required section
        review_models = []
        for model_name, result in promotion_results.items():
            if result.get('reason') == 'requires_manual_review':
                improvement = result.get('improvement_percent', 0)
                review_models.append(
                    f"  - {model_name} (+{improvement:.2f}%)"
                )
        
        review_text = "\n".join(review_models) if review_models else "  None"
        
        body = f"""
Model Retraining Summary
========================

Automated model retraining has completed successfully.

Timestamp: {deployment_results.get('timestamp', 'N/A')}

Trigger: {trigger_text}

Results:
--------
Models Promoted: {summary.get('models_promoted', 0)}
Models Requiring Manual Review: {summary.get('models_requiring_review', 0)}
Models Not Promoted: {summary.get('models_not_promoted', 0)}

Promoted Models:
{promoted_text}

Models Requiring Manual Review:
{review_text}

Action Required:
- Review promoted models in production
- Monitor model performance
- Review models flagged for manual review

---
This is an automated notification from the ML Pipeline Monitoring System.
"""
        
        return body
    
    def _send_email(
        self,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email notification
        
        Args:
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            True if email sent successfully
        """
        if not self.email_recipients:
            logger.warning("No email recipients configured. Skipping email notification.")
            # Log the notification instead
            logger.info(f"NOTIFICATION: {subject}\n{body}")
            return True  # Consider it successful since we logged it
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username or "ml-pipeline@example.com"
            msg['To'] = ", ".join(self.email_recipients)
            
            # Attach plain text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_username and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent to {len(self.email_recipients)} recipient(s)")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            # Log the notification as fallback
            logger.info(f"NOTIFICATION (email failed): {subject}\n{body}")
            return False
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items for email body"""
        if not items:
            return "  None"
        return "\n".join([f"  - {item}" for item in items])
    
    def _format_metrics(self, metrics: Dict[str, float]) -> str:
        """Format metrics dictionary for email body"""
        if not metrics:
            return "  No metrics available"
        
        lines = []
        for metric, value in metrics.items():
            if isinstance(value, float):
                lines.append(f"  - {metric}: {value:.4f}")
            else:
                lines.append(f"  - {metric}: {value}")
        
        return "\n".join(lines)
