"""
Celery tasks for pattern monitoring and proactive alerts.
"""

from celery import Task
from typing import List
import logging
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.pattern_detection_service import pattern_detection_service
from app.models.user import User

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""
    
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='patterns.monitor_user',
    max_retries=2
)
def monitor_user_patterns_task(
    self,
    user_id: str,
    send_alerts: bool = True
):
    """
    Monitor patterns for a specific user and send alerts if needed.
    
    Args:
        user_id: User ID to monitor
        send_alerts: Whether to send alerts for detected patterns
        
    Requirements: 14.4, 14.5
    """
    try:
        logger.info(f"Monitoring patterns for user {user_id}")
        
        result = pattern_detection_service.monitor_user_patterns(
            db=self.db,
            user_id=user_id,
            send_alerts=send_alerts
        )
        
        if result['patterns_detected'] > 0:
            logger.warning(
                f"Detected {result['patterns_detected']} concerning patterns for user {user_id}"
            )
            if send_alerts:
                logger.info(f"Sent {result['alerts_sent']} alerts for user {user_id}")
        else:
            logger.info(f"No concerning patterns detected for user {user_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error monitoring patterns for user {user_id}: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='patterns.monitor_all_users',
    max_retries=1
)
def monitor_all_users_task(
    self,
    send_alerts: bool = True
):
    """
    Monitor patterns for all active users.
    
    Args:
        send_alerts: Whether to send alerts for detected patterns
        
    Requirements: 14.4, 14.5
    """
    try:
        logger.info("Starting pattern monitoring for all users")
        
        # Get all active users (active in last 30 days)
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        users = self.db.query(User).filter(
            User.last_active >= cutoff_date
        ).all()
        
        logger.info(f"Monitoring {len(users)} active users")
        
        results = []
        total_patterns = 0
        total_alerts = 0
        
        for user in users:
            try:
                result = pattern_detection_service.monitor_user_patterns(
                    db=self.db,
                    user_id=str(user.id),
                    send_alerts=send_alerts
                )
                
                results.append({
                    'user_id': str(user.id),
                    'patterns_detected': result['patterns_detected'],
                    'alerts_sent': result['alerts_sent']
                })
                
                total_patterns += result['patterns_detected']
                total_alerts += result['alerts_sent']
                
            except Exception as e:
                logger.error(f"Error monitoring user {user.id}: {str(e)}")
                results.append({
                    'user_id': str(user.id),
                    'error': str(e)
                })
        
        logger.info(
            f"Pattern monitoring completed: {len(users)} users, "
            f"{total_patterns} patterns detected, {total_alerts} alerts sent"
        )
        
        return {
            'status': 'completed',
            'users_monitored': len(users),
            'total_patterns_detected': total_patterns,
            'total_alerts_sent': total_alerts,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in monitor_all_users_task: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='patterns.check_medication_adherence',
    max_retries=2
)
def check_medication_adherence_task(
    self,
    user_id: str
):
    """
    Check medication adherence for a specific user.
    
    Args:
        user_id: User ID to check
        
    Requirements: 14.4
    """
    try:
        logger.info(f"Checking medication adherence for user {user_id}")
        
        pattern = pattern_detection_service.check_medication_adherence(
            db=self.db,
            user_id=user_id
        )
        
        if pattern:
            logger.warning(
                f"Low medication adherence detected for user {user_id}: "
                f"{pattern['adherence_rate']}%"
            )
            
            # Send alert
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                pattern_detection_service.send_pattern_alerts(
                    db=self.db,
                    user_id=user_id,
                    patterns=[pattern]
                )
        
        return {
            'user_id': user_id,
            'pattern_detected': pattern is not None,
            'pattern': pattern
        }
        
    except Exception as e:
        logger.error(f"Error checking medication adherence for {user_id}: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='patterns.check_inactivity',
    max_retries=2
)
def check_inactivity_task(
    self,
    user_id: str
):
    """
    Check for app inactivity for a specific user.
    
    Args:
        user_id: User ID to check
        
    Requirements: 14.4
    """
    try:
        logger.info(f"Checking inactivity for user {user_id}")
        
        pattern = pattern_detection_service.check_app_inactivity(
            db=self.db,
            user_id=user_id
        )
        
        if pattern:
            logger.warning(
                f"Prolonged inactivity detected for user {user_id}: "
                f"{pattern['hours']} hours"
            )
            
            # Send alert
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                pattern_detection_service.send_pattern_alerts(
                    db=self.db,
                    user_id=user_id,
                    patterns=[pattern]
                )
        
        return {
            'user_id': user_id,
            'pattern_detected': pattern is not None,
            'pattern': pattern
        }
        
    except Exception as e:
        logger.error(f"Error checking inactivity for {user_id}: {str(e)}")
        raise self.retry(exc=e)


# Periodic task configuration
# These would be configured in celery beat schedule
@celery_app.task(name='patterns.scheduled_monitoring')
def scheduled_monitoring_task():
    """
    Scheduled task to monitor all users periodically.
    This should be configured in Celery Beat to run every few hours.
    
    Requirements: 14.5
    """
    try:
        logger.info("Running scheduled pattern monitoring")
        
        # Trigger monitoring for all users
        result = monitor_all_users_task.delay(send_alerts=True)
        
        return {
            'status': 'scheduled',
            'task_id': result.id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in scheduled monitoring: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }
