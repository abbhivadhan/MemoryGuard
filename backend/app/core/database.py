from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Create database engine with connection pooling optimized for Supabase
# Use NullPool in dev mode to avoid connection issues
try:
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,  # Don't pre-connect
        pool_pre_ping=False,  # Don't ping on checkout
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        connect_args={
            "connect_timeout": 2,
            "options": "-c timezone=utc"
        },
        isolation_level="AUTOCOMMIT"  # Avoid transaction overhead
    )
    logger.info("Database engine created (lazy connection)")
except Exception as e:
    logger.warning(f"Database engine creation failed: {e} - running in no-DB mode")
    engine = None

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
) if engine else None

# Create Base class for models
Base = declarative_base()

# Database connection event listeners
if engine:
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        logger.info("Database connection established")

    @event.listens_for(engine, "close")
    def receive_close(dbapi_conn, connection_record):
        logger.info("Database connection closed")

# Dependency to get database session
def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    if not SessionLocal:
        logger.warning("Database not available - using dev mode")
        yield None
        return
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to initialize database
def init_db():
    """
    Initialize database by creating all tables.
    This should be called on application startup.
    Note: With Supabase, you can also use their dashboard for migrations.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully in Supabase")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Function to check database connection
def check_db_connection() -> bool:
    """
    Check if Supabase database connection is working.
    Returns True if connection is successful, False otherwise.
    """
    if not engine:
        logger.warning("Database engine not available")
        return False
        
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
