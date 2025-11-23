"""
QR Code generation service for emergency medical information.
"""
import qrcode
from io import BytesIO
import base64
from typing import Dict, Any
import json


def generate_qr_code(data: str, size: int = 300) -> str:
    """
    Generate a QR code from the provided data and return as base64 encoded image.
    
    Args:
        data: The data to encode in the QR code (URL, text, JSON, etc.)
        size: Size of the QR code in pixels (default: 300x300)
    
    Returns:
        Base64 encoded PNG image string
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size in boxes
    )
    
    # Add data to QR code
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize if needed
    if size != 300:
        img = img.resize((size, size))
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def generate_medical_info_qr(medical_info: Dict[str, Any], user_id: str, base_url: str) -> str:
    """
    Generate a QR code for emergency medical information.
    Contains plain text that displays when scanned, not a URL.
    
    Args:
        medical_info: Dictionary containing medical information
        user_id: User ID for the medical information
        base_url: Base URL of the application (not used, kept for compatibility)
    
    Returns:
        Base64 encoded QR code image
    """
    # Format medical information as readable text
    emergency_text = _format_emergency_text(medical_info)
    
    # Generate QR code with the text
    qr_code = generate_qr_code(emergency_text, size=400)
    
    return qr_code


def _format_emergency_text(medical_info: Dict[str, Any]) -> str:
    """
    Format medical information into readable emergency text.
    
    Args:
        medical_info: Dictionary containing medical information
    
    Returns:
        Formatted text string for QR code
    """
    lines = ["🚨 EMERGENCY MEDICAL INFO 🚨", ""]
    
    # Patient name
    if medical_info.get('name'):
        lines.append(f"Patient: {medical_info['name']}")
        lines.append("")
    
    # Medical condition
    lines.append("Condition: Memory Impairment")
    lines.append("(Alzheimer's/Dementia)")
    lines.append("")
    
    # Emergency contacts
    emergency_contacts = medical_info.get('emergency_contacts', [])
    if emergency_contacts:
        lines.append("EMERGENCY CONTACTS:")
        for i, contact in enumerate(emergency_contacts[:3], 1):  # Limit to 3 contacts
            if isinstance(contact, dict):
                name = contact.get('name', 'Unknown')
                phone = contact.get('phone', 'N/A')
                relationship = contact.get('relationship', '')
                lines.append(f"{i}. {name}")
                if relationship:
                    lines.append(f"   ({relationship})")
                lines.append(f"   Tel: {phone}")
            elif isinstance(contact, str):
                lines.append(f"{i}. {contact}")
        lines.append("")
    
    # Medications
    medications = medical_info.get('medications', [])
    if medications:
        lines.append("MEDICATIONS:")
        for med in medications[:5]:  # Limit to 5 medications
            if isinstance(med, dict):
                med_name = med.get('name', 'Unknown')
                dosage = med.get('dosage', '')
                if dosage:
                    lines.append(f"- {med_name} ({dosage})")
                else:
                    lines.append(f"- {med_name}")
            else:
                lines.append(f"- {med}")
        lines.append("")
    
    # Allergies
    allergies = medical_info.get('allergies', [])
    if allergies:
        if isinstance(allergies, list):
            lines.append(f"ALLERGIES: {', '.join(allergies)}")
        else:
            lines.append(f"ALLERGIES: {allergies}")
        lines.append("")
    
    # Blood type
    blood_type = medical_info.get('blood_type', '')
    if blood_type:
        lines.append(f"BLOOD TYPE: {blood_type}")
        lines.append("")
    
    # Medical conditions
    conditions = medical_info.get('conditions', [])
    if conditions:
        if isinstance(conditions, list):
            lines.append(f"CONDITIONS: {', '.join(conditions)}")
        else:
            lines.append(f"CONDITIONS: {conditions}")
        lines.append("")
    
    # Medical notes
    if medical_info.get('medical_notes'):
        lines.append(f"NOTES: {medical_info['medical_notes']}")
        lines.append("")
    
    # Important instructions
    lines.append("⚠️ IMPORTANT:")
    lines.append("• Patient may be disoriented")
    lines.append("• Contact emergency contacts above")
    lines.append("• Do not leave patient alone")
    lines.append("• Patient has memory impairment")
    
    return "\n".join(lines)


def generate_contact_qr(contact_info: Dict[str, Any]) -> str:
    """
    Generate a QR code for emergency contact information (vCard format).
    
    Args:
        contact_info: Dictionary containing contact information
    
    Returns:
        Base64 encoded QR code image
    """
    # Create vCard format for contact
    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{contact_info.get('name', 'Emergency Contact')}
TEL:{contact_info.get('phone', '')}
EMAIL:{contact_info.get('email', '')}
NOTE:Emergency Contact - {contact_info.get('relationship', '')}
END:VCARD"""
    
    # Generate QR code with vCard data
    qr_code = generate_qr_code(vcard, size=300)
    
    return qr_code
