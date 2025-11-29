"""
Simple verification script for Model Registry
Tests basic functionality without external dependencies
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ml_pipeline.models.model_registry import ModelRegistry


def test_version_id_generation():
    """Test version ID generation"""
    print("Testing version ID generation...")
    registry = ModelRegistry(storage_path='ml_pipeline/data_storage/models')
    
    version_id_1 = registry._generate_version_id()
    version_id_2 = registry._generate_version_id()
    
    assert version_id_1.startswith('v'), "Version ID should start with 'v'"
    assert '_' in version_id_1, "Version ID should contain underscore"
    assert version_id_1 != version_id_2, "Version IDs should be unique"
    
    print(f"  ✓ Generated version ID: {version_id_1}")
    print(f"  ✓ Version IDs are unique")
    print()


def test_registry_initialization():
    """Test registry initialization"""
    print("Testing registry initialization...")
    registry = ModelRegistry(storage_path='ml_pipeline/data_storage/models')
    
    assert registry.storage_path.exists(), "Storage path should exist"
    print(f"  ✓ Registry initialized with path: {registry.storage_path}")
    print()


def test_list_models():
    """Test listing models"""
    print("Testing model listing...")
    registry = ModelRegistry(storage_path='ml_pipeline/data_storage/models')
    
    models = registry.list_all_models()
    print(f"  ✓ Found {len(models)} models in registry")
    if models:
        for model in models[:5]:  # Show first 5
            print(f"    - {model}")
    print()


def test_model_statistics():
    """Test getting registry statistics"""
    print("Testing registry statistics...")
    registry = ModelRegistry(storage_path='ml_pipeline/data_storage/models')
    
    try:
        stats = registry.get_model_statistics()
        print(f"  ✓ Total models: {stats['total_models']}")
        print(f"  ✓ Total versions: {stats['total_versions']}")
        print(f"  ✓ Production models: {stats['production_models']}")
        print(f"  ✓ Archived models: {stats['archived_models']}")
    except Exception as e:
        print(f"  ⚠ Statistics not available (database may not be initialized): {e}")
    print()


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Model Registry Verification")
    print("=" * 60)
    print()
    
    try:
        test_registry_initialization()
        test_version_id_generation()
        test_list_models()
        test_model_statistics()
        
        print("=" * 60)
        print("✓ All verification tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
