"""
Daily routine model for tracking user routines and activities.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Time, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.models.base import BaseModel
from datetime import datetime


class DailyRoutine(BaseModel):
    """
    Daily routine model for storing user's daily routine items.
    """
    __tablename__ = "daily_routines"
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Routine details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_time = Column(Time, nullable=True)  # Time of day (e.g., 08:00)
    time_of_day = Column(String(50), nullable=True)  # morning, afternoon, evening
    
    # Days of week (0=Monday, 6=Sunday)
    days_of_week = Column(ARRAY(Integer), default=list, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)  # For sorting
    
    # Tracking
    reminder_enabled = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<DailyRoutine(id={self.id}, title={self.title}, user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert routine to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "time_of_day": self.time_of_day,
            "days_of_week": self.days_of_week,
            "is_active": self.is_active,
            "order_index": self.order_index,
            "reminder_enabled": self.reminder_enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class RoutineCompletion(BaseModel):
    """
    Track completion of daily routine items.
    """
    __tablename__ = "routine_completions"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    routine_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Completion details
    completion_date = Column(DateTime(timezone=True), nullable=False, index=True)
    completed = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<RoutineCompletion(routine_id={self.routine_id}, date={self.completion_date}, completed={self.completed})>"
    
    def to_dict(self):
        """Convert completion to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "routine_id": str(self.routine_id),
            "completion_date": self.completion_date.isoformat(),
            "completed": self.completed,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
