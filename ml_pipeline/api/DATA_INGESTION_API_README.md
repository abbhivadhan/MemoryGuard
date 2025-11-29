# Data Ingestion API

REST API for biomedical data ingestion, validation, and feature engineering.

## Overview

The Data Ingestion API provides endpoints for:
- Uploading biomedical data (CSV, JSON, DICOM formats)
- Listing available data sources (ADNI, OASIS, NACC)
- Generating data quality reports
- Extracting features from raw data
- Retrieving patient features
- Getting feature distribution statistics

## Base URL

```
http://localhost:8000/api/v1/data
```

## Endpoints

### 1. Upload Data

Upload biomedical data for processing.

**Endpoint:** `POST /ingest`

**Parameters:**
- `format` (query, required): File format - `csv`, `json`, or `dicom`
- `validate` (query, optional): Run validation checks (default: `true`)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/data/ingest?format=csv&validate=true" \
  -F "file=@sample_data.csv"
```

**Response:**
```json
{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sample_data.csv",
  "format": "csv",
  "num_records": 1000,
  "num_columns": 15,
  "validation_status": "passed",
  "validation_summary": {
    "phi_detected": false,
    "completeness": 0.95,
    "duplicates_detected": false
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "processing_time": 2.5
}
```

**Validation Status:**
- `passed`: All validation checks passed
- `warning`: Some non-critical issues detected
- `failed_phi_detected`: PHI detected in data (critical)
- `not_validated`: Validation was skipped

**Supported Formats:**
- **CSV**: Comma-separated values
- **JSON**: JSON array of records
- **DICOM**: Medical imaging format (planned)

---

### 2. List Data Sources

List available biomedical data sources.

**Endpoint:** `GET /sources`

**Request:**
```bash
curl http://localhost:8000/api/v1/data/sources
```

**Response:**
```json
{
  "sources": [
    {
      "source_name": "ADNI",
      "source_type": "external",
      "description": "Alzheimer's Disease Neuroimaging Initiative",
      "available_data_types": [
        "cognitive_assessments",
        "csf_biomarkers",
        "mri_scans",
        "pet_imaging",
        "genetic_data"
      ],
      "total_records": null,
      "last_updated": null
    },
    {
      "source_name": "OASIS",
      "source_type": "external",
      "description": "Open Access Series of Imaging Studies",
      "available_data_types": [
        "mri_scans",
        "volumetric_data",
        "cdr_scores"
      ]
    },
    {
      "source_name": "NACC",
      "source_type": "external",
      "description": "National Alzheimer's Coordinating Center",
      "available_data_types": [
        "clinical_assessments",
        "neuropathology",
        "cognitive_tests"
      ]
    }
  ],
  "total_sources": 3
}
```

---

### 3. Get Quality Report

Generate comprehensive data quality report.

**Endpoint:** `GET /quality/{dataset_id}`

**Request:**
```bash
curl http://localhost:8000/api/v1/data/quality/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "dataset_name": "sample_dataset",
  "validation_passed": true,
  "report": {
    "phi_detection": {
      "phi_detected": false,
      "categories_detected": []
    },
    "completeness": {
      "overall_completeness": 0.95,
      "validation": {
        "validation_passed": true,
        "threshold": 0.70
      }
    },
    "outliers": {
      "total_outliers": 12,
      "outlier_percentage": 0.012
    },
    "duplicates": {
      "duplicate_rows": 0,
      "validation_passed": true
    },
    "range_validation": {
      "validation_summary": {
        "validation_passed": true,
        "total_violations": 0
      }
    }
  },
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**Quality Checks:**
- **PHI Detection**: Scans for 18 HIPAA identifiers
- **Completeness**: Checks for missing values
- **Outliers**: Detects statistical outliers (IQR, Z-score)
- **Duplicates**: Identifies duplicate records
- **Range Validation**: Validates biomarker and score ranges
- **Temporal Consistency**: Validates date sequences

---

### 4. Extract Features

Trigger feature engineering on uploaded data.

**Endpoint:** `POST /features/extract`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/data/features/extract \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
    "patient_id_col": "patient_id",
    "visit_date_col": "visit_date",
    "include_temporal": true,
    "save_to_store": true
  }'
```

**Response:**
```json
{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "num_features": 45,
  "feature_names": [
    "mmse_score",
    "moca_score",
    "cdr_global",
    "csf_ab42",
    "csf_tau",
    "hippocampus_volume",
    "age",
    "apoe_e4_count",
    "..."
  ],
  "num_records": 1000,
  "saved_to_store": true,
  "timestamp": "2024-01-15T10:40:00Z",
  "processing_time": 15.3
}
```

**Feature Engineering Steps:**
1. **Cognitive Features**: Extract MMSE, MoCA, CDR scores
2. **Biomarker Features**: Process CSF Aβ42, Tau, p-Tau
3. **Imaging Features**: Extract hippocampal volume, cortical thickness
4. **Genetic Features**: Encode APOE genotype
5. **Demographic Features**: Process age, sex, education
6. **Missing Data Imputation**: Handle missing values
7. **Feature Normalization**: Standardize continuous features
8. **Temporal Features**: Calculate rates of change (optional)

---

### 5. Get Patient Features

Retrieve features for a specific patient.

**Endpoint:** `GET /features/{patient_id}`

**Request:**
```bash
curl http://localhost:8000/api/v1/data/features/P001
```

**Response:**
```json
{
  "patient_id": "P001",
  "features": {
    "mmse_score": 24.0,
    "moca_score": 22.0,
    "cdr_global": 0.5,
    "csf_ab42": 450.0,
    "csf_tau": 350.0,
    "hippocampus_volume": 6500.0,
    "age": 72,
    "apoe_e4_count": 1
  },
  "num_features": 45,
  "last_updated": "2024-01-15T10:45:00Z"
}
```

---

### 6. Get Feature Statistics

Get distribution statistics for all features.

**Endpoint:** `GET /features/statistics`

**Request:**
```bash
curl http://localhost:8000/api/v1/data/features/statistics
```

**Response:**
```json
{
  "num_features": 45,
  "feature_statistics": {
    "mmse_score": {
      "mean": 24.5,
      "std": 4.2,
      "min": 10.0,
      "max": 30.0,
      "median": 25.0,
      "q25": 22.0,
      "q75": 27.0,
      "missing_count": 5,
      "missing_percentage": 0.5
    },
    "csf_ab42": {
      "mean": 475.3,
      "std": 125.8,
      "min": 200.0,
      "max": 800.0,
      "median": 480.0,
      "q25": 400.0,
      "q75": 550.0,
      "missing_count": 12,
      "missing_percentage": 1.2
    }
  },
  "timestamp": "2024-01-15T10:50:00Z"
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `500`: Internal server error

---

## Requirements Mapping

This API implements the following requirements from the design document:

- **Requirement 1.4**: Support CSV, JSON, and DICOM file formats
- **Requirements 1.1, 1.2, 1.3**: List available datasets (ADNI, OASIS, NACC)
- **Requirement 4.6**: Return validation results
- **Requirements 3.1-3.8**: Trigger feature engineering
- **Requirement 12.4**: Return patient features
- **Requirement 10.1**: Return feature distributions

---

## Example Usage

See `ml_pipeline/examples/data_ingestion_api_example.py` for complete examples.

### Quick Start

1. Start the API server:
```bash
python -m uvicorn ml_pipeline.api.main:app --reload
```

2. Upload data:
```bash
curl -X POST "http://localhost:8000/api/v1/data/ingest?format=csv" \
  -F "file=@your_data.csv"
```

3. Get quality report:
```bash
curl http://localhost:8000/api/v1/data/quality/{dataset_id}
```

4. Extract features:
```bash
curl -X POST http://localhost:8000/api/v1/data/features/extract \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "{dataset_id}", "patient_id_col": "patient_id"}'
```

---

## Testing

Run the test suite:
```bash
pytest ml_pipeline/tests/test_data_ingestion_api.py -v
```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Dataset IDs are UUIDs
- Processing times are in seconds
- Feature store must be initialized before retrieving patient features
- DICOM support is planned but not yet implemented
