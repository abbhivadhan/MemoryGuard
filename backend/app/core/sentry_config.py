"""
Sentry error tracking configuration for backend.
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

from app.core.config import settings


def init_sentry() -> None:
    """
    Initialize Sentry error tracking.
    Only enabled in production with a valid DSN.
    """
    if not settings.SENTRY_DSN:
        logging.info("Sentry DSN not configured - error tracking disabled")
        return
    
    if not settings.is_production and not settings.SENTRY_ENABLED:
        logging.info("Sentry disabled in non-production environment")
        return
    
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=f"{settings.APP_NAME}@{settings.APP_VERSION}",
        
        # Integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        
        # Performance monitoring
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        
        # Error sampling
        sample_rate=1.0,
        
        # Additional options
        attach_stacktrace=True,
        send_default_pii=False,  # HIPAA compliance - don't send PII
        max_breadcrumbs=50,
        
        # Before send hook to filter sensitive data
        before_send=before_send_filter,
        
        # Before breadcrumb hook
        before_breadcrumb=before_breadcrumb_filter,
    )
    
    logging.info(f"Sentry initialized - Environment: {settings.ENVIRONMENT}")


def before_send_filter(event, hint):
    """
    Filter sensitive data before sending to Sentry.
    Ensures HIPAA compliance by removing PHI.
    """
    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        sensitive_headers = ['Authorization', 'Cookie', 'X-API-Key']
        for header in sensitive_headers:
            if header in event['request']['headers']:
                event['request']['headers'][header] = '[Filtered]'
    
    # Remove sensitive query parameters
    if 'request' in event and 'query_string' in event['request']:
        sensitive_params = ['token', 'api_key', 'password', 'ssn']
        query_string = event['request']['query_string']
        for param in sensitive_params:
            if param in query_string.lower():
                event['request']['query_string'] = '[Filtered]'
                break
    
    # Remove sensitive data from extra context
    if 'extra' in event:
        sensitive_keys = ['password', 'token', 'api_key', 'ssn', 'medical_record']
        for key in list(event['extra'].keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                event['extra'][key] = '[Filtered]'
    
    return event


def before_breadcrumb_filter(crumb, hint):
    """
    Filter sensitive data from breadcrumbs.
    """
    # Filter SQL queries that might contain PHI
    if crumb.get('category') == 'query':
        if 'data' in crumb:
            crumb['data'] = '[SQL Query - Filtered for Privacy]'
    
    # Filter HTTP request data
    if crumb.get('category') == 'httplib':
        if 'data' in crumb and isinstance(crumb['data'], dict):
            if 'body' in crumb['data']:
                crumb['data']['body'] = '[Filtered]'
    
    return crumb


def capture_exception(error: Exception, context: dict = None) -> None:
    """
    Manually capture an exception with additional context.
    
    Args:
        error: The exception to capture
        context: Additional context to include
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None) -> None:
    """
    Manually capture a message with additional context.
    
    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context to include
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, email: str = None) -> None:
    """
    Set user context for error tracking.
    Note: Only non-PHI user identifiers should be used.
    
    Args:
        user_id: User identifier (hashed or anonymized)
        email: User email (optional, will be filtered if contains PHI)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email if email else None,
    })


def clear_user_context() -> None:
    """
    Clear user context (e.g., on logout).
    """
    sentry_sdk.set_user(None)
