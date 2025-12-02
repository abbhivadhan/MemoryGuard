import json
import logging
import time
import uuid

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.audit import audit_logger
from app.core.config import settings
from app.core.database import check_db_connection
from app.core.input_validation import input_validator
from app.core.logging_config import setup_logging, get_logger
from app.core.rate_limiter import rate_limit_middleware
from app.core.redis import redis_client
from app.core.security import verify_access_token
from app.core.sentry_config import init_sentry

# Configure logging
setup_logging()
logger = get_logger(__name__)

# Initialize Sentry error tracking
init_sentry()


def _get_client_ip(request: Request) -> str:
    """Extract client IP from headers or request client info."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize Redis connection
    try:
        redis_client.connect()
        logger.info("Redis connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
    
    # Check database connection (non-blocking in dev mode)
    try:
        if check_db_connection():
            logger.info("Database connection verified")
        else:
            logger.warning("Database connection check failed - continuing in dev mode")
    except Exception as e:
        logger.warning(f"Database connection error: {e} - continuing in dev mode")
    
    # Run startup migrations (for Render free tier without shell access)
    try:
        from app.core.startup_migrations import run_startup_migrations
        run_startup_migrations()
    except Exception as e:
        logger.warning(f"Startup migrations failed: {e} - continuing anyway")
    
    # Load ML models on startup - TEMPORARILY DISABLED FOR FASTER STARTUP
    logger.warning("ML model pre-loading disabled for faster startup. Models will load on first use.")
    # try:
    #     from app.ml.model_registry import get_model_registry
    #     
    #     registry = get_model_registry()
    #     summary = registry.get_registry_summary()
    #     
    #     if summary['production_version']:
    #         logger.info(f"Production model available: {summary['production_version']}")
    #     elif summary['latest_model']:
    #         logger.info(f"Latest model available: {summary['latest_model']['version']}")
    #     else:
    #         logger.warning("No trained ML models found. Models need to be trained.")
    #     
    #     # Pre-load models for faster first prediction
    #     logger.info("Pre-loading ML models...")
    #     from app.services.ml_service import MLService
    #     from app.core.database import SessionLocal
    #     
    #     db = SessionLocal()
    #     try:
    #         ml_service = MLService(db)
    #         if ml_service.ensemble_model and ml_service.ensemble_model.is_trained:
    #             logger.info(f"ML models loaded successfully: {ml_service.model_version}")
    #         else:
    #             logger.warning("ML models not loaded - predictions will not be available")
    #     finally:
    #         db.close()
    #         
    # except Exception as e:
    #     logger.error(f"Error loading ML models: {e}")
    #     logger.warning("Application will start without ML capabilities")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    redis_client.disconnect()

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Alzheimer's Early Detection & Support",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication context middleware
@app.middleware("http")
async def attach_auth_context(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = verify_access_token(token)
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")
        except HTTPException:
            request.state.user_id = None
        except Exception as exc:
            logger.debug("Auth context middleware error: %s", exc)
    return await call_next(request)


# Input validation middleware
@app.middleware("http")
async def validate_request_payload(request: Request, call_next):
    if not settings.INPUT_VALIDATION_ENABLED:
        return await call_next(request)
    
    if request.query_params:
        params = {key: value for key, value in request.query_params.multi_items()}
        input_validator.validate_query_params(params)
    
    input_validator.validate_headers(request.headers)
    
    content_type = request.headers.get("content-type", "").lower()
    should_inspect_body = (
        request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}
        and "application/json" in content_type
    )
    
    if should_inspect_body:
        body_bytes = await request.body()
        if body_bytes:
            input_validator.enforce_body_size(body_bytes)
            try:
                payload = json.loads(body_bytes.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Malformed JSON payload.",
                ) from exc
            sanitized_payload = input_validator.sanitize_payload(payload)
            request._body = json.dumps(sanitized_payload).encode("utf-8")
        else:
            request._body = body_bytes
    
    return await call_next(request)


# Rate limiting middleware
@app.middleware("http")
async def rate_limiting(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)


# Audit logging middleware
@app.middleware("http")
async def audit_trail(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.client_ip = _get_client_ip(request)
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as exc:
        duration = time.time() - start_time
        audit_logger.log_event(
            event_type="http.request",
            user_id=getattr(request.state, "user_id", None),
            ip=request.state.client_ip,
            path=request.url.path,
            method=request.method,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            metadata={"duration_ms": int(duration * 1000), "error": str(exc)},
            request_id=request_id,
        )
        raise
    
    duration = time.time() - start_time
    audit_logger.log_event(
        event_type="http.request",
        user_id=getattr(request.state, "user_id", None),
        ip=request.state.client_ip,
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        metadata={"duration_ms": int(duration * 1000)},
        request_id=request_id,
    )
    response.headers["X-Request-ID"] = request_id
    return response


# Request logging and performance monitoring middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    from app.core.performance_monitor import performance_metrics
    
    start_time = time.time()
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    user_id = getattr(request.state, "user_id", "anonymous")
    
    logger.info(
        "Request: %s %s [request_id=%s user=%s]",
        request.method,
        request.url.path,
        request_id,
        user_id,
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        process_time_ms = process_time * 1000
        
        # Record performance metrics
        performance_metrics.record_request(
            request.url.path,
            process_time_ms,
            response.status_code
        )
        
        logger.info(
            "Response: %s %s Status: %s Duration: %.3fs [request_id=%s]",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            request_id,
        )
        response.headers.setdefault("X-Request-ID", request_id)
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        process_time_ms = process_time * 1000
        
        # Record error in performance metrics
        performance_metrics.record_request(
            request.url.path,
            process_time_ms,
            500
        )
        
        logger.error(
            "Error: %s %s Duration: %.3fs Error: %s [request_id=%s]",
            request.method,
            request.url.path,
            process_time,
            str(e),
            request_id,
        )
        raise


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = settings.CONTENT_SECURITY_POLICY
    response.headers["Referrer-Policy"] = settings.REFERRER_POLICY
    response.headers["Permissions-Policy"] = settings.PERMISSIONS_POLICY
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-site"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else "Please contact support",
                "timestamp": time.time()
            }
        }
    )

# Include API routers
from app.api.v1 import api_router as v1_router

app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/migration-status")
async def migration_status():
    """Check if critical migrations have been applied"""
    from sqlalchemy import text
    from app.core.database import engine
    
    try:
        with engine.connect() as conn:
            # Check photo_url column type
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'face_profiles' 
                AND column_name = 'photo_url'
            """))
            
            column_info = result.fetchone()
            
            if not column_info:
                return {
                    "status": "pending",
                    "message": "face_profiles table not created yet",
                    "photo_url_migration": "not_applicable"
                }
            
            current_type = column_info[1]
            max_length = column_info[2]
            
            if current_type == 'text':
                return {
                    "status": "complete",
                    "message": "All migrations applied successfully",
                    "photo_url_migration": "complete",
                    "photo_url_type": "TEXT"
                }
            else:
                return {
                    "status": "incomplete",
                    "message": "Migration needed - redeploy to apply",
                    "photo_url_migration": "needed",
                    "photo_url_type": f"{current_type}({max_length})"
                }
                
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
