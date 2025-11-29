"""
Tests for ML Training Pipeline

Basic tests to verify the training pipeline components work correctly.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil

# Import training components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.data_loader import DataLoader
from training.class_balancer import ClassBalancer
from training.trainers import RandomForestTrainer, XGBoostTrainer
from training.ensemble import EnsemblePredictor
from training.cross_validator import CrossValidator


@pytest.fixture
def sample_data():
    """Create sample dataset for testing."""
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    # Create features
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    # Create imbalanced target (70% class 0, 30% class 1)
    y = pd.Series(
        np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3]),
        name='diagnosis'
    )
    
    return X, y


@pytest.fixture
def temp_feature_store(sample_data):
    """Create temporary feature store."""
    X, y = sample_data
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    feature_store_path = Path(temp_dir) / "features"
    feature_store_path.mkdir(parents=True)
    
    # Save sample data
    data = pd.concat([X, y], axis=1)
    data.to_parquet(feature_store_path / "train_features.parquet")
    
    yield feature_store_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestDataLoader:
    """Test DataLoader functionality."""
    
    def test_load_features(self, temp_feature_store):
        """Test loading features from feature store."""
        loader = DataLoader(temp_feature_store)
        X, y = loader.load_features("train_features", "diagnosis")
        
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert len(X) == len(y)
        assert len(X) == 1000
    
    def test_split_data(self, sample_data):
        """Test data splitting."""
        X, y = sample_data
        loader = DataLoader(Path("."))
        
        splits = loader.split_data(X, y, test_size=0.2, val_size=0.2)
        
        assert 'X_train' in splits
        assert 'X_val' in splits
        assert 'X_test' in splits
        assert len(splits['X_train']) + len(splits['X_val']) + len(splits['X_test']) == len(X)


class TestClassBalancer:
    """Test ClassBalancer functionality."""
    
    def test_calculate_distribution(self, sample_data):
        """Test class distribution calculation."""
        _, y = sample_data
        balancer = ClassBalancer()
        
        dist = balancer.calculate_class_distribution(y)
        
        assert 'class_counts' in dist
        assert 'imbalance_ratio' in dist
        assert dist['total_samples'] == len(y)
    
    def test_should_apply_smote(self, sample_data):
        """Test SMOTE decision logic."""
        _, y = sample_data
        balancer = ClassBalancer(imbalance_threshold=3.0)
        
        # With 70-30 split, ratio is ~2.3, should not apply SMOTE
        should_apply = balancer.should_apply_smote(y)
        assert not should_apply
    
    def test_compute_class_weights(self, sample_data):
        """Test class weight computation."""
        _, y = sample_data
        balancer = ClassBalancer()
        
        weights = balancer.compute_class_weights(y)
        
        assert isinstance(weights, dict)
        assert len(weights) == 2
        assert all(w > 0 for w in weights.values())


class TestTrainers:
    """Test model trainers."""
    
    def test_random_forest_trainer(self, sample_data):
        """Test Random Forest trainer."""
        X, y = sample_data
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        trainer = RandomForestTrainer(n_estimators=50, random_state=42)
        result = trainer.train(X_train, y_train, X_val, y_val)
        
        assert 'model' in result
        assert 'metrics' in result
        assert 'feature_importance' in result
        assert result['metrics']['train_roc_auc'] > 0.5
    
    def test_xgboost_trainer(self, sample_data):
        """Test XGBoost trainer."""
        X, y = sample_data
        
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        trainer = XGBoostTrainer(n_estimators=50, random_state=42)
        result = trainer.train(X_train, y_train, X_val, y_val)
        
        assert 'model' in result
        assert 'metrics' in result
        assert result['metrics']['train_roc_auc'] > 0.5


class TestEnsemble:
    """Test ensemble predictor."""
    
    def test_ensemble_predictions(self, sample_data):
        """Test ensemble predictions."""
        X, y = sample_data
        
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        import xgboost as xgb
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train simple models
        rf = RandomForestClassifier(n_estimators=50, random_state=42)
        rf.fit(X_train, y_train)
        
        xgb_model = xgb.XGBClassifier(n_estimators=50, random_state=42)
        xgb_model.fit(X_train, y_train)
        
        # Create ensemble
        ensemble = EnsemblePredictor(
            models=[rf, xgb_model],
            model_names=['rf', 'xgb']
        )
        
        # Test predictions
        predictions = ensemble.predict_proba(X_test)
        assert len(predictions) == len(X_test)
        assert all(0 <= p <= 1 for p in predictions)
    
    def test_confidence_intervals(self, sample_data):
        """Test confidence interval calculation."""
        X, y = sample_data
        
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train models
        models = []
        for i in range(3):
            rf = RandomForestClassifier(n_estimators=50, random_state=42+i)
            rf.fit(X_train, y_train)
            models.append(rf)
        
        ensemble = EnsemblePredictor(
            models=models,
            model_names=['rf1', 'rf2', 'rf3']
        )
        
        pred, lower, upper = ensemble.predict_with_confidence(X_test)
        
        assert len(pred) == len(X_test)
        assert len(lower) == len(X_test)
        assert len(upper) == len(X_test)
        assert all(lower <= pred)
        assert all(pred <= upper)


class TestCrossValidator:
    """Test cross-validator."""
    
    def test_cross_validation(self, sample_data):
        """Test cross-validation."""
        X, y = sample_data
        
        from sklearn.ensemble import RandomForestClassifier
        
        cv = CrossValidator(n_splits=3, random_state=42)
        
        results = cv.evaluate_model(
            RandomForestClassifier,
            {'n_estimators': 50, 'random_state': 42},
            X, y
        )
        
        assert 'cv_results' in results
        assert 'fold_results' in results
        assert len(results['fold_results']) == 3
        assert 'roc_auc_mean' in results['cv_results']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
