"""
Reminder model for memory assistant features.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from datetime import datetime
import enum


class ReminderType(str, enum.Enum):
    """Types of reminders"""
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    ROUTINE = "routine"
    CUSTOM = "custom"


class ReminderFrequency(str, enum.Enum):
    """Reminder frequency options"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Reminder(BaseModel):
    """
    Reminder model for storing user reminders.
    Supports medication, appointment, routine, and custom reminders.
    """
    __tablename__ = "reminders"
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Reminder details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reminder_type = Column(SQLEnum(ReminderType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=ReminderType.CUSTOM)
    
    # Scheduling
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    frequency = Column(SQLEnum(ReminderFrequency, values_callable=lambda x: [e.value for e in x]), nullable=False, default=ReminderFrequency.ONCE)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notification settings
    send_notification = Column(Boolean, default=True, nullable=False)
    notification_sent = Column(Boolean, default=False, nullable=False)
    
    # Optional: Link to related entities (medication_id, etc.)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    def __repr__(self):
        return f"<Reminder(id={self.id}, title={self.title}, type={self.reminder_type})>"
    
    def to_dict(self):
        """Convert reminder to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "reminder_type": self.reminder_type.value,
            "scheduled_time": self.scheduled_time.isoformat(),
            "frequency": self.frequency.value,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "send_notification": self.send_notification,
            "notification_sent": self.notification_sent,
            "related_entity_id": str(self.related_entity_id) if self.related_entity_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
