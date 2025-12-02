#!/usr/bin/env python3
"""
Database initialization script for Render deployment.
This script ensures all tables are created and migrations are applied.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
from app.core.database import Base

# Import all models to register them with Base
from app.models import (
    User,
    HealthMetric,
    Assessment,
    Medication,
    Prediction,
    EmergencyContact,
)

def check_database_connection():
    """Check if database is accessible"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_tables_exist():
    """Check which tables exist"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Found {len(tables)} tables: {', '.join(tables) if tables else 'none'}")
        return tables
    except Exception as e:
        print(f"❌ Could not check tables: {e}")
        return []

def create_tables():
    """Create all tables using SQLAlchemy"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        print("🔨 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def run_migrations():
    """Run Alembic migrations"""
    import subprocess
    
    try:
        print("🗄️  Running Alembic migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
            print(result.stdout)
            return True
        else:
            print(f"⚠️  Migration warning (exit code {result.returncode})")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run migrations: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Initializing MemoryGuard Database...")
    print(f"📍 Database URL: {settings.DATABASE_URL[:50]}...")
    
    # Step 1: Check connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Step 2: Check existing tables
    existing_tables = check_tables_exist()
    
    # Step 3: Run migrations (preferred method)
    if run_migrations():
        print("✅ Database initialized via migrations")
    else:
        print("⚠️  Migrations failed, trying direct table creation...")
        # Step 4: Fallback to direct table creation
        if create_tables():
            print("✅ Database initialized via direct creation")
        else:
            print("❌ Database initialization failed")
            sys.exit(1)
    
    # Step 5: Verify tables were created
    final_tables = check_tables_exist()
    
    if 'users' in final_tables:
        print("✅ Database initialization complete!")
        print(f"📊 Total tables: {len(final_tables)}")
    else:
        print("❌ Users table not found after initialization")
        sys.exit(1)

if __name__ == "__main__":
    main()
