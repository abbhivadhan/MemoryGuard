# Data Validation and Quality Engine

Comprehensive data validation system for biomedical datasets ensuring HIPAA compliance, data quality, and ML readiness.

## Features

### 1. PHI Detection
- Detects 18 HIPAA identifiers using regex patterns
- NLP-based detection for complex PHI
- Automatic quarantine mechanism for PHI data
- Comprehensive PHI reporting

### 2. De-identification Verification
- Verifies removal of all direct identifiers
- K-anonymity checking (k ≥ 5)
- Age generalization validation (ages > 89 → 90+)
- ZIP code generalization (5 digits → 3 digits)
- Date generalization verification

### 3. Completeness Checking
- Calculates percentage of non-null values per column
- Generates completeness reports
- Rejects datasets below 70% completeness threshold
- Identifies missing value patterns
- Suggests columns to drop

### 4. Outlier Detection
- IQR (Interquartile Range) method
- Z-score method
- Modified Z-score (robust to outliers)
- Generates outlier reports with statistics
- Flags extreme outliers

### 5. Range Validation
- Predefined ranges for biomarkers and cognitive scores
- Custom range definitions
- Validates data against expected ranges
- Identifies out-of-range values
- Comprehensive violation reporting

### 6. Duplicate Detection
- Exact duplicate detection
- Patient duplicate detection
- Visit duplicate detection
- Fuzzy/near duplicate detection
- Automatic duplicate removal

### 7. Temporal Consistency Validation
- Validates date sequences in longitudinal data
- Checks chronological ordering
- Validates visit intervals
- Ensures logical temporal ordering
- Date range validation

### 8. Quality Reporting
- Comprehensive quality reports (JSON/HTML)
- Overall quality score (0-100)
- Letter grades (A-F)
- Issues and recommendations
- ML readiness assessment

## Usage

### Basic Validation

```python
from ml_pipeline.data_validation import DataValidationEngine
import pandas as pd

# Initialize engine
engine = DataValidationEngine(
    completeness_threshold=0.70,
    k_anonymity_threshold=5
)

# Load data
data = pd.read_csv('biomedical_data.csv')

# Validate dataset
report = engine.validate_dataset(
    data=data,
    dataset_name="ADNI Cognitive Assessments",
    patient_id_col='patient_id',
    visit_date_col='visit_date',
    strict_mode=True
)

# Print summary
engine.print_summary(report)

# Check if ready for ML
is_ready, issues = engine.validate_for_ml_training(data)
print(f"Ready for ML: {is_ready}")
if issues:
    print("Blocking issues:", issues)
```

### Quick Validation

```python
# Quick validation (PHI, completeness, duplicates only)
quick_results = engine.quick_validate(data)

if quick_results['quick_validation_passed']:
    print("✓ Quick validation passed")
else:
    print("✗ Quick validation failed")
    print(f"PHI detected: {quick_results['phi_detected']}")
    print(f"Completeness: {quick_results['completeness']*100:.1f}%")
```

### Validate and Clean

```python
# Automatically clean dataset
cleaned_data, cleaning_report = engine.validate_and_clean(
    data=data,
    remove_duplicates=True,
    remove_incomplete_columns=True,
    incomplete_threshold=0.50
)

print(f"Original shape: {cleaning_report['original_shape']}")
print(f"Final shape: {cleaning_report['final_shape']}")
print(f"Rows removed: {cleaning_report['rows_removed']}")
print(f"Columns removed: {cleaning_report['columns_removed']}")
```

### Generate Reports

```python
from pathlib import Path

# Generate JSON report
report = engine.generate_report(
    data=data,
    dataset_name="ADNI Dataset",
    patient_id_col='patient_id',
    visit_date_col='visit_date',
    output_path=Path('reports/quality_report.json'),
    format='json'
)

# Generate HTML report
engine.generate_report(
    data=data,
    dataset_name="ADNI Dataset",
    output_path=Path('reports/quality_report.html'),
    format='html'
)
```

### Individual Validators

```python
from ml_pipeline.data_validation import (
    PHIDetector,
    CompletenessChecker,
    OutlierDetector,
    RangeValidator
)

# PHI Detection
phi_detector = PHIDetector()
phi_report = phi_detector.get_phi_report(data)

# Completeness Check
completeness_checker = CompletenessChecker(completeness_threshold=0.70)
validation_passed, details = completeness_checker.validate_dataset_completeness(data)

# Outlier Detection
outlier_detector = OutlierDetector()
outlier_report = outlier_detector.generate_outlier_report(data, method='both')

# Range Validation
range_validator = RangeValidator()
range_report = range_validator.generate_range_report(data)
```

## Validation Thresholds

### Default Thresholds
- **Completeness**: 70% (configurable)
- **K-anonymity**: k ≥ 5 (configurable)
- **IQR Multiplier**: 1.5
- **Z-score Threshold**: 3.0
- **Visit Interval**: 1-730 days

### Quality Score Grading
- **A (90-100)**: Excellent quality
- **B (80-89)**: Good quality
- **C (70-79)**: Acceptable quality
- **D (60-69)**: Poor quality
- **F (0-59)**: Unacceptable quality

## Predefined Ranges

### Cognitive Scores
- MMSE: 0-30 points
- MoCA: 0-30 points
- CDR: 0-3 score
- ADAS-Cog: 0-70 points

### CSF Biomarkers
- Aβ42: 0-2000 pg/mL
- Total Tau: 0-1500 pg/mL
- Phosphorylated Tau: 0-150 pg/mL

### Brain Volumes
- Hippocampus: 1.0-10.0 cm³
- Entorhinal Cortex: 0.5-5.0 cm³
- Ventricular Volume: 10-200 cm³
- Whole Brain: 800-1800 cm³

### Demographics
- Age: 18-120 years
- Education: 0-30 years
- APOE e4 count: 0-2 alleles

## Output Formats

### JSON Report
```json
{
  "report_metadata": {
    "dataset_name": "ADNI Dataset",
    "generated_at": "2025-01-15T10:30:00",
    "report_version": "1.0"
  },
  "quality_score": {
    "overall_score": 85.5,
    "grade": "B",
    "component_scores": {...}
  },
  "overall_assessment": {
    "overall_status": "GOOD",
    "ready_for_ml": true,
    "issues": [],
    "recommendations": []
  }
}
```

### HTML Report
Interactive HTML report with:
- Visual quality score display
- Color-coded status indicators
- Detailed validation tables
- Issues and recommendations
- Exportable format

## Integration with Data Pipeline

```python
from ml_pipeline.data_ingestion import DataAcquisitionService
from ml_pipeline.data_validation import DataValidationEngine

# Acquire data
acquisition = DataAcquisitionService()
data = acquisition.download_adni_data('cognitive', ('2020-01-01', '2024-12-31'))

# Validate data
engine = DataValidationEngine()
report = engine.validate_dataset(data, dataset_name="ADNI Cognitive")

# Check if validation passed
if report['validation_passed']:
    # Proceed to feature engineering
    print("✓ Data validation passed - proceeding to feature engineering")
else:
    # Handle validation failures
    print("✗ Data validation failed")
    engine.print_summary(report)
```

## Best Practices

1. **Always check for PHI first** - Critical for HIPAA compliance
2. **Use strict mode for production** - Ensures highest quality standards
3. **Review outliers manually** - Not all outliers are errors
4. **Save validation reports** - Maintain audit trail
5. **Validate after each transformation** - Catch issues early
6. **Use appropriate thresholds** - Adjust based on use case
7. **Document custom ranges** - For domain-specific validations

## Requirements

- pandas >= 1.5.0
- numpy >= 1.23.0
- scipy >= 1.9.0
- python >= 3.11

## Logging

All validators use Python's logging module:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run validation with logging
engine = DataValidationEngine()
report = engine.validate_dataset(data)
```

## Error Handling

The validation engine handles errors gracefully:

```python
try:
    report = engine.validate_dataset(data)
except Exception as e:
    logger.error(f"Validation failed: {str(e)}")
    # Handle error appropriately
```

## Performance Considerations

- **Large datasets**: Validation scales linearly with dataset size
- **Fuzzy matching**: Limited to 1000 rows for performance
- **Outlier detection**: Efficient for numeric columns
- **PHI detection**: Samples up to 1000 values per column

## Support

For issues or questions, refer to the main ML Pipeline documentation.
