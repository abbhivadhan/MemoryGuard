# Feature Engineering Module

This module provides comprehensive feature engineering capabilities for biomedical data, transforming raw data from ADNI, OASIS, and NACC datasets into ML-ready features.

## Overview

The feature engineering pipeline processes multiple types of biomedical data:

- **Cognitive Features**: MMSE, MoCA, CDR, ADAS-Cog scores
- **Biomarker Features**: CSF Aβ42, Total Tau, Phosphorylated Tau, and ratios
- **Imaging Features**: Hippocampal volume, cortical thickness, ventricular volume
- **Genetic Features**: APOE genotype encoding and risk stratification
- **Demographic Features**: Age, sex, education, race, lifestyle factors
- **Temporal Features**: Time since baseline, decline rates, trajectories

## Components

### 1. CognitiveFeatureExtractor
Extracts cognitive assessment scores from standardized tests.

```python
from feature_engineering import CognitiveFeatureExtractor

extractor = CognitiveFeatureExtractor()
cognitive_features = extractor.extract_features(data)
```

### 2. BiomarkerFeatureProcessor
Processes CSF biomarker measurements and calculates diagnostic ratios.

```python
from feature_engineering import BiomarkerFeatureProcessor

processor = BiomarkerFeatureProcessor()
biomarker_features = processor.extract_features(data)
```

### 3. ImagingFeatureExtractor
Extracts volumetric and morphometric features from MRI data.

```python
from feature_engineering import ImagingFeatureExtractor

extractor = ImagingFeatureExtractor()
imaging_features = extractor.extract_features(data)
```

### 4. GeneticFeatureEncoder
Encodes APOE genotype and calculates genetic risk factors.

```python
from feature_engineering import GeneticFeatureEncoder

encoder = GeneticFeatureEncoder()
genetic_features = encoder.extract_features(data)
```

### 5. DemographicFeatureProcessor
Processes demographic and lifestyle information.

```python
from feature_engineering import DemographicFeatureProcessor

processor = DemographicFeatureProcessor()
demographic_features = processor.extract_features(data)
```

### 6. MissingDataImputer
Handles missing values using multiple imputation techniques.

```python
from feature_engineering import MissingDataImputer

imputer = MissingDataImputer(strategy='iterative')
imputed_data = imputer.fit_transform(data)
```

### 7. FeatureNormalizer
Normalizes continuous features using standardization or other methods.

```python
from feature_engineering import FeatureNormalizer

normalizer = FeatureNormalizer(method='standard')
normalized_data = normalizer.fit_transform(data)
```

### 8. TemporalFeatureEngineer
Creates temporal features from longitudinal data.

```python
from feature_engineering import TemporalFeatureEngineer

engineer = TemporalFeatureEngineer()
temporal_features = engineer.extract_features(data, 'patient_id', 'visit_date')
```

### 9. FeatureReportGenerator
Generates comprehensive reports on extracted features.

```python
from feature_engineering import FeatureReportGenerator

reporter = FeatureReportGenerator()
report = reporter.generate_report(features)
```

## Complete Pipeline

The `FeatureEngineeringPipeline` class orchestrates all feature engineering steps:

```python
from feature_engineering import FeatureEngineeringPipeline

# Initialize pipeline
pipeline = FeatureEngineeringPipeline(
    imputation_strategy='iterative',
    normalization_method='standard',
    include_temporal=True
)

# Fit and transform training data
engineered_features = pipeline.fit_transform(
    train_data,
    patient_id_col='patient_id',
    visit_date_col='visit_date'
)

# Transform new data
new_features = pipeline.transform(new_data)

# Get feature report
report = pipeline.get_feature_report()

# Save documentation
pipeline.save_feature_documentation('features/report.txt')
```

## Example Usage

See `examples/feature_engineering_example.py` for a complete example:

```bash
cd ml_pipeline
python examples/feature_engineering_example.py
```

## Feature Categories

### Cognitive Features
- MMSE total score and components
- MoCA total score and components
- CDR global score and sum of boxes
- ADAS-Cog total score
- Severity indicators

### Biomarker Features
- CSF Aβ42, Total Tau, Phosphorylated Tau levels
- Aβ42/Tau ratio, p-Tau/Tau ratio
- Biomarker positivity indicators
- AD biomarker profile (A+T+)

### Imaging Features
- Hippocampal volume (left, right, total)
- Entorhinal cortex thickness
- Ventricular volume
- Whole brain volume
- Cortical thickness for multiple regions
- ICV-normalized volumes
- Derived features (asymmetry, atrophy indices)

### Genetic Features
- APOE genotype (one-hot encoded)
- APOE e4 allele count (0, 1, 2)
- Risk stratification (low, baseline, moderate, high)
- Carrier status indicators
- Family history of dementia

### Demographic Features
- Age, sex, education years
- Race/ethnicity (one-hot encoded)
- BMI and BMI categories
- Smoking status, alcohol consumption
- Physical activity level
- Social engagement
- Derived risk scores

### Temporal Features
- Time since baseline (months)
- Visit number
- Cognitive decline rates
- Biomarker change rates
- Visit frequency
- Trajectory classifications

## Data Requirements

### Input Data Format

The pipeline expects a pandas DataFrame with the following structure:

```python
data = pd.DataFrame({
    # Identifiers
    'patient_id': [...],
    'visit_date': [...],
    
    # Cognitive assessments
    'MMSE': [...],
    'MoCA': [...],
    'CDR': [...],
    
    # Biomarkers
    'CSF_AB42': [...],
    'CSF_TAU': [...],
    'CSF_PTAU': [...],
    
    # Imaging
    'hippocampus_left': [...],
    'hippocampus_right': [...],
    
    # Genetics
    'APOE': [...],
    
    # Demographics
    'age': [...],
    'sex': [...],
    'education': [...]
})
```

### Column Name Variations

The pipeline handles multiple column name variations:
- MMSE: 'MMSE', 'mmse_total', 'MMSCORE'
- MoCA: 'MoCA', 'moca_total', 'MOCA'
- CDR: 'CDR', 'cdr_global', 'CDGLOBAL'
- And many more...

## Validation

Each component includes validation methods to ensure data quality:

```python
# Validate cognitive features
validation = extractor.validate_features(cognitive_features)

# Validate entire pipeline
validation = pipeline.validate_pipeline(engineered_features)
```

## Performance

The pipeline is optimized for large datasets:
- Vectorized operations using pandas/numpy
- Efficient imputation algorithms
- Minimal memory footprint
- Parallel processing support (where applicable)

## Requirements

- pandas >= 1.3.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- scipy >= 1.7.0

## References

1. ADNI: Alzheimer's Disease Neuroimaging Initiative
2. OASIS: Open Access Series of Imaging Studies
3. NACC: National Alzheimer's Coordinating Center
4. EARS: Easy Approach to Requirements Syntax
5. INCOSE: International Council on Systems Engineering
