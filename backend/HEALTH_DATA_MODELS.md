# Health Data Models Implementation

This document summarizes the database models implemented for health data tracking in MemoryGuard.

## Models Implemented

### 1. HealthMetric Model (`health_metric.py`)
**Purpose:** Track various health indicators for Alzheimer's risk assessment

**Features:**
- Supports 5 metric types: cognitive, biomarker, imaging, lifestyle, cardiovascular
- Tracks metric source (manual, assessment, device, lab)
- Stores value with unit and timestamp
- Comprehensive indexing for efficient queries

**Key Fields:**
- `type`: MetricType enum (cognitive, biomarker, imaging, lifestyle, cardiovascular)
- `name`: Metric name (e.g., "MMSE", "Amyloid-beta 42")
- `value`: Numeric value
- `unit`: Unit of measurement
- `source`: MetricSource enum (manual, assessment, device, lab)
- `timestamp`: When the metric was recorded

**Indexes:**
- Single: user_id, type, name, timestamp
- Composite: user_id+type, user_id+timestamp, user_id+type+timestamp, user_id+name

**Requirements Satisfied:** 11.1, 11.2, 11.3, 11.4, 11.5, 11.6

---

### 2. Assessment Model (`assessment.py`)
**Purpose:** Store cognitive test results and responses

**Features:**
- Supports MMSE, MoCA, CDR, and Clock Drawing tests
- Tracks assessment status (in_progress, completed, abandoned)
- Stores detailed responses as JSON
- Automatic scoring support
- Duration tracking

**Key Fields:**
- `type`: AssessmentType enum (MMSE, MoCA, CDR, ClockDrawing)
- `status`: AssessmentStatus enum (in_progress, completed, abandoned)
- `score`: Test score (null until completed)
- `max_score`: Maximum possible score
- `responses`: JSON object with detailed test responses
- `duration`: Time taken in seconds
- `started_at`, `completed_at`: Timing information

**Indexes:**
- Single: user_id, type, completed_at
- Composite: user_id+type, user_id+completed_at, user_id+type+completed_at

**Requirements Satisfied:** 12.1, 12.4

---

### 3. Medication Model (`medication.py`)
**Purpose:** Track medication schedules, adherence, and side effects

**Features:**
- Medication schedule management
- Adherence logging with timestamps
- Side effects tracking
- Active/inactive status
- Adherence rate calculation method

**Key Fields:**
- `name`, `dosage`, `frequency`: Medication details
- `schedule`: Array of scheduled dose times
- `adherence_log`: JSON array of adherence records
- `side_effects`: Array of side effect descriptions
- `active`: Boolean status
- `start_date`, `end_date`: Medication period

**Methods:**
- `calculate_adherence_rate(days)`: Calculate adherence percentage for last N days

**Indexes:**
- Single: user_id, active
- Composite: user_id+active, user_id+start_date

**Requirements Satisfied:** 13.1, 13.3, 13.4

---

### 4. Prediction Model (`prediction.py`)
**Purpose:** Store ML-based risk assessment results with interpretability

**Features:**
- Risk score and category
- Confidence intervals
- SHAP feature importance values
- Progression forecasts (6, 12, 24 months)
- Personalized recommendations
- Model versioning

**Key Fields:**
- `risk_score`: 0-1 scale risk probability
- `risk_category`: RiskCategory enum (low, moderate, high)
- `confidence_interval_lower`, `confidence_interval_upper`: Confidence bounds
- `feature_importance`: JSON object with SHAP values
- `forecast_six_month`, `forecast_twelve_month`, `forecast_twenty_four_month`: Progression predictions
- `recommendations`: Array of personalized recommendations
- `model_version`, `model_type`: Model metadata
- `input_features`: JSON object with input data for reproducibility

**Indexes:**
- Single: user_id, risk_category, prediction_date
- Composite: user_id+prediction_date, user_id+risk_category

**Requirements Satisfied:** 3.3, 3.4, 4.1

---

### 5. EmergencyContact Model (`emergency_contact.py`)
**Purpose:** Store emergency contact information

**Features:**
- Contact details (name, phone, email, address)
- Relationship type classification
- Priority ordering
- Active/inactive status

**Key Fields:**
- `name`, `phone`, `email`: Contact information
- `relationship`: RelationshipType enum (family, friend, caregiver, healthcare_provider, other)
- `priority`: Priority level (1 = primary)
- `active`: Boolean status

**Indexes:**
- Single: user_id
- Composite: user_id+active, user_id+priority

**Requirements Satisfied:** 14.3

---

### 6. CaregiverRelationship Model (`emergency_contact.py`)
**Purpose:** Manage caregiver access and permissions

**Features:**
- Patient-caregiver relationship tracking
- Granular permission system
- Approval workflow
- Active/inactive status

**Key Fields:**
- `patient_id`, `caregiver_id`: User IDs
- `relationship_type`: RelationshipType enum
- Permission flags:
  - `can_view_health_data`
  - `can_view_assessments`
  - `can_view_medications`
  - `can_manage_reminders`
  - `can_receive_alerts`
- `active`, `approved`: Status flags

**Indexes:**
- Single: patient_id, caregiver_id, active
- Composite: patient_id+active, caregiver_id+active, patient_id+caregiver_id (unique)

**Requirements Satisfied:** 6.1

---

### 7. ProviderRelationship Model (`emergency_contact.py`)
**Purpose:** Manage healthcare provider access

**Features:**
- Patient-provider relationship tracking
- Provider metadata (type, specialty, organization)
- Permission system
- Approval workflow

**Key Fields:**
- `patient_id`, `provider_id`: User IDs
- `provider_type`, `specialty`, `organization`: Provider details
- Permission flags:
  - `can_view_all_data`
  - `can_add_notes`
  - `can_view_predictions`
- `active`, `approved`: Status flags

**Indexes:**
- Single: patient_id, provider_id, active
- Composite: patient_id+active, provider_id+active, patient_id+provider_id (unique)

**Requirements Satisfied:** 6.1

---

## Database Migration

A comprehensive migration file has been created: `002_create_health_data_tables.py`

**Migration includes:**
- All 7 tables with proper foreign keys
- All enum types (MetricType, MetricSource, AssessmentType, etc.)
- Comprehensive indexes for query optimization
- CASCADE delete for referential integrity
- Default values for arrays and JSON fields
- Proper upgrade and downgrade functions

**To run migrations:**
```bash
make migrate
# or
docker-compose exec backend alembic upgrade head
```

See `MIGRATIONS.md` for detailed migration documentation.

---

## Model Features

### Common Features (All Models)
- UUID primary keys
- `created_at` and `updated_at` timestamps (auto-managed)
- Foreign key to `users` table with CASCADE delete
- `to_dict()` method for JSON serialization
- `__repr__()` method for debugging

### Data Types Used
- **UUID**: Primary keys and foreign keys
- **String**: Text fields
- **Float**: Numeric measurements
- **Integer**: Scores and durations
- **Boolean**: Status flags
- **DateTime**: Timestamps
- **JSON**: Complex nested data (responses, feature_importance, input_features)
- **ARRAY**: Lists (schedule, side_effects, recommendations)
- **Enum**: Categorical data with predefined values

### Indexing Strategy
All models include strategic indexes for:
- Single column lookups (user_id, type, status)
- Composite queries (user_id+type, user_id+timestamp)
- Unique constraints (patient_id+caregiver_id)

This ensures efficient queries for common access patterns.

---

## Usage Examples

### Creating a Health Metric
```python
from app.models import HealthMetric, MetricType, MetricSource

metric = HealthMetric(
    user_id=user.id,
    type=MetricType.COGNITIVE,
    name="MMSE",
    value=28.0,
    unit="points",
    source=MetricSource.ASSESSMENT,
    timestamp=datetime.utcnow()
)
db.add(metric)
db.commit()
```

### Creating an Assessment
```python
from app.models import Assessment, AssessmentType, AssessmentStatus

assessment = Assessment(
    user_id=user.id,
    type=AssessmentType.MMSE,
    status=AssessmentStatus.IN_PROGRESS,
    max_score=30,
    responses={}
)
db.add(assessment)
db.commit()
```

### Creating a Prediction
```python
from app.models import Prediction, RiskCategory

prediction = Prediction(
    user_id=user.id,
    risk_score=0.65,
    risk_category=RiskCategory.MODERATE,
    confidence_interval_lower=0.55,
    confidence_interval_upper=0.75,
    feature_importance={"age": 0.3, "mmse": 0.25, "apoe": 0.2},
    forecast_six_month=0.68,
    forecast_twelve_month=0.72,
    forecast_twenty_four_month=0.78,
    recommendations=["Increase physical activity", "Improve sleep quality"],
    model_version="1.0.0",
    model_type="ensemble",
    input_features={},
    prediction_date=datetime.utcnow()
)
db.add(prediction)
db.commit()
```

---

## Next Steps

With these models in place, you can now:

1. **Build API endpoints** (Task 7) for health metrics CRUD operations
2. **Implement ML prediction system** (Task 8) using the Prediction model
3. **Create health metrics dashboard** (Task 9) to visualize the data
4. **Develop cognitive assessment system** (Task 11) using the Assessment model
5. **Build medication tracking** (Task 13) using the Medication model

All models are production-ready with proper validation, indexing, and relationships.
