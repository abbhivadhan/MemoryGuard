# ML Model Training and Deployment Guide

This guide covers the complete workflow for training, evaluating, deploying, and monitoring ML models for Alzheimer's disease prediction.

## Table of Contents

1. [Overview](#overview)
2. [Data Preparation](#data-preparation)
3. [Model Training](#model-training)
4. [Model Evaluation](#model-evaluation)
5. [Model Versioning](#model-versioning)
6. [Model Deployment](#model-deployment)
7. [Model Monitoring](#model-monitoring)
8. [Automated Retraining](#automated-retraining)

## Overview

The ML system uses an ensemble approach combining three models:
- **Random Forest**: Tree-based ensemble for robust predictions
- **XGBoost**: Gradient boosting for high accuracy
- **Neural Network**: Deep learning for complex patterns

### Architecture

```
Data Preparation → Training → Evaluation → Registry → Deployment → Monitoring → Retraining
```

## Data Preparation

### Step 1: Obtain Dataset

Download de-identified Alzheimer's disease datasets from:
- **ADNI** (Alzheimer's Disease Neuroimaging Initiative): https://adni.loni.usc.edu/
- **OASIS** (Open Access Series of Imaging Studies): https://www.oasis-brains.org/

Place the CSV file in `backend/data/raw/`

### Step 2: Prepare Training Data

```bash
cd backend

# For ADNI format
python scripts/prepare_training_data.py \
    --data-source data/raw/adni_data.csv \
    --data-format adni \
    --output-dir data/processed

# For OASIS format
python scripts/prepare_training_data.py \
    --data-source data/raw/oasis_data.csv \
    --data-format oasis \
    --output-dir data/processed
```

This will:
- Clean and standardize the data
- Engineer relevant features
- Split into train (70%), validation (10%), test (20%) sets
- Save processed data to `data/processed/`

### Expected Output

```
data/processed/
├── X_train.npy          # Training features
├── y_train.npy          # Training labels
├── X_val.npy            # Validation features
├── y_val.npy            # Validation labels
├── X_test.npy           # Test features
├── y_test.npy           # Test labels
└── metadata.json        # Dataset metadata
```

## Model Training

### Train Ensemble Model

```bash
python scripts/train_models.py \
    --data-dir data/processed \
    --output-dir models \
    --version v1.0.0_initial
```

### Training Options

```bash
# Custom model weights
python scripts/train_models.py \
    --rf-weight 0.4 \
    --xgb-weight 0.3 \
    --nn-weight 0.3

# Custom random seed
python scripts/train_models.py \
    --random-state 123
```

### Training Output

The training script will:
1. Load preprocessed data
2. Train Random Forest, XGBoost, and Neural Network
3. Calculate training and validation metrics
4. Save trained models with versioning
5. Create symlink to `models/latest`

### Expected Metrics

- **Accuracy**: > 85%
- **F1 Score**: > 0.80
- **AUC-ROC**: > 0.90
- **Sensitivity**: > 85%
- **Specificity**: > 85%

## Model Evaluation

### Comprehensive Evaluation

```bash
python scripts/evaluate_models.py \
    --model-dir models/latest \
    --data-dir data/processed
```

This generates:
- Test set metrics (accuracy, precision, recall, F1, AUC)
- 5-fold cross-validation results
- Confusion matrix visualization
- ROC curve
- Precision-recall curve
- Feature importance plot
- Detailed evaluation report

### Evaluation Output

```
models/latest/evaluation/
├── evaluation_report.json      # Detailed metrics
├── evaluation_report.txt       # Human-readable report
├── confusion_matrix.png        # Confusion matrix plot
├── roc_curve.png              # ROC curve
├── precision_recall_curve.png # PR curve
└── feature_importance.png     # Feature importance
```

## Model Versioning

### Model Registry

The model registry manages all trained model versions.

### List Models

```bash
python scripts/manage_models.py list
```

### View Model Info

```bash
python scripts/manage_models.py info v1.0.0_initial
```

### Promote to Staging

```bash
python scripts/manage_models.py promote-staging v1.0.0_initial
```

### Promote to Production

```bash
python scripts/manage_models.py promote-production v1.0.0_initial
```

### Compare Models

```bash
python scripts/manage_models.py compare v1.0.0_initial v1.0.0_retrain_20250115
```

### Rollback Production

```bash
python scripts/manage_models.py rollback
```

### Registry Summary

```bash
python scripts/manage_models.py summary
```

## Model Deployment

### Automatic Loading on Startup

Models are automatically loaded when the FastAPI application starts:

```bash
cd backend
uvicorn app.main:app --reload
```

The application will:
1. Check the model registry
2. Load the production model (or latest if no production model)
3. Warm up models with dummy predictions
4. Make models available for inference

### Manual Model Reload

Use the API endpoint to reload models without restarting:

```bash
# Reload production model
curl -X POST http://localhost:8000/api/v1/ml/model/reload \
    -H "Authorization: Bearer <admin_token>"

# Reload specific version
curl -X POST "http://localhost:8000/api/v1/ml/model/reload?version=v1.0.0_initial" \
    -H "Authorization: Bearer <admin_token>"
```

### Check Model Status

```bash
# ML service health check
curl http://localhost:8000/api/v1/ml/health

# Model information
curl http://localhost:8000/api/v1/ml/model/info \
    -H "Authorization: Bearer <token>"

# Registry information
curl http://localhost:8000/api/v1/ml/model/registry \
    -H "Authorization: Bearer <token>"
```

## Model Monitoring

### Prediction Logging

All predictions are automatically logged for monitoring:
- Input features
- Prediction and probability
- Confidence score
- Model version used
- Actual outcome (when available)

### Monitor Accuracy Over Time

```python
from app.ml.model_monitoring import get_model_monitor

monitor = get_model_monitor()

# Calculate accuracy for last 30 days
metrics = monitor.calculate_accuracy_over_time(window_days=30)
print(f"Recent accuracy: {metrics['overall_accuracy']:.3f}")
```

### Detect Data Drift

```python
# Compare current data distribution with training data
drift_results = monitor.detect_data_drift(
    reference_features=training_features,
    current_features=recent_features
)

if drift_results['overall_drift_detected']:
    print(f"Drift detected in {len(drift_results['drifted_features'])} features")
```

### Check Performance Degradation

```python
degradation = monitor.check_performance_degradation(
    baseline_accuracy=0.87,
    current_window_days=30
)

if degradation['degradation_detected']:
    print(f"Performance degraded by {degradation['accuracy_drop']:.3f}")
```

### Monitoring Dashboard

View monitoring summary:

```python
summary = monitor.get_monitoring_summary()
print(f"Total predictions: {summary['total_predictions']}")
print(f"Recent accuracy: {summary['recent_accuracy']:.3f}")
```

## Automated Retraining

### Check if Retraining Needed

```bash
python scripts/automated_retraining.py --check-only
```

### Run Automated Retraining

```bash
# Automatic retraining if needed
python scripts/automated_retraining.py

# Force retraining
python scripts/automated_retraining.py --force

# Retrain without auto-promotion
python scripts/automated_retraining.py --no-auto-promote
```

### Retraining Pipeline

The automated pipeline:
1. Checks monitoring data for performance degradation or data drift
2. Prepares updated training dataset
3. Trains new model version
4. Evaluates new model on test set
5. Compares with production model
6. Promotes to staging if performance improves
7. Logs results for audit trail

### Retraining Triggers

Retraining is triggered when:
- **Performance degradation**: Accuracy drops > 5% from baseline
- **Data drift**: > 30% of features show significant distribution changes
- **Minimum predictions**: At least 100 predictions with actual outcomes

### Schedule Automated Retraining

Use cron to schedule regular checks:

```bash
# Check daily at 2 AM
0 2 * * * cd /path/to/backend && python scripts/automated_retraining.py
```

## Best Practices

### Data Quality

- Ensure minimum 500+ samples (preferably 1000+)
- Maintain class balance (at least 30% each class)
- Verify feature completeness (> 50% features per sample)
- Always include critical features (age, MMSE score)

### Model Training

- Use consistent random seeds for reproducibility
- Monitor training metrics for overfitting
- Validate on held-out test set
- Document training parameters and data sources

### Model Deployment

- Always test in staging before production
- Use gradual rollout for production deployment
- Monitor performance closely after deployment
- Keep previous production model for quick rollback

### Model Monitoring

- Log all predictions with timestamps
- Collect actual outcomes when available
- Monitor accuracy trends weekly
- Check for data drift monthly
- Set up alerts for performance degradation

### Model Versioning

- Use semantic versioning (v1.0.0)
- Include timestamp in version name
- Document changes in model metadata
- Keep at least 3 previous versions
- Archive old models after 6 months

## Troubleshooting

### Training Fails

**Issue**: Out of memory during training

**Solution**: Reduce batch size for Neural Network or use smaller dataset

### Low Accuracy

**Issue**: Model accuracy < 80%

**Solution**: 
- Check data quality and class balance
- Increase training data size
- Tune hyperparameters
- Add more relevant features

### Model Not Loading

**Issue**: Models not found on startup

**Solution**:
- Verify models exist in `models/` directory
- Check model registry: `python scripts/manage_models.py list`
- Train initial model if none exist

### Prediction Errors

**Issue**: Predictions fail with missing features

**Solution**:
- Ensure all required features are provided
- Check feature names match training data
- Verify data preprocessing is consistent

## API Reference

### Training Endpoints

- `POST /api/v1/ml/predict` - Create prediction
- `GET /api/v1/ml/predictions/{user_id}` - Get user predictions
- `GET /api/v1/ml/explain/{prediction_id}` - Get SHAP explanation

### Model Management Endpoints

- `GET /api/v1/ml/model/info` - Get model information
- `POST /api/v1/ml/model/reload` - Reload models
- `GET /api/v1/ml/model/registry` - Get registry info
- `POST /api/v1/ml/model/promote/{version}` - Promote model
- `GET /api/v1/ml/health` - Health check

## References

- [ADNI Dataset](https://adni.loni.usc.edu/)
- [OASIS Dataset](https://www.oasis-brains.org/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [SHAP Documentation](https://shap.readthedocs.io/)

## Support

For issues or questions:
1. Check this documentation
2. Review error logs in `backend/logs/`
3. Check model registry status
4. Verify data quality and completeness
