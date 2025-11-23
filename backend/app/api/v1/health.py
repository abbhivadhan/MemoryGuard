"""
Health check endpoints for monitoring system status.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import time
import psutil
import os

from app.core.database import get_db, check_db_connection
from app.core.redis import redis_client
from app.core.config import settings
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns overall system health status.
    """
    start_time = time.time()
    
    # Check database
    db_status = check_db_connection()
    
    # Check Redis
    redis_status = redis_client.check_connection()
    
    # Determine overall status
    overall_status = "healthy" if (db_status and redis_status) else "degraded"
    
    response_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "response_time_ms": round(response_time, 2),
        "services": {
            "database": "connected" if db_status else "disconnected",
            "redis": "connected" if redis_status else "disconnected",
        }
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with comprehensive system information.
    Includes database, Redis, ML models, and system resources.
    """
    start_time = time.time()
    health_data: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Database check
    try:
        db_start = time.time()
        db_status = check_db_connection()
        db_latency = (time.time() - db_start) * 1000
        
        health_data["checks"]["database"] = {
            "status": "healthy" if db_status else "unhealthy",
            "latency_ms": round(db_latency, 2),
            "url": settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else "hidden"
        }
        
        if not db_status:
            health_data["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_data["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Redis check
    try:
        redis_start = time.time()
        redis_status = redis_client.check_connection()
        redis_latency = (time.time() - redis_start) * 1000
        
        # Get Redis info if connected
        redis_info = {}
        if redis_status:
            try:
                info = redis_client.client.info()
                redis_info = {
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "uptime_in_days": info.get("uptime_in_days"),
                }
            except Exception:
                pass
        
        health_data["checks"]["redis"] = {
            "status": "healthy" if redis_status else "unhealthy",
            "latency_ms": round(redis_latency, 2),
            "info": redis_info
        }
        
        if not redis_status:
            health_data["status"] = "degraded"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_data["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # ML Models check
    try:
        from app.ml.model_registry import get_model_registry
        
        registry = get_model_registry()
        summary = registry.get_registry_summary()
        
        ml_status = "healthy" if summary.get("production_version") or summary.get("latest_model") else "warning"
        
        health_data["checks"]["ml_models"] = {
            "status": ml_status,
            "production_version": summary.get("production_version"),
            "latest_version": summary.get("latest_model", {}).get("version") if summary.get("latest_model") else None,
            "total_models": summary.get("total_models", 0)
        }
        
        if ml_status == "warning":
            health_data["status"] = "degraded"
    except Exception as e:
        logger.error(f"ML models health check failed: {e}")
        health_data["checks"]["ml_models"] = {
            "status": "warning",
            "error": str(e)
        }
    
    # System resources check
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data["checks"]["system_resources"] = {
            "status": "healthy",
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory.percent, 2),
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": round(disk.percent, 2),
            "disk_free_gb": round(disk.free / (1024**3), 2)
        }
        
        # Warn if resources are high
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_data["checks"]["system_resources"]["status"] = "warning"
            health_data["status"] = "degraded"
    except Exception as e:
        logger.error(f"System resources check failed: {e}")
        health_data["checks"]["system_resources"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    # Celery check (if available)
    try:
        from app.core.celery_app import celery_app
        
        # Check if Celery workers are active
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        celery_status = "healthy" if active_workers else "warning"
        
        health_data["checks"]["celery"] = {
            "status": celery_status,
            "active_workers": len(active_workers) if active_workers else 0,
            "worker_names": list(active_workers.keys()) if active_workers else []
        }
        
        if celery_status == "warning":
            health_data["status"] = "degraded"
    except Exception as e:
        logger.debug(f"Celery health check skipped: {e}")
        health_data["checks"]["celery"] = {
            "status": "unknown",
            "message": "Celery not configured or not running"
        }
    
    # Calculate total response time
    response_time = (time.time() - start_time) * 1000
    health_data["response_time_ms"] = round(response_time, 2)
    
    return health_data


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes/container orchestration.
    Returns 200 if the service is ready to accept traffic.
    """
    # Check critical services
    db_status = check_db_connection()
    redis_status = redis_client.check_connection()
    
    is_ready = db_status and redis_status
    
    return {
        "ready": is_ready,
        "timestamp": time.time(),
        "checks": {
            "database": db_status,
            "redis": redis_status,
        }
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes/container orchestration.
    Returns 200 if the service is alive (even if degraded).
    """
    return {
        "alive": True,
        "timestamp": time.time(),
        "uptime_seconds": time.time() - psutil.Process(os.getpid()).create_time()
    }


@router.get("/health/startup")
async def startup_check() -> Dict[str, Any]:
    """
    Startup check for Kubernetes/container orchestration.
    Returns 200 when the service has completed initialization.
    """
    # Check if critical components are initialized
    db_status = check_db_connection()
    
    # Check if ML models are loaded (optional)
    ml_loaded = False
    try:
        from app.ml.model_registry import get_model_registry
        registry = get_model_registry()
        summary = registry.get_registry_summary()
        ml_loaded = bool(summary.get("production_version") or summary.get("latest_model"))
    except Exception:
        pass
    
    is_started = db_status  # ML models are optional for startup
    
    return {
        "started": is_started,
        "timestamp": time.time(),
        "checks": {
            "database": db_status,
            "ml_models_loaded": ml_loaded,
        }
    }


@router.get("/health/metrics")
async def performance_metrics() -> Dict[str, Any]:
    """
    Get performance metrics for monitoring.
    Includes API response times, database query performance, and ML inference times.
    """
    from app.core.performance_monitor import performance_metrics
    
    # Get stats for last 5 minutes
    stats = performance_metrics.get_all_stats(time_window_seconds=300)
    
    return stats
