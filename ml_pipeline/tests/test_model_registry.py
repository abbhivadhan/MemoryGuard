"""
Tests for Model Registry

Tests cover:
- Model registration with versioning
- Metadata storage
- Model comparison
- Production deployment
- Rollback mechanism
- Deployment history tracking
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

from ml_pipeline.models.model_registry import ModelRegistry


@pytest.fixture
def temp_storage():
    """Create temporary storage directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_model():
    """Create a sample trained model"""
    X, y = make_classification(n_samples=100, n_features=10, random_state=42)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model


@pytest.fixture
def sample_metrics():
    """Sample performance metrics"""
    return {
        'accuracy': 0.85,
        'balanced_accuracy': 0.84,
        'precision': 0.83,
        'recall': 0.87,
        'f1_score': 0.85,
        'roc_auc': 0.90,
        'pr_auc': 0.88
    }


@pytest.fixture
def sample_hyperparameters():
    """Sample hyperparameters"""
    return {
        'n_estimators': 10,
        'max_depth': 5,
        'random_state': 42
    }


class TestModelRegistry:
    """Test suite for ModelRegistry"""
    
    def test_initialization(self, temp_storage):
        """Test registry initialization"""
        registry = ModelRegistry(storage_path=temp_storage)
        assert registry.storage_path == Path(temp_storage)
        assert registry.storage_path.exists()
    
    def test_generate_version_id(self, temp_storage):
        """Test version ID generation"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        version_id_1 = registry._generate_version_id()
        version_id_2 = registry._generate_version_id()
        
        # Check format
        assert version_id_1.startswith('v')
        assert '_' in version_id_1
        
        # Check uniqueness
        assert version_id_1 != version_id_2
    
    def test_register_model(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test model registration"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        version_id = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.0',
            hyperparameters=sample_hyperparameters,
            feature_names=['f1', 'f2', 'f3'],
            n_training_samples=100
        )
        
        # Check version ID format
        assert version_id.startswith('v')
        
        # Check artifact was saved
        model_dir = Path(temp_storage) / 'test_classifier' / version_id
        assert model_dir.exists()
        assert (model_dir / 'model.pkl').exists()
        assert (model_dir / 'hyperparameters.json').exists()
        assert (model_dir / 'features.json').exists()
    
    def test_register_model_performance(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test that model registration completes within 5 seconds (Requirement 8.6)"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        start_time = datetime.utcnow()
        
        version_id = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.0',
            hyperparameters=sample_hyperparameters
        )
        
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        
        assert elapsed_time < 5.0, f"Registration took {elapsed_time}s, should be < 5s"
        assert version_id is not None
    
    def test_load_model(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test model loading"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        # Register model
        version_id = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.0',
            hyperparameters=sample_hyperparameters
        )
        
        # Promote to production
        registry.promote_to_production('test_classifier', version_id)
        
        # Load model
        loaded_model, metadata = registry.load_model('test_classifier')
        
        assert loaded_model is not None
        assert metadata['version_id'] == version_id
        assert metadata['model_name'] == 'test_classifier'
        assert metadata['metrics']['roc_auc'] == sample_metrics['roc_auc']
    
    def test_promote_to_production(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test promoting model to production"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        # Register model
        version_id = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.0',
            hyperparameters=sample_hyperparameters
        )
        
        # Promote to production
        success = registry.promote_to_production('test_classifier', version_id)
        
        assert success is True
        
        # Check production model
        prod_model = registry.get_production_model('test_classifier')
        assert prod_model is not None
        assert prod_model['version_id'] == version_id
        assert prod_model['metrics']['roc_auc'] == sample_metrics['roc_auc']
    
    def test_compare_versions(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test comparing model versions"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        # Register multiple versions
        version_id_1 = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.0',
            hyperparameters=sample_hyperparameters
        )
        
        # Second version with better metrics
        better_metrics = sample_metrics.copy()
        better_metrics['roc_auc'] = 0.95
        
        version_id_2 = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=better_metrics,
            dataset_version='v1.1',
            hyperparameters=sample_hyperparameters
        )
        
        # Compare versions
        comparisons = registry.compare_versions('test_classifier', metric='roc_auc')
        
        assert len(comparisons) == 2
        # Should be sorted by roc_auc descending
        assert comparisons[0]['version_id'] == version_id_2
        assert comparisons[0]['metrics']['roc_auc'] == 0.95
        assert comparisons[1]['version_id'] == version_id_1
        assert comparisons[1]['metrics']['roc_auc'] == 0.90
    
    def test_rollback_to_version(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test rolling back to a previous version"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        # Register two versions
        version_id_1 = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.0',
            hyperparameters=sample_hyperparameters
        )
        
        version_id_2 = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.1',
            hyperparameters=sample_hyperparameters
        )
        
        # Promote version 2
        registry.promote_to_production('test_classifier', version_id_2)
        
        # Rollback to version 1
        success = registry.rollback_to_version('test_classifier', version_id_1)
        
        assert success is True
        
        # Check production model is now version 1
        prod_model = registry.get_production_model('test_classifier')
        assert prod_model['version_id'] == version_id_1
    
    def test_list_versions(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test listing model versions"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        # Register multiple versions
        version_ids = []
        for i in range(3):
            version_id = registry.register_model(
                model=sample_model,
                model_name='test_classifier',
                model_type='random_forest',
                metrics=sample_metrics,
                dataset_version=f'v1.{i}',
                hyperparameters=sample_hyperparameters
            )
            version_ids.append(version_id)
        
        # List versions
        versions = registry.list_versions('test_classifier')
        
        assert len(versions) == 3
        # Should be sorted by created_at descending (most recent first)
        assert versions[0]['version_id'] == version_ids[2]
    
    def test_deployment_history(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test tracking deployment history"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        # Register and deploy multiple versions
        version_id_1 = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.0',
            hyperparameters=sample_hyperparameters
        )
        registry.promote_to_production('test_classifier', version_id_1)
        
        version_id_2 = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.1',
            hyperparameters=sample_hyperparameters
        )
        registry.promote_to_production('test_classifier', version_id_2)
        
        # Get deployment history
        history = registry.get_deployment_history('test_classifier')
        
        assert len(history) >= 2
        # Most recent deployment should be first
        assert history[0]['version_id'] == version_id_2
        assert history[1]['version_id'] == version_id_1
    
    def test_model_statistics(self, temp_storage, sample_model, sample_metrics, sample_hyperparameters):
        """Test getting registry statistics"""
        registry = ModelRegistry(storage_path=temp_storage)
        
        # Register models
        version_id = registry.register_model(
            model=sample_model,
            model_name='test_classifier',
            model_type='random_forest',
            metrics=sample_metrics,
            dataset_version='v1.0',
            hyperparameters=sample_hyperparameters
        )
        registry.promote_to_production('test_classifier', version_id)
        
        # Get statistics
        stats = registry.get_model_statistics()
        
        assert stats['total_models'] >= 1
        assert stats['total_versions'] >= 1
        assert stats['production_models'] >= 1
        assert 'average_production_metrics' in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
