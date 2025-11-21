"""
Provider portal API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.provider import Provider, ProviderAccess, ProviderAccessLog, ClinicalNote, AccessStatus
from app.models.assessment import Assessment
from app.models.health_metric import HealthMetric
from app.models.medication import Medication
from app.models.prediction import Prediction
from app.schemas.provider import (
    ProviderAccessGrant,
    ProviderAccessResponse,
    ProviderAccessWithProvider,
    ProviderAccessUpdate,
    ProviderAccessLogResponse,
    ClinicalNoteCreate,
    ClinicalNoteUpdate,
    ClinicalNoteResponse,
    ClinicalNoteWithProvider,
    PatientDashboardData,
    PatientSummary,
    PatientHealthOverview
)

router = APIRouter()


# Helper function to log provider access
async def log_provider_access(
    db: Session,
    provider_access_id: uuid.UUID,
    action: str,
    resource_type: str = None,
    resource_id: str = None,
    request: Request = None
):
    """Log provider access for audit trail"""
    log = ProviderAccessLog(
        id=uuid.uuid4(),
        provider_access_id=provider_access_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(log)
    db.commit()


# Helper function to check provider access
def check_provider_access(
    db: Session,
    provider_id: uuid.UUID,
    patient_id: uuid.UUID,
    permission: str = None
) -> ProviderAccess:
    """Check if provider has active access to patient"""
    access = db.query(ProviderAccess).filter(
        and_(
            ProviderAccess.provider_id == provider_id,
            ProviderAccess.patient_id == patient_id,
            ProviderAccess.status == AccessStatus.ACTIVE
        )
    ).first()
    
    if not access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provider does not have access to this patient"
        )
    
    # Check if access has expired
    if access.expires_at and access.expires_at < datetime.utcnow():
        access.status = AccessStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provider access has expired"
        )
    
    # Check specific permission if provided
    if permission:
        permission_map = {
            "view_assessments": access.can_view_assessments,
            "view_health_metrics": access.can_view_health_metrics,
            "view_medications": access.can_view_medications,
            "view_imaging": access.can_view_imaging,
            "add_notes": access.can_add_notes
        }
        if not permission_map.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Provider does not have permission to {permission}"
            )
    
    return access


# Patient endpoints for managing provider access
@router.post("/access/grant", response_model=ProviderAccessResponse)
async def grant_provider_access(
    access_grant: ProviderAccessGrant,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Grant a healthcare provider access to patient data.
    Patient must be authenticated.
    """
    # Find provider by email
    provider = db.query(Provider).filter(Provider.email == access_grant.provider_email).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found with this email"
        )
    
    if not provider.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider account is not active"
        )
    
    # Check if access already exists
    existing_access = db.query(ProviderAccess).filter(
        and_(
            ProviderAccess.patient_id == current_user.id,
            ProviderAccess.provider_id == provider.id,
            ProviderAccess.status.in_([AccessStatus.ACTIVE, AccessStatus.PENDING])
        )
    ).first()
    
    if existing_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider already has active or pending access"
        )
    
    # Create new access grant
    provider_access = ProviderAccess(
        id=uuid.uuid4(),
        patient_id=current_user.id,
        provider_id=provider.id,
        status=AccessStatus.ACTIVE,
        granted_at=datetime.utcnow(),
        expires_at=access_grant.expires_at,
        can_view_assessments=access_grant.can_view_assessments,
        can_view_health_metrics=access_grant.can_view_health_metrics,
        can_view_medications=access_grant.can_view_medications,
        can_view_imaging=access_grant.can_view_imaging,
        can_add_notes=access_grant.can_add_notes,
        granted_by_patient=True,
        access_reason=access_grant.access_reason
    )
    
    db.add(provider_access)
    db.commit()
    db.refresh(provider_access)
    
    return provider_access.to_dict()


@router.get("/access/my-providers", response_model=List[ProviderAccessWithProvider])
async def get_my_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all providers who have access to current patient's data.
    """
    accesses = db.query(ProviderAccess).filter(
        ProviderAccess.patient_id == current_user.id
    ).all()
    
    result = []
    for access in accesses:
        provider = db.query(Provider).filter(Provider.id == access.provider_id).first()
        access_dict = access.to_dict()
        access_dict["provider"] = provider.to_dict() if provider else None
        result.append(access_dict)
    
    return result


@router.put("/access/{access_id}", response_model=ProviderAccessResponse)
async def update_provider_access(
    access_id: str,
    access_update: ProviderAccessUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update provider access permissions.
    Patient must be authenticated.
    """
    try:
        access_uuid = uuid.UUID(access_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access ID")
    
    access = db.query(ProviderAccess).filter(
        and_(
            ProviderAccess.id == access_uuid,
            ProviderAccess.patient_id == current_user.id
        )
    ).first()
    
    if not access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider access not found"
        )
    
    # Update fields
    if access_update.status is not None:
        access.status = access_update.status
        if access_update.status == AccessStatus.REVOKED:
            access.revoked_at = datetime.utcnow()
    
    if access_update.can_view_assessments is not None:
        access.can_view_assessments = access_update.can_view_assessments
    if access_update.can_view_health_metrics is not None:
        access.can_view_health_metrics = access_update.can_view_health_metrics
    if access_update.can_view_medications is not None:
        access.can_view_medications = access_update.can_view_medications
    if access_update.can_view_imaging is not None:
        access.can_view_imaging = access_update.can_view_imaging
    if access_update.can_add_notes is not None:
        access.can_add_notes = access_update.can_add_notes
    if access_update.expires_at is not None:
        access.expires_at = access_update.expires_at
    
    db.commit()
    db.refresh(access)
    
    return access.to_dict()


@router.delete("/access/{access_id}")
async def revoke_provider_access(
    access_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke provider access to patient data.
    Patient must be authenticated.
    """
    try:
        access_uuid = uuid.UUID(access_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access ID")
    
    access = db.query(ProviderAccess).filter(
        and_(
            ProviderAccess.id == access_uuid,
            ProviderAccess.patient_id == current_user.id
        )
    ).first()
    
    if not access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider access not found"
        )
    
    access.status = AccessStatus.REVOKED
    access.revoked_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Provider access revoked successfully"}


@router.get("/access/{access_id}/logs", response_model=List[ProviderAccessLogResponse])
async def get_access_logs(
    access_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific provider access.
    Patient must be authenticated.
    """
    try:
        access_uuid = uuid.UUID(access_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access ID")
    
    # Verify patient owns this access
    access = db.query(ProviderAccess).filter(
        and_(
            ProviderAccess.id == access_uuid,
            ProviderAccess.patient_id == current_user.id
        )
    ).first()
    
    if not access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider access not found"
        )
    
    logs = db.query(ProviderAccessLog).filter(
        ProviderAccessLog.provider_access_id == access_uuid
    ).order_by(ProviderAccessLog.created_at.desc()).all()
    
    return [log.to_dict() for log in logs]


# Provider endpoints for accessing patient data
@router.get("/patients", response_model=List[PatientSummary])
async def get_my_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all patients that the current provider has access to.
    Provider must be authenticated.
    """
    # Check if current user is a provider
    provider = db.query(Provider).filter(Provider.email == current_user.email).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered provider"
        )
    
    # Get all active accesses
    accesses = db.query(ProviderAccess).filter(
        and_(
            ProviderAccess.provider_id == provider.id,
            ProviderAccess.status == AccessStatus.ACTIVE
        )
    ).all()
    
    patients = []
    for access in accesses:
        patient = db.query(User).filter(User.id == access.patient_id).first()
        if patient:
            patients.append({
                "id": str(patient.id),
                "name": patient.name,
                "email": patient.email,
                "date_of_birth": patient.date_of_birth,
                "apoe_genotype": patient.apoe_genotype.value if patient.apoe_genotype else None,
                "last_active": patient.last_active
            })
    
    return patients


@router.get("/patients/{patient_id}/dashboard", response_model=PatientDashboardData)
async def get_patient_dashboard(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard data for a specific patient.
    Provider must have active access.
    """
    try:
        patient_uuid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid patient ID")
    
    # Check if current user is a provider
    provider = db.query(Provider).filter(Provider.email == current_user.email).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered provider"
        )
    
    # Check access
    access = check_provider_access(db, provider.id, patient_uuid)
    
    # Log access
    await log_provider_access(
        db, access.id, "viewed_dashboard", "patient", patient_id, request
    )
    
    # Get patient
    patient = db.query(User).filter(User.id == patient_uuid).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    # Build dashboard data
    dashboard_data = {
        "patient": {
            "id": str(patient.id),
            "name": patient.name,
            "email": patient.email,
            "date_of_birth": patient.date_of_birth,
            "apoe_genotype": patient.apoe_genotype.value if patient.apoe_genotype else None,
            "last_active": patient.last_active
        },
        "health_overview": {},
        "recent_assessments": [],
        "recent_health_metrics": [],
        "active_medications": [],
        "recent_predictions": [],
        "clinical_notes": []
    }
    
    # Get health overview
    if access.can_view_assessments:
        latest_assessments = db.query(Assessment).filter(
            Assessment.user_id == patient_uuid
        ).order_by(Assessment.completed_at.desc()).limit(1).all()
        
        if latest_assessments:
            latest = latest_assessments[0]
            dashboard_data["health_overview"]["last_assessment_date"] = latest.completed_at
            if latest.test_type == "MMSE":
                dashboard_data["health_overview"]["latest_mmse_score"] = latest.total_score
            elif latest.test_type == "MoCA":
                dashboard_data["health_overview"]["latest_moca_score"] = latest.total_score
    
    if access.can_view_medications:
        medications = db.query(Medication).filter(
            and_(
                Medication.user_id == patient_uuid,
                Medication.is_active == True
            )
        ).all()
        
        # Calculate adherence rate
        total_doses = 0
        taken_doses = 0
        for med in medications:
            for log in med.adherence_log:
                total_doses += 1
                if not log.get("skipped", False):
                    taken_doses += 1
        
        if total_doses > 0:
            dashboard_data["health_overview"]["medication_adherence_rate"] = (taken_doses / total_doses) * 100
    
    # Get recent predictions
    predictions = db.query(Prediction).filter(
        Prediction.user_id == patient_uuid
    ).order_by(Prediction.created_at.desc()).limit(1).all()
    
    if predictions:
        latest_pred = predictions[0]
        dashboard_data["health_overview"]["latest_risk_score"] = latest_pred.risk_score
        dashboard_data["health_overview"]["last_prediction_date"] = latest_pred.created_at
    
    # Get recent assessments
    if access.can_view_assessments:
        assessments = db.query(Assessment).filter(
            Assessment.user_id == patient_uuid
        ).order_by(Assessment.completed_at.desc()).limit(5).all()
        dashboard_data["recent_assessments"] = [
            {
                "id": str(a.id),
                "test_type": a.test_type,
                "total_score": a.total_score,
                "max_score": a.max_score,
                "completed_at": a.completed_at
            }
            for a in assessments
        ]
    
    # Get recent health metrics
    if access.can_view_health_metrics:
        metrics = db.query(HealthMetric).filter(
            HealthMetric.user_id == patient_uuid
        ).order_by(HealthMetric.recorded_at.desc()).limit(10).all()
        dashboard_data["recent_health_metrics"] = [
            {
                "id": str(m.id),
                "metric_type": m.metric_type,
                "metric_name": m.metric_name,
                "value": m.value,
                "unit": m.unit,
                "recorded_at": m.recorded_at
            }
            for m in metrics
        ]
    
    # Get active medications
    if access.can_view_medications:
        medications = db.query(Medication).filter(
            and_(
                Medication.user_id == patient_uuid,
                Medication.is_active == True
            )
        ).all()
        dashboard_data["active_medications"] = [
            {
                "id": str(m.id),
                "name": m.name,
                "dosage": m.dosage,
                "frequency": m.frequency
            }
            for m in medications
        ]
    
    # Get recent predictions
    predictions = db.query(Prediction).filter(
        Prediction.user_id == patient_uuid
    ).order_by(Prediction.created_at.desc()).limit(3).all()
    dashboard_data["recent_predictions"] = [
        {
            "id": str(p.id),
            "risk_score": p.risk_score,
            "risk_category": p.risk_category,
            "created_at": p.created_at
        }
        for p in predictions
    ]
    
    # Get clinical notes
    if access.can_add_notes:
        notes = db.query(ClinicalNote).filter(
            ClinicalNote.patient_id == patient_uuid
        ).order_by(ClinicalNote.created_at.desc()).all()
        dashboard_data["clinical_notes"] = [note.to_dict() for note in notes]
    
    return dashboard_data


# Clinical notes endpoints
@router.post("/notes", response_model=ClinicalNoteResponse)
async def create_clinical_note(
    note: ClinicalNoteCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a clinical note for a patient.
    Provider must have active access and add_notes permission.
    """
    try:
        patient_uuid = uuid.UUID(note.patient_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid patient ID")
    
    # Check if current user is a provider
    provider = db.query(Provider).filter(Provider.email == current_user.email).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered provider"
        )
    
    # Check access
    access = check_provider_access(db, provider.id, patient_uuid, "add_notes")
    
    # Create note
    clinical_note = ClinicalNote(
        id=uuid.uuid4(),
        patient_id=patient_uuid,
        provider_id=provider.id,
        title=note.title,
        content=note.content,
        note_type=note.note_type,
        is_private=note.is_private
    )
    
    db.add(clinical_note)
    db.commit()
    db.refresh(clinical_note)
    
    # Log access
    await log_provider_access(
        db, access.id, "added_note", "clinical_note", clinical_note.id, request
    )
    
    return clinical_note.to_dict()


@router.get("/notes/{patient_id}", response_model=List[ClinicalNoteWithProvider])
async def get_patient_notes(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all clinical notes for a patient.
    Provider must have active access.
    """
    try:
        patient_uuid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid patient ID")
    
    # Check if current user is a provider
    provider = db.query(Provider).filter(Provider.email == current_user.email).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered provider"
        )
    
    # Check access
    access = check_provider_access(db, provider.id, patient_uuid)
    
    # Log access
    await log_provider_access(
        db, access.id, "viewed_notes", "clinical_note", patient_id, request
    )
    
    # Get notes
    notes = db.query(ClinicalNote).filter(
        ClinicalNote.patient_id == patient_uuid
    ).order_by(ClinicalNote.created_at.desc()).all()
    
    result = []
    for note in notes:
        note_provider = db.query(Provider).filter(Provider.id == note.provider_id).first()
        note_dict = note.to_dict()
        note_dict["provider"] = note_provider.to_dict() if note_provider else None
        result.append(note_dict)
    
    return result


@router.put("/notes/{note_id}", response_model=ClinicalNoteResponse)
async def update_clinical_note(
    note_id: str,
    note_update: ClinicalNoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a clinical note.
    Only the provider who created the note can update it.
    """
    try:
        note_uuid = uuid.UUID(note_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid note ID")
    
    # Check if current user is a provider
    provider = db.query(Provider).filter(Provider.email == current_user.email).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered provider"
        )
    
    # Get note
    note = db.query(ClinicalNote).filter(
        and_(
            ClinicalNote.id == note_uuid,
            ClinicalNote.provider_id == provider.id
        )
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found or you don't have permission to update it"
        )
    
    # Update fields
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    if note_update.note_type is not None:
        note.note_type = note_update.note_type
    if note_update.is_private is not None:
        note.is_private = note_update.is_private
    
    db.commit()
    db.refresh(note)
    
    return note.to_dict()


@router.delete("/notes/{note_id}")
async def delete_clinical_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a clinical note.
    Only the provider who created the note can delete it.
    """
    try:
        note_uuid = uuid.UUID(note_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid note ID")
    
    # Check if current user is a provider
    provider = db.query(Provider).filter(Provider.email == current_user.email).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered provider"
        )
    
    # Get note
    note = db.query(ClinicalNote).filter(
        and_(
            ClinicalNote.id == note_uuid,
            ClinicalNote.provider_id == provider.id
        )
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found or you don't have permission to delete it"
        )
    
    db.delete(note)
    db.commit()
    
    return {"message": "Clinical note deleted successfully"}


# Clinical report generation
@router.get("/patients/{patient_id}/report")
async def generate_clinical_report(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a comprehensive clinical report for a patient.
    Returns JSON data that can be used to generate PDF on frontend.
    """
    try:
        patient_uuid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid patient ID")
    
    # Check if current user is a provider
    provider = db.query(Provider).filter(Provider.email == current_user.email).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered provider"
        )
    
    # Check access
    access = check_provider_access(db, provider.id, patient_uuid)
    
    # Log access
    await log_provider_access(
        db, access.id, "generated_report", "patient", patient_id, request
    )
    
    # Get patient
    patient = db.query(User).filter(User.id == patient_uuid).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    # Build comprehensive report data
    report_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": {
            "name": provider.name,
            "email": provider.email,
            "provider_type": provider.provider_type.value,
            "institution": provider.institution,
            "specialty": provider.specialty
        },
        "patient": {
            "id": str(patient.id),
            "name": patient.name,
            "email": patient.email,
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "apoe_genotype": patient.apoe_genotype.value if patient.apoe_genotype else None,
            "last_active": patient.last_active.isoformat()
        },
        "assessments": [],
        "health_metrics": [],
        "medications": [],
        "predictions": [],
        "clinical_notes": []
    }
    
    # Get all assessments
    if access.can_view_assessments:
        assessments = db.query(Assessment).filter(
            Assessment.user_id == patient_uuid
        ).order_by(Assessment.completed_at.desc()).all()
        
        report_data["assessments"] = [
            {
                "id": str(a.id),
                "test_type": a.test_type,
                "total_score": a.total_score,
                "max_score": a.max_score,
                "completed_at": a.completed_at.isoformat(),
                "duration_seconds": a.duration_seconds
            }
            for a in assessments
        ]
    
    # Get all health metrics
    if access.can_view_health_metrics:
        metrics = db.query(HealthMetric).filter(
            HealthMetric.user_id == patient_uuid
        ).order_by(HealthMetric.recorded_at.desc()).all()
        
        report_data["health_metrics"] = [
            {
                "id": str(m.id),
                "metric_type": m.metric_type,
                "metric_name": m.metric_name,
                "value": m.value,
                "unit": m.unit,
                "recorded_at": m.recorded_at.isoformat(),
                "source": m.source
            }
            for m in metrics
        ]
    
    # Get all medications
    if access.can_view_medications:
        medications = db.query(Medication).filter(
            Medication.user_id == patient_uuid
        ).all()
        
        report_data["medications"] = [
            {
                "id": str(m.id),
                "name": m.name,
                "dosage": m.dosage,
                "frequency": m.frequency,
                "is_active": m.is_active,
                "start_date": m.start_date.isoformat() if m.start_date else None,
                "end_date": m.end_date.isoformat() if m.end_date else None,
                "side_effects": m.side_effects
            }
            for m in medications
        ]
    
    # Get all predictions
    predictions = db.query(Prediction).filter(
        Prediction.user_id == patient_uuid
    ).order_by(Prediction.created_at.desc()).all()
    
    report_data["predictions"] = [
        {
            "id": str(p.id),
            "risk_score": p.risk_score,
            "risk_category": p.risk_category,
            "confidence_lower": p.confidence_lower,
            "confidence_upper": p.confidence_upper,
            "six_month_forecast": p.six_month_forecast,
            "twelve_month_forecast": p.twelve_month_forecast,
            "twenty_four_month_forecast": p.twenty_four_month_forecast,
            "created_at": p.created_at.isoformat()
        }
        for p in predictions
    ]
    
    # Get clinical notes
    if access.can_add_notes:
        notes = db.query(ClinicalNote).filter(
            ClinicalNote.patient_id == patient_uuid
        ).order_by(ClinicalNote.created_at.desc()).all()
        
        report_data["clinical_notes"] = [
            {
                "id": str(n.id),
                "title": n.title,
                "content": n.content,
                "note_type": n.note_type,
                "is_private": n.is_private,
                "created_at": n.created_at.isoformat(),
                "provider_name": provider.name if n.provider_id == provider.id else "Other Provider"
            }
            for n in notes
        ]
    
    return report_data
