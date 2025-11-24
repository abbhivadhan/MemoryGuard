"""
API endpoints for reminder management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.reminder import Reminder, ReminderType, ReminderFrequency
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse
)

router = APIRouter()


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new reminder for the current user.
    """
    try:
        # Convert to lowercase to match database enum values
        reminder = Reminder(
            user_id=current_user.id,
            title=reminder_data.title,
            description=reminder_data.description,
            reminder_type=reminder_data.reminder_type.lower(),  # Convert to lowercase
            scheduled_time=reminder_data.scheduled_time,
            frequency=reminder_data.frequency.lower(),  # Convert to lowercase
            send_notification=reminder_data.send_notification,
            related_entity_id=reminder_data.related_entity_id
        )
        
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        
        return reminder
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid enum value: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating reminder: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reminder: {str(e)}"
        )


@router.get("/", response_model=ReminderListResponse)
async def get_reminders(
    reminder_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_completed: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reminders for the current user with optional filters.
    """
    query = db.query(Reminder).filter(Reminder.user_id == current_user.id)
    
    # Apply filters
    if reminder_type:
        query = query.filter(Reminder.reminder_type == reminder_type)  # String comparison, SQLAlchemy handles enum
    
    if is_active is not None:
        query = query.filter(Reminder.is_active == is_active)
    
    if is_completed is not None:
        query = query.filter(Reminder.is_completed == is_completed)
    
    if start_date:
        query = query.filter(Reminder.scheduled_time >= start_date)
    
    if end_date:
        query = query.filter(Reminder.scheduled_time <= end_date)
    
    # Order by scheduled time
    query = query.order_by(Reminder.scheduled_time.asc())
    
    reminders = query.all()
    
    return ReminderListResponse(
        reminders=reminders,
        total=len(reminders)
    )


@router.get("/upcoming", response_model=ReminderListResponse)
async def get_upcoming_reminders(
    hours: int = Query(default=24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get upcoming reminders for the next N hours.
    """
    now = datetime.utcnow()
    end_time = now + timedelta(hours=hours)
    
    reminders = db.query(Reminder).filter(
        and_(
            Reminder.user_id == current_user.id,
            Reminder.is_active == True,
            Reminder.is_completed == False,
            Reminder.scheduled_time >= now,
            Reminder.scheduled_time <= end_time
        )
    ).order_by(Reminder.scheduled_time.asc()).all()
    
    return ReminderListResponse(
        reminders=reminders,
        total=len(reminders)
    )


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific reminder by ID.
    """
    reminder = db.query(Reminder).filter(
        and_(
            Reminder.id == reminder_id,
            Reminder.user_id == current_user.id
        )
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return reminder


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    reminder_data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a reminder.
    """
    reminder = db.query(Reminder).filter(
        and_(
            Reminder.id == reminder_id,
            Reminder.user_id == current_user.id
        )
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # Update fields
    update_data = reminder_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "frequency" and value:
            value = ReminderFrequency(value)
        setattr(reminder, field, value)
    
    # If marking as completed, set completed_at
    if reminder_data.is_completed and not reminder.completed_at:
        reminder.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(reminder)
    
    return reminder


@router.post("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a reminder as completed.
    """
    reminder = db.query(Reminder).filter(
        and_(
            Reminder.id == reminder_id,
            Reminder.user_id == current_user.id
        )
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    reminder.is_completed = True
    reminder.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(reminder)
    
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a reminder.
    """
    reminder = db.query(Reminder).filter(
        and_(
            Reminder.id == reminder_id,
            Reminder.user_id == current_user.id
        )
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    db.delete(reminder)
    db.commit()
    
    return None
