"""
Rate limit management endpoints for administrators.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Optional
from pydantic import BaseModel
from app.core.rate_limiter import rate_limiter, get_rate_limit_info, RateLimitConfig
from app.api.dependencies import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rate-limits", tags=["rate-limits"])


class RateLimitStatus(BaseModel):
    """Rate limit status response model"""
    limit: int
    remaining: int
    reset: int
    used: int
    endpoint: str


class RateLimitResetRequest(BaseModel):
    """Request model for resetting rate limits"""
    identifier: str
    endpoint: str


@router.get("/status", response_model=RateLimitStatus)
async def get_current_rate_limit_status(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get current rate limit status for the authenticated user.
    
    Returns:
        Current rate limit information including remaining requests
    """
    try:
        rate_limit_info = get_rate_limit_info(request, str(current_user.id))
        
        return RateLimitStatus(
            limit=rate_limit_info['limit'],
            remaining=rate_limit_info['remaining'],
            reset=rate_limit_info['reset'],
            used=rate_limit_info['used'],
            endpoint=request.url.path
        )
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve rate limit status"
        )


@router.get("/config")
async def get_rate_limit_config(
    current_user: User = Depends(get_current_user)
):
    """
    Get rate limit configuration for all endpoints.
    
    Returns:
        Dictionary of endpoint rate limits
    """
    return {
        "default_limit": RateLimitConfig.DEFAULT_LIMIT,
        "window_seconds": 60,
        "endpoint_limits": RateLimitConfig.ENDPOINT_LIMITS
    }


@router.post("/reset")
async def reset_rate_limit(
    reset_request: RateLimitResetRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Reset rate limit for a specific identifier and endpoint.
    
    Note: This endpoint should be restricted to administrators in production.
    Currently allows users to reset their own rate limits.
    
    Args:
        reset_request: Contains identifier and endpoint to reset
        
    Returns:
        Success message
    """
    try:
        # In production, add admin check here
        # For now, users can only reset their own rate limits
        user_identifier = f"user:{current_user.id}"
        
        if reset_request.identifier != user_identifier:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only reset your own rate limits"
            )
        
        success = rate_limiter.reset_rate_limit(
            reset_request.identifier,
            reset_request.endpoint
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset rate limit"
            )
        
        return {
            "message": "Rate limit reset successfully",
            "identifier": reset_request.identifier,
            "endpoint": reset_request.endpoint
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting rate limit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset rate limit"
        )
