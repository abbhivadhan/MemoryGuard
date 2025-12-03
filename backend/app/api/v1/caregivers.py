"""
Caregiver API endpoints for managing caregiver relationships and access control.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.emergency_contact import CaregiverRelationship, RelationshipType
from app.models.assessment import Assessment
from app.models.medication import Medication
from app.models.routine import DailyRoutine, RoutineCompletion
from app.models.reminder import Reminder
from app.models.emergency_alert import EmergencyAlert
from pydantic import BaseModel, Field


router = APIRouter()


# Pydantic schemas
class CaregiverInviteRequest(BaseModel):
    """Request to invite a caregiver"""
    caregiver_email: str = Field(..., description="Email of the caregiver to invite")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    relationship_description: Optional[str] = Field(None, description="Additional relationship details")
    can_view_health_data: bool = Field(True, description="Permission to view health data")
    can_view_assessments: bool = Field(True, description="Permission to view assessments")
    can_view_medications: bool = Field(True, description="Permission to view medications")
    can_manage_reminders: bool = Field(True, description="Permission to manage reminders")
    can_receive_alerts: bool = Field(True, description="Permission to receive alerts")


class CaregiverPermissionsUpdate(BaseModel):
    """Update caregiver permissions"""
    can_view_health_data: Optional[bool] = None
    can_view_assessments: Optional[bool] = None
    can_view_medications: Optional[bool] = None
    can_manage_reminders: Optional[bool] = None
    can_receive_alerts: Optional[bool] = None


class CaregiverResponse(BaseModel):
    """Caregiver relationship response"""
    id: str
    patient_id: str
    caregiver_id: str
    caregiver_name: str
    caregiver_email: str
    relationship_type: str
    relationship_description: Optional[str]
    permissions: dict
    active: bool
    approved: bool
    created_at: str
    updated_at: str


class PatientSummary(BaseModel):
    """Summary of patient information for caregiver dashboard"""
    patient_id: str
    patient_name: str
    last_active: str
    cognitive_status: Optional[dict]
    medication_adherence: Optional[dict]
    daily_activities: Optional[dict]
    recent_alerts: List[dict]


@router.post("/invite", response_model=CaregiverResponse, status_code=status.HTTP_201_CREATED)
async def invite_caregiver(
    request: CaregiverInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a caregiver to access patient data.
    
    Requirements: 6.1
    """
    # Find caregiver by email
    caregiver = db.query(User).filter(User.email == request.caregiver_email).first()
    
    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver not found. They must have an account first."
        )
    
    if caregiver.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as a caregiver"
        )
    
    # Check if relationship already exists
    existing = db.query(CaregiverRelationship).filter(
        and_(
            CaregiverRelationship.patient_id == current_user.id,
            CaregiverRelationship.caregiver_id == caregiver.id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caregiver relationship already exists"
        )
    
    # Create caregiver relationship
    relationship = CaregiverRelationship(
        patient_id=current_user.id,
        caregiver_id=caregiver.id,
        relationship_type=request.relationship_type,
        relationship_description=request.relationship_description,
        can_view_health_data=request.can_view_health_data,
        can_view_assessments=request.can_view_assessments,
        can_view_medications=request.can_view_medications,
        can_manage_reminders=request.can_manage_reminders,
        can_receive_alerts=request.can_receive_alerts,
        active=True,
        approved=True  # Auto-approve for now
    )
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    
    return CaregiverResponse(
        id=str(relationship.id),
        patient_id=str(relationship.patient_id),
        caregiver_id=str(relationship.caregiver_id),
        caregiver_name=caregiver.name,
        caregiver_email=caregiver.email,
        relationship_type=relationship.relationship_type.value,
        relationship_description=relationship.relationship_description,
        permissions={
            "can_view_health_data": relationship.can_view_health_data,
            "can_view_assessments": relationship.can_view_assessments,
            "can_view_medications": relationship.can_view_medications,
            "can_manage_reminders": relationship.can_manage_reminders,
            "can_receive_alerts": relationship.can_receive_alerts
        },
        active=relationship.active,
        approved=relationship.approved,
        created_at=relationship.created_at.isoformat(),
        updated_at=relationship.updated_at.isoformat()
    )


@router.get("/my-caregivers", response_model=List[CaregiverResponse])
async def get_my_caregivers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all caregivers for the current user (patient).
    
    Requirements: 6.1
    """
    relationships = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.patient_id == current_user.id
    ).all()
    
    result = []
    for rel in relationships:
        caregiver = db.query(User).filter(User.id == rel.caregiver_id).first()
        if caregiver:
            result.append(CaregiverResponse(
                id=str(rel.id),
                patient_id=str(rel.patient_id),
                caregiver_id=str(rel.caregiver_id),
                caregiver_name=caregiver.name,
                caregiver_email=caregiver.email,
                relationship_type=rel.relationship_type.value,
                relationship_description=rel.relationship_description,
                permissions={
                    "can_view_health_data": rel.can_view_health_data,
                    "can_view_assessments": rel.can_view_assessments,
                    "can_view_medications": rel.can_view_medications,
                    "can_manage_reminders": rel.can_manage_reminders,
                    "can_receive_alerts": rel.can_receive_alerts
                },
                active=rel.active,
                approved=rel.approved,
                created_at=rel.created_at.isoformat(),
                updated_at=rel.updated_at.isoformat()
            ))
    
    return result


@router.get("/my-patients", response_model=List[PatientSummary])
async def get_my_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all patients that the current user is a caregiver for.
    
    Requirements: 6.1, 6.2, 6.3
    """
    relationships = db.query(CaregiverRelationship).filter(
        and_(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.active == True,
            CaregiverRelationship.approved == True
        )
    ).all()
    
    result = []
    for rel in relationships:
        try:
            patient = db.query(User).filter(User.id == rel.patient_id).first()
            if not patient:
                continue
            
            # Get cognitive status (latest assessment)
            cognitive_status = None
            if rel.can_view_assessments:
                latest_assessment = db.query(Assessment).filter(
                    Assessment.user_id == patient.id
                ).order_by(desc(Assessment.completed_at)).first()
                
                if latest_assessment:
                    cognitive_status = {
                        "type": latest_assessment.type,
                        "score": latest_assessment.score,
                        "max_score": latest_assessment.max_score,
                        "completed_at": latest_assessment.completed_at.isoformat()
                    }
            
            # Get medication adherence
            medication_adherence = None
            if rel.can_view_medications:
                # Calculate adherence for last 7 days
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                medications = db.query(Medication).filter(
                    and_(
                        Medication.user_id == patient.id,
                        Medication.active == True
                    )
                ).all()
                
                total_logs = 0
                taken_logs = 0
                
                for med in medications:
                    if med.adherence_log:
                        for log in med.adherence_log:
                            try:
                                scheduled_time_str = log.get("scheduled_time", "")
                                if not scheduled_time_str:
                                    continue
                                scheduled_time = datetime.fromisoformat(scheduled_time_str)
                                if scheduled_time >= seven_days_ago:
                                    total_logs += 1
                                    if not log.get("skipped", True):
                                        taken_logs += 1
                            except (ValueError, TypeError):
                                # Skip invalid datetime formats
                                continue
                
                if total_logs > 0:
                    adherence_rate = (taken_logs / total_logs * 100)
                    
                    medication_adherence = {
                        "adherence_rate": round(adherence_rate, 1),
                        "taken": taken_logs,
                        "total": total_logs,
                        "period_days": 7
                    }
            
            # Get daily activities completion
            daily_activities = None
            today = datetime.utcnow().date()
            completions = db.query(RoutineCompletion).join(DailyRoutine).filter(
                and_(
                    DailyRoutine.user_id == patient.id,
                    RoutineCompletion.completion_date >= today
                )
            ).all()
            
            if completions:
                completed = sum(1 for c in completions if c.completed)
                total = len(completions)
                
                daily_activities = {
                    "completed": completed,
                    "total": total,
                    "completion_rate": round((completed / total * 100) if total > 0 else 0, 1)
                }
            
            # Get recent alerts
            recent_alerts = []
            if rel.can_receive_alerts:
                alerts = db.query(EmergencyAlert).filter(
                    EmergencyAlert.user_id == patient.id
                ).order_by(desc(EmergencyAlert.created_at)).limit(5).all()
                
                recent_alerts = [
                    {
                        "id": str(alert.id),
                        "type": alert.alert_type,
                        "message": alert.message,
                        "severity": alert.severity,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in alerts
                ]
        
            result.append(PatientSummary(
                patient_id=str(patient.id),
                patient_name=patient.name,
                last_active=patient.last_active.isoformat() if patient.last_active else datetime.utcnow().isoformat(),
                cognitive_status=cognitive_status,
                medication_adherence=medication_adherence,
                daily_activities=daily_activities,
                recent_alerts=recent_alerts
            ))
        except Exception as e:
            # Log error but continue processing other patients
            print(f"Error processing patient {rel.patient_id}: {str(e)}")
            continue
    
    return result


@router.put("/{relationship_id}/permissions", response_model=CaregiverResponse)
async def update_caregiver_permissions(
    relationship_id: UUID,
    permissions: CaregiverPermissionsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update caregiver permissions.
    
    Requirements: 6.1
    """
    relationship = db.query(CaregiverRelationship).filter(
        and_(
            CaregiverRelationship.id == relationship_id,
            CaregiverRelationship.patient_id == current_user.id
        )
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver relationship not found"
        )
    
    # Update permissions
    if permissions.can_view_health_data is not None:
        relationship.can_view_health_data = permissions.can_view_health_data
    if permissions.can_view_assessments is not None:
        relationship.can_view_assessments = permissions.can_view_assessments
    if permissions.can_view_medications is not None:
        relationship.can_view_medications = permissions.can_view_medications
    if permissions.can_manage_reminders is not None:
        relationship.can_manage_reminders = permissions.can_manage_reminders
    if permissions.can_receive_alerts is not None:
        relationship.can_receive_alerts = permissions.can_receive_alerts
    
    db.commit()
    db.refresh(relationship)
    
    caregiver = db.query(User).filter(User.id == relationship.caregiver_id).first()
    
    return CaregiverResponse(
        id=str(relationship.id),
        patient_id=str(relationship.patient_id),
        caregiver_id=str(relationship.caregiver_id),
        caregiver_name=caregiver.name if caregiver else "Unknown",
        caregiver_email=caregiver.email if caregiver else "Unknown",
        relationship_type=relationship.relationship_type.value,
        relationship_description=relationship.relationship_description,
        permissions={
            "can_view_health_data": relationship.can_view_health_data,
            "can_view_assessments": relationship.can_view_assessments,
            "can_view_medications": relationship.can_view_medications,
            "can_manage_reminders": relationship.can_manage_reminders,
            "can_receive_alerts": relationship.can_receive_alerts
        },
        active=relationship.active,
        approved=relationship.approved,
        created_at=relationship.created_at.isoformat(),
        updated_at=relationship.updated_at.isoformat()
    )


@router.delete("/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_caregiver_access(
    relationship_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke caregiver access.
    
    Requirements: 6.1
    """
    relationship = db.query(CaregiverRelationship).filter(
        and_(
            CaregiverRelationship.id == relationship_id,
            CaregiverRelationship.patient_id == current_user.id
        )
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver relationship not found"
        )
    
    # Soft delete by setting active to False
    relationship.active = False
    db.commit()
    
    return None


class ActivityStatus(BaseModel):
    """Real-time activity status for a patient"""
    patient_id: str
    patient_name: str
    current_activities: List[dict]
    missed_activities: List[dict]
    completed_today: int
    total_today: int
    last_activity_time: Optional[str]


@router.get("/patients/{patient_id}/activity-status", response_model=ActivityStatus)
async def get_patient_activity_status(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get real-time activity status for a patient.
    
    Requirements: 6.2
    """
    # Verify caregiver relationship
    relationship = db.query(CaregiverRelationship).filter(
        and_(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.patient_id == patient_id,
            CaregiverRelationship.active == True,
            CaregiverRelationship.approved == True
        )
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's data"
        )
    
    # Get patient
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Get today's routines and completions
    today = datetime.utcnow().date()
    routines = db.query(DailyRoutine).filter(
        and_(
            DailyRoutine.user_id == patient_id,
            DailyRoutine.is_active == True
        )
    ).all()
    
    current_activities = []
    missed_activities = []
    completed_today = 0
    total_today = 0
    last_activity_time = None
    
    for routine in routines:
        # Get today's completion
        completion = db.query(RoutineCompletion).filter(
            and_(
                RoutineCompletion.routine_id == routine.id,
                RoutineCompletion.completion_date >= today
            )
        ).first()
        
        total_today += 1
        
        if completion and completion.completed:
            completed_today += 1
            if not last_activity_time or completion.completed_at > datetime.fromisoformat(last_activity_time):
                last_activity_time = completion.completed_at.isoformat()
        else:
            # Check if it's a missed activity (past scheduled time)
            now = datetime.utcnow()
            scheduled_time = datetime.combine(today, datetime.min.time())
            
            if routine.time_of_day == 'morning':
                scheduled_time = scheduled_time.replace(hour=8)
            elif routine.time_of_day == 'afternoon':
                scheduled_time = scheduled_time.replace(hour=14)
            elif routine.time_of_day == 'evening':
                scheduled_time = scheduled_time.replace(hour=18)
            
            if now > scheduled_time:
                missed_activities.append({
                    'id': str(routine.id),
                    'name': routine.title,
                    'description': routine.description,
                    'time_of_day': routine.time_of_day,
                    'scheduled_time': scheduled_time.isoformat()
                })
            else:
                current_activities.append({
                    'id': str(routine.id),
                    'name': routine.title,
                    'description': routine.description,
                    'time_of_day': routine.time_of_day,
                    'scheduled_time': scheduled_time.isoformat()
                })
    
    # Also check reminders
    reminders = db.query(Reminder).filter(
        and_(
            Reminder.user_id == patient_id,
            Reminder.active == True,
            Reminder.reminder_time >= datetime.combine(today, datetime.min.time()),
            Reminder.reminder_time < datetime.combine(today, datetime.max.time())
        )
    ).all()
    
    for reminder in reminders:
        if reminder.completed:
            completed_today += 1
            if not last_activity_time or reminder.completed_at > datetime.fromisoformat(last_activity_time):
                last_activity_time = reminder.completed_at.isoformat()
        elif datetime.utcnow() > reminder.reminder_time:
            missed_activities.append({
                'id': str(reminder.id),
                'name': reminder.title,
                'description': reminder.description,
                'type': 'reminder',
                'scheduled_time': reminder.reminder_time.isoformat()
            })
        else:
            current_activities.append({
                'id': str(reminder.id),
                'name': reminder.title,
                'description': reminder.description,
                'type': 'reminder',
                'scheduled_time': reminder.reminder_time.isoformat()
            })
        
        total_today += 1
    
    return ActivityStatus(
        patient_id=str(patient_id),
        patient_name=patient.name,
        current_activities=current_activities,
        missed_activities=missed_activities,
        completed_today=completed_today,
        total_today=total_today,
        last_activity_time=last_activity_time
    )


class CaregiverAlertResponse(BaseModel):
    """Alert for caregiver"""
    id: str
    patient_id: str
    patient_name: str
    alert_type: str
    message: str
    severity: str
    created_at: str
    acknowledged: bool
    acknowledged_at: Optional[str]


@router.get("/alerts", response_model=List[CaregiverAlertResponse])
async def get_caregiver_alerts(
    acknowledged: Optional[bool] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get alerts for all patients the caregiver monitors.
    
    Requirements: 6.4
    """
    # Get all patient relationships
    relationships = db.query(CaregiverRelationship).filter(
        and_(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.active == True,
            CaregiverRelationship.approved == True,
            CaregiverRelationship.can_receive_alerts == True
        )
    ).all()
    
    patient_ids = [rel.patient_id for rel in relationships]
    
    if not patient_ids:
        return []
    
    # Build query for alerts
    query = db.query(EmergencyAlert).filter(
        EmergencyAlert.user_id.in_(patient_ids)
    )
    
    if acknowledged is not None:
        query = query.filter(EmergencyAlert.acknowledged == acknowledged)
    
    if severity:
        query = query.filter(EmergencyAlert.severity == severity)
    
    alerts = query.order_by(desc(EmergencyAlert.created_at)).limit(limit).all()
    
    # Get patient names
    patients = db.query(User).filter(User.id.in_(patient_ids)).all()
    patient_map = {str(p.id): p.name for p in patients}
    
    result = []
    for alert in alerts:
        result.append(CaregiverAlertResponse(
            id=str(alert.id),
            patient_id=str(alert.user_id),
            patient_name=patient_map.get(str(alert.user_id), "Unknown"),
            alert_type=alert.alert_type,
            message=alert.message,
            severity=alert.severity,
            created_at=alert.created_at.isoformat(),
            acknowledged=alert.acknowledged,
            acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        ))
    
    return result


@router.post("/alerts/{alert_id}/acknowledge", status_code=status.HTTP_200_OK)
async def acknowledge_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert.
    
    Requirements: 6.4
    """
    alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Verify caregiver has access to this patient
    relationship = db.query(CaregiverRelationship).filter(
        and_(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.patient_id == alert.user_id,
            CaregiverRelationship.active == True,
            CaregiverRelationship.approved == True,
            CaregiverRelationship.can_receive_alerts == True
        )
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this alert"
        )
    
    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = str(current_user.id)
    
    db.commit()
    
    return {"message": "Alert acknowledged successfully"}


class ActivityLogEntry(BaseModel):
    """Activity log entry"""
    id: str
    patient_id: str
    activity_type: str
    activity_name: str
    description: str
    timestamp: str
    status: str
    metadata: Optional[dict]


@router.get("/patients/{patient_id}/activity-log", response_model=List[ActivityLogEntry])
async def get_patient_activity_log(
    patient_id: UUID,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    activity_type: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive activity log for a patient.
    
    Requirements: 6.5
    """
    # Verify caregiver relationship
    relationship = db.query(CaregiverRelationship).filter(
        and_(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.patient_id == patient_id,
            CaregiverRelationship.active == True,
            CaregiverRelationship.approved == True
        )
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's data"
        )
    
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
    end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
    
    activity_log = []
    
    # Get routine completions
    if not activity_type or activity_type == 'routine':
        completions = db.query(RoutineCompletion).join(DailyRoutine).filter(
            and_(
                DailyRoutine.user_id == patient_id,
                RoutineCompletion.completion_date >= start_dt.date(),
                RoutineCompletion.completion_date <= end_dt.date()
            )
        ).order_by(desc(RoutineCompletion.created_at)).limit(limit).all()
        
        for completion in completions:
            routine = db.query(DailyRoutine).filter(DailyRoutine.id == completion.routine_id).first()
            if routine:
                activity_log.append({
                    'id': str(completion.id),
                    'patient_id': str(patient_id),
                    'activity_type': 'routine',
                    'activity_name': routine.title,
                    'description': routine.description or '',
                    'timestamp': completion.completion_date.isoformat(),
                    'status': 'completed' if completion.completed else 'missed',
                    'metadata': {
                        'time_of_day': routine.time_of_day,
                        'notes': completion.notes
                    }
                })
    
    # Get medication logs
    if not activity_type or activity_type == 'medication':
        if relationship.can_view_medications:
            medications = db.query(Medication).filter(
                Medication.user_id == patient_id
            ).all()
            
            for medication in medications:
                if medication.adherence_log:
                    for log in medication.adherence_log:
                        scheduled_time = datetime.fromisoformat(log.get("scheduled_time", ""))
                        if start_dt <= scheduled_time <= end_dt:
                            taken_time = log.get("taken_time")
                            activity_log.append({
                                'id': f"{medication.id}_{log.get('scheduled_time')}",
                                'patient_id': str(patient_id),
                                'activity_type': 'medication',
                                'activity_name': medication.name,
                                'description': f'{medication.dosage} - {medication.frequency}',
                                'timestamp': taken_time if taken_time else scheduled_time.isoformat(),
                                'status': 'taken' if not log.get('skipped', True) else 'skipped',
                                'metadata': {
                                    'scheduled_time': scheduled_time.isoformat(),
                                    'dosage': medication.dosage
                                }
                            })
    
    # Get assessments
    if not activity_type or activity_type == 'assessment':
        if relationship.can_view_assessments:
            assessments = db.query(Assessment).filter(
                and_(
                    Assessment.user_id == patient_id,
                    Assessment.completed_at >= start_dt,
                    Assessment.completed_at <= end_dt
                )
            ).order_by(desc(Assessment.completed_at)).limit(limit).all()
            
            for assessment in assessments:
                activity_log.append({
                    'id': str(assessment.id),
                    'patient_id': str(patient_id),
                    'activity_type': 'assessment',
                    'activity_name': f'{assessment.type} Test',
                    'description': f'Score: {assessment.score}/{assessment.max_score}',
                    'timestamp': assessment.completed_at.isoformat(),
                    'status': 'completed',
                    'metadata': {
                        'score': assessment.score,
                        'max_score': assessment.max_score,
                        'duration': assessment.duration
                    }
                })
    
    # Get reminders
    if not activity_type or activity_type == 'reminder':
        reminders = db.query(Reminder).filter(
            and_(
                Reminder.user_id == patient_id,
                Reminder.reminder_time >= start_dt,
                Reminder.reminder_time <= end_dt
            )
        ).order_by(desc(Reminder.reminder_time)).limit(limit).all()
        
        for reminder in reminders:
            activity_log.append({
                'id': str(reminder.id),
                'patient_id': str(patient_id),
                'activity_type': 'reminder',
                'activity_name': reminder.title,
                'description': reminder.description or '',
                'timestamp': reminder.completed_at.isoformat() if reminder.completed_at else reminder.reminder_time.isoformat(),
                'status': 'completed' if reminder.completed else 'pending',
                'metadata': {
                    'reminder_time': reminder.reminder_time.isoformat(),
                    'repeat_type': reminder.repeat_type
                }
            })
    
    # Sort by timestamp
    activity_log.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Convert to response models
    result = [
        ActivityLogEntry(
            id=entry['id'],
            patient_id=entry['patient_id'],
            activity_type=entry['activity_type'],
            activity_name=entry['activity_name'],
            description=entry['description'],
            timestamp=entry['timestamp'],
            status=entry['status'],
            metadata=entry['metadata']
        )
        for entry in activity_log[:limit]
    ]
    
    return result
