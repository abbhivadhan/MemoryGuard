# Quick ML Reference Guide

## Quick Start

### 1. Prepare Data (5 minutes)
```bash
cd backend
python scripts/prepare_training_data.py \
    --data-source data/raw/your_dataset.csv \
    --data-format adni \
    --output-dir data/processed
```

### 2. Train Models (15-30 minutes)
```bash
python scripts/train_models.py \
    --data-dir data/processed \
    --output-dir models
```

### 3. Evaluate Models (2 minutes)
```bash
python scripts/evaluate_models.py \
    --model-dir models/latest \
    --data-dir data/processed
```

### 4. Promote to Production (1 minute)
```bash
python scripts/manage_models.py list
python scripts/manage_models.py promote-production <version>
```

### 5. Start Application
```bash
uvicorn app.main:app --reload
```

## Common Commands

### Model Management
```bash
# List all models
python scripts/manage_models.py list

# Show model details
python scripts/manage_models.py info v1.0.0

# Compare two models
python scripts/manage_models.py compare v1.0.0 v1.1.0

# Promote to staging
python scripts/manage_models.py promote-staging v1.0.0

# Promote to production (requires confirmation)
python scripts/manage_models.py promote-production v1.0.0 --yes

# Rollback production
python scripts/manage_models.py rollback --yes

# Show summary
python scripts/manage_models.py summary
```

### Monitoring
```bash
# Check if retraining needed
python scripts/automated_retraining.py --check-only

# Run automated retraining
python scripts/automated_retraining.py

# Force retraining
python scripts/automated_retraining.py --force
```

### API Endpoints
```bash
# Health check
curl http://localhost:8000/api/v1/ml/health

# Model info
curl http://localhost:8000/api/v1/ml/model/info \
    -H "Authorization: Bearer <token>"

# Registry info
curl http://localhost:8000/api/v1/ml/model/registry \
    -H "Authorization: Bearer <token>"

# Reload model (admin only)
curl -X POST http://localhost:8000/api/v1/ml/model/reload \
    -H "Authorization: Bearer <admin_token>"

# Promote model (admin only)
curl -X POST http://localhost:8000/api/v1/ml/model/promote/v1.0.0?environment=production \
    -H "Authorization: Bearer <admin_token>"
```

## File Locations

### Data
- Raw data: `backend/data/raw/`
- Processed data: `backend/data/processed/`
- Data README: `backend/data/README.md`

### Models
- Trained models: `backend/models/<version>/`
- Latest model: `backend/models/latest/` (symlink)
- Model registry: `backend/models/registry.json`
- Monitoring data: `backend/models/monitoring/`

### Scripts
- Data prep: `backend/scripts/prepare_training_data.py`
- Training: `backend/scripts/train_models.py`
- Evaluation: `backend/scripts/evaluate_models.py`
- Management: `backend/scripts/manage_models.py`
- Retraining: `backend/scripts/automated_retraining.py`

### Documentation
- Full guide: `backend/ML_TRAINING_DEPLOYMENT.md`
- Implementation summary: `ML_TRAINING_IMPLEMENTATION_SUMMARY.md`
- This quick reference: `backend/QUICK_ML_REFERENCE.md`

## Model Versions

### Version Format
`v<major>.<minor>.<patch>_<description>_<timestamp>`

Examples:
- `v1.0.0_initial_20250115_143022`
- `v1.0.0_retrain_20250201_090000`
- `v1.1.0_new_features_20250301_120000`

### Model States
- **registered**: Newly trained, not deployed
- **staging**: Promoted for testing
- **production**: Active model serving predictions
- **archived**: Previous production model

## Expected Performance

### Minimum Requirements
- Accuracy: > 80%
- F1 Score: > 0.75
- AUC-ROC: > 0.85

### Target Performance
- Accuracy: > 85%
- F1 Score: > 0.80
- AUC-ROC: > 0.90
- Sensitivity: > 85%
- Specificity: > 85%

## Troubleshooting

### Models not loading
```bash
# Check registry
python scripts/manage_models.py list

# If empty, train initial model
python scripts/train_models.py
```

### Low accuracy
- Check data quality: `cat data/processed/metadata.json`
- Verify class balance
- Increase training data size
- Tune hyperparameters

### Prediction errors
- Verify all required features are provided
- Check feature names match training data
- Ensure data preprocessing is consistent

### Memory errors during training
- Reduce Neural Network batch size
- Use smaller dataset for testing
- Increase system memory

## Monitoring Checklist

### Daily
- [ ] Check ML service health: `/api/v1/ml/health`
- [ ] Monitor prediction volume
- [ ] Review error logs

### Weekly
- [ ] Calculate accuracy over last 7 days
- [ ] Check confidence calibration
- [ ] Review prediction distribution

### Monthly
- [ ] Run data drift detection
- [ ] Check for performance degradation
- [ ] Evaluate retraining need
- [ ] Archive old model versions

## Scheduled Tasks

### Cron Jobs
```bash
# Daily retraining check at 2 AM
0 2 * * * cd /path/to/backend && python scripts/automated_retraining.py

# Weekly monitoring report at 9 AM Monday
0 9 * * 1 cd /path/to/backend && python scripts/generate_monitoring_report.py

# Monthly model cleanup at 3 AM on 1st
0 3 1 * * cd /path/to/backend && python scripts/cleanup_old_models.py
```

## Support

For detailed information, see:
- `backend/ML_TRAINING_DEPLOYMENT.md` - Complete workflow
- `ML_TRAINING_IMPLEMENTATION_SUMMARY.md` - Implementation details
- Script help: `python <script>.py --help`

## Quick Checks

### Is everything working?
```bash
# 1. Check data
ls -la data/processed/

# 2. Check models
python scripts/manage_models.py summary

# 3. Check API
curl http://localhost:8000/api/v1/ml/health

# 4. Check logs
tail -f backend.log
```

### Ready for production?
- [ ] Real dataset prepared
- [ ] Models trained and evaluated
- [ ] Production model promoted
- [ ] API health check passes
- [ ] Monitoring configured
- [ ] Documentation reviewed
