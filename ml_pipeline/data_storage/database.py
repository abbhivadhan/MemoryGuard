"""
Database connection and session management for PostgreSQL
Implements connection pooling for efficient database access
"""
from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import main_logger


# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


# Event listeners for connection pool monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections"""
    main_logger.debug(
        "Database connection established",
        extra={'operation': 'db_connect', 'user_id': 'system'}
    )


@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database disconnections"""
    main_logger.debug(
        "Database connection closed",
        extra={'operation': 'db_close', 'user_id': 'system'}
    )


def get_db() -> Generator[Session, None, None]:
    """
    Get database session
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions
    
    Usage:
        with get_db_context() as db:
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        main_logger.error(
            f"Database transaction failed: {str(e)}",
            extra={'operation': 'db_transaction', 'user_id': 'system'}
        )
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        main_logger.info(
            "Database tables created successfully",
            extra={'operation': 'db_init', 'user_id': 'system'}
        )
    except Exception as e:
        main_logger.error(
            f"Failed to create database tables: {str(e)}",
            extra={'operation': 'db_init', 'user_id': 'system'}
        )
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working
    
    Returns:
        True if connection successful
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        main_logger.info(
            "Database connection check successful",
            extra={'operation': 'db_health_check', 'user_id': 'system'}
        )
        return True
    except Exception as e:
        main_logger.error(
            f"Database connection check failed: {str(e)}",
            extra={'operation': 'db_health_check', 'user_id': 'system'}
        )
        return False


def get_pool_status() -> dict:
    """
    Get connection pool status
    
    Returns:
        Dictionary with pool statistics
    """
    pool_obj = engine.pool
    return {
        'size': pool_obj.size(),
        'checked_in': pool_obj.checkedin(),
        'checked_out': pool_obj.checkedout(),
        'overflow': pool_obj.overflow(),
        'total': pool_obj.size() + pool_obj.overflow()
    }
