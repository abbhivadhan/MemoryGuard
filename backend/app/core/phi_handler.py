"""
Protected Health Information (PHI) handler utilities.
Provides helpers for identifying, handling, and protecting PHI data.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from app.core.audit import audit_logger

logger = logging.getLogger(__name__)


class PHIDataType(str, Enum):
    """Types of PHI data in the system"""
    IDENTIFIABLE = "identifiable"  # Names, emails, phone numbers, addresses
    HEALTH_METRICS = "health_metrics"  # Cognitive scores, biomarkers, vitals
    MEDICAL_IMAGING = "medical_imaging"  # MRI, CT scans
    MEDICATIONS = "medications"  # Medication names, dosages, schedules
    GENETIC = "genetic"  # APOE genotype, genetic markers
    CLINICAL_NOTES = "clinical_notes"  # Provider notes
    ASSESSMENTS = "assessments"  # Cognitive test results
    BEHAVIORAL = "behavioral"  # Daily routines, exercise performance


class PHIAccessLevel(str, Enum):
    """Access levels for PHI data"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    FULL = "full"


# Fields that contain PHI and require encryption
PHI_ENCRYPTED_FIELDS: Dict[str, Set[str]] = {
    "user": {"email", "name"},
    "emergency_contact": {"name", "phone", "email", "address", "notes", "relationship_description"},
    "medication": {"name", "dosage", "frequency", "instructions", "prescriber", "pharmacy"},
    "clinical_note": {"content", "diagnosis", "treatment_plan"},
    "face_recognition": {"name", "relationship"},
}

# Fields that should be redacted in logs
PHI_REDACTED_FIELDS: Set[str] = {
    "email", "phone", "name", "address", "ssn", "medical_record_number",
    "dosage", "diagnosis", "treatment_plan", "clinical_notes"
}


class PHIHandler:
    """
    Handler for Protected Health Information (PHI) operations.
    Ensures proper logging, access control, and data protection.
    """
    
    @staticmethod
    def log_phi_access(
        user_id: str,
        patient_id: str,
        data_type: PHIDataType,
        action: str,
        resource_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip: Optional[str] = None
    ) -> None:
        """
        Log PHI data access for audit trail.
        
        Args:
            user_id: ID of user accessing the data
            patient_id: ID of patient whose data is being accessed
            data_type: Type of PHI data being accessed
            action: Action being performed (read, write, update, delete)
            resource_id: Optional specific resource ID
            request_id: Optional request ID for correlation
            ip: Optional IP address of requester
        """
        metadata = {
            "patient_id": patient_id,
            "data_type": data_type.value,
            "action": action,
        }
        
        if resource_id:
            metadata["resource_id"] = resource_id
        
        if ip:
            metadata["ip"] = ip
        
        audit_logger.log_data_access(
            resource=f"phi.{data_type.value}",
            action=action,
            user_id=user_id,
            metadata=metadata,
            request_id=request_id
        )
        
        logger.info(
            f"PHI Access: user={user_id} patient={patient_id} "
            f"type={data_type.value} action={action}"
        )
    
    @staticmethod
    def redact_phi_from_logs(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact PHI fields from data before logging.
        
        Args:
            data: Dictionary containing potential PHI
            
        Returns:
            Dictionary with PHI fields redacted
        """
        redacted = data.copy()
        
        for field in PHI_REDACTED_FIELDS:
            if field in redacted:
                redacted[field] = "[REDACTED]"
        
        # Recursively redact nested dictionaries
        for key, value in redacted.items():
            if isinstance(value, dict):
                redacted[key] = PHIHandler.redact_phi_from_logs(value)
            elif isinstance(value, list):
                redacted[key] = [
                    PHIHandler.redact_phi_from_logs(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return redacted
    
    @staticmethod
    def validate_phi_access(
        user_id: str,
        patient_id: str,
        data_type: PHIDataType,
        required_access: PHIAccessLevel = PHIAccessLevel.READ
    ) -> bool:
        """
        Validate if user has required access level to patient's PHI.
        
        Args:
            user_id: ID of user requesting access
            patient_id: ID of patient whose data is being accessed
            data_type: Type of PHI data
            required_access: Required access level
            
        Returns:
            True if access is allowed, False otherwise
            
        Note:
            This is a basic implementation. In production, this should
            query the database for actual access permissions.
        """
        # Self-access always allowed
        if user_id == patient_id:
            return True
        
        # In production, check caregiver/provider access permissions
        # from database (ProviderAccess, CaregiverAccess models)
        
        # For now, log the access attempt
        logger.info(
            f"PHI access validation: user={user_id} patient={patient_id} "
            f"type={data_type.value} level={required_access.value}"
        )
        
        return False
    
    @staticmethod
    def get_phi_fields_for_model(model_name: str) -> Set[str]:
        """
        Get list of PHI fields for a given model.
        
        Args:
            model_name: Name of the database model
            
        Returns:
            Set of field names that contain PHI
        """
        return PHI_ENCRYPTED_FIELDS.get(model_name.lower(), set())
    
    @staticmethod
    def anonymize_for_analytics(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize PHI data for analytics purposes.
        Removes all identifiable information while preserving statistical value.
        
        Args:
            data: Dictionary containing PHI
            
        Returns:
            Anonymized dictionary safe for analytics
        """
        anonymized = {}
        
        # Fields safe for analytics (non-identifiable)
        safe_fields = {
            "age", "gender", "score", "value", "timestamp", "date",
            "category", "type", "status", "count", "duration"
        }
        
        for key, value in data.items():
            if key in safe_fields:
                anonymized[key] = value
            elif isinstance(value, (int, float, bool)):
                # Numeric and boolean values are generally safe
                anonymized[key] = value
            elif isinstance(value, dict):
                # Recursively anonymize nested dictionaries
                anonymized[key] = PHIHandler.anonymize_for_analytics(value)
            elif isinstance(value, list):
                # Anonymize list items
                anonymized[key] = [
                    PHIHandler.anonymize_for_analytics(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return anonymized
    
    @staticmethod
    def check_minimum_necessary(
        requested_fields: List[str],
        purpose: str
    ) -> List[str]:
        """
        Apply minimum necessary principle - only return fields needed for purpose.
        
        Args:
            requested_fields: List of fields requested
            purpose: Purpose of data access
            
        Returns:
            Filtered list of fields that are necessary for the purpose
            
        Note:
            This is a simplified implementation. In production, this should
            have detailed rules for each purpose.
        """
        # Define minimum necessary fields for common purposes
        minimum_necessary_rules = {
            "emergency": ["name", "phone", "address", "medications", "allergies"],
            "caregiver_monitoring": ["daily_routine", "medication_adherence", "assessment_scores"],
            "provider_review": ["assessments", "health_metrics", "medications", "imaging"],
            "analytics": ["age", "gender", "scores", "timestamps"],
        }
        
        necessary_fields = minimum_necessary_rules.get(purpose, requested_fields)
        
        # Filter requested fields to only include necessary ones
        filtered = [field for field in requested_fields if field in necessary_fields]
        
        logger.info(
            f"Minimum necessary check: purpose={purpose} "
            f"requested={len(requested_fields)} allowed={len(filtered)}"
        )
        
        return filtered


# Global PHI handler instance
phi_handler = PHIHandler()


__all__ = [
    "PHIHandler",
    "PHIDataType",
    "PHIAccessLevel",
    "phi_handler",
    "PHI_ENCRYPTED_FIELDS",
    "PHI_REDACTED_FIELDS",
]
