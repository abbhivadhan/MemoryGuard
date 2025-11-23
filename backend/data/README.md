# Alzheimer's Disease Dataset Preparation

This directory contains scripts and instructions for preparing real Alzheimer's disease datasets for ML model training.

## Supported Datasets

### 1. ADNI (Alzheimer's Disease Neuroimaging Initiative)

**Source**: https://adni.loni.usc.edu/

**Access**: Requires registration and data use agreement

**Description**: Longitudinal study with comprehensive biomarker, imaging, and clinical data

**Features**:
- Demographics (age, gender, education)
- Cognitive assessments (MMSE, ADAS-Cog, CDR)
- CSF biomarkers (Aβ42, tau, p-tau)
- MRI volumetric measurements
- PET imaging data
- Genetic information (APOE genotype)

### 2. OASIS (Open Access Series of Imaging Studies)

**Source**: https://www.oasis-brains.org/

**Access**: Publicly available with registration

**Description**: Cross-sectional and longitudinal MRI data

**Features**:
- Demographics
- Clinical Dementia Rating (CDR)
- MRI-derived brain volumes
- Cognitive assessments

### 3. NACC (National Alzheimer's Coordinating Center)

**Source**: https://naccdata.org/

**Access**: Requires application and approval

**Description**: Uniform Data Set (UDS) from Alzheimer's Disease Centers

## Data Preparation Pipeline

### Step 1: Download Dataset

1. Register for access to ADNI or OASIS
2. Download the dataset in CSV format
3. Place the CSV file in `backend/data/raw/`

### Step 2: Prepare Training Data

Run the preparation script:

```bash
cd backend

# For ADNI format data
python scripts/prepare_training_data.py \
    --data-source data/raw/adni_data.csv \
    --data-format adni \
    --output-dir data/processed

# For OASIS format data
python scripts/prepare_training_data.py \
    --data-source data/raw/oasis_data.csv \
    --data-format oasis \
    --output-dir data/processed
```

This will:
- Clean and standardize the data
- Engineer relevant features
- Split into train/validation/test sets (70%/10%/20%)
- Save processed data to `data/processed/`

### Step 3: Verify Processed Data

Check the generated files:

```
data/processed/
├── X_train.npy          # Training features
├── y_train.npy          # Training labels
├── X_val.npy            # Validation features
├── y_val.npy            # Validation labels
├── X_test.npy           # Test features
├── y_test.npy           # Test labels
└── metadata.json        # Dataset metadata
```

## Expected Features

The preprocessing pipeline extracts and standardizes the following features:

### Demographics (4 features)
- `age`: Age in years
- `gender`: 0=Male, 1=Female
- `education_years`: Years of education
- `apoe4_alleles`: Number of APOE4 alleles (0, 1, or 2)

### Cognitive Assessments (3 features)
- `mmse_score`: Mini-Mental State Examination (0-30)
- `moca_score`: Montreal Cognitive Assessment (0-30)
- `cdr_score`: Clinical Dementia Rating (0-3)

### Biomarkers (4 features)
- `csf_abeta42`: CSF Amyloid-beta 42 (pg/mL)
- `csf_tau`: CSF Total Tau (pg/mL)
- `csf_ptau`: CSF Phosphorylated Tau (pg/mL)
- `tau_abeta_ratio`: Calculated ratio

### Imaging (5 features)
- `hippocampal_volume`: Hippocampus volume (mm³)
- `entorhinal_thickness`: Entorhinal cortex thickness (mm)
- `whole_brain_volume`: Total brain volume (mm³)
- `ventricular_volume`: Ventricular volume (mm³)
- `hippocampal_ratio`: Hippocampus/whole brain ratio

### Engineered Features (3 features)
- `age_squared`: Age squared for non-linear effects
- `age_group`: Age category (0-3)
- `cognitive_impairment`: Binary indicator (MMSE < 24)

**Total**: Up to 19 features (depending on data availability)

## Target Variable

- `diagnosis`: Binary classification
  - 0 = Cognitively Normal (CN)
  - 1 = Alzheimer's Disease (AD)

Note: MCI (Mild Cognitive Impairment) cases are currently classified as 0 (negative class).

## Data Quality Requirements

For successful model training, the dataset should have:

1. **Minimum samples**: 500+ subjects (preferably 1000+)
2. **Class balance**: At least 30% representation of each class
3. **Feature completeness**: At least 50% of features available per sample
4. **Critical features**: Age and MMSE score must be present

## Privacy and Ethics

**IMPORTANT**: All datasets must be:
- De-identified (no PHI/PII)
- Used in compliance with data use agreements
- Not redistributed without permission
- Handled according to HIPAA guidelines

## Troubleshooting

### Issue: Missing columns

**Solution**: Check that your CSV has the expected column names. The script supports multiple naming conventions (see `standardize_column_names` function).

### Issue: Too few samples after cleaning

**Solution**: Adjust outlier removal threshold or missing data handling in the script.

### Issue: Class imbalance

**Solution**: The training script will handle class imbalance using class weights. For severe imbalance, consider oversampling or undersampling techniques.

## Next Steps

After preparing the data:

1. Train the ML models: `python scripts/train_models.py`
2. Evaluate model performance: `python scripts/evaluate_models.py`
3. Deploy trained models to production

## References

- ADNI: http://adni.loni.usc.edu/
- OASIS: https://www.oasis-brains.org/
- NACC: https://naccdata.org/
- Alzheimer's Association: https://www.alz.org/
