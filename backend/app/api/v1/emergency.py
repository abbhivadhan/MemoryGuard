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


class EmergencyContactInfo(BaseModel):
    name: str
    phone: str
    relationship: Optional[str] = None


class MedicalInfo(BaseModel):
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    blood_type: Optional[str] = None
    emergency_notes: Optional[str] = None
    emergency_contacts: Optional[List[EmergencyContactInfo]] = None


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


@router.get("/medical-info", response_model=dict)
async def get_medical_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the user's stored medical information for emergencies.
    """
    # Get the most recent medical info from emergency alerts
    latest_alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.user_id == current_user.id,
        EmergencyAlert.medical_info.isnot(None)
    ).order_by(desc(EmergencyAlert.created_at)).first()
    
    if latest_alert and latest_alert.medical_info:
        # Ensure emergency_contacts field exists
        medical_info = latest_alert.medical_info
        if isinstance(medical_info, dict) and 'emergency_contacts' not in medical_info:
            medical_info['emergency_contacts'] = []
        return medical_info
    
    return {
        "medications": [],
        "allergies": [],
        "conditions": [],
        "blood_type": "",
        "emergency_notes": "",
        "emergency_contacts": []
    }


@router.put("/medical-info", response_model=dict)
async def update_medical_info(
    medical_info: MedicalInfo,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the user's medical information for emergencies.
    Stores it by creating/updating an emergency alert record.
    """
    # Create a new alert record to store the medical info
    # This allows us to track history of medical info changes
    alert = EmergencyAlert(
        user_id=current_user.id,
        medical_info=medical_info.dict(),
        is_active=False,  # Not an active alert, just storing info
        trigger_type="manual",
        notes="Medical information update"
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return alert.medical_info


@router.get("/medical-info/debug", response_model=dict)
async def debug_medical_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Debug endpoint to check what medical info will be included in QR code.
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        # Get emergency contacts
        emergency_contacts = db.query(EmergencyContact).filter(
            EmergencyContact.user_id == current_user.id,
            EmergencyContact.active == True
        ).order_by(EmergencyContact.priority).all()
        
        # Get active medications
        from app.models.medication import Medication
        medications = db.query(Medication).filter(
            Medication.user_id == current_user.id,
            Medication.active == True
        ).all()
        
        # Get latest medical info
        latest_alert = db.query(EmergencyAlert).filter(
            EmergencyAlert.user_id == current_user.id,
            EmergencyAlert.medical_info.isnot(None)
        ).order_by(desc(EmergencyAlert.created_at)).first()
        
        # Get contacts from medical_info
        contacts_from_medical_info = []
        if latest_alert and latest_alert.medical_info:
            if isinstance(latest_alert.medical_info, dict):
                contacts_from_medical_info = latest_alert.medical_info.get("emergency_contacts", [])
        
        return {
            "user_id": str(current_user.id),
            "user_email": current_user.email,
            "user_name": current_user.name if hasattr(current_user, 'name') else None,
            "emergency_contacts_table_count": len(emergency_contacts),
            "emergency_contacts_from_table": [
                {
                    "id": str(contact.id),
                    "name": contact.name,
                    "phone": contact.phone,
                    "relationship": contact.relationship_type,
                    "active": contact.active
                }
                for contact in emergency_contacts
            ],
            "emergency_contacts_from_medical_info_count": len(contacts_from_medical_info),
            "emergency_contacts_from_medical_info": contacts_from_medical_info,
            "medications_count": len(medications),
            "medications": [
                {
                    "name": med.name,
                    "dosage": getattr(med, 'dosage', ''),
                    "frequency": getattr(med, 'frequency', '')
                }
                for med in medications
            ],
            "has_medical_info_alert": latest_alert is not None,
            "medical_info_from_alert": latest_alert.medical_info if latest_alert else None,
            "which_contacts_will_be_used": "table" if len(emergency_contacts) > 0 else "medical_info" if len(contacts_from_medical_info) > 0 else "none"
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in debug endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}"
        )


@router.post("/medical-info/qr-code", response_model=dict)
async def generate_medical_qr_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a QR code for the user's emergency medical information.
    Returns a base64 encoded image that can be displayed or downloaded.
    """
    try:
        from app.services.qr_service import generate_medical_info_qr
        from app.core.config import settings
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Generating QR code for user {current_user.id}")
        
        # Get user's medical info from the database
        # First, get the most recent medical info from emergency alerts
        latest_alert = db.query(EmergencyAlert).filter(
            EmergencyAlert.user_id == current_user.id,
            EmergencyAlert.medical_info.isnot(None)
        ).order_by(desc(EmergencyAlert.created_at)).first()
        
        # Get emergency contacts
        emergency_contacts = db.query(EmergencyContact).filter(
            EmergencyContact.user_id == current_user.id,
            EmergencyContact.active == True
        ).order_by(EmergencyContact.priority).all()
        
        logger.info(f"Found {len(emergency_contacts)} emergency contacts for user {current_user.id}")
        
        # Get active medications
        from app.models.medication import Medication
        medications = db.query(Medication).filter(
            Medication.user_id == current_user.id,
            Medication.active == True
        ).all()
        
        logger.info(f"Found {len(medications)} medications for user {current_user.id}")
        
        # Start with contacts from emergency_contacts table
        contacts_from_table = [
            {
                "name": contact.name,
                "phone": contact.phone,
                "relationship": contact.relationship_type,
                "email": contact.email if hasattr(contact, 'email') else None
            }
            for contact in emergency_contacts
        ]
        
        logger.info(f"Found {len(contacts_from_table)} contacts from emergency_contacts table")
        
        # Get contacts from medical_info if available
        contacts_from_medical_info = []
        if latest_alert and latest_alert.medical_info:
            if isinstance(latest_alert.medical_info, dict):
                contacts_from_medical_info = latest_alert.medical_info.get("emergency_contacts", [])
                logger.info(f"Found {len(contacts_from_medical_info)} contacts from medical_info")
        
        # Use contacts from medical_info if table is empty, otherwise prefer table
        # This prioritizes the dedicated emergency_contacts table but falls back to medical_info
        final_contacts = contacts_from_table if contacts_from_table else contacts_from_medical_info
        
        logger.info(f"Using {len(final_contacts)} contacts for QR code")
        if final_contacts:
            logger.info(f"Contact details: {final_contacts}")
        
        # Build comprehensive medical info
        medical_info = {
            "user_id": str(current_user.id),
            "name": current_user.name if hasattr(current_user, 'name') else current_user.email,
            "email": current_user.email,
            "emergency_contacts": final_contacts,
            "medications": [
                {
                    "name": med.name,
                    "dosage": med.dosage if hasattr(med, 'dosage') else '',
                    "frequency": med.frequency if hasattr(med, 'frequency') else ''
                }
                for med in medications
            ]
        }
        
        # Add medical info from latest alert if available
        if latest_alert and latest_alert.medical_info:
            if isinstance(latest_alert.medical_info, dict):
                medical_info.update({
                    "allergies": latest_alert.medical_info.get("allergies", []),
                    "conditions": latest_alert.medical_info.get("conditions", []),
                    "blood_type": latest_alert.medical_info.get("blood_type", ""),
                    "medical_notes": latest_alert.medical_info.get("emergency_notes", "")
                })
        
        # Generate base URL
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        logger.info(f"Using base URL: {base_url}")
        
        # Generate QR code
        qr_code_data = generate_medical_info_qr(
            medical_info=medical_info,
            user_id=str(current_user.id),
            base_url=base_url
        )
        
        logger.info("QR code generated successfully")
        
        return {
            "qr_code": qr_code_data,
            "url": f"{base_url}/emergency-info/{current_user.id}",
            "message": "QR code generated successfully"
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating QR code: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {str(e)}"
        )
