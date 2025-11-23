"""
Tests for infrastructure setup
Verifies database, cache, and object storage connectivity
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml_pipeline.data_storage.database import check_db_connection, get_pool_status
from ml_pipeline.data_storage.cache import cache
from ml_pipeline.data_storage.object_storage import storage_client
from ml_pipeline.config.settings import settings


class TestDatabaseConnection:
    """Test PostgreSQL database connectivity"""
    
    def test_database_connection(self):
        """Test that database connection works"""
        assert check_db_connection(), "Database connection failed"
    
    def test_connection_pool(self):
        """Test that connection pool is configured"""
        pool_status = get_pool_status()
        assert 'size' in pool_status
        assert pool_status['size'] > 0


class TestRedisCache:
    """Test Redis cache functionality"""
    
    def test_redis_connection(self):
        """Test that Redis connection works"""
        assert cache.health_check(), "Redis connection failed"
    
    def test_cache_set_get(self):
        """Test basic cache operations"""
        test_key = "test:key"
        test_value = {"data": "test_value"}
        
        # Set value
        assert cache.set(test_key, test_value), "Failed to set cache value"
        
        # Get value
        retrieved = cache.get(test_key)
        assert retrieved == test_value, "Retrieved value doesn't match"
        
        # Clean up
        cache.delete(test_key)
    
    def test_cache_expiration(self):
        """Test that cache TTL works"""
        import time
        
        test_key = "test:expiring"
        test_value = "expires_soon"
        
        # Set with 1 second TTL
        cache.set(test_key, test_value, ttl=1)
        
        # Should exist immediately
        assert cache.exists(test_key), "Key should exist"
        
        # Wait for expiration
        time.sleep(2)
        
        # Should not exist after TTL
        assert not cache.exists(test_key), "Key should have expired"


class TestObjectStorage:
    """Test object storage functionality"""
    
    def test_storage_connection(self):
        """Test that object storage is accessible"""
        # This will raise an exception if connection fails
        assert storage_client is not None
    
    def test_upload_download(self):
        """Test basic upload and download operations"""
        test_object = "test/test_file.txt"
        test_data = b"Test data for object storage"
        
        # Upload
        success = storage_client.upload_bytes(
            test_data,
            test_object,
            content_type="text/plain"
        )
        assert success, "Failed to upload object"
        
        # Check existence
        assert storage_client.object_exists(test_object), "Object should exist"
        
        # Download
        downloaded = storage_client.download_bytes(test_object)
        assert downloaded == test_data, "Downloaded data doesn't match"
        
        # Clean up
        storage_client.delete_object(test_object)
    
    def test_list_objects(self):
        """Test listing objects"""
        # Upload test objects
        test_prefix = "test/list/"
        for i in range(3):
            storage_client.upload_bytes(
                f"data_{i}".encode(),
                f"{test_prefix}file_{i}.txt"
            )
        
        # List objects
        objects = storage_client.list_objects(prefix=test_prefix)
        assert len(objects) >= 3, "Should list uploaded objects"
        
        # Clean up
        for obj in objects:
            storage_client.delete_object(obj)


class TestConfiguration:
    """Test configuration settings"""
    
    def test_settings_loaded(self):
        """Test that settings are loaded correctly"""
        assert settings.PROJECT_ROOT is not None
        assert settings.DATABASE_URL is not None
        assert settings.REDIS_URL is not None
    
    def test_paths_exist(self):
        """Test that required paths exist"""
        assert settings.RAW_DATA_PATH.exists()
        assert settings.PROCESSED_DATA_PATH.exists()
        assert settings.FEATURES_PATH.exists()
        assert settings.MODELS_PATH.exists()
        assert settings.LOGS_PATH.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
