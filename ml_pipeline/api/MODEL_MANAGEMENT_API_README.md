# Model Management API

REST API endpoints for managing ML models in the registry.

## Overview

The Model Management API provides endpoints for:
- Listing all registered models
- Viewing version history for models
- Promoting models to production
- Getting production model information
- Comparing model versions
- Viewing deployment history

## Requirements

This implementation satisfies the following requirements:
- **Requirement 8.1**: Model versioning and storage
- **Requirement 8.4**: Rollback mechanism (via promotion)
- **Requirement 8.5**: Track production deployments
- **Requirement 8.7**: Maintain model version history

## API Endpoints

### 1. List All Models

**Endpoint:** `GET /api/v1/models`

**Description:** Returns a list of all unique model names in the registry with basic information.

**Requirements:** 8.1

**Response:**
```json
[
  {
    "model_name": "random_forest",
    "total_versions": 5,
    "production_version": "v20250126_a1b2c3d4",
    "latest_version": "v20250127_e5f6g7h8"
  }
]
```

**Example:**
```bash
curl http://localhost:8000/api/v1/models
```

---

### 2. List Model Versions

**Endpoint:** `GET /api/v1/models/{model_name}/versions`

**Description:** Returns version history for a specific model, ordered by creation date (most recent first).

**Requirements:** 8.1, 8.7

**Parameters:**
- `model_name` (path): Name of the model
- `limit` (query, optional): Maximum number of versions to return (default: 10, max: 100)

**Response:**
```json
[
  {
    "version_id": "v20250127_e5f6g7h8",
    "model_type": "random_forest",
    "created_at": "2025-01-27T10:30:00",
    "status": "registered",
    "roc_auc": 0.8542,
    "accuracy": 0.8123,
    "dataset_version": "v2025_01"
  }
]
```

**Example:**
```bash
curl http://localhost:8000/api/v1/models/random_forest/versions?limit=5
```

---

### 3. Promote Model to Production

**Endpoint:** `POST /api/v1/models/{model_name}/promote/{version_id}`

**Description:** Promotes a model version to production status. The current production version (if any) is automatically demoted to archived status.

**Requirements:** 8.4, 8.5

**Parameters:**
- `model_name` (path): Name of the model
- `version_id` (path): Version ID to promote

**Request Body:**
```json
{
  "user_id": "data_scientist_1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully promoted random_forest v20250127_e5f6g7h8 to production. Previous production version v20250126_a1b2c3d4 archived.",
  "model_name": "random_forest",
  "version_id": "v20250127_e5f6g7h8",
  "previous_production": "v20250126_a1b2c3d4"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/models/random_forest/promote/v20250127_e5f6g7h8 \
  -H "Content-Type: application/json" \
  -d '{"user_id": "data_scientist_1"}'
```

---

### 4. Get Production Model

**Endpoint:** `GET /api/v1/models/{model_name}/production`

**Description:** Returns information about the model version currently deployed in production.

**Requirements:** 8.5

**Parameters:**
- `model_name` (path): Name of the model

**Response:**
```json
{
  "version_id": "v20250127_e5f6g7h8",
  "model_name": "random_forest",
  "model_type": "random_forest",
  "deployed_at": "2025-01-27T11:00:00",
  "metrics": {
    "accuracy": 0.8123,
    "balanced_accuracy": 0.8056,
    "precision": 0.7890,
    "recall": 0.8234,
    "f1_score": 0.8058,
    "roc_auc": 0.8542,
    "pr_auc": 0.8123
  },
  "dataset_version": "v2025_01",
  "artifact_path": "ml_pipeline/data_storage/models/random_forest/v20250127_e5f6g7h8/model.pkl"
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/models/random_forest/production
```

---

### 5. Compare Model Versions

**Endpoint:** `GET /api/v1/models/{model_name}/compare`

**Description:** Compares performance metrics across different versions of a model.

**Parameters:**
- `model_name` (path): Name of the model
- `version_ids` (query, optional): Specific version IDs to compare
- `metric` (query, optional): Metric to sort by (default: "roc_auc")

**Response:**
```json
{
  "model_name": "random_forest",
  "comparison_metric": "roc_auc",
  "versions": [
    {
      "version_id": "v20250127_e5f6g7h8",
      "model_type": "random_forest",
      "created_at": "2025-01-27T10:30:00",
      "status": "production",
      "metrics": {
        "accuracy": 0.8123,
        "roc_auc": 0.8542,
        "f1_score": 0.8058
      },
      "dataset_version": "v2025_01",
      "n_training_samples": 10000,
      "training_duration_seconds": 45.2
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/models/random_forest/compare?metric=roc_auc
```

---

### 6. Get Deployment History

**Endpoint:** `GET /api/v1/models/{model_name}/deployment-history`

**Description:** Returns the history of production deployments for a model.

**Parameters:**
- `model_name` (path): Name of the model
- `limit` (query, optional): Maximum number of deployments to return (default: 10, max: 50)

**Response:**
```json
{
  "model_name": "random_forest",
  "deployment_count": 3,
  "deployments": [
    {
      "timestamp": "2025-01-27T11:00:00",
      "version_id": "v20250127_e5f6g7h8",
      "previous_version": "v20250126_a1b2c3d4",
      "user_id": "data_scientist_1",
      "success": true
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/models/random_forest/deployment-history?limit=5
```

---

### 7. Get Registry Statistics

**Endpoint:** `GET /api/v1/models/statistics/registry`

**Description:** Returns aggregate statistics about all models in the registry.

**Response:**
```json
{
  "registry_statistics": {
    "total_models": 3,
    "total_versions": 15,
    "production_models": 3,
    "archived_models": 12,
    "average_production_metrics": {
      "accuracy": 0.8234,
      "roc_auc": 0.8567,
      "f1_score": 0.8123
    }
  },
  "timestamp": "2025-01-27T12:00:00"
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/models/statistics/registry
```

---

## Usage Examples

### Python Example

See `ml_pipeline/examples/model_management_api_example.py` for a complete Python example demonstrating all endpoints.

```python
import requests

# List all models
response = requests.get("http://localhost:8000/api/v1/models")
models = response.json()

# Get production model
response = requests.get("http://localhost:8000/api/v1/models/random_forest/production")
production_model = response.json()

# Promote a model
response = requests.post(
    "http://localhost:8000/api/v1/models/random_forest/promote/v20250127_e5f6g7h8",
    json={"user_id": "data_scientist_1"}
)
result = response.json()
```

### cURL Examples

```bash
# List all models
curl http://localhost:8000/api/v1/models

# List versions for a model
curl http://localhost:8000/api/v1/models/random_forest/versions

# Get production model
curl http://localhost:8000/api/v1/models/random_forest/production

# Promote a model
curl -X POST http://localhost:8000/api/v1/models/random_forest/promote/v20250127_e5f6g7h8 \
  -H "Content-Type: application/json" \
  -d '{"user_id": "data_scientist_1"}'

# Compare versions
curl http://localhost:8000/api/v1/models/random_forest/compare?metric=roc_auc

# Get deployment history
curl http://localhost:8000/api/v1/models/random_forest/deployment-history
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `404 Not Found`: Model or version not found
- `400 Bad Request`: Invalid request (e.g., promoting non-existent version)
- `500 Internal Server Error`: Server error

Error responses include a detail message:

```json
{
  "detail": "Model not found: nonexistent_model"
}
```

---

## Integration with Model Registry

The API is built on top of the `ModelRegistry` class, which provides:

- **Automatic versioning**: Generates unique version IDs
- **Metadata storage**: Stores metrics, hyperparameters, and training info
- **Artifact management**: Saves model files and associated data
- **Audit logging**: Tracks all operations for compliance
- **Production tracking**: Manages deployment status

---

## Running the API

Start the API server:

```bash
python -m ml_pipeline.api.main
```

The API will be available at `http://localhost:8000`

View interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Testing

Run the test suite:

```bash
pytest ml_pipeline/tests/test_model_management_api.py -v
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Application                     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │     Model Management API Router                │    │
│  │                                                 │    │
│  │  • GET /api/v1/models                          │    │
│  │  • GET /api/v1/models/{name}/versions          │    │
│  │  • POST /api/v1/models/{name}/promote/{ver}    │    │
│  │  • GET /api/v1/models/{name}/production        │    │
│  │  • GET /api/v1/models/{name}/compare           │    │
│  │  • GET /api/v1/models/{name}/deployment-history│    │
│  │  • GET /api/v1/models/statistics/registry      │    │
│  └────────────────────────────────────────────────┘    │
│                         │                               │
└─────────────────────────┼───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Model Registry                         │
│                                                          │
│  • Version Management                                   │
│  • Artifact Storage                                     │
│  • Metadata Tracking                                    │
│  • Production Deployment                                │
│  • Audit Logging                                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Storage Layer                           │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐            │
│  │  PostgreSQL  │         │  File System │            │
│  │  (Metadata)  │         │  (Artifacts) │            │
│  └──────────────┘         └──────────────┘            │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Notes

1. **Automatic Demotion**: When promoting a model to production, the current production version is automatically demoted to "archived" status.

2. **Audit Trail**: All promotion operations are logged in the audit log with user ID, timestamp, and details.

3. **Version Immutability**: Once registered, model versions cannot be modified. This ensures reproducibility.

4. **Production Safety**: Only one version per model can be in production at a time.

5. **Rollback Support**: Rolling back to a previous version is accomplished by promoting that version back to production.

---

## Future Enhancements

Potential future additions:
- Model deletion endpoint (with safety checks)
- Batch promotion for multiple models
- Model comparison across different model types
- Performance trend analysis over time
- Automated promotion based on metrics
- A/B testing support for gradual rollout
- Model approval workflow

---

## Related Documentation

- [Model Registry Documentation](../models/README.md)
- [Inference API Documentation](./README.md)
- [Training Pipeline Documentation](../training/README.md)
