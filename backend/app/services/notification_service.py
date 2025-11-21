"""
Notification service for sending alerts and notifications.
"""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications via various channels.
    In a production environment, this would integrate with:
    - Twilio for SMS
    - SendGrid for email
    - Firebase Cloud Messaging for push notifications
    
    Requirements: 14.2, 14.5
    """
    
    def send_emergency_notification(
        self,
        contact: Any,
        user: Any,
        alert: Any,
        location: Optional[Dict[str, Any]] = None,
        medical_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send emergency notification to a contact.
        
        Args:
            contact: Emergency contact object
            user: User who triggered the alert
            alert: Emergency alert object
            location: Location data (latitude, longitude, address)
            medical_info: Medical information
            
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Build notification message
            message = self._build_emergency_message(
                user_name=user.name,
                location=location,
                medical_info=medical_info
            )
            
            # Log the notification (in production, send via SMS/email/push)
            logger.info(f"Emergency notification to {contact.name} ({contact.phone})")
            logger.info(f"Message: {message}")
            
            # In production, implement actual notification sending:
            # - SMS via Twilio
            # - Email via SendGrid
            # - Push notification via FCM
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send emergency notification: {str(e)}")
            return False
    
    def send_pattern_alert(
        self,
        contact: Any,
        user: Any,
        pattern_type: str,
        details: Dict[str, Any]
    ) -> bool:
        """
        Send alert about concerning patterns detected.
        
        Args:
            contact: Contact to notify
            user: User being monitored
            pattern_type: Type of pattern detected
            details: Additional details about the pattern
            
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            message = self._build_pattern_alert_message(
                user_name=user.name,
                pattern_type=pattern_type,
                details=details
            )
            
            logger.info(f"Pattern alert to {contact.name} ({contact.phone})")
            logger.info(f"Message: {message}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send pattern alert: {str(e)}")
            return False
    
    def _build_emergency_message(
        self,
        user_name: str,
        location: Optional[Dict[str, Any]] = None,
        medical_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build emergency notification message."""
        message = f"🚨 EMERGENCY ALERT 🚨\n\n"
        message += f"{user_name} has activated an emergency alert.\n\n"
        
        if location:
            message += "📍 Location:\n"
            if location.get('address'):
                message += f"{location['address']}\n"
            message += f"Coordinates: {location.get('latitude')}, {location.get('longitude')}\n"
            message += f"Google Maps: https://www.google.com/maps?q={location.get('latitude')},{location.get('longitude')}\n\n"
        
        if medical_info:
            message += "🏥 Medical Information:\n"
            if medical_info.get('medications'):
                message += f"Medications: {', '.join(medical_info['medications'])}\n"
            if medical_info.get('allergies'):
                message += f"Allergies: {', '.join(medical_info['allergies'])}\n"
            if medical_info.get('conditions'):
                message += f"Conditions: {', '.join(medical_info['conditions'])}\n"
            if medical_info.get('blood_type'):
                message += f"Blood Type: {medical_info['blood_type']}\n"
            if medical_info.get('emergency_notes'):
                message += f"Notes: {medical_info['emergency_notes']}\n"
        
        message += "\nPlease check on them immediately or contact emergency services if needed."
        
        return message
    
    def _build_pattern_alert_message(
        self,
        user_name: str,
        pattern_type: str,
        details: Dict[str, Any]
    ) -> str:
        """Build pattern alert message."""
        message = f"⚠️ HEALTH ALERT ⚠️\n\n"
        message += f"Concerning pattern detected for {user_name}.\n\n"
        
        pattern_messages = {
            'low_medication_adherence': f"Medication adherence has dropped to {details.get('adherence_rate', 0)}% over the past {details.get('days', 7)} days.",
            'missed_routines': f"Missed {details.get('missed_count', 0)} daily routine items in the past {details.get('days', 7)} days.",
            'cognitive_decline': f"Cognitive test scores have declined by {details.get('decline_percentage', 0)}% since last assessment.",
            'inactivity': f"No app activity detected for {details.get('hours', 0)} hours."
        }
        
        message += pattern_messages.get(pattern_type, f"Pattern type: {pattern_type}")
        message += "\n\nPlease check in with them to ensure they are okay."
        
        return message


# Singleton instance
notification_service = NotificationService()
