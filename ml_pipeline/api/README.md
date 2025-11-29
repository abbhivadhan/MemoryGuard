# ML Pipeline Inference API

REST API for biomedical ML pipeline providing predictions, explanations, and forecasting for Alzheimer's Disease detection.

## Features

- **Predictions**: Generate predictions with confidence intervals
- **SHAP Explanations**: Interpretable model explanations
- **Progression Forecasting**: 6, 12, and 24-month MMSE forecasts
- **Batch Processing**: Efficient batch predictions
- **Model Caching**: In-memory model caching for fast inference
- **Input Validation**: Comprehensive feature validation

## Requirements

Implements the following requirements from the design document:

- **Requirement 7.1**: Generate SHAP values for all predictions
- **Requirement 7.5**: Provide confidence intervals for all predictions
- **Requirement 9.2**: Generate 6, 12, 24-month progression forecasts
- **Requirement 12.3**: Cache loaded models in memory
- **Requirement 3.5**: Validate feature inputs

## Installation

```bash
# Install dependencies
pip install -r ml_pipeline/requirements.txt

# Additional dependencies for API
pip install fastapi uvicorn python-multipart
```

## Running the API

### Development Mode

```bash
# Run with auto-reload
python ml_pipeline/api/main.py
```

### Production Mode

```bash
# Using uvicorn directly
uvicorn ml_pipeline.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn with uvicorn workers
gunicorn ml_pipeline.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### Prediction Endpoints

#### POST /api/v1/predict

Generate a single prediction with optional SHAP explanation.

**Request Body:**
```json
{
  "features": {
    "mmse_score": 24.0,
    "moca_score": 22.0,
    "cdr_global": 0.5,
    "csf_ab42": 450.0,
    "csf_tau": 350.0,
    "csf_ptau": 65.0,
    "hippocampus_volume": 6500.0,
    "age": 72,
    "sex": 1,
    "education_years": 16,
    "apoe_e4_count": 1
  },
  "model_name": "ensemble",
  "include_explanation": true,
  "include_confidence": true
}
```

**Response:**
```json
{
  "prediction_id": "uuid",
  "prediction": 1,
  "probability": 0.75,
  "confidence_interval": {
    "lower": 0.65,
    "upper": 0.85,
    "confidence_level": 0.95
  },
  "risk_category": "High Risk",
  "timestamp": "2025-01-26T12:00:00",
  "model_name": "ensemble",
  "model_version": "v20250126_abc123",
  "explanation": {
    "top_features": [
      {
        "feature": "csf_ab42",
        "shap_value": -0.15,
        "feature_value": 450.0
      }
    ]
  },
  "generation_time": 0.5
}
```

#### POST /api/v1/predict/batch

Generate predictions for multiple samples efficiently.

**Request Body:**
```json
{
  "features_list": [
    {
      "mmse_score": 28.0,
      "age": 65,
      "csf_ab42": 600.0
    },
    {
      "mmse_score": 22.0,
      "age": 75,
      "csf_ab42": 400.0
    }
  ],
  "model_name": "ensemble",
  "include_explanation": false,
  "include_confidence": true
}
```

**Response:**
```json
{
  "predictions": [
    {
      "prediction_id": "uuid1",
      "prediction": 0,
      "probability": 0.25,
      "risk_category": "Low Risk",
      ...
    },
    {
      "prediction_id": "uuid2",
      "prediction": 1,
      "probability": 0.85,
      "risk_category": "Very High Risk",
      ...
    }
  ],
  "total_count": 2,
  "generation_time": 0.3
}
```

### Explanation Endpoints

#### GET /api/v1/explain/{prediction_id}

Retrieve SHAP explanation for a previous prediction.

**Response:**
```json
{
  "prediction_id": "uuid",
  "explanation": {
    "top_features": [...],
    "shap_values": [...],
    "base_value": 0.5
  },
  "generation_time": 0.1
}
```

### Forecasting Endpoints

#### POST /api/v1/forecast

Generate progression forecast for 6, 12, and 24 months.

**Request Body:**
```json
{
  "patient_id": "PATIENT_001",
  "patient_history": [
    {"mmse_score": 28.0, "age": 70, "csf_ab42": 500.0},
    {"mmse_score": 26.0, "age": 71, "csf_ab42": 480.0},
    {"mmse_score": 24.0, "age": 72, "csf_ab42": 450.0},
    {"mmse_score": 22.0, "age": 73, "csf_ab42": 420.0}
  ]
}
```

**Response:**
```json
{
  "patient_id": "PATIENT_001",
  "forecasts": {
    "6_month_mmse": 20.5,
    "12_month_mmse": 18.2,
    "24_month_mmse": 15.8
  },
  "uncertainty": {
    "6_month_mmse": 2.0,
    "12_month_mmse": 2.0,
    "24_month_mmse": 2.0
  },
  "timestamp": "2025-01-26T12:00:00",
  "generation_time": 0.4
}
```

### Cache Management

#### GET /api/v1/models/cache/status

Get status of model cache.

**Response:**
```json
{
  "cached_models": ["ensemble_production", "random_forest_production"],
  "cached_interpretability_systems": ["ensemble_v123"],
  "cached_forecasters": ["progression_forecaster"],
  "total_cached": 4
}
```

#### POST /api/v1/models/cache/clear

Clear model cache (useful after model updates).

**Response:**
```json
{
  "success": true,
  "message": "Model cache cleared",
  "models_cleared": 2,
  "interpretability_systems_cleared": 1,
  "forecasters_cleared": 1
}
```

### Health Check

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "ml-inference-api",
  "timestamp": "2025-01-26T12:00:00"
}
```

## Feature Validation

All feature inputs are validated according to Requirement 3.5:

- **MMSE Score**: 0-30
- **MoCA Score**: 0-30
- **CDR Global**: 0-3
- **CSF Biomarkers**: Non-negative values within physiological ranges
- **Imaging Features**: Non-negative volumes
- **APOE e4 Count**: 0, 1, or 2
- **Age**: 0-120 years
- **Education**: 0-30 years

Invalid inputs will return a 400 Bad Request error with details.

## Model Caching

The API implements in-memory model caching (Requirement 12.3) to reduce loading time:

- Models are loaded once and cached in memory
- Subsequent predictions use the cached model
- Cache can be cleared manually via API endpoint
- Cache is automatically updated when models are promoted

## Performance

- **Single Prediction**: ~0.5s (including SHAP explanation)
- **Batch Prediction**: ~0.1s per sample (without explanations)
- **Progression Forecast**: ~0.4s
- **SHAP Explanation**: <2s (Requirement 7.7)

## Example Usage

See `ml_pipeline/examples/inference_api_example.py` for complete examples.

### Python Client

```python
import requests

# Make a prediction
response = requests.post(
    "http://localhost:8000/api/v1/predict",
    json={
        "features": {
            "mmse_score": 24.0,
            "age": 72,
            "csf_ab42": 450.0,
            "hippocampus_volume": 6500.0,
            "apoe_e4_count": 1
        },
        "model_name": "ensemble",
        "include_explanation": True
    }
)

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Probability: {result['probability']}")
```

### cURL

```bash
# Make a prediction
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "mmse_score": 24.0,
      "age": 72,
      "csf_ab42": 450.0
    },
    "model_name": "ensemble"
  }'
```

## Error Handling

The API returns standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid input)
- **404**: Not Found (model or resource not found)
- **500**: Internal Server Error

Error responses include details:

```json
{
  "error": "Validation error",
  "detail": "Missing required features: ['mmse_score', 'age']"
}
```

## Security Considerations

For production deployment:

1. **Authentication**: Add API key or OAuth authentication
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **HTTPS**: Use TLS/SSL for encrypted communication
4. **CORS**: Configure CORS appropriately for your domain
5. **Input Sanitization**: Already implemented via Pydantic validation
6. **Audit Logging**: All predictions are logged for audit trails

## Monitoring

The API logs all operations including:

- Prediction requests and results
- Model loading and caching
- Errors and exceptions
- Performance metrics

Logs are written to `ml_pipeline/logs/ml_pipeline.log`.

## Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ml_pipeline/ ml_pipeline/

EXPOSE 8000

CMD ["uvicorn", "ml_pipeline.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t ml-pipeline-api .
docker run -p 8000:8000 ml-pipeline-api
```

## Troubleshooting

### Model Not Found

If you get "Model not found" errors:

1. Ensure models are registered in the model registry
2. Check that production models are promoted
3. Verify model storage path is correct

### Slow Predictions

If predictions are slow:

1. Check if models are being cached (use `/api/v1/models/cache/status`)
2. Disable SHAP explanations for faster predictions
3. Use batch predictions for multiple samples
4. Consider using GPU acceleration for neural networks

### Memory Issues

If running out of memory:

1. Clear model cache periodically
2. Reduce `max_background_samples` for SHAP explainer
3. Use smaller models or quantization
4. Deploy with more memory or use model serving infrastructure

## Support

For issues or questions:
- Check the API documentation at `/docs`
- Review logs in `ml_pipeline/logs/`
- See examples in `ml_pipeline/examples/`
