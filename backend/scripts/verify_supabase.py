#!/usr/bin/env python3
"""
Script to verify Supabase PostgreSQL connection and setup.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.core.database import engine, check_db_connection
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_connection():
    """Verify database connection."""
    print("\n" + "="*60)
    print("SUPABASE CONNECTION VERIFICATION")
    print("="*60 + "\n")
    
    # Check if DATABASE_URL is set
    if not settings.DATABASE_URL:
        print("❌ DATABASE_URL not set in environment variables")
        return False
    
    # Mask password in URL for display
    masked_url = settings.DATABASE_URL
    if "@" in masked_url:
        parts = masked_url.split("@")
        user_pass = parts[0].split("//")[1]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            masked_url = masked_url.replace(user_pass, f"{user}:****")
    
    print(f"📍 Database URL: {masked_url}\n")
    
    # Test connection
    print("🔌 Testing connection...")
    if check_db_connection():
        print("✅ Connection successful!\n")
    else:
        print("❌ Connection failed!\n")
        return False
    
    return True


def get_database_info():
    """Get database information."""
    print("📊 Database Information:")
    print("-" * 60)
    
    try:
        with engine.connect() as conn:
            # PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL Version: {version.split(',')[0]}\n")
            
            # Database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"Database Name: {db_name}")
            
            # Current user
            result = conn.execute(text("SELECT current_user"))
            user = result.fetchone()[0]
            print(f"Current User: {user}")
            
            # Database size
            result = conn.execute(text(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            ))
            size = result.fetchone()[0]
            print(f"Database Size: {size}")
            
            # Connection count
            result = conn.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
            ))
            connections = result.fetchone()[0]
            print(f"Active Connections: {connections}\n")
            
    except Exception as e:
        print(f"❌ Error getting database info: {e}\n")
        return False
    
    return True


def list_tables():
    """List all tables in the database."""
    print("📋 Database Tables:")
    print("-" * 60)
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("⚠️  No tables found. Run migrations with: alembic upgrade head\n")
            return False
        
        print(f"Found {len(tables)} tables:\n")
        for table in sorted(tables):
            # Get row count
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
            
            print(f"  • {table:<30} ({count} rows)")
        
        print()
        
    except Exception as e:
        print(f"❌ Error listing tables: {e}\n")
        return False
    
    return True


def check_migrations():
    """Check migration status."""
    print("🔄 Migration Status:")
    print("-" * 60)
    
    try:
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'alembic_version')"
            ))
            exists = result.fetchone()[0]
            
            if not exists:
                print("⚠️  Alembic not initialized. Run: alembic upgrade head\n")
                return False
            
            # Get current version
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            
            if version:
                print(f"✅ Current migration version: {version[0]}\n")
            else:
                print("⚠️  No migrations applied yet\n")
                return False
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}\n")
        return False
    
    return True


def test_crud_operations():
    """Test basic CRUD operations."""
    print("🧪 Testing CRUD Operations:")
    print("-" * 60)
    
    try:
        with engine.connect() as conn:
            # Create test table
            print("Creating test table...")
            conn.execute(text(
                "CREATE TABLE IF NOT EXISTS _test_table (id SERIAL PRIMARY KEY, data TEXT)"
            ))
            conn.commit()
            
            # Insert
            print("Testing INSERT...")
            conn.execute(text("INSERT INTO _test_table (data) VALUES ('test')"))
            conn.commit()
            
            # Select
            print("Testing SELECT...")
            result = conn.execute(text("SELECT * FROM _test_table"))
            rows = result.fetchall()
            
            # Update
            print("Testing UPDATE...")
            conn.execute(text("UPDATE _test_table SET data = 'updated' WHERE data = 'test'"))
            conn.commit()
            
            # Delete
            print("Testing DELETE...")
            conn.execute(text("DELETE FROM _test_table"))
            conn.commit()
            
            # Drop test table
            print("Cleaning up...")
            conn.execute(text("DROP TABLE _test_table"))
            conn.commit()
            
            print("✅ All CRUD operations successful!\n")
            
    except Exception as e:
        print(f"❌ CRUD test failed: {e}\n")
        return False
    
    return True


def main():
    """Run all verification checks."""
    checks = [
        ("Connection", verify_connection),
        ("Database Info", get_database_info),
        ("Tables", list_tables),
        ("Migrations", check_migrations),
        ("CRUD Operations", test_crud_operations),
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            logger.error(f"Error in {name} check: {e}")
            results[name] = False
    
    # Summary
    print("="*60)
    print("VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:<20} {status}")
    
    print()
    
    all_passed = all(results.values())
    
    if all_passed:
        print("🎉 All checks passed! Supabase is configured correctly.\n")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the errors above.\n")
        print("💡 Tips:")
        print("  • Ensure DATABASE_URL is set correctly in .env")
        print("  • Run migrations: alembic upgrade head")
        print("  • Check Supabase dashboard for connection issues")
        print("  • Verify your Supabase project is not paused\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
