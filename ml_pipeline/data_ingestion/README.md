# Data Acquisition Layer

The data acquisition layer provides a comprehensive system for loading, validating, and tracking biomedical datasets from multiple sources.

## Overview

This module integrates data from three major Alzheimer's disease research datasets:
- **ADNI** (Alzheimer's Disease Neuroimaging Initiative)
- **OASIS** (Open Access Series of Imaging Studies)
- **NACC** (National Alzheimer's Coordinating Center)

## Features

- **Multi-source data loading**: Unified interface for ADNI, OASIS, and NACC datasets
- **Schema validation**: Automatic validation of data against predefined schemas
- **Provenance tracking**: Complete lineage tracking from source to processed data
- **Data parsing**: Specialized parsers for different data types (cognitive, biomarkers, imaging, genetic)
- **Error handling**: Comprehensive logging and error reporting

## Components

### 1. Data Loaders

#### ADNIDataLoader
Loads data from the Alzheimer's Disease Neuroimaging Initiative:
- Cognitive assessments (MMSE, ADAS-Cog, CDR, MoCA)
- CSF biomarkers (Aβ42, Tau, p-Tau)
- MRI metadata and volumetric data
- APOE genotype data

#### OASISDataLoader
Loads data from the Open Access Series of Imaging Studies:
- MRI volumetric data
- CDR scores
- Demographics
- Longitudinal data (OASIS-3)

#### NACCDataLoader
Loads data from the National Alzheimer's Coordinating Center:
- Clinical assessments (UDS forms)
- Cognitive test batteries
- Medical history
- Neuropathology data

### 2. Schema Validator

Validates data against predefined schemas to ensure:
- Required columns are present
- Data types are correct
- Values are within valid ranges
- No invalid or out-of-range values

### 3. Provenance Tracker

Tracks complete data lineage including:
- Data source and ingestion timestamp
- Processing stages (raw, validated, cleaned, transformed)
- Parent-child relationships for derived datasets
- Data hashes for integrity verification
- Processing steps applied

## Usage

### Basic Usage

```python
from ml_pipeline.data_ingestion import DataAcquisitionService

# Initialize service
service = DataAcquisitionService()

# Acquire ADNI data
adni_data = service.acquire_adni_data(
    data_types=['cognitive', 'biomarkers'],
    validate=True
)

# Acquire OASIS data
oasis_data = service.acquire_oasis_data(
    version="OASIS-3",
    validate=True
)

# Acquire NACC data
nacc_data = service.acquire_nacc_data(
    modules=['clinical', 'medical_history'],
    validate=True
)

# Get data summary
all_data = {
    'adni': adni_data,
    'oasis': oasis_data,
    'nacc': nacc_data
}
summary = service.get_data_summary(all_data)
print(summary)
```

### Individual Loaders

```python
from ml_pipeline.data_ingestion import ADNIDataLoader, OASISDataLoader, NACCDataLoader

# ADNI
adni_loader = ADNIDataLoader()
cognitive_data = adni_loader.load_cognitive_assessments()
biomarker_data = adni_loader.load_csf_biomarkers()

# OASIS
oasis_loader = OASISDataLoader()
oasis_data = oasis_loader.load_oasis_data(version="OASIS-3")

# NACC
nacc_loader = NACCDataLoader()
clinical_data = nacc_loader.load_clinical_assessments()
```

### Schema Validation

```python
from ml_pipeline.data_ingestion import SchemaValidator

validator = SchemaValidator()

# Validate data
result = validator.validate(data, schema_name='adni_cognitive')

if result.valid:
    print("Validation passed!")
else:
    print(f"Validation failed with {len(result.errors)} errors")
    for error in result.errors:
        print(f"  - {error.message}")
```

### Provenance Tracking

```python
from ml_pipeline.data_ingestion import ProvenanceTracker, DataSource

tracker = ProvenanceTracker()

# Track data ingestion
record = tracker.track_ingestion(
    dataset_name='adni_cognitive',
    data_source=DataSource.ADNI,
    data=cognitive_data,
    source_file=Path('/path/to/data.csv')
)

# Track processing step
processed_record = tracker.track_processing(
    parent_record_id=record.record_id,
    dataset_name='adni_cognitive_cleaned',
    processing_stage=ProcessingStage.CLEANED,
    data=cleaned_data,
    processing_steps=['remove_duplicates', 'handle_missing_values']
)

# Get lineage
lineage = tracker.get_lineage(processed_record.record_id)

# Export lineage graph
tracker.export_lineage_graph(
    record_id=processed_record.record_id,
    output_file=Path('lineage.json'),
    format='json'
)
```

## Data Schemas

### ADNI Cognitive Assessment
- `patient_id` (string, required)
- `visit_date` (date, required)
- `mmse_score` (float, 0-30)
- `adas_cog_score` (float, 0-70)
- `cdr_global` (float, 0/0.5/1/2/3)
- `cdr_sob` (float, 0-18)
- `moca_score` (float, 0-30)

### ADNI CSF Biomarker
- `patient_id` (string, required)
- `visit_date` (date, required)
- `csf_ab42` (float, 0-2000 pg/mL)
- `csf_tau` (float, 0-1500 pg/mL)
- `csf_ptau` (float, 0-200 pg/mL)
- `ab42_tau_ratio` (float)
- `ptau_tau_ratio` (float, 0-1)

### OASIS MRI
- `patient_id` (string, required)
- `visit_date` (date)
- `hippocampus_left` (float, mm³)
- `hippocampus_right` (float, mm³)
- `hippocampus_total` (float, mm³)
- `ventricle_volume` (float, mm³)
- `whole_brain_volume` (float, mm³)
- `icv` (float, mm³)

### NACC Clinical
- `patient_id` (string, required)
- `visit_date` (date, required)
- `visit_number` (integer)
- `mmse_score` (float, 0-30)
- `moca_score` (float, 0-30)
- `cdr_global` (float, 0/0.5/1/2/3)
- `cdr_sob` (float, 0-18)

## Data Sources

### ADNI
- Website: https://adni.loni.usc.edu/
- Access: Requires registration and data use agreement
- Data types: Cognitive, biomarkers, imaging, genetic

### OASIS
- Website: https://www.oasis-brains.org/
- Access: Publicly available
- Data types: MRI, demographics, CDR scores

### NACC
- Website: https://naccdata.org/
- Access: Requires registration
- Data types: Clinical assessments, medical history, neuropathology

## Configuration

Set the following environment variables or update `ml_pipeline/config/settings.py`:

```bash
# ADNI
ADNI_API_KEY=your_api_key
ADNI_BASE_URL=https://ida.loni.usc.edu/services

# OASIS
OASIS_DATA_PATH=/path/to/oasis/data

# NACC
NACC_DATA_PATH=/path/to/nacc/data

# Storage
RAW_DATA_PATH=/path/to/raw/data
METADATA_PATH=/path/to/metadata
```

## Example Script

Run the example script to see the data acquisition layer in action:

```bash
python ml_pipeline/examples/data_acquisition_example.py
```

## Requirements

The data acquisition layer requires the following Python packages:
- pandas
- numpy
- pydantic
- requests

See `ml_pipeline/requirements.txt` for complete list.

## Logging

All components use Python's logging module. Configure logging level:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Error Handling

The data acquisition layer handles errors gracefully:
- Missing files: Returns empty DataFrames with warnings
- Invalid data: Logs validation errors but continues processing
- Network errors: Retries with exponential backoff (ADNI API)

## Testing

Run tests for the data acquisition layer:

```bash
pytest ml_pipeline/tests/test_data_ingestion.py
```

## Contributing

When adding new data sources:
1. Create a new loader class in `ml_pipeline/data_ingestion/<source>/`
2. Implement parsers for each data type
3. Add schema definitions to `SchemaValidator`
4. Update `DataAcquisitionService` to integrate the new loader
5. Add tests and documentation

## License

This code is part of the MemoryGuard ML Pipeline project.
