# Model Registry

The Model Registry provides centralized versioning, storage, and deployment management for machine learning models in the biomedical data ML pipeline.

## Features

- **Automatic Versioning**: Generates unique version identifiers for each model
- **Metadata Storage**: Stores comprehensive model metadata including metrics, hyperparameters, and training information
- **Model Comparison**: Compare performance metrics across different model versions
- **Production Deployment**: Promote models to production with automatic demotion of previous versions
- **Rollback Capability**: Easily rollback to previous model versions
- **Deployment History**: Track all model deployments with audit logs
- **Artifact Management**: Store and retrieve model artifacts efficiently

## Quick Start

```python
from ml_pipeline.models import ModelRegistry

# Initialize registry
registry = ModelRegistry()

# Register a model
version_id = registry.register_model(
    model=trained_model,
    model_name='alzheimer_classifier',
    model_type='random_forest',
    metrics={
        'accuracy': 0.85,
        'roc_auc': 0.90,
        'precision': 0.83,
        'recall': 0.87,
        'f1_score': 0.85
    },
    dataset_version='v1.0',
    hyperparameters={'n_estimators': 200, 'max_depth': 15},
    feature_names=['age', 'mmse_score', 'csf_ab42', ...],
    n_training_samples=10000
)

# Promote to production
registry.promote_to_production('alzheimer_classifier', version_id)

# Load production model
model, metadata = registry.load_model('alzheimer_classifier')

# Compare versions
comparisons = registry.compare_versions('alzheimer_classifier')

# Rollback if needed
registry.rollback_to_version('alzheimer_classifier', previous_version_id)
```

## Architecture

### Version ID Format

Version IDs follow the format: `v{timestamp}_{uuid}`

Example: `v20250126143022_a1b2c3d4`

This ensures:
- Chronological ordering
- Uniqueness
- Human-readable timestamps

### Storage Structure

```
ml_pipeline/data_storage/models/
├── alzheimer_classifier/
│   ├── v20250126143022_a1b2c3d4/
│   │   ├── model.pkl
│   │   ├── hyperparameters.json
│   │   └── features.json
│   └── v20250126150315_b5c6d7e8/
│       ├── model.pkl
│       ├── hyperparameters.json
│       └── features.json
└── progression_forecaster/
    └── v20250126152045_c9d0e1f2/
        ├── model.pkl
        ├── hyperparameters.json
        └── features.json
```

### Database Schema

The registry uses PostgreSQL to store model metadata:

```sql
CREATE TABLE model_versions (
    version_id VARCHAR(50) PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP,
    deployed_at TIMESTAMP,
    
    -- Performance metrics
    accuracy FLOAT,
    balanced_accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    roc_auc FLOAT,
    pr_auc FLOAT,
    
    -- Training info
    dataset_version VARCHAR(50),
    n_training_samples INTEGER,
    n_validation_samples INTEGER,
    n_test_samples INTEGER,
    hyperparameters JSON,
    feature_names JSON,
    
    -- Deployment
    status VARCHAR(20),  -- registered, production, archived
    artifact_path VARCHAR(255),
    training_duration_seconds FLOAT,
    notes TEXT
);
```

## API Reference

### ModelRegistry Class

#### `__init__(storage_path: str = None)`

Initialize the model registry.

**Parameters:**
- `storage_path`: Base path for storing model artifacts (default: from env or `ml_pipeline/data_storage/models`)

#### `register_model(...) -> str`

Register a new model version with automatic versioning.

**Parameters:**
- `model`: Trained model object
- `model_name`: Name of the model
- `model_type`: Type of model (e.g., 'random_forest', 'xgboost', 'neural_network')
- `metrics`: Dictionary of performance metrics
- `dataset_version`: Version of the dataset used for training
- `hyperparameters`: Model hyperparameters
- `feature_names`: List of feature names (optional)
- `training_duration`: Training time in seconds (optional)
- `n_training_samples`: Number of training samples (optional)
- `n_validation_samples`: Number of validation samples (optional)
- `n_test_samples`: Number of test samples (optional)
- `notes`: Additional notes (optional)
- `user_id`: User who registered the model (default: 'system')

**Returns:** Unique version identifier

**Performance:** Completes within 5 seconds (Requirement 8.6)

#### `load_model(model_name: str, version_id: str = None) -> Tuple[Any, Dict]`

Load a model and its metadata.

**Parameters:**
- `model_name`: Name of the model
- `version_id`: Specific version ID (if None, loads production version)

**Returns:** Tuple of (model object, metadata dict)

#### `compare_versions(model_name: str, version_ids: List[str] = None, metric: str = 'roc_auc') -> List[Dict]`

Compare metrics across model versions.

**Parameters:**
- `model_name`: Name of the model
- `version_ids`: List of specific version IDs to compare (if None, compares all)
- `metric`: Primary metric to sort by (default: 'roc_auc')

**Returns:** List of version comparisons sorted by the specified metric

**Validates:** Requirement 8.3

#### `promote_to_production(model_name: str, version_id: str, user_id: str = 'system') -> bool`

Promote a model version to production.

**Parameters:**
- `model_name`: Name of the model
- `version_id`: Version ID to promote
- `user_id`: User performing the promotion

**Returns:** True if successful, False otherwise

**Validates:** Requirements 8.4, 8.5

#### `rollback_to_version(model_name: str, version_id: str, user_id: str = 'system') -> bool`

Rollback to a previous model version.

**Parameters:**
- `model_name`: Name of the model
- `version_id`: Version ID to rollback to
- `user_id`: User performing the rollback

**Returns:** True if successful, False otherwise

**Validates:** Requirement 8.4

#### `get_production_model(model_name: str) -> Optional[Dict]`

Get the currently deployed production model.

**Parameters:**
- `model_name`: Name of the model

**Returns:** Dictionary with production model metadata or None

**Validates:** Requirement 8.5

#### `get_deployment_history(model_name: str, limit: int = 10) -> List[Dict]`

Get deployment history for a model.

**Parameters:**
- `model_name`: Name of the model
- `limit`: Maximum number of deployments to return

**Returns:** List of deployment records

**Validates:** Requirement 19.4

#### `list_versions(model_name: str, limit: int = 10) -> List[Dict]`

List all versions of a model.

**Parameters:**
- `model_name`: Name of the model
- `limit`: Maximum number of versions to return

**Returns:** List of version metadata dictionaries

**Validates:** Requirements 8.1, 8.7

#### `get_model_statistics() -> Dict`

Get overall statistics about the model registry.

**Returns:** Dictionary with registry statistics including total models, versions, and average metrics

## Usage Examples

### Example 1: Register and Deploy a Model

```python
from sklearn.ensemble import RandomForestClassifier
from ml_pipeline.models import ModelRegistry

# Train your model
model = RandomForestClassifier(n_estimators=200)
model.fit(X_train, y_train)

# Calculate metrics
metrics = {
    'accuracy': 0.85,
    'roc_auc': 0.90,
    'precision': 0.83,
    'recall': 0.87,
    'f1_score': 0.85
}

# Register model
registry = ModelRegistry()
version_id = registry.register_model(
    model=model,
    model_name='alzheimer_classifier',
    model_type='random_forest',
    metrics=metrics,
    dataset_version='v1.0',
    hyperparameters={'n_estimators': 200},
    n_training_samples=10000
)

# Promote to production
registry.promote_to_production('alzheimer_classifier', version_id)
```

### Example 2: Compare Model Versions

```python
registry = ModelRegistry()

# Compare all versions
comparisons = registry.compare_versions(
    model_name='alzheimer_classifier',
    metric='roc_auc'
)

for comp in comparisons:
    print(f"Version: {comp['version_id']}")
    print(f"ROC-AUC: {comp['metrics']['roc_auc']:.4f}")
    print(f"Status: {comp['status']}")
    print()
```

### Example 3: Load and Use Production Model

```python
registry = ModelRegistry()

# Load production model
model, metadata = registry.load_model('alzheimer_classifier')

# Make predictions
predictions = model.predict(X_new)
probabilities = model.predict_proba(X_new)

print(f"Using model version: {metadata['version_id']}")
print(f"Model ROC-AUC: {metadata['metrics']['roc_auc']:.4f}")
```

### Example 4: Rollback After Issues

```python
registry = ModelRegistry()

# Get deployment history
history = registry.get_deployment_history('alzheimer_classifier')
previous_version = history[1]['version_id']  # Get previous version

# Rollback
registry.rollback_to_version(
    model_name='alzheimer_classifier',
    version_id=previous_version,
    user_id='admin'
)
```

## Integration with Training Pipeline

The model registry integrates seamlessly with the training pipeline:

```python
from ml_pipeline.training import MLTrainingPipeline
from ml_pipeline.models import ModelRegistry

# Train models
pipeline = MLTrainingPipeline(config)
results = pipeline.train_all_models()

# Register each model
registry = ModelRegistry()
for model_name, result in results.items():
    version_id = registry.register_model(
        model=result['model'],
        model_name=model_name,
        model_type=model_name,
        metrics=result['metrics'],
        dataset_version='v1.0',
        hyperparameters=result['hyperparameters'],
        training_duration=result['training_time']
    )
    
    # Auto-promote if better than current production
    current_prod = registry.get_production_model(model_name)
    if not current_prod or result['metrics']['roc_auc'] > current_prod['metrics']['roc_auc']:
        registry.promote_to_production(model_name, version_id)
```

## Compliance and Audit

The model registry maintains comprehensive audit logs for compliance:

- All model registrations are logged
- All promotions and deployments are tracked
- All rollbacks are recorded
- User IDs are captured for all operations
- Audit logs are retained for 7 years (Requirement 19.6)

## Performance

- Model registration completes within 5 seconds (Requirement 8.6)
- Model loading is optimized with efficient artifact storage
- Metadata queries use indexed database columns for fast retrieval

## Best Practices

1. **Versioning**: Always register models with meaningful notes
2. **Testing**: Test models thoroughly before promoting to production
3. **Monitoring**: Track deployment history and model performance
4. **Rollback**: Keep at least the last 10 versions for rollback capability
5. **Cleanup**: Periodically archive old non-production versions
6. **Documentation**: Document hyperparameters and training configurations

## Troubleshooting

### Model Not Found

```python
# Check if model exists
versions = registry.list_versions('model_name')
if not versions:
    print("Model not found in registry")
```

### Production Model Not Set

```python
# Check production status
prod_model = registry.get_production_model('model_name')
if not prod_model:
    print("No production model set")
    # Promote a version
    registry.promote_to_production('model_name', version_id)
```

### Artifact File Missing

```python
# Verify artifact path
model_version = registry.get_model_version('model_name', version_id)
artifact_path = Path(model_version.artifact_path)
if not artifact_path.exists():
    print(f"Artifact missing: {artifact_path}")
```

## See Also

- [Training Pipeline Documentation](../training/README.md)
- [Model Evaluation Documentation](../training/EVALUATION_README.md)
- [Automated Retraining](../../backend/scripts/automated_retraining.py)
