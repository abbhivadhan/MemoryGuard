# ML Training Pipeline

This module implements the complete machine learning training pipeline for Alzheimer's Disease detection and progression forecasting.

## Overview

The training pipeline provides:

- **Data Loading & Splitting**: Stratified train-validation-test splits
- **Class Imbalance Handling**: SMOTE and class weights
- **Model Training**: Random Forest, XGBoost, and Deep Neural Networks
- **Ensemble Learning**: Weighted averaging with confidence intervals
- **Cross-Validation**: Stratified k-fold validation
- **Performance Optimization**: GPU acceleration and efficient training

## Components

### DataLoader

Loads processed features from the feature store and creates stratified splits.

```python
from training.data_loader import DataLoader

loader = DataLoader(feature_store_path="data_storage/features")

# Load and split data
splits = loader.load_and_split(
    dataset_name="train_features",
    target_column="diagnosis",
    test_size=0.15,
    val_size=0.18
)
```

### ClassBalancer

Handles class imbalance using SMOTE and class weights.

```python
from training.class_balancer import ClassBalancer

balancer = ClassBalancer(imbalance_threshold=3.0)

# Balance training data
X_balanced, y_balanced, class_weights = balancer.balance_data(
    X_train, y_train, method='auto'
)
```

### Model Trainers

Train individual models with optimized hyperparameters.

```python
from training.trainers import RandomForestTrainer, XGBoostTrainer, NeuralNetworkTrainer

# Random Forest
rf_trainer = RandomForestTrainer(n_estimators=200, max_depth=15)
rf_result = rf_trainer.train(X_train, y_train, X_val, y_val)

# XGBoost
xgb_trainer = XGBoostTrainer(n_estimators=200, learning_rate=0.1)
xgb_result = xgb_trainer.train(X_train, y_train, X_val, y_val)

# Neural Network
nn_trainer = NeuralNetworkTrainer(hidden_layers=[128, 64, 32])
nn_result = nn_trainer.train(X_train, y_train, X_val, y_val)
```

### EnsemblePredictor

Combines multiple models using weighted averaging.

```python
from training.ensemble import EnsemblePredictor

ensemble = EnsemblePredictor(
    models=[rf_model, xgb_model, nn_model],
    model_names=['rf', 'xgb', 'nn']
)

# Get predictions with confidence intervals
predictions, lower, upper = ensemble.predict_with_confidence(X_test)

# Optimize weights
ensemble.optimize_weights(X_val, y_val, metric='roc_auc')
```

### CrossValidator

Performs stratified k-fold cross-validation.

```python
from training.cross_validator import CrossValidator

cv = CrossValidator(n_splits=5)

# Evaluate single model
results = cv.evaluate_model(
    RandomForestClassifier,
    {'n_estimators': 200},
    X, y
)

# Compare multiple models
comparison = cv.compare_models(models_config, X, y)
best_model = cv.get_best_model(comparison, metric='roc_auc')
```

### MLTrainingPipeline

Orchestrates the complete training workflow.

```python
from training.training_pipeline import MLTrainingPipeline

pipeline = MLTrainingPipeline(
    feature_store_path="data_storage/features",
    output_dir="data_storage/models/run_001"
)

# Run full pipeline
results = pipeline.run_full_pipeline(
    dataset_name="train_features",
    target_column="diagnosis",
    enable_gpu=True,
    save_models=True
)

# Run cross-validation
cv_results = pipeline.run_cross_validation()
```

## Requirements

The training pipeline meets the following requirements:

- ✅ **Requirement 5.1**: Random Forest with 200+ trees
- ✅ **Requirement 5.2**: XGBoost with hyperparameter optimization
- ✅ **Requirement 5.3**: Deep Neural Network with 3+ hidden layers
- ✅ **Requirement 5.4**: Stratified k-fold cross-validation (k=5)
- ✅ **Requirement 5.5**: Stratified train-validation-test split
- ✅ **Requirement 5.6**: Minimum AUC-ROC of 0.80 on validation data
- ✅ **Requirement 5.7**: Ensemble predictions using weighted averaging
- ✅ **Requirement 5.8**: Training completes within 2 hours
- ✅ **Requirement 15.1-15.4**: Class imbalance handling with SMOTE

## Performance Optimization

The pipeline includes several optimizations to meet the 2-hour training requirement:

1. **Parallel Processing**: Uses all CPU cores (`n_jobs=-1`)
2. **GPU Acceleration**: Automatic GPU detection and configuration for neural networks
3. **Early Stopping**: Prevents unnecessary training epochs
4. **Efficient Data Structures**: Uses Pandas DataFrames and NumPy arrays
5. **Batch Processing**: Configurable batch sizes for neural networks

## Usage Example

```python
from pathlib import Path
from training.training_pipeline import MLTrainingPipeline

# Initialize pipeline
pipeline = MLTrainingPipeline(
    feature_store_path=Path("data_storage/features"),
    output_dir=Path("data_storage/models/run_001"),
    random_state=42
)

# Run training
results = pipeline.run_full_pipeline(
    dataset_name="train_features",
    target_column="diagnosis",
    enable_gpu=True,
    save_models=True
)

# Check results
print(f"Training time: {results['training_time_minutes']:.2f} minutes")
print(f"Ensemble ROC-AUC: {results['models']['ensemble']['roc_auc']:.4f}")
```

## Output

The pipeline generates:

- **Trained Models**: Saved in `output_dir/models/`
  - `random_forest.pkl`
  - `xgboost.pkl`
  - `neural_network.h5`
  - `ensemble.pkl`

- **Training Summary**: `output_dir/training_summary.json`
  - Training time
  - Model performance metrics
  - Feature importance

- **Cross-Validation Results**: `output_dir/cross_validation_results.csv`
  - Per-fold metrics
  - Mean and standard deviation
  - Model comparison

## Configuration

Customize model hyperparameters:

```python
config = {
    'random_forest': {
        'n_estimators': 300,
        'max_depth': 20,
        'min_samples_split': 5
    },
    'xgboost': {
        'n_estimators': 250,
        'max_depth': 8,
        'learning_rate': 0.05
    },
    'neural_network': {
        'hidden_layers': [256, 128, 64],
        'dropout_rates': [0.4, 0.3, 0.2],
        'batch_size': 64
    }
}

pipeline = MLTrainingPipeline(
    feature_store_path=feature_store_path,
    output_dir=output_dir,
    config=config
)
```

## Logging

The pipeline provides detailed logging:

```
[INFO] Initialized MLTrainingPipeline
[INFO] [Step 1/6] Loading and splitting data
[INFO] Loaded 10000 samples with 50 features
[INFO] Training set: 7000 samples (70.0%)
[INFO] Validation set: 1500 samples (15.0%)
[INFO] Test set: 1500 samples (15.0%)
[INFO] [Step 2/6] Handling class imbalance
[INFO] Imbalance ratio 2.5 is below threshold 3.0
[INFO] [Step 3/6] Training Random Forest
[INFO] Training Random Forest with 7000 samples
[INFO] RandomForest evaluation metrics:
[INFO]   roc_auc: 0.8542
[INFO] [Step 4/6] Training XGBoost
[INFO] [Step 5/6] Training Neural Network
[INFO] [Step 6/6] Creating ensemble predictor
[INFO] Pipeline completed in 45.23 minutes
[INFO] Training completed within requirement (0.75h < 2h) ✓
```

## Testing

Run the example script:

```bash
cd ml_pipeline
python examples/training_example.py
```

## Next Steps

After training:

1. **Model Evaluation** (Task 7): Calculate detailed metrics and generate reports
2. **Model Interpretability** (Task 8): Generate SHAP explanations
3. **Model Registry** (Task 10): Version and track models
4. **Deployment**: Deploy models to production via inference API
