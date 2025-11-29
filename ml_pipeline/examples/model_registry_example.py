"""
Example usage of the Model Registry

This script demonstrates how to:
1. Register models with versioning
2. Compare model versions
3. Promote models to production
4. Rollback to previous versions
5. Track deployment history
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score

from ml_pipeline.models.model_registry import ModelRegistry
from ml_pipeline.config.logging_config import get_logger

logger = get_logger(__name__)


def train_sample_model():
    """Train a simple model for demonstration"""
    # Generate synthetic data
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Calculate metrics
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_proba)
    }
    
    hyperparameters = {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    }
    
    feature_names = [f'feature_{i}' for i in range(20)]
    
    return model, metrics, hyperparameters, feature_names


def example_register_models():
    """Example: Register multiple model versions"""
    logger.info("=" * 60)
    logger.info("Example 1: Registering Models")
    logger.info("=" * 60)
    
    registry = ModelRegistry()
    
    # Register first version
    logger.info("\nRegistering first model version...")
    model1, metrics1, hyperparams1, features = train_sample_model()
    
    version_id_1 = registry.register_model(
        model=model1,
        model_name='alzheimer_classifier',
        model_type='random_forest',
        metrics=metrics1,
        dataset_version='v1.0',
        hyperparameters=hyperparams1,
        feature_names=features,
        training_duration=45.2,
        n_training_samples=800,
        n_validation_samples=200,
        notes='Initial baseline model'
    )
    
    logger.info(f"Registered version: {version_id_1}")
    logger.info(f"Metrics: ROC-AUC={metrics1['roc_auc']:.4f}, Accuracy={metrics1['accuracy']:.4f}")
    
    # Register second version with better performance
    logger.info("\nRegistering improved model version...")
    model2, metrics2, hyperparams2, features = train_sample_model()
    # Simulate better performance
    metrics2['roc_auc'] = metrics2['roc_auc'] * 1.05
    metrics2['accuracy'] = metrics2['accuracy'] * 1.03
    
    version_id_2 = registry.register_model(
        model=model2,
        model_name='alzheimer_classifier',
        model_type='random_forest',
        metrics=metrics2,
        dataset_version='v1.1',
        hyperparameters=hyperparams2,
        feature_names=features,
        training_duration=48.5,
        n_training_samples=1000,
        n_validation_samples=250,
        notes='Improved model with more training data'
    )
    
    logger.info(f"Registered version: {version_id_2}")
    logger.info(f"Metrics: ROC-AUC={metrics2['roc_auc']:.4f}, Accuracy={metrics2['accuracy']:.4f}")
    
    return version_id_1, version_id_2


def example_compare_versions():
    """Example: Compare model versions"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Comparing Model Versions")
    logger.info("=" * 60)
    
    registry = ModelRegistry()
    
    # Compare all versions
    comparisons = registry.compare_versions(
        model_name='alzheimer_classifier',
        metric='roc_auc'
    )
    
    logger.info(f"\nFound {len(comparisons)} versions:")
    for i, comp in enumerate(comparisons, 1):
        logger.info(f"\n{i}. Version: {comp['version_id']}")
        logger.info(f"   Status: {comp['status']}")
        logger.info(f"   ROC-AUC: {comp['metrics']['roc_auc']:.4f}")
        logger.info(f"   Accuracy: {comp['metrics']['accuracy']:.4f}")
        logger.info(f"   Dataset: {comp['dataset_version']}")
        logger.info(f"   Training samples: {comp['n_training_samples']}")


def example_promote_to_production(version_id: str):
    """Example: Promote a model to production"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Promoting Model to Production")
    logger.info("=" * 60)
    
    registry = ModelRegistry()
    
    logger.info(f"\nPromoting version {version_id} to production...")
    success = registry.promote_to_production(
        model_name='alzheimer_classifier',
        version_id=version_id,
        user_id='data_scientist_1'
    )
    
    if success:
        logger.info("✓ Model promoted successfully!")
        
        # Get production model info
        prod_model = registry.get_production_model('alzheimer_classifier')
        logger.info(f"\nCurrent production model:")
        logger.info(f"  Version: {prod_model['version_id']}")
        logger.info(f"  ROC-AUC: {prod_model['metrics']['roc_auc']:.4f}")
        logger.info(f"  Deployed at: {prod_model['deployed_at']}")
    else:
        logger.error("✗ Failed to promote model")


def example_load_model():
    """Example: Load a model from registry"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Loading Models")
    logger.info("=" * 60)
    
    registry = ModelRegistry()
    
    # Load production model
    logger.info("\nLoading production model...")
    model, metadata = registry.load_model('alzheimer_classifier')
    
    logger.info(f"Loaded model: {metadata['model_name']}")
    logger.info(f"Version: {metadata['version_id']}")
    logger.info(f"Type: {metadata['model_type']}")
    logger.info(f"Status: {metadata['status']}")
    logger.info(f"ROC-AUC: {metadata['metrics']['roc_auc']:.4f}")
    
    # Test prediction
    X_test = np.random.randn(5, 20)
    predictions = model.predict(X_test)
    logger.info(f"\nTest predictions: {predictions}")


def example_deployment_history():
    """Example: View deployment history"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 5: Deployment History")
    logger.info("=" * 60)
    
    registry = ModelRegistry()
    
    history = registry.get_deployment_history('alzheimer_classifier')
    
    logger.info(f"\nDeployment history ({len(history)} deployments):")
    for i, deployment in enumerate(history, 1):
        logger.info(f"\n{i}. Timestamp: {deployment['timestamp']}")
        logger.info(f"   Version: {deployment['version_id']}")
        logger.info(f"   Previous: {deployment['previous_version']}")
        logger.info(f"   User: {deployment['user_id']}")
        logger.info(f"   Success: {deployment['success']}")


def example_rollback(version_id: str):
    """Example: Rollback to a previous version"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 6: Rolling Back to Previous Version")
    logger.info("=" * 60)
    
    registry = ModelRegistry()
    
    logger.info(f"\nRolling back to version {version_id}...")
    success = registry.rollback_to_version(
        model_name='alzheimer_classifier',
        version_id=version_id,
        user_id='data_scientist_1'
    )
    
    if success:
        logger.info("✓ Rollback successful!")
        
        prod_model = registry.get_production_model('alzheimer_classifier')
        logger.info(f"\nCurrent production model after rollback:")
        logger.info(f"  Version: {prod_model['version_id']}")
    else:
        logger.error("✗ Rollback failed")


def example_registry_statistics():
    """Example: Get registry statistics"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 7: Registry Statistics")
    logger.info("=" * 60)
    
    registry = ModelRegistry()
    
    stats = registry.get_model_statistics()
    
    logger.info("\nModel Registry Statistics:")
    logger.info(f"  Total models: {stats['total_models']}")
    logger.info(f"  Total versions: {stats['total_versions']}")
    logger.info(f"  Production models: {stats['production_models']}")
    logger.info(f"  Archived models: {stats['archived_models']}")
    logger.info(f"\nAverage production metrics:")
    logger.info(f"  Accuracy: {stats['average_production_metrics']['accuracy']:.4f}")
    logger.info(f"  ROC-AUC: {stats['average_production_metrics']['roc_auc']:.4f}")
    logger.info(f"  F1-Score: {stats['average_production_metrics']['f1_score']:.4f}")


def main():
    """Run all examples"""
    logger.info("Model Registry Examples")
    logger.info("=" * 60)
    
    # Example 1: Register models
    version_id_1, version_id_2 = example_register_models()
    
    # Example 2: Compare versions
    example_compare_versions()
    
    # Example 3: Promote to production
    example_promote_to_production(version_id_2)
    
    # Example 4: Load model
    example_load_model()
    
    # Example 5: Deployment history
    example_deployment_history()
    
    # Example 6: Rollback
    example_rollback(version_id_1)
    
    # Example 7: Registry statistics
    example_registry_statistics()
    
    logger.info("\n" + "=" * 60)
    logger.info("All examples completed successfully!")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
