"""
Pattern detection service for monitoring user health patterns and detecting concerning trends.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from app.models.user import User
from app.models.medication import Medication
from app.models.routine import DailyRoutine, RoutineCompletion
from app.models.assessment import Assessment
from app.models.emergency_contact import EmergencyContact, CaregiverRelationship
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class PatternDetectionService:
    """
    Service for detecting concerning patterns in user behavior and health metrics.
    
    Requirements: 14.4, 14.5
    """
    
    # Thresholds for pattern detection
    MEDICATION_ADHERENCE_THRESHOLD = 0.80  # 80%
    MEDICATION_MONITORING_DAYS = 7
    
    ROUTINE_MISSED_THRESHOLD = 3
    ROUTINE_MONITORING_DAYS = 7
    
    COGNITIVE_DECLINE_THRESHOLD = 0.20  # 20% decline
    
    INACTIVITY_THRESHOLD_HOURS = 48
    
    def check_medication_adherence(
        self,
        db: Session,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check medication adherence patterns.
        
        Returns pattern data if adherence is below threshold, None otherwise.
        """
        try:
            # Get active medications
            medications = db.query(Medication).filter(
                Medication.user_id == user_id,
                Medication.active == True
            ).all()
            
            if not medications:
                return None
            
            # Calculate adherence over monitoring period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=self.MEDICATION_MONITORING_DAYS)
            
            total_scheduled = 0
            total_taken = 0
            
            for medication in medications:
                # Count scheduled doses in the period
                scheduled_doses = [
                    log for log in medication.adherence_log
                    if start_date <= datetime.fromisoformat(log['scheduled_time']) <= end_date
                ]
                
                total_scheduled += len(scheduled_doses)
                total_taken += sum(1 for log in scheduled_doses if not log.get('skipped', False))
            
            if total_scheduled == 0:
                return None
            
            adherence_rate = total_taken / total_scheduled
            
            if adherence_rate < self.MEDICATION_ADHERENCE_THRESHOLD:
                return {
                    'pattern_type': 'low_medication_adherence',
                    'adherence_rate': round(adherence_rate * 100, 1),
                    'days': self.MEDICATION_MONITORING_DAYS,
                    'total_scheduled': total_scheduled,
                    'total_taken': total_taken,
                    'severity': 'high' if adherence_rate < 0.60 else 'medium'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking medication adherence: {str(e)}")
            return None
    
    def check_routine_completion(
        self,
        db: Session,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check daily routine completion patterns.
        
        Returns pattern data if too many routines are missed, None otherwise.
        """
        try:
            # Get active routines
            routines = db.query(DailyRoutine).filter(
                DailyRoutine.user_id == user_id,
                DailyRoutine.is_active == True
            ).all()
            
            if not routines:
                return None
            
            # Check completions over monitoring period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=self.ROUTINE_MONITORING_DAYS)
            
            # Count missed routine items
            missed_count = 0
            total_items = 0
            
            for routine in routines:
                # Get completions in the period
                completions = db.query(RoutineCompletion).filter(
                    RoutineCompletion.routine_id == routine.id,
                    RoutineCompletion.completion_date >= start_date,
                    RoutineCompletion.completion_date <= end_date
                ).all()
                
                # Count expected completions based on days_of_week
                expected_days = len(routine.days_of_week) if routine.days_of_week else 7
                expected_completions = expected_days  # Simplified: one per scheduled day
                
                total_items += expected_completions
                completed_count = sum(1 for c in completions if c.completed)
                missed_count += (expected_completions - completed_count)
            
            if total_items == 0:
                return None
            
            if missed_count >= self.ROUTINE_MISSED_THRESHOLD:
                return {
                    'pattern_type': 'missed_routines',
                    'missed_count': missed_count,
                    'total_items': total_items,
                    'days': self.ROUTINE_MONITORING_DAYS,
                    'severity': 'high' if missed_count > 5 else 'medium'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking routine completion: {str(e)}")
            return None
    
    def check_cognitive_decline(
        self,
        db: Session,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check for cognitive test score declines.
        
        Returns pattern data if significant decline detected, None otherwise.
        """
        try:
            # Get recent assessments
            assessments = db.query(Assessment).filter(
                Assessment.user_id == user_id
            ).order_by(desc(Assessment.completed_at)).limit(10).all()
            
            if len(assessments) < 2:
                return None
            
            # Compare most recent to previous
            latest = assessments[0]
            previous = assessments[1]
            
            # Calculate percentage change
            if previous.score == 0:
                return None
            
            score_change = (latest.score - previous.score) / previous.score
            
            if score_change < -self.COGNITIVE_DECLINE_THRESHOLD:
                return {
                    'pattern_type': 'cognitive_decline',
                    'decline_percentage': round(abs(score_change) * 100, 1),
                    'latest_score': latest.score,
                    'previous_score': previous.score,
                    'assessment_type': latest.type,
                    'severity': 'high' if score_change < -0.30 else 'medium'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking cognitive decline: {str(e)}")
            return None
    
    def check_app_inactivity(
        self,
        db: Session,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check for prolonged app inactivity.
        
        Returns pattern data if user has been inactive too long, None otherwise.
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.last_active:
                return None
            
            # Calculate hours since last activity
            hours_inactive = (datetime.utcnow() - user.last_active).total_seconds() / 3600
            
            if hours_inactive >= self.INACTIVITY_THRESHOLD_HOURS:
                return {
                    'pattern_type': 'inactivity',
                    'hours': round(hours_inactive, 1),
                    'last_active': user.last_active.isoformat(),
                    'severity': 'high' if hours_inactive > 72 else 'medium'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking app inactivity: {str(e)}")
            return None
    
    def detect_all_patterns(
        self,
        db: Session,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Run all pattern detection checks for a user.
        
        Returns list of detected patterns.
        """
        patterns = []
        
        # Check medication adherence
        med_pattern = self.check_medication_adherence(db, user_id)
        if med_pattern:
            patterns.append(med_pattern)
        
        # Check routine completion
        routine_pattern = self.check_routine_completion(db, user_id)
        if routine_pattern:
            patterns.append(routine_pattern)
        
        # Check cognitive decline
        cognitive_pattern = self.check_cognitive_decline(db, user_id)
        if cognitive_pattern:
            patterns.append(cognitive_pattern)
        
        # Check app inactivity
        inactivity_pattern = self.check_app_inactivity(db, user_id)
        if inactivity_pattern:
            patterns.append(inactivity_pattern)
        
        return patterns
    
    def send_pattern_alerts(
        self,
        db: Session,
        user_id: str,
        patterns: List[Dict[str, Any]]
    ) -> int:
        """
        Send alerts to caregivers for detected patterns.
        
        Returns number of alerts sent.
        """
        if not patterns:
            return 0
        
        try:
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return 0
            
            # Get caregivers who can receive alerts
            caregiver_relationships = db.query(CaregiverRelationship).filter(
                CaregiverRelationship.patient_id == user_id,
                CaregiverRelationship.active == True,
                CaregiverRelationship.approved == True,
                CaregiverRelationship.can_receive_alerts == True
            ).all()
            
            # Get emergency contacts
            emergency_contacts = db.query(EmergencyContact).filter(
                EmergencyContact.user_id == user_id,
                EmergencyContact.active == True
            ).order_by(EmergencyContact.priority).all()
            
            alerts_sent = 0
            
            # Send alerts for each pattern
            for pattern in patterns:
                # Send to caregivers
                for relationship in caregiver_relationships:
                    caregiver = db.query(User).filter(
                        User.id == relationship.caregiver_id
                    ).first()
                    
                    if caregiver:
                        # Create a contact-like object for the notification service
                        contact = type('obj', (object,), {
                            'name': caregiver.name,
                            'phone': caregiver.email,  # Using email as phone for now
                            'email': caregiver.email
                        })()
                        
                        notification_service.send_pattern_alert(
                            contact=contact,
                            user=user,
                            pattern_type=pattern['pattern_type'],
                            details=pattern
                        )
                        alerts_sent += 1
                
                # Send to emergency contacts for high severity patterns
                if pattern.get('severity') == 'high':
                    for contact in emergency_contacts[:2]:  # Top 2 priority contacts
                        notification_service.send_pattern_alert(
                            contact=contact,
                            user=user,
                            pattern_type=pattern['pattern_type'],
                            details=pattern
                        )
                        alerts_sent += 1
            
            return alerts_sent
            
        except Exception as e:
            logger.error(f"Error sending pattern alerts: {str(e)}")
            return 0
    
    def monitor_user_patterns(
        self,
        db: Session,
        user_id: str,
        send_alerts: bool = True
    ) -> Dict[str, Any]:
        """
        Monitor all patterns for a user and optionally send alerts.
        
        Returns summary of detected patterns and alerts sent.
        """
        patterns = self.detect_all_patterns(db, user_id)
        
        alerts_sent = 0
        if send_alerts and patterns:
            alerts_sent = self.send_pattern_alerts(db, user_id, patterns)
        
        return {
            'user_id': user_id,
            'patterns_detected': len(patterns),
            'patterns': patterns,
            'alerts_sent': alerts_sent,
            'checked_at': datetime.utcnow().isoformat()
        }


# Singleton instance
pattern_detection_service = PatternDetectionService()
