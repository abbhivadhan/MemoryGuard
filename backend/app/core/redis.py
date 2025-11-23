import redis
from redis import Redis
from typing import Optional, Any
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """
    Redis client wrapper for caching and session management.
    """
    
    def __init__(self):
        self._client: Optional[Redis] = None
    
    def connect(self):
        """Initialize Redis connection"""
        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            # Test connection
            self._client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def disconnect(self):
        """Close Redis connection"""
        if self._client:
            self._client.close()
            logger.info("Redis connection closed")
    
    @property
    def client(self) -> Redis:
        """Get Redis client instance"""
        if not self._client:
            self.connect()
        return self._client
    
    def check_connection(self) -> bool:
        """Check if Redis connection is working"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            return False

# Global Redis client instance
redis_client = RedisClient()

def get_redis() -> Redis:
    """
    Get Redis client instance.
    Used for dependency injection in FastAPI routes.
    """
    return redis_client.client

# Cache utility functions
def get_cache(key: str) -> Optional[Any]:
    """
    Get value from cache by key.
    Returns None if key doesn't exist or on error.
    """
    try:
        value = redis_client.client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Error getting cache for key {key}: {e}")
        return None

def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """
    Set value in cache with expiration time.
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        expire: Expiration time in seconds (default: 1 hour)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        serialized_value = json.dumps(value)
        redis_client.client.setex(key, expire, serialized_value)
        return True
    except Exception as e:
        logger.error(f"Error setting cache for key {key}: {e}")
        return False

def delete_cache(key: str) -> bool:
    """
    Delete value from cache by key.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client.client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Error deleting cache for key {key}: {e}")
        return False

def clear_cache_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "user:*")
    
    Returns:
        Number of keys deleted
    """
    try:
        keys = redis_client.client.keys(pattern)
        if keys:
            return redis_client.client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Error clearing cache pattern {pattern}: {e}")
        return 0

# Session utility functions
def set_session(session_id: str, data: dict, expire: int = 86400) -> bool:
    """
    Store session data in Redis.
    
    Args:
        session_id: Unique session identifier
        data: Session data dictionary
        expire: Expiration time in seconds (default: 24 hours)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        key = f"session:{session_id}"
        return set_cache(key, data, expire)
    except Exception as e:
        logger.error(f"Error setting session {session_id}: {e}")
        return False

def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieve session data from Redis.
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        Session data dictionary or None if not found
    """
    try:
        key = f"session:{session_id}"
        return get_cache(key)
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        return None

def delete_session(session_id: str) -> bool:
    """
    Delete session data from Redis.
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        True if successful, False otherwise
    """
    try:
        key = f"session:{session_id}"
        return delete_cache(key)
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return False

def extend_session(session_id: str, expire: int = 86400) -> bool:
    """
    Extend session expiration time.
    
    Args:
        session_id: Unique session identifier
        expire: New expiration time in seconds (default: 24 hours)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        key = f"session:{session_id}"
        return redis_client.client.expire(key, expire)
    except Exception as e:
        logger.error(f"Error extending session {session_id}: {e}")
        return False

# Rate limiting utility
def check_rate_limit(identifier: str, limit: int = 100, window: int = 60) -> bool:
    """
    Check if request is within rate limit.
    
    Args:
        identifier: Unique identifier (e.g., user_id, IP address)
        limit: Maximum number of requests allowed
        window: Time window in seconds
    
    Returns:
        True if within limit, False if exceeded
    """
    try:
        key = f"rate_limit:{identifier}"
        current = redis_client.client.get(key)
        
        if current is None:
            # First request in window
            redis_client.client.setex(key, window, 1)
            return True
        
        current_count = int(current)
        if current_count >= limit:
            return False
        
        # Increment counter
        redis_client.client.incr(key)
        return True
    except Exception as e:
        logger.error(f"Error checking rate limit for {identifier}: {e}")
        # On error, allow the request
        return True
