"""
PHI Access Control decorators and utilities for API endpoints.
Provides easy-to-use decorators for enforcing PHI access controls.
"""
from functools import wraps
from typing import Callable, Optional
from fastapi import HTTPException, status, Request
from app.core.phi_handler import PHIHandler, PHIDataType, PHIAccessLevel
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


def require_phi_access(
    data_type: PHIDataType,
    access_level: PHIAccessLevel = PHIAccessLevel.READ,
    patient_id_param: str = "patient_id"
):
    """
    Decorator to enforce PHI access control on API endpoints.
    
    Args:
        data_type: Type of PHI data being accessed
        access_level: Required access level (READ, WRITE, FULL)
        patient_id_param: Name of the parameter containing patient ID
        
    Usage:
        @router.get("/health/metrics/{patient_id}")
        @require_phi_access(PHIDataType.HEALTH_METRICS, PHIAccessLevel.READ)
        async def get_health_metrics(
            patient_id: str,
            current_user: User = Depends(get_current_user)
        ):
            # Access is already validated
            return metrics
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract patient_id from kwargs
            patient_id = kwargs.get(patient_id_param)
            if not patient_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required parameter: {patient_id_param}"
                )
            
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Extract request for IP logging
            request = kwargs.get("request")
            ip = None
            if request and isinstance(request, Request):
                ip = request.client.host if request.client else None
            
            # Validate access
            user_id = str(current_user.id)
            has_access = PHIHandler.validate_phi_access(
                user_id=user_id,
                patient_id=patient_id,
                data_type=data_type,
                required_access=access_level
            )
            
            if not has_access and user_id != patient_id:
                # Log unauthorized access attempt
                PHIHandler.log_phi_access(
                    user_id=user_id,
                    patient_id=patient_id,
                    data_type=data_type,
                    action="access_denied",
                    request_id=getattr(request.state, "request_id", None) if request else None,
                    ip=ip
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this data"
                )
            
            # Log successful access
            PHIHandler.log_phi_access(
                user_id=user_id,
                patient_id=patient_id,
                data_type=data_type,
                action=access_level.value,
                request_id=getattr(request.state, "request_id", None) if request else None,
                ip=ip
            )
            
            # Call the original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_phi_operation(
    data_type: PHIDataType,
    action: str,
    patient_id_param: str = "patient_id",
    resource_id_param: Optional[str] = None
):
    """
    Decorator to log PHI operations without enforcing access control.
    Useful for operations where access is already validated.
    
    Args:
        data_type: Type of PHI data
        action: Action being performed (create, update, delete, export)
        patient_id_param: Name of parameter containing patient ID
        resource_id_param: Optional name of parameter containing resource ID
        
    Usage:
        @router.post("/medications")
        @log_phi_operation(PHIDataType.MEDICATIONS, "create")
        async def create_medication(
            medication: MedicationCreate,
            current_user: User = Depends(get_current_user)
        ):
            # Operation is logged automatically
            return created_medication
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract parameters
            patient_id = kwargs.get(patient_id_param)
            current_user = kwargs.get("current_user")
            request = kwargs.get("request")
            
            if not patient_id or not current_user:
                # If required params missing, just call function
                # (will likely fail with appropriate error)
                return await func(*args, **kwargs)
            
            # Extract optional resource ID
            resource_id = None
            if resource_id_param:
                resource_id = kwargs.get(resource_id_param)
            
            # Extract IP
            ip = None
            if request and isinstance(request, Request):
                ip = request.client.host if request.client else None
            
            # Log the operation
            PHIHandler.log_phi_access(
                user_id=str(current_user.id),
                patient_id=patient_id,
                data_type=data_type,
                action=action,
                resource_id=resource_id,
                request_id=getattr(request.state, "request_id", None) if request else None,
                ip=ip
            )
            
            # Call the original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class PHIAccessValidator:
    """
    Helper class for validating PHI access in API endpoints.
    Can be used as a dependency or called directly.
    """
    
    @staticmethod
    async def validate_patient_access(
        patient_id: str,
        current_user: User,
        data_type: PHIDataType,
        access_level: PHIAccessLevel = PHIAccessLevel.READ
    ) -> None:
        """
        Validate that current user has access to patient's PHI.
        Raises HTTPException if access is denied.
        
        Args:
            patient_id: ID of patient whose data is being accessed
            current_user: Current authenticated user
            data_type: Type of PHI data
            access_level: Required access level
            
        Raises:
            HTTPException: If access is denied
        """
        user_id = str(current_user.id)
        
        # Self-access always allowed
        if user_id == patient_id:
            return
        
        # Validate access through PHI handler
        has_access = PHIHandler.validate_phi_access(
            user_id=user_id,
            patient_id=patient_id,
            data_type=data_type,
            required_access=access_level
        )
        
        if not has_access:
            logger.warning(
                f"Access denied: user={user_id} patient={patient_id} "
                f"type={data_type.value} level={access_level.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this data"
            )
    
    @staticmethod
    async def validate_caregiver_access(
        patient_id: str,
        caregiver_id: str
    ) -> bool:
        """
        Validate that caregiver has active access to patient data.
        
        Args:
            patient_id: ID of patient
            caregiver_id: ID of caregiver
            
        Returns:
            True if access is granted, False otherwise
            
        Note:
            In production, this should query the database for
            active caregiver access grants.
        """
        # TODO: Implement database query for caregiver access
        # For now, log the check
        logger.info(
            f"Caregiver access check: patient={patient_id} caregiver={caregiver_id}"
        )
        return False
    
    @staticmethod
    async def validate_provider_access(
        patient_id: str,
        provider_id: str,
        data_type: PHIDataType
    ) -> bool:
        """
        Validate that provider has access to specific patient data type.
        
        Args:
            patient_id: ID of patient
            provider_id: ID of provider
            data_type: Type of PHI data
            
        Returns:
            True if access is granted, False otherwise
            
        Note:
            In production, this should query the ProviderAccess model
            for granular permissions.
        """
        # TODO: Implement database query for provider access
        # Check ProviderAccess model for specific permissions
        logger.info(
            f"Provider access check: patient={patient_id} provider={provider_id} "
            f"type={data_type.value}"
        )
        return False


__all__ = [
    "require_phi_access",
    "log_phi_operation",
    "PHIAccessValidator",
]
