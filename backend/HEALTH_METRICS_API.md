# Health Metrics API Documentation

## Overview

The Health Metrics API provides comprehensive endpoints for managing, validating, and exporting health data related to Alzheimer's disease monitoring. This implementation covers Requirements 11.1-11.6, 3.5, 11.7, and 11.9.

## Implemented Features

### 1. CRUD Operations (Task 7.1)

#### Create Health Metric
- **Endpoint**: `POST /api/v1/health/metrics`
- **Description**: Create a new health metric with validation
- **Authentication**: Required (JWT Bearer token)
- **Request Body**:
```json
{
  "type": "cognitive",
  "name": "MMSE Score",
  "value": 28.0,
  "unit": "points",
  "source": "assessment",
  "timestamp": "2025-11-16T10:30:00Z",
  "notes": "Patient was alert and cooperative"
}
```

#### Get All User Metrics
- **Endpoint**: `GET /api/v1/health/metrics/{user_id}`
- **Query Parameters**: 
  - `limit` (default: 100, max: 1000)
  - `offset` (default: 0)
- **Description**: Retrieve all health metrics for a user with pagination

#### Get Metrics by Type
- **Endpoint**: `GET /api/v1/health/metrics/{user_id}/{metric_type}`
- **Metric Types**: `cognitive`, `biomarker`, `imaging`, `lifestyle`, `cardiovascular`
- **Description**: Filter metrics by specific type

#### Update Health Metric
- **Endpoint**: `PUT /api/v1/health/metrics/{metric_id}`
- **Description**: Update value, unit, or notes of an existing metric

#### Delete Health Metric
- **Endpoint**: `DELETE /api/v1/health/metrics/{metric_id}`
- **Description**: Permanently delete a health metric

### 2. Data Validation (Task 7.2)

#### Validation Service
- **File**: `backend/app/services/health_validation.py`
- **Features**:
  - Type-specific validation rules for all metric types
  - Value range validation with warnings for unusual values
  - Unit validation against expected units
  - Data completeness checking
  - Batch validation support

#### Supported Metrics

**Cognitive Metrics**:
- MMSE Score (0-30 points)
- MoCA Score (0-30 points)
- CDR Score (0-3 rating)
- Clock Drawing Score (0-10 points)

**Biomarker Metrics**:
- Amyloid-beta 42 (0-2000 pg/mL)
- Total Tau (0-1500 pg/mL)
- Phosphorylated Tau (0-200 pg/mL)
- Tau/Aβ42 Ratio (0-5 ratio)

**Imaging Metrics**:
- Hippocampal Volume (1000-8000 mm³)
- Cortical Thickness (1.0-5.0 mm)
- Entorhinal Cortex Volume (500-4000 mm³)
- Whole Brain Volume (800000-1600000 mm³)

**Lifestyle Metrics**:
- Sleep Duration (0-24 hours)
- Physical Activity (0-1440 minutes)
- Diet Quality Score (0-100 score)
- Social Engagement (0-100 score)
- Cognitive Activity (0-100 score)

**Cardiovascular Metrics**:
- Systolic/Diastolic Blood Pressure (mmHg)
- Total/LDL/HDL Cholesterol (mg/dL)
- Triglycerides (mg/dL)
- Fasting Glucose (mg/dL)
- HbA1c (%)

#### Validation Endpoints

**Check Data Completeness**
- **Endpoint**: `GET /api/v1/health/metrics/{user_id}/completeness`
- **Query Parameter**: `metric_type` (required)
- **Returns**: Completeness percentage, missing metrics, recommendations

**Get Metric Definitions**
- **Endpoint**: `GET /api/v1/health/metrics/definitions/{metric_type}`
- **Returns**: All standard metric definitions with ranges and units

**Batch Validation**
- **Endpoint**: `POST /api/v1/health/metrics/validate-batch`
- **Description**: Validate up to 100 metrics before submission
- **Returns**: Valid/invalid metrics with detailed error messages

### 3. Export Functionality (Task 7.3)

#### Export Service
- **File**: `backend/app/services/health_export.py`
- **Supported Formats**: CSV, FHIR R4 (JSON), PDF (HTML)

#### CSV Export
- **Endpoint**: `GET /api/v1/health/metrics/{user_id}/export/csv`
- **Query Parameter**: `metric_type` (optional filter)
- **Format**: Standard CSV with all metric fields
- **Use Case**: Data analysis, spreadsheet import

#### FHIR Export
- **Endpoint**: `GET /api/v1/health/metrics/{user_id}/export/fhir`
- **Query Parameter**: `metric_type` (optional filter)
- **Format**: FHIR R4 Bundle with Observation resources
- **Features**:
  - LOINC code mapping for standard metrics
  - Patient reference inclusion
  - FHIR-compliant metadata
- **Use Case**: EHR integration, healthcare interoperability

#### PDF Export
- **Endpoint**: `GET /api/v1/health/metrics/{user_id}/export/pdf`
- **Query Parameter**: `metric_type` (optional filter)
- **Format**: Styled HTML suitable for PDF conversion
- **Features**:
  - Professional report layout
  - Metrics grouped by type
  - Patient information header
  - Timestamp and metadata
- **Use Case**: Medical records, patient reports, provider sharing

## Security Features

- **Authentication**: All endpoints require JWT Bearer token
- **Authorization**: Users can only access their own data
- **Input Validation**: Pydantic models with custom validators
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Error Handling**: Comprehensive try-catch with proper HTTP status codes
- **Logging**: All operations logged for audit trail

## Database Optimization

- **Indexes**: Composite indexes on frequently queried columns
  - `user_id + type`
  - `user_id + timestamp`
  - `user_id + type + timestamp`
  - `user_id + name`
- **Pagination**: Limit/offset support for large datasets
- **Ordering**: Results ordered by timestamp (most recent first)

## Error Responses

All endpoints return consistent error format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

Common status codes:
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Not authorized to access resource
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Usage Examples

### Creating a Cognitive Metric
```bash
curl -X POST "http://localhost:8000/api/v1/health/metrics" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "cognitive",
    "name": "MMSE Score",
    "value": 28.0,
    "unit": "points",
    "source": "assessment"
  }'
```

### Checking Data Completeness
```bash
curl -X GET "http://localhost:8000/api/v1/health/metrics/{user_id}/completeness?metric_type=cognitive" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Exporting to CSV
```bash
curl -X GET "http://localhost:8000/api/v1/health/metrics/{user_id}/export/csv" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o health_metrics.csv
```

## Future Enhancements

- Caregiver/provider access control
- Real-time data updates via WebSocket
- Metric trend analysis endpoints
- Automated anomaly detection
- Integration with wearable devices
- Bulk import from CSV/FHIR

## Testing

To test the endpoints:
1. Start the backend server: `make backend-dev`
2. Authenticate to get JWT token
3. Use the token in Authorization header
4. Test CRUD operations
5. Validate data completeness
6. Test export functionality

## Requirements Coverage

- ✅ **11.1-11.6**: All metric types supported (cognitive, biomarker, imaging, lifestyle, cardiovascular)
- ✅ **3.5**: Comprehensive input validation with type and range checking
- ✅ **11.7**: Data completeness checking with recommendations
- ✅ **11.9**: Export to PDF, CSV, and FHIR formats

## Files Created

1. `backend/app/api/v1/health.py` - Health metrics API endpoints
2. `backend/app/services/health_validation.py` - Validation service
3. `backend/app/services/health_export.py` - Export service
4. `backend/HEALTH_METRICS_API.md` - This documentation

## Integration

The health metrics API is automatically registered in the FastAPI application through `backend/app/api/v1/__init__.py`. All endpoints are available under the `/api/v1/health` prefix.
