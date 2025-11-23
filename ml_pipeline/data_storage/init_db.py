"""
Database initialization script
Creates all tables and sets up the database schema
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml_pipeline.data_storage.database import init_db, check_db_connection, engine
from ml_pipeline.data_storage.models import (
    ProcessedFeature,
    ModelVersion,
    DataQualityReport,
    DataDriftReport,
    TrainingJob,
    AuditLog
)
from ml_pipeline.config.logging_config import main_logger


def create_database_schema():
    """Create all database tables"""
    try:
        # Check database connection
        if not check_db_connection():
            raise Exception("Cannot connect to database")
        
        # Create all tables
        init_db()
        
        main_logger.info(
            "Database schema created successfully",
            extra={'operation': 'db_init', 'user_id': 'system'}
        )
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'processed_features',
            'model_versions',
            'data_quality_reports',
            'data_drift_reports',
            'training_jobs',
            'audit_logs'
        ]
        
        for table in expected_tables:
            if table in tables:
                main_logger.info(
                    f"Table '{table}' created successfully",
                    extra={'operation': 'db_init', 'user_id': 'system'}
                )
            else:
                main_logger.warning(
                    f"Table '{table}' not found",
                    extra={'operation': 'db_init', 'user_id': 'system'}
                )
        
        return True
        
    except Exception as e:
        main_logger.error(
            f"Failed to create database schema: {str(e)}",
            extra={'operation': 'db_init', 'user_id': 'system'}
        )
        return False


if __name__ == "__main__":
    print("Initializing database schema...")
    success = create_database_schema()
    
    if success:
        print("✓ Database schema created successfully")
        sys.exit(0)
    else:
        print("✗ Failed to create database schema")
        sys.exit(1)
