"""
Performance monitoring utilities for tracking API response times,
database queries, and system metrics.
"""
import time
import functools
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

from app.core.logging_config import get_logger
from app.core.redis import redis_client

logger = get_logger(__name__)


class PerformanceMetrics:
    """
    In-memory performance metrics storage with Redis backup.
    Tracks response times, throughput, and error rates.
    """
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self.counters: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
    
    def record_request(self, endpoint: str, duration_ms: float, status_code: int) -> None:
        """
        Record a request's performance metrics.
        
        Args:
            endpoint: API endpoint path
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
        """
        key = f"endpoint:{endpoint}"
        
        # Store duration
        self.metrics[key].append({
            "duration_ms": duration_ms,
            "status_code": status_code,
            "timestamp": time.time()
        })
        
        # Increment counters
        self.counters[f"{key}:total"] += 1
        
        if status_code >= 400:
            self.error_counts[key] += 1
        
        # Store in Redis for persistence (async, non-blocking)
        try:
            redis_key = f"perf:{key}:recent"
            redis_client.client.lpush(redis_key, f"{duration_ms}:{status_code}:{time.time()}")
            redis_client.client.ltrim(redis_key, 0, 99)  # Keep last 100
            redis_client.client.expire(redis_key, 3600)  # 1 hour TTL
        except Exception as e:
            logger.debug(f"Failed to store metrics in Redis: {e}")
    
    def record_db_query(self, query_type: str, duration_ms: float) -> None:
        """
        Record a database query's performance.
        
        Args:
            query_type: Type of query (SELECT, INSERT, UPDATE, etc.)
            duration_ms: Query duration in milliseconds
        """
        key = f"db:{query_type}"
        self.metrics[key].append({
            "duration_ms": duration_ms,
            "timestamp": time.time()
        })
        self.counters[f"{key}:total"] += 1
    
    def record_ml_inference(self, model_name: str, duration_ms: float, success: bool) -> None:
        """
        Record ML model inference performance.
        
        Args:
            model_name: Name of the ML model
            duration_ms: Inference duration in milliseconds
            success: Whether inference was successful
        """
        key = f"ml:{model_name}"
        self.metrics[key].append({
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": time.time()
        })
        self.counters[f"{key}:total"] += 1
        
        if not success:
            self.error_counts[key] += 1
    
    def get_endpoint_stats(self, endpoint: str, time_window_seconds: int = 300) -> Dict[str, Any]:
        """
        Get statistics for a specific endpoint.
        
        Args:
            endpoint: API endpoint path
            time_window_seconds: Time window for statistics (default 5 minutes)
        
        Returns:
            Dictionary with performance statistics
        """
        key = f"endpoint:{endpoint}"
        metrics = self.metrics.get(key, deque())
        
        if not metrics:
            return {
                "endpoint": endpoint,
                "sample_count": 0,
                "error": "No data available"
            }
        
        # Filter by time window
        cutoff_time = time.time() - time_window_seconds
        recent_metrics = [m for m in metrics if m["timestamp"] >= cutoff_time]
        
        if not recent_metrics:
            return {
                "endpoint": endpoint,
                "sample_count": 0,
                "error": "No recent data"
            }
        
        durations = [m["duration_ms"] for m in recent_metrics]
        error_count = sum(1 for m in recent_metrics if m["status_code"] >= 400)
        
        return {
            "endpoint": endpoint,
            "time_window_seconds": time_window_seconds,
            "sample_count": len(recent_metrics),
            "total_requests": self.counters.get(f"{key}:total", 0),
            "error_count": error_count,
            "error_rate": error_count / len(recent_metrics) if recent_metrics else 0,
            "duration_ms": {
                "min": min(durations),
                "max": max(durations),
                "mean": statistics.mean(durations),
                "median": statistics.median(durations),
                "p95": statistics.quantiles(durations, n=20)[18] if len(durations) > 1 else durations[0],
                "p99": statistics.quantiles(durations, n=100)[98] if len(durations) > 1 else durations[0],
            }
        }
    
    def get_all_stats(self, time_window_seconds: int = 300) -> Dict[str, Any]:
        """
        Get statistics for all tracked metrics.
        
        Args:
            time_window_seconds: Time window for statistics
        
        Returns:
            Dictionary with all performance statistics
        """
        stats = {
            "time_window_seconds": time_window_seconds,
            "timestamp": time.time(),
            "endpoints": {},
            "database": {},
            "ml_models": {}
        }
        
        # Endpoint stats
        for key in self.metrics.keys():
            if key.startswith("endpoint:"):
                endpoint = key.replace("endpoint:", "")
                stats["endpoints"][endpoint] = self.get_endpoint_stats(endpoint, time_window_seconds)
        
        # Database stats
        for key in self.metrics.keys():
            if key.startswith("db:"):
                query_type = key.replace("db:", "")
                metrics = [m for m in self.metrics[key] if m["timestamp"] >= time.time() - time_window_seconds]
                if metrics:
                    durations = [m["duration_ms"] for m in metrics]
                    stats["database"][query_type] = {
                        "sample_count": len(metrics),
                        "mean_ms": statistics.mean(durations),
                        "median_ms": statistics.median(durations),
                        "max_ms": max(durations)
                    }
        
        # ML model stats
        for key in self.metrics.keys():
            if key.startswith("ml:"):
                model_name = key.replace("ml:", "")
                metrics = [m for m in self.metrics[key] if m["timestamp"] >= time.time() - time_window_seconds]
                if metrics:
                    durations = [m["duration_ms"] for m in metrics]
                    success_count = sum(1 for m in metrics if m.get("success", True))
                    stats["ml_models"][model_name] = {
                        "sample_count": len(metrics),
                        "success_rate": success_count / len(metrics),
                        "mean_ms": statistics.mean(durations),
                        "median_ms": statistics.median(durations)
                    }
        
        return stats


# Global performance metrics instance
performance_metrics = PerformanceMetrics()


def track_performance(metric_type: str = "endpoint"):
    """
    Decorator to track function performance.
    
    Args:
        metric_type: Type of metric (endpoint, db, ml)
    
    Example:
        @track_performance("endpoint")
        async def my_endpoint():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                if metric_type == "endpoint":
                    status_code = 500 if error else 200
                    performance_metrics.record_request(
                        func.__name__,
                        duration_ms,
                        status_code
                    )
                elif metric_type == "db":
                    performance_metrics.record_db_query(
                        func.__name__,
                        duration_ms
                    )
                elif metric_type == "ml":
                    performance_metrics.record_ml_inference(
                        func.__name__,
                        duration_ms,
                        error is None
                    )
                
                logger.debug(
                    f"Performance: {func.__name__} completed in {duration_ms:.2f}ms",
                    extra={"duration_ms": duration_ms, "function": func.__name__}
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                if metric_type == "db":
                    performance_metrics.record_db_query(
                        func.__name__,
                        duration_ms
                    )
                elif metric_type == "ml":
                    performance_metrics.record_ml_inference(
                        func.__name__,
                        duration_ms,
                        error is None
                    )
                
                logger.debug(
                    f"Performance: {func.__name__} completed in {duration_ms:.2f}ms",
                    extra={"duration_ms": duration_ms, "function": func.__name__}
                )
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
