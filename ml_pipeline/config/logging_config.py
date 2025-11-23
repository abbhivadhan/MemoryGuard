"""
Logging configuration for the ML pipeline
Implements structured logging with timestamps for all operations
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional

from ml_pipeline.config.settings import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information"""
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add context information
        if not hasattr(record, 'operation'):
            record.operation = 'general'
        if not hasattr(record, 'user_id'):
            record.user_id = 'system'
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: bool = True
) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_console: Whether to enable console logging
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("ml_pipeline")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = StructuredFormatter(
        fmt='%(timestamp)s - %(name)s - %(levelname)s - %(operation)s - %(user_id)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler (max 10MB per file, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_audit_logging() -> logging.Logger:
    """
    Set up audit logging for compliance
    Maintains logs for 7 years as per requirements
    """
    audit_logger = logging.getLogger("ml_pipeline.audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.handlers.clear()
    
    # Audit log formatter
    audit_formatter = StructuredFormatter(
        fmt='%(timestamp)s - AUDIT - %(operation)s - %(user_id)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Daily rotating file handler
    audit_log_path = settings.LOGS_PATH / "audit.log"
    audit_handler = TimedRotatingFileHandler(
        audit_log_path,
        when='midnight',
        interval=1,
        backupCount=365 * 7  # Keep 7 years
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(audit_formatter)
    audit_logger.addHandler(audit_handler)
    
    return audit_logger


# Initialize loggers
main_logger = setup_logging(
    log_level="INFO",
    log_file=settings.LOGS_PATH / "ml_pipeline.log",
    enable_console=True
)

audit_logger = setup_audit_logging()


def log_operation(operation: str, user_id: str = "system", **kwargs):
    """
    Log an operation with structured information
    
    Args:
        operation: Operation name
        user_id: User performing the operation
        **kwargs: Additional context information
    """
    extra = {
        'operation': operation,
        'user_id': user_id,
        **kwargs
    }
    return extra


def log_audit(operation: str, user_id: str, details: str):
    """
    Log an audit event
    
    Args:
        operation: Operation performed
        user_id: User who performed the operation
        details: Additional details
    """
    audit_logger.info(
        details,
        extra={'operation': operation, 'user_id': user_id}
    )
