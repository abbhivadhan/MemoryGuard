"""
Redis caching utilities for ML pipeline
Implements caching for frequently accessed features and model predictions
"""
import json
import pickle
from typing import Any, Optional, Callable
from functools import wraps
import hashlib

import redis
from redis.connection import ConnectionPool

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import main_logger


class RedisCache:
    """
    Redis cache client with connection pooling
    """
    
    def __init__(self):
        """Initialize Redis connection pool"""
        try:
            # Create connection pool
            self.pool = ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=False,  # We'll handle encoding/decoding
                max_connections=50
            )
            
            # Create Redis client
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            self.client.ping()
            
            main_logger.info(
                "Redis cache initialized",
                extra={'operation': 'cache_init', 'user_id': 'system'}
            )
            
        except Exception as e:
            main_logger.error(
                f"Failed to initialize Redis cache: {str(e)}",
                extra={'operation': 'cache_init', 'user_id': 'system'}
            )
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists, None otherwise
        """
        try:
            value = self.client.get(key)
            if value is not None:
                # Try to unpickle
                try:
                    return pickle.loads(value)
                except:
                    # If unpickling fails, return as string
                    return value.decode('utf-8')
            return None
            
        except Exception as e:
            main_logger.error(
                f"Failed to get cache key {key}: {str(e)}",
                extra={'operation': 'cache_get', 'user_id': 'system'}
            )
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default from settings)
            
        Returns:
            True if successful
        """
        try:
            # Pickle the value
            pickled_value = pickle.dumps(value)
            
            # Set with TTL
            ttl = ttl or settings.CACHE_TTL
            self.client.setex(key, ttl, pickled_value)
            
            return True
            
        except Exception as e:
            main_logger.error(
                f"Failed to set cache key {key}: {str(e)}",
                extra={'operation': 'cache_set', 'user_id': 'system'}
            )
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            main_logger.error(
                f"Failed to delete cache key {key}: {str(e)}",
                extra={'operation': 'cache_delete', 'user_id': 'system'}
            )
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            main_logger.error(
                f"Failed to check cache key {key}: {str(e)}",
                extra={'operation': 'cache_exists', 'user_id': 'system'}
            )
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern
        
        Args:
            pattern: Pattern to match (e.g., "features:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            main_logger.error(
                f"Failed to clear cache pattern {pattern}: {str(e)}",
                extra={'operation': 'cache_clear', 'user_id': 'system'}
            )
            return 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        try:
            info = self.client.info('stats')
            return {
                'total_connections': info.get('total_connections_received', 0),
                'total_commands': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
        except Exception as e:
            main_logger.error(
                f"Failed to get cache stats: {str(e)}",
                extra={'operation': 'cache_stats', 'user_id': 'system'}
            )
            return {}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return 0.0
        return hits / total * 100
    
    def flush_all(self) -> bool:
        """
        Flush all cache data (use with caution)
        
        Returns:
            True if successful
        """
        try:
            self.client.flushdb()
            main_logger.warning(
                "Cache flushed",
                extra={'operation': 'cache_flush', 'user_id': 'system'}
            )
            return True
        except Exception as e:
            main_logger.error(
                f"Failed to flush cache: {str(e)}",
                extra={'operation': 'cache_flush', 'user_id': 'system'}
            )
            return False
    
    def health_check(self) -> bool:
        """
        Check if Redis is healthy
        
        Returns:
            True if healthy
        """
        try:
            self.client.ping()
            return True
        except:
            return False


# Global cache instance
cache = RedisCache()


def cache_result(
    key_prefix: str,
    ttl: Optional[int] = None,
    use_args: bool = True
):
    """
    Decorator to cache function results
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
        use_args: Whether to include function arguments in cache key
        
    Usage:
        @cache_result('features', ttl=3600)
        def get_patient_features(patient_id: str):
            # Expensive operation
            return features
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if use_args:
                # Create hash of arguments
                args_str = json.dumps({
                    'args': [str(arg) for arg in args],
                    'kwargs': {k: str(v) for k, v in kwargs.items()}
                }, sort_keys=True)
                args_hash = hashlib.md5(args_str.encode()).hexdigest()
                cache_key = f"{key_prefix}:{func.__name__}:{args_hash}"
            else:
                cache_key = f"{key_prefix}:{func.__name__}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                main_logger.debug(
                    f"Cache hit for {cache_key}",
                    extra={'operation': 'cache_hit', 'user_id': 'system'}
                )
                return cached_value
            
            # Cache miss - execute function
            main_logger.debug(
                f"Cache miss for {cache_key}",
                extra={'operation': 'cache_miss', 'user_id': 'system'}
            )
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


class FeatureCache:
    """
    Specialized cache for ML features
    """
    
    @staticmethod
    def get_patient_features(patient_id: str) -> Optional[dict]:
        """Get cached patient features"""
        key = f"features:patient:{patient_id}"
        return cache.get(key)
    
    @staticmethod
    def set_patient_features(
        patient_id: str,
        features: dict,
        ttl: int = 3600
    ) -> bool:
        """Cache patient features"""
        key = f"features:patient:{patient_id}"
        return cache.set(key, features, ttl=ttl)
    
    @staticmethod
    def clear_patient_features(patient_id: str) -> bool:
        """Clear cached patient features"""
        key = f"features:patient:{patient_id}"
        return cache.delete(key)


class ModelCache:
    """
    Specialized cache for ML models
    """
    
    @staticmethod
    def get_model(model_name: str, version_id: str) -> Optional[Any]:
        """Get cached model"""
        key = f"model:{model_name}:{version_id}"
        return cache.get(key)
    
    @staticmethod
    def set_model(
        model_name: str,
        version_id: str,
        model: Any,
        ttl: int = 7200
    ) -> bool:
        """Cache model (2 hour default TTL)"""
        key = f"model:{model_name}:{version_id}"
        return cache.set(key, model, ttl=ttl)
    
    @staticmethod
    def clear_model(model_name: str, version_id: str) -> bool:
        """Clear cached model"""
        key = f"model:{model_name}:{version_id}"
        return cache.delete(key)
    
    @staticmethod
    def clear_all_models() -> int:
        """Clear all cached models"""
        return cache.clear_pattern("model:*")


class PredictionCache:
    """
    Specialized cache for predictions
    """
    
    @staticmethod
    def get_prediction(patient_id: str, model_version: str) -> Optional[dict]:
        """Get cached prediction"""
        key = f"prediction:{patient_id}:{model_version}"
        return cache.get(key)
    
    @staticmethod
    def set_prediction(
        patient_id: str,
        model_version: str,
        prediction: dict,
        ttl: int = 1800
    ) -> bool:
        """Cache prediction (30 minute default TTL)"""
        key = f"prediction:{patient_id}:{model_version}"
        return cache.set(key, prediction, ttl=ttl)
    
    @staticmethod
    def clear_prediction(patient_id: str, model_version: str) -> bool:
        """Clear cached prediction"""
        key = f"prediction:{patient_id}:{model_version}"
        return cache.delete(key)
