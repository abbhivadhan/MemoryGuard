"""
Emergency alert API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.emergency_alert import EmergencyAlert
from app.models.emergency_contact import EmergencyContact
from app.services.notification_service import notification_service
from app.services.pattern_detection_service import pattern_detection_service

router = APIRouter()


# Pydantic schemas
class LocationData(BaseModel):
    latitude: float
    longitude: float
    accuracy: float
    address: Optional[str] = None


class MedicalInfo(BaseModel):
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    blood_type: Optional[str] = None
    emergency_notes: Optional[str] = None


class EmergencyAlertCreate(BaseModel):
    location: Optional[LocationData] = None
    medical_info: Optional[MedicalInfo] = None
    trigger_type: str = Field(default="manual", pattern="^(manual|automatic)$")
    notes: Optional[str] = None


class EmergencyAlertResolve(BaseModel):
    resolution_notes: Optional[str] = None


class EmergencyAlertResponse(BaseModel):
    id: str
    user_id: str
    location: Optional[dict] = None
    medical_info: Optional[dict] = None
    is_active: bool
    resolved_at: Optional[str] = None
    resolution_notes: Optional[str] = None
    contacts_notified: Optional[List[str]] = None
    notification_sent_at: Optional[str] = None
    trigger_type: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str


@router.post("/activate", response_model=EmergencyAlertResponse, status_code=status.HTTP_201_CREATED)
async def activate_emergency_alert(
    alert_data: EmergencyAlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Activate an emergency alert.
    Sends notifications to all emergency contacts with location and medical information.
    
    Requirements: 14.1, 14.2, 14.3
    """
    try:
        # Create emergency alert
        alert = EmergencyAlert(
            user_id=current_user.id,
            latitude=alert_data.location.latitude if alert_data.location else None,
            longitude=alert_data.location.longitude if alert_data.location else None,
            location_accuracy=alert_data.location.accuracy if alert_data.location else None,
            location_address=alert_data.location.address if alert_data.location else None,
            medical_info=alert_data.medical_info.dict() if alert_data.medical_info else None,
            trigger_type=alert_data.trigger_type,
            notes=alert_data.notes,
            is_active=True
        )
        
        db.add(alert)
        db.flush()  # Get the alert ID
        
        # Get emergency contacts
        emergency_contacts = db.query(EmergencyContact).filter(
            EmergencyContact.user_id == current_user.id,
            EmergencyContact.active == True
        ).order_by(EmergencyContact.priority).all()
        
        # Send notifications to emergency contacts
        contacts_notified = []
        if emergency_contacts:
            for contact in emergency_contacts:
                try:
                    # In a real implementation, this would send SMS/email/push notifications
                    # For now, we'll just log the notification
                    notification_service.send_emergency_notification(
                        contact=contact,
                        user=current_user,
                        alert=alert,
                        location=alert_data.location.dict() if alert_data.location else None,
                        medical_info=alert_data.medical_info.dict() if alert_data.medical_info else None
                    )
                    contacts_notified.append(str(contact.id))
                except Exception as e:
                    print(f"Failed to notify contact {contact.id}: {str(e)}")
        
        # Update alert with notification info
        alert.contacts_notified = contacts_notified
        alert.notification_sent_at = datetime.utcnow().isoformat()
        
        db.commit()
        db.refresh(alert)
        
        return alert.to_dict()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate emergency alert: {str(e)}"
        )


@router.get("/alerts", response_model=List[EmergencyAlertResponse])
async def get_emergency_alerts(
    active_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get emergency alerts for the current user.
    
    Requirements: 14.2
    """
    try:
        query = db.query(EmergencyAlert).filter(
            EmergencyAlert.user_id == current_user.id
        )
        
        if active_only:
            query = query.filter(EmergencyAlert.is_active == True)
        
        alerts = query.order_by(desc(EmergencyAlert.created_at)).limit(limit).all()
        
        return [alert.to_dict() for alert in alerts]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emergency alerts: {str(e)}"
        )


@router.get("/alerts/{alert_id}", response_model=EmergencyAlertResponse)
async def get_emergency_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific emergency alert.
    
    Requirements: 14.2
    """
    try:
        alert = db.query(EmergencyAlert).filter(
            EmergencyAlert.id == alert_id,
            EmergencyAlert.user_id == current_user.id
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency alert not found"
            )
        
        return alert.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emergency alert: {str(e)}"
        )


@router.post("/alerts/{alert_id}/resolve", response_model=EmergencyAlertResponse)
async def resolve_emergency_alert(
    alert_id: str,
    resolve_data: EmergencyAlertResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resolve an active emergency alert.
    
    Requirements: 14.2
    """
    try:
        alert = db.query(EmergencyAlert).filter(
            EmergencyAlert.id == alert_id,
            EmergencyAlert.user_id == current_user.id
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency alert not found"
            )
        
        if not alert.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Emergency alert is already resolved"
            )
        
        # Resolve the alert
        alert.is_active = False
        alert.resolved_at = datetime.utcnow().isoformat()
        alert.resolution_notes = resolve_data.resolution_notes
        
        db.commit()
        db.refresh(alert)
        
        return alert.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve emergency alert: {str(e)}"
        )


@router.get("/contacts", response_model=List[dict])
async def get_emergency_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all emergency contacts for the current user.
    
    Requirements: 14.3
    """
    try:
        contacts = db.query(EmergencyContact).filter(
            EmergencyContact.user_id == current_user.id,
            EmergencyContact.active == True
        ).order_by(EmergencyContact.priority).all()
        
        return [contact.to_dict() for contact in contacts]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emergency contacts: {str(e)}"
        )


@router.post("/contacts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(
    contact_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new emergency contact.
    
    Requirements: 14.3
    """
    try:
        contact = EmergencyContact(
            user_id=current_user.id,
            **contact_data
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        return contact.to_dict()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create emergency contact: {str(e)}"
        )


@router.put("/contacts/{contact_id}", response_model=dict)
async def update_emergency_contact(
    contact_id: str,
    contact_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an emergency contact.
    
    Requirements: 14.3
    """
    try:
        contact = db.query(EmergencyContact).filter(
            EmergencyContact.id == contact_id,
            EmergencyContact.user_id == current_user.id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        
        for key, value in contact_data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        
        db.commit()
        db.refresh(contact)
        
        return contact.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update emergency contact: {str(e)}"
        )


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emergency_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an emergency contact.
    
    Requirements: 14.3
    """
    try:
        contact = db.query(EmergencyContact).filter(
            EmergencyContact.id == contact_id,
            EmergencyContact.user_id == current_user.id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        
        db.delete(contact)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete emergency contact: {str(e)}"
        )



@router.get("/patterns/check", response_model=dict)
async def check_patterns(
    send_alerts: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check for concerning patterns in user behavior and health metrics.
    
    Requirements: 14.4, 14.5
    """
    try:
        result = pattern_detection_service.monitor_user_patterns(
            db=db,
            user_id=str(current_user.id),
            send_alerts=send_alerts
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check patterns: {str(e)}"
        )


@router.post("/patterns/alert", response_model=dict)
async def send_pattern_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger pattern detection and send alerts to caregivers.
    
    Requirements: 14.5
    """
    try:
        # Detect patterns
        patterns = pattern_detection_service.detect_all_patterns(
            db=db,
            user_id=str(current_user.id)
        )
        
        if not patterns:
            return {
                'message': 'No concerning patterns detected',
                'patterns_detected': 0,
                'alerts_sent': 0
            }
        
        # Send alerts
        alerts_sent = pattern_detection_service.send_pattern_alerts(
            db=db,
            user_id=str(current_user.id),
            patterns=patterns
        )
        
        return {
            'message': 'Pattern alerts sent successfully',
            'patterns_detected': len(patterns),
            'patterns': patterns,
            'alerts_sent': alerts_sent
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send pattern alerts: {str(e)}"
        )
