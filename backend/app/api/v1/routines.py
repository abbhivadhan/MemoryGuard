"""
API endpoints for daily routine management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import datetime, date, timedelta
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.routine import DailyRoutine, RoutineCompletion
from app.schemas.routine import (
    DailyRoutineCreate,
    DailyRoutineUpdate,
    DailyRoutineResponse,
    RoutineCompletionCreate,
    RoutineCompletionResponse,
    DailyRoutineWithCompletion,
    RoutineListResponse
)

router = APIRouter()


@router.post("/", response_model=DailyRoutineResponse, status_code=status.HTTP_201_CREATED)
async def create_routine(
    routine_data: DailyRoutineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new daily routine for the current user.
    """
    routine = DailyRoutine(
        user_id=current_user.id,
        title=routine_data.title,
        description=routine_data.description,
        scheduled_time=routine_data.scheduled_time,
        time_of_day=routine_data.time_of_day,
        days_of_week=routine_data.days_of_week,
        reminder_enabled=routine_data.reminder_enabled,
        order_index=routine_data.order_index
    )
    
    db.add(routine)
    db.commit()
    db.refresh(routine)
    
    return routine


@router.get("/", response_model=RoutineListResponse)
async def get_routines(
    is_active: Optional[bool] = Query(None),
    time_of_day: Optional[str] = Query(None),
    include_today: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all routines for the current user with optional filters.
    If include_today is True, includes today's completion status.
    """
    query = db.query(DailyRoutine).filter(DailyRoutine.user_id == current_user.id)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(DailyRoutine.is_active == is_active)
    
    if time_of_day:
        query = query.filter(DailyRoutine.time_of_day == time_of_day)
    
    # Order by order_index
    query = query.order_by(DailyRoutine.order_index.asc())
    
    routines = query.all()
    
    # Get today's completions if requested
    routines_with_completion = []
    if include_today:
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        
        for routine in routines:
            completion = db.query(RoutineCompletion).filter(
                and_(
                    RoutineCompletion.routine_id == routine.id,
                    RoutineCompletion.user_id == current_user.id,
                    RoutineCompletion.completion_date >= today_start,
                    RoutineCompletion.completion_date <= today_end
                )
            ).first()
            
            routines_with_completion.append(
                DailyRoutineWithCompletion(
                    routine=routine,
                    completion=completion
                )
            )
    else:
        routines_with_completion = [
            DailyRoutineWithCompletion(routine=r, completion=None)
            for r in routines
        ]
    
    return RoutineListResponse(
        routines=routines_with_completion,
        total=len(routines)
    )


@router.get("/today", response_model=RoutineListResponse)
async def get_today_routines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's routines based on day of week.
    """
    today_weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
    
    routines = db.query(DailyRoutine).filter(
        and_(
            DailyRoutine.user_id == current_user.id,
            DailyRoutine.is_active == True,
            DailyRoutine.days_of_week.contains([today_weekday])
        )
    ).order_by(DailyRoutine.order_index.asc()).all()
    
    # Get today's completions
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    routines_with_completion = []
    for routine in routines:
        completion = db.query(RoutineCompletion).filter(
            and_(
                RoutineCompletion.routine_id == routine.id,
                RoutineCompletion.user_id == current_user.id,
                RoutineCompletion.completion_date >= today_start,
                RoutineCompletion.completion_date <= today_end
            )
        ).first()
        
        routines_with_completion.append(
            DailyRoutineWithCompletion(
                routine=routine,
                completion=completion
            )
        )
    
    return RoutineListResponse(
        routines=routines_with_completion,
        total=len(routines)
    )


@router.get("/{routine_id}", response_model=DailyRoutineResponse)
async def get_routine(
    routine_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific routine by ID.
    """
    routine = db.query(DailyRoutine).filter(
        and_(
            DailyRoutine.id == routine_id,
            DailyRoutine.user_id == current_user.id
        )
    ).first()
    
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )
    
    return routine


@router.put("/{routine_id}", response_model=DailyRoutineResponse)
async def update_routine(
    routine_id: UUID,
    routine_data: DailyRoutineUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a routine.
    """
    routine = db.query(DailyRoutine).filter(
        and_(
            DailyRoutine.id == routine_id,
            DailyRoutine.user_id == current_user.id
        )
    ).first()
    
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )
    
    # Update fields
    update_data = routine_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(routine, field, value)
    
    db.commit()
    db.refresh(routine)
    
    return routine


@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routine(
    routine_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a routine.
    """
    routine = db.query(DailyRoutine).filter(
        and_(
            DailyRoutine.id == routine_id,
            DailyRoutine.user_id == current_user.id
        )
    ).first()
    
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )
    
    db.delete(routine)
    db.commit()
    
    return None


# Completion endpoints
@router.post("/completions", response_model=RoutineCompletionResponse, status_code=status.HTTP_201_CREATED)
async def create_completion(
    completion_data: RoutineCompletionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update a routine completion.
    """
    # Verify routine belongs to user
    routine = db.query(DailyRoutine).filter(
        and_(
            DailyRoutine.id == completion_data.routine_id,
            DailyRoutine.user_id == current_user.id
        )
    ).first()
    
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )
    
    # Check if completion already exists for this date
    completion_date_start = datetime.combine(
        completion_data.completion_date.date(),
        datetime.min.time()
    )
    completion_date_end = datetime.combine(
        completion_data.completion_date.date(),
        datetime.max.time()
    )
    
    existing_completion = db.query(RoutineCompletion).filter(
        and_(
            RoutineCompletion.routine_id == completion_data.routine_id,
            RoutineCompletion.user_id == current_user.id,
            RoutineCompletion.completion_date >= completion_date_start,
            RoutineCompletion.completion_date <= completion_date_end
        )
    ).first()
    
    if existing_completion:
        # Update existing
        existing_completion.completed = completion_data.completed
        existing_completion.notes = completion_data.notes
        existing_completion.completion_date = completion_data.completion_date
        db.commit()
        db.refresh(existing_completion)
        return existing_completion
    else:
        # Create new
        completion = RoutineCompletion(
            user_id=current_user.id,
            routine_id=completion_data.routine_id,
            completion_date=completion_data.completion_date,
            completed=completion_data.completed,
            notes=completion_data.notes
        )
        
        db.add(completion)
        db.commit()
        db.refresh(completion)
        
        return completion


@router.get("/completions/stats")
async def get_completion_stats(
    days: int = Query(default=7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get completion statistics for the last N days.
    """
    start_date = datetime.now() - timedelta(days=days)
    
    completions = db.query(RoutineCompletion).filter(
        and_(
            RoutineCompletion.user_id == current_user.id,
            RoutineCompletion.completion_date >= start_date
        )
    ).all()
    
    total_completions = len(completions)
    completed_count = sum(1 for c in completions if c.completed)
    completion_rate = (completed_count / total_completions * 100) if total_completions > 0 else 0
    
    return {
        "total_completions": total_completions,
        "completed_count": completed_count,
        "skipped_count": total_completions - completed_count,
        "completion_rate": round(completion_rate, 2),
        "days": days
    }
