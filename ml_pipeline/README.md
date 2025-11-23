# Biomedical Data ML Pipeline

A production-grade system for acquiring, processing, and utilizing real de-identified biomedical datasets to train and deploy machine learning models for Alzheimer's Disease detection and progression forecasting.

## Features

- **Data Integration**: Support for ADNI, OASIS, and NACC datasets
- **Data Quality**: Comprehensive validation and PHI detection
- **Feature Engineering**: Automated extraction of cognitive, biomarker, imaging, and genetic features
- **ML Training**: Ensemble models (Random Forest, XGBoost, Neural Networks)
- **Model Interpretability**: SHAP-based explanations
- **Drift Detection**: Automated monitoring and retraining
- **HIPAA Compliance**: De-identification, encryption, and audit logging

## Project Structure

```
ml_pipeline/
├── config/              # Configuration and settings
├── data_ingestion/      # Data loaders for ADNI, OASIS, NACC
├── data_processing/     # Data preprocessing utilities
├── data_storage/        # Data storage (raw, processed, features, models)
├── feature_engineering/ # Feature extraction and transformation
├── validation/          # Data quality and validation
├── models/              # ML model implementations
├── monitoring/          # Drift detection and monitoring
├── api/                 # REST API endpoints
├── logs/                # Application and audit logs
└── tests/               # Unit and integration tests
```

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Set Up Infrastructure

See the infrastructure setup guide for PostgreSQL, Redis, and MinIO configuration.

## Usage

### Data Ingestion

```python
from ml_pipeline.data_ingestion import ADNILoader

loader = ADNILoader()
data = loader.download_data(data_type='cognitive', date_range=('2020-01-01', '2023-12-31'))
```

### Feature Engineering

```python
from ml_pipeline.feature_engineering import FeatureEngineeringPipeline

pipeline = FeatureEngineeringPipeline()
features = pipeline.extract_features(raw_data)
```

### Model Training

```python
from ml_pipeline.models import MLTrainingPipeline

trainer = MLTrainingPipeline(config)
results = trainer.train_all_models()
```

## Monitoring

Access monitoring dashboards at:
- MLflow: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Compliance

This system implements HIPAA-compliant data handling:
- All data is de-identified before processing
- AES-256 encryption at rest
- Audit logging for all operations
- 7-year log retention

## License

Proprietary - All rights reserved
