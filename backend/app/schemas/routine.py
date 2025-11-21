"""
Pydantic schemas for daily routine endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional
from uuid import UUID


class DailyRoutineCreate(BaseModel):
    """Schema for creating a daily routine"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    time_of_day: Optional[str] = Field(None, pattern="^(morning|afternoon|evening)$")
    days_of_week: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])
    reminder_enabled: bool = True
    order_index: int = 0


class DailyRoutineUpdate(BaseModel):
    """Schema for updating a daily routine"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    time_of_day: Optional[str] = Field(None, pattern="^(morning|afternoon|evening)$")
    days_of_week: Optional[list[int]] = None
    is_active: Optional[bool] = None
    reminder_enabled: Optional[bool] = None
    order_index: Optional[int] = None


class DailyRoutineResponse(BaseModel):
    """Schema for daily routine response"""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    scheduled_time: Optional[time]
    time_of_day: Optional[str]
    days_of_week: list[int]
    is_active: bool
    order_index: int
    reminder_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoutineCompletionCreate(BaseModel):
    """Schema for creating a routine completion"""
    routine_id: UUID
    completion_date: datetime
    completed: bool
    notes: Optional[str] = None


class RoutineCompletionResponse(BaseModel):
    """Schema for routine completion response"""
    id: UUID
    user_id: UUID
    routine_id: UUID
    completion_date: datetime
    completed: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyRoutineWithCompletion(BaseModel):
    """Schema for routine with today's completion status"""
    routine: DailyRoutineResponse
    completion: Optional[RoutineCompletionResponse]


class RoutineListResponse(BaseModel):
    """Schema for list of routines"""
    routines: list[DailyRoutineWithCompletion]
    total: int
