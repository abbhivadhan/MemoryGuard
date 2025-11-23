"""
Rate limiting middleware and utilities for API endpoints.
Implements token bucket algorithm using Redis for distributed rate limiting.
"""
from typing import Optional, Dict, Tuple, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import logging
from app.core.redis import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Configuration for rate limiting rules per endpoint."""
    
    # Default rate limits (requests per minute)
    DEFAULT_LIMIT = settings.RATE_LIMIT_PER_MINUTE
    
    # Endpoint-specific rate limits (requests per minute)
    ENDPOINT_LIMITS: Dict[str, int] = {
        # Authentication endpoints - moderate limits
        "/api/v1/auth/google": 10,
        "/api/v1/auth/refresh": 20,
        "/api/v1/auth/logout": 20,
        
        # ML prediction endpoints - lower limits (resource intensive)
        "/api/v1/ml/predict": 10,
        "/api/v1/ml/explain": 20,
        
        # Health metrics - higher limits (frequent updates)
        "/api/v1/health/metrics": 200,
        
        # Assessments - moderate limits
        "/api/v1/assessments/start": 20,
        "/api/v1/assessments/complete": 20,
        
        # Imaging uploads - very low limits (large files)
        "/api/v1/imaging/upload": 5,
        
        # Emergency endpoints - higher limits (critical)
        "/api/v1/emergency/alert": 50,
        
        # Community endpoints - moderate limits
        "/api/v1/community/posts": 60,
        
        # Medications - higher limits (frequent access)
        "/api/v1/medications": 100,
        
        # Reminders - higher limits (frequent access)
        "/api/v1/reminders": 100,
    }
    
    @classmethod
    def get_limit_for_endpoint(cls, path: str) -> int:
        """
        Get rate limit for a specific endpoint.
        
        Args:
            path: Request path
            
        Returns:
            Rate limit (requests per minute)
        """
        # Check for exact match
        if path in cls.ENDPOINT_LIMITS:
            return cls.ENDPOINT_LIMITS[path]
        
        # Check for prefix match (e.g., /api/v1/health/metrics/123)
        for endpoint_path, limit in cls.ENDPOINT_LIMITS.items():
            if path.startswith(endpoint_path):
                return limit
        
        # Return default limit
        return cls.DEFAULT_LIMIT


class RateLimiter:
    """
    Rate limiter using token bucket algorithm with Redis backend.
    Supports per-user and per-IP rate limiting.
    """
    
    def __init__(self):
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS or 60  # default fallback
    
    def _rate_limit_info(self, limit: int, remaining: int, reset_time: Optional[int] = None) -> Dict[str, Any]:
        """
        Build a standard rate limit metadata payload.
        """
        if reset_time is None:
            reset_time = int(time.time()) + self.window_seconds
        
        return {
            "limit": limit,
            "remaining": max(0, remaining),
            "reset": reset_time,
            "reset_in_seconds": max(0, reset_time - int(time.time()))
        }
    
    def _get_identifier(self, request: Request, user_id: Optional[str] = None) -> str:
        """
        Get unique identifier for rate limiting.
        Uses user_id if authenticated, otherwise uses IP address.
        
        Args:
            request: FastAPI request object
            user_id: Optional authenticated user ID
            
        Returns:
            Unique identifier string
        """
        if user_id:
            return f"user:{user_id}"
        
        # Get client IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
    
    def _get_redis_key(self, identifier: str, endpoint: str) -> str:
        """
        Generate Redis key for rate limiting.
        
        Args:
            identifier: User or IP identifier
            endpoint: API endpoint path
            
        Returns:
            Redis key string
        """
        # Use endpoint in key for per-endpoint rate limiting
        return f"rate_limit:{identifier}:{endpoint}"
    
    def check_rate_limit(
        self,
        request: Request,
        user_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit using token bucket algorithm.
        
        Args:
            request: FastAPI request object
            user_id: Optional authenticated user ID
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
            rate_limit_info contains: limit, remaining, reset_time
        """
        limit = RateLimitConfig.get_limit_for_endpoint(request.url.path)

        if not settings.RATE_LIMIT_ENABLED:
            return True, self._rate_limit_info(limit, limit)

        try:
            identifier = self._get_identifier(request, user_id)
            endpoint = request.url.path
            
            redis_key = self._get_redis_key(identifier, endpoint)
            current_time = int(time.time())
            window_start = current_time - self.window_seconds
            
            # Use Redis sorted set for sliding window
            pipe = redis_client.client.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(redis_key, 0, window_start)
            
            # Count requests in current window
            pipe.zcard(redis_key)
            
            # Add current request
            pipe.zadd(redis_key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(redis_key, self.window_seconds + 10)
            
            results = pipe.execute()
            request_count = results[1]  # Count before adding current request
            
            # Calculate remaining requests
            remaining = max(0, limit - request_count - 1)
            reset_time = current_time + self.window_seconds
            
            rate_limit_info = self._rate_limit_info(limit, remaining, reset_time)
            
            # Check if limit exceeded
            if request_count >= limit:
                logger.warning(
                    f"Rate limit exceeded for {identifier} on {endpoint}. "
                    f"Count: {request_count}, Limit: {limit}"
                )
                return False, rate_limit_info
            
            return True, rate_limit_info
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}", exc_info=True)
            # On error, allow the request (fail open)
            return True, self._rate_limit_info(limit, limit)
    
    def reset_rate_limit(self, identifier: str, endpoint: str) -> bool:
        """
        Reset rate limit for a specific identifier and endpoint.
        Useful for testing or administrative purposes.
        
        Args:
            identifier: User or IP identifier
            endpoint: API endpoint path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            redis_key = self._get_redis_key(identifier, endpoint)
            redis_client.client.delete(redis_key)
            logger.info(f"Rate limit reset for {identifier} on {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")
            return False


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting on all API requests.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler in chain
        
    Returns:
        Response or rate limit error
    """
    if not settings.RATE_LIMIT_ENABLED:
        return await call_next(request)
    
    # Skip rate limiting for health check and root endpoints
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    # Extract user_id from request state if available (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    
    # Check rate limit
    is_allowed, rate_limit_info = rate_limiter.check_rate_limit(request, user_id)
    
    if not is_allowed:
        # Return 429 Too Many Requests
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "details": f"Rate limit: {rate_limit_info['limit']} requests per minute",
                    "retry_after": rate_limit_info['reset_in_seconds']
                }
            },
            headers={
                "X-RateLimit-Limit": str(rate_limit_info['limit']),
                "X-RateLimit-Remaining": str(rate_limit_info['remaining']),
                "X-RateLimit-Reset": str(rate_limit_info['reset']),
                "Retry-After": str(rate_limit_info['reset_in_seconds'])
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limit_info['limit'])
    response.headers["X-RateLimit-Remaining"] = str(rate_limit_info['remaining'])
    response.headers["X-RateLimit-Reset"] = str(rate_limit_info['reset'])
    
    return response


def get_rate_limit_info(request: Request, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current rate limit information for a request without incrementing counter.
    Useful for displaying rate limit status to users.
    
    Args:
        request: FastAPI request object
        user_id: Optional authenticated user ID
        
    Returns:
        Dictionary with rate limit information
    """
    if not settings.RATE_LIMIT_ENABLED:
        limit = RateLimitConfig.get_limit_for_endpoint(request.url.path)
        return rate_limiter._rate_limit_info(limit, limit)

    try:
        identifier = rate_limiter._get_identifier(request, user_id)
        endpoint = request.url.path
        limit = RateLimitConfig.get_limit_for_endpoint(endpoint)
        redis_key = rate_limiter._get_redis_key(identifier, endpoint)
        
        current_time = int(time.time())
        window_start = current_time - rate_limiter.window_seconds
        
        # Count requests in current window
        pipe = redis_client.client.pipeline()
        pipe.zremrangebyscore(redis_key, 0, window_start)
        pipe.zcard(redis_key)
        results = pipe.execute()
        
        request_count = results[1]
        remaining = max(0, limit - request_count)
        reset_time = current_time + rate_limiter.window_seconds
        
        return {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "used": request_count
        }
    except Exception as e:
        logger.error(f"Error getting rate limit info: {e}")
        return {
            "limit": limit,
            "remaining": limit,
            "reset": int(time.time()) + rate_limiter.window_seconds,
            "used": 0
        }
