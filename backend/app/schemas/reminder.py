"""
Pydantic schemas for reminder endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ReminderCreate(BaseModel):
    """Schema for creating a new reminder"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    reminder_type: str = Field(..., pattern="^(medication|appointment|routine|custom)$")
    scheduled_time: datetime
    frequency: str = Field(..., pattern="^(once|daily|weekly|monthly|custom)$")
    send_notification: bool = True
    related_entity_id: Optional[UUID] = None


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    frequency: Optional[str] = Field(None, pattern="^(once|daily|weekly|monthly|custom)$")
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None
    send_notification: Optional[bool] = None


class ReminderResponse(BaseModel):
    """Schema for reminder response"""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    reminder_type: str
    scheduled_time: datetime
    frequency: str
    is_active: bool
    is_completed: bool
    completed_at: Optional[datetime]
    send_notification: bool
    notification_sent: bool
    related_entity_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    """Schema for list of reminders"""
    reminders: list[ReminderResponse]
    total: int
