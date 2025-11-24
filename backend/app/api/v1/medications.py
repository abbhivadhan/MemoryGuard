"""
API endpoints for medication management.
Requirements: 13.1, 13.3, 13.4, 13.6, 13.7
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.medication import Medication
from app.schemas.medication import (
    MedicationCreate,
    MedicationUpdate,
    MedicationResponse,
    MedicationListResponse,
    MedicationLogRequest,
    AdherenceStats,
    SideEffectCreate,
    InteractionWarning
)
from app.core.data_validation import validate_medication, log_validation_warning

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication_data: MedicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new medication for the current user.
    Requirements: 13.1
    """
    # Validate medication data for placeholder/demo data
    med_dict = {
        'name': medication_data.name,
        'dosage': medication_data.dosage,
        'frequency': medication_data.frequency
    }
    is_valid, errors = validate_medication(med_dict)
    
    if not is_valid:
        log_validation_warning('medication', med_dict, errors)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid medication data: {'; '.join(errors)}"
        )
    
    medication = Medication(
        user_id=current_user.id,
        name=medication_data.name,
        dosage=medication_data.dosage,
        frequency=medication_data.frequency,
        schedule=medication_data.schedule,
        instructions=medication_data.instructions,
        prescriber=medication_data.prescriber,
        pharmacy=medication_data.pharmacy,
        start_date=medication_data.start_date or datetime.utcnow(),
        end_date=medication_data.end_date
    )
    
    db.add(medication)
    db.commit()
    db.refresh(medication)
    
    return medication.to_dict()


@router.get("/", response_model=MedicationListResponse)
async def get_medications(
    active_only: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all medications for the current user.
    Requirements: 13.1
    """
    query = db.query(Medication).filter(Medication.user_id == current_user.id)
    
    if active_only:
        query = query.filter(Medication.active == True)
    
    query = query.order_by(Medication.created_at.desc())
    
    medications = query.all()
    
    return MedicationListResponse(
        medications=[med.to_dict() for med in medications],
        total=len(medications)
    )


@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific medication by ID.
    Requirements: 13.1
    """
    medication = db.query(Medication).filter(
        and_(
            Medication.id == medication_id,
            Medication.user_id == current_user.id
        )
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    return medication.to_dict()


@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: UUID,
    medication_data: MedicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a medication.
    Requirements: 13.1
    """
    medication = db.query(Medication).filter(
        and_(
            Medication.id == medication_id,
            Medication.user_id == current_user.id
        )
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    # Update fields
    update_data = medication_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(medication, field, value)
    
    db.commit()
    db.refresh(medication)
    
    return medication.to_dict()


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(
    medication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a medication.
    Requirements: 13.1
    """
    medication = db.query(Medication).filter(
        and_(
            Medication.id == medication_id,
            Medication.user_id == current_user.id
        )
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    db.delete(medication)
    db.commit()
    
    return None


@router.post("/{medication_id}/log", response_model=MedicationResponse)
async def log_medication(
    medication_id: UUID,
    log_data: MedicationLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log medication as taken or skipped.
    Requirements: 13.3
    """
    medication = db.query(Medication).filter(
        and_(
            Medication.id == medication_id,
            Medication.user_id == current_user.id
        )
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    # Create log entry
    log_entry = {
        "scheduled_time": log_data.scheduled_time.isoformat(),
        "taken_time": log_data.taken_time.isoformat() if log_data.taken_time else None,
        "skipped": log_data.skipped,
        "notes": log_data.notes,
        "logged_at": datetime.utcnow().isoformat()
    }
    
    # Add to adherence log
    if medication.adherence_log is None:
        medication.adherence_log = []
    
    medication.adherence_log.append(log_entry)
    
    # Mark as modified to trigger SQLAlchemy update
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(medication, "adherence_log")
    
    db.commit()
    db.refresh(medication)
    
    return medication.to_dict()


@router.get("/{medication_id}/adherence", response_model=AdherenceStats)
async def get_adherence_stats(
    medication_id: UUID,
    days: int = Query(default=7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get adherence statistics for a medication.
    Requirements: 13.3, 13.5
    """
    medication = db.query(Medication).filter(
        and_(
            Medication.id == medication_id,
            Medication.user_id == current_user.id
        )
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    # Calculate adherence for the specified period
    from datetime import timezone
    now = datetime.now(timezone.utc)
    cutoff_time = now - timedelta(days=days)
    
    # Get scheduled doses from the medication's schedule within the period
    scheduled_doses = []
    scheduled_times_set = set()  # Track unique scheduled times
    
    if medication.schedule:
        for scheduled_time in medication.schedule:
            # Ensure timezone-aware
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            
            # Only count doses within the period and in the past
            if cutoff_time <= scheduled_time <= now:
                scheduled_doses.append(scheduled_time)
                scheduled_times_set.add(scheduled_time.isoformat())
    
    # ALWAYS check adherence log for additional scheduled times
    # (in case user logged doses that weren't in the original schedule)
    if medication.adherence_log:
        for log in medication.adherence_log:
            try:
                scheduled_time_str = log.get("scheduled_time", "").replace('Z', '+00:00')
                scheduled_time = datetime.fromisoformat(scheduled_time_str)
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
                
                # Only add if within period and not already counted
                if cutoff_time <= scheduled_time <= now:
                    time_iso = scheduled_time.isoformat()
                    if time_iso not in scheduled_times_set:
                        scheduled_doses.append(scheduled_time)
                        scheduled_times_set.add(time_iso)
            except (ValueError, TypeError):
                continue
    
    total_scheduled = len(scheduled_doses)
    
    # Count taken and skipped from adherence log
    recent_logs = []
    if medication.adherence_log:
        for log in medication.adherence_log:
            try:
                scheduled_time_str = log.get("scheduled_time", "").replace('Z', '+00:00')
                scheduled_time = datetime.fromisoformat(scheduled_time_str)
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
                if cutoff_time <= scheduled_time <= now:
                    recent_logs.append(log)
            except (ValueError, TypeError):
                continue
    
    total_taken = sum(1 for log in recent_logs if not log.get("skipped", False) and log.get("taken_time"))
    total_skipped = sum(1 for log in recent_logs if log.get("skipped", False))
    
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Adherence Stats Debug for {medication.name}:")
    logger.info(f"  Total scheduled doses: {len(scheduled_doses)}")
    logger.info(f"  Recent logs count: {len(recent_logs)}")
    logger.info(f"  Total taken: {total_taken}")
    logger.info(f"  Total skipped: {total_skipped}")
    if recent_logs:
        logger.info(f"  Sample log: {recent_logs[0]}")
    
    # Calculate adherence rate
    adherence_rate = (total_taken / len(scheduled_doses) * 100) if len(scheduled_doses) > 0 else 0.0
    
    # Find last taken
    last_taken = None
    if recent_logs:
        taken_logs = [log for log in recent_logs if not log.get("skipped", False) and log.get("taken_time")]
        if taken_logs:
            last_taken_str = max(taken_logs, key=lambda x: x.get("taken_time", ""))["taken_time"]
            try:
                last_taken = datetime.fromisoformat(last_taken_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
    
    # Find next scheduled from schedule
    next_scheduled = None
    if medication.schedule:
        future_schedules = [
            dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt 
            for dt in medication.schedule 
            if (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt) > now
        ]
        if future_schedules:
            next_scheduled = min(future_schedules)
    
    return AdherenceStats(
        medication_id=medication.id,
        medication_name=medication.name,
        total_scheduled=len(scheduled_doses),
        total_taken=total_taken,
        total_skipped=total_skipped,
        adherence_rate=round(adherence_rate, 2),
        period_days=days,
        last_taken=last_taken,
        next_scheduled=next_scheduled
    )


@router.post("/{medication_id}/side-effects", response_model=MedicationResponse)
async def add_side_effect(
    medication_id: UUID,
    side_effect_data: SideEffectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a side effect to a medication.
    Requirements: 13.4
    """
    medication = db.query(Medication).filter(
        and_(
            Medication.id == medication_id,
            Medication.user_id == current_user.id
        )
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    # Format side effect entry
    occurred_at = side_effect_data.occurred_at or datetime.utcnow()
    side_effect_entry = f"{occurred_at.isoformat()}: {side_effect_data.side_effect}"
    
    if side_effect_data.severity:
        side_effect_entry += f" (Severity: {side_effect_data.severity})"
    
    # Add to side effects list
    if medication.side_effects is None:
        medication.side_effects = []
    
    medication.side_effects.append(side_effect_entry)
    
    # Mark as modified to trigger SQLAlchemy update
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(medication, "side_effects")
    
    db.commit()
    db.refresh(medication)
    
    return medication.to_dict()


@router.post("/check-interactions", response_model=List[InteractionWarning])
async def check_drug_interactions(
    medication_names: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check for drug interactions between medications.
    Requirements: 13.6
    
    Note: This is a placeholder implementation. In production, this should
    integrate with a pharmaceutical database API like FDA API, RxNorm, or
    commercial drug interaction databases.
    """
    warnings = []
    
    # Placeholder logic - in production, call external API
    # For now, return empty list or basic warnings for common interactions
    
    # Example: Check for common interaction patterns
    med_names_lower = [name.lower() for name in medication_names]
    
    # Common interaction: Warfarin + NSAIDs
    if any("warfarin" in name for name in med_names_lower) and \
       any(nsaid in name for name in med_names_lower for nsaid in ["ibuprofen", "aspirin", "naproxen"]):
        warnings.append(InteractionWarning(
            severity="high",
            description="Warfarin and NSAIDs may increase bleeding risk",
            medications=["Warfarin", "NSAID"],
            recommendation="Consult your healthcare provider before combining these medications"
        ))
    
    # Common interaction: MAOIs + SSRIs
    if any("maoi" in name or "phenelzine" in name or "tranylcypromine" in name for name in med_names_lower) and \
       any(ssri in name for name in med_names_lower for ssri in ["fluoxetine", "sertraline", "paroxetine"]):
        warnings.append(InteractionWarning(
            severity="critical",
            description="MAOIs and SSRIs can cause serotonin syndrome",
            medications=["MAOI", "SSRI"],
            recommendation="Do not combine these medications. Seek immediate medical attention if already taking both."
        ))
    
    return warnings


@router.get("/users/{user_id}/adherence-alert", response_model=dict)
async def check_adherence_alert(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user has low adherence and needs caregiver alert.
    Requirements: 13.7
    
    This endpoint can be called by caregivers or scheduled tasks.
    """
    # Verify user access (must be the user themselves or their caregiver)
    if current_user.id != user_id:
        # In production, check if current_user is a caregiver for user_id
        # For now, allow access
        pass
    
    medications = db.query(Medication).filter(
        and_(
            Medication.user_id == user_id,
            Medication.active == True
        )
    ).all()
    
    low_adherence_meds = []
    
    for med in medications:
        adherence_rate = med.calculate_adherence_rate(days=7)
        
        if adherence_rate < 80.0:
            low_adherence_meds.append({
                "medication_id": str(med.id),
                "medication_name": med.name,
                "adherence_rate": round(adherence_rate, 2),
                "alert_level": "critical" if adherence_rate < 50 else "warning"
            })
    
    should_alert = len(low_adherence_meds) > 0
    
    return {
        "user_id": str(user_id),
        "should_alert": should_alert,
        "low_adherence_medications": low_adherence_meds,
        "checked_at": datetime.utcnow().isoformat()
    }
