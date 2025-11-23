# Data Sources & Privacy Information

## Current Data Status

### ❌ NO REAL MEDICAL DATA
This system **does NOT contain real patient data**. Here's why:

1. **Privacy & HIPAA Compliance**: Real patient data requires:
   - IRB approval
   - Patient consent
   - HIPAA-compliant infrastructure
   - Data use agreements
   - Proper de-identification

2. **Legal Requirements**: Using real medical data without authorization is:
   - Illegal under HIPAA
   - Violation of patient privacy
   - Subject to severe penalties

## What Data IS Used?

### 1. Synthetic Demo Data
- **Purpose**: Development and testing
- **Source**: Randomly generated
- **Characteristics**: Mimics real data patterns but is completely artificial
- **Location**: `backend/data/training/synthetic_alzheimer_data.csv`

### 2. Public Research Datasets (Optional)
You can use de-identified public datasets:

#### ADNI (Alzheimer's Disease Neuroimaging Initiative)
- **Website**: https://adni.loni.usc.edu/
- **Access**: Requires application and approval
- **Data**: De-identified neuroimaging, biomarkers, cognitive assessments
- **Cost**: Free for approved researchers

#### OASIS (Open Access Series of Imaging Studies)
- **Website**: https://www.oasis-brains.org/
- **Access**: Publicly available
- **Data**: De-identified MRI scans and clinical data
- **Cost**: Free

#### UK Biobank
- **Website**: https://www.ukbiobank.ac.uk/
- **Access**: Requires application
- **Data**: Large-scale health data
- **Cost**: Varies

## Face Recognition

### Current Implementation
- **Library**: Standard face detection (OpenCV/dlib)
- **Training**: Uses pre-trained models (NOT trained on patient data)
- **Purpose**: Help patients recognize family members
- **Privacy**: All face data stored locally, encrypted

### NOT Using:
- ❌ Real patient faces
- ❌ Medical imaging of faces
- ❌ Unauthorized photos

## ML Models

### Current Status
- **Training Data**: Synthetic data only
- **Purpose**: Demonstration and development
- **Accuracy**: NOT validated for clinical use
- **Disclaimer**: For research/educational purposes only

### For Production Use
To use real data, you need:

1. **IRB Approval**: Institutional Review Board approval
2. **Data Use Agreement**: With data providers (ADNI, OASIS, etc.)
3. **HIPAA Compliance**: Proper infrastructure and procedures
4. **Clinical Validation**: FDA approval for clinical use
5. **Patient Consent**: For any patient-specific data

## How to Add Real Data (Properly)

### Step 1: Get Approved Access
```bash
# Apply for ADNI access
# Visit: https://adni.loni.usc.edu/data-samples/access-data/

# Or download OASIS
# Visit: https://www.oasis-brains.org/
```

### Step 2: Download De-identified Data
```bash
# Place data in:
backend/data/raw/adni_data.csv
# or
backend/data/raw/oasis_data.csv
```

### Step 3: Prepare Data
```bash
cd backend
python scripts/prepare_training_data.py \
  --data-source data/raw/adni_data.csv \
  --output-dir data/training
```

### Step 4: Train Models
```bash
python scripts/train_models.py \
  --data-path data/training/prepared_data.csv
```

## Quick Setup (Demo Mode)

To set up the system with synthetic data:

```bash
cd backend
python scripts/setup_demo_system.py
```

This creates:
- ✓ Database tables
- ✓ Demo user account
- ✓ Sample health metrics
- ✓ Synthetic training data
- ✓ Basic ML models

## Important Disclaimers

### ⚠️ NOT FOR CLINICAL USE
This system is for:
- Research purposes
- Educational demonstrations
- Software development
- Proof of concept

### ⚠️ NOT A MEDICAL DEVICE
- Not FDA approved
- Not clinically validated
- Not intended for diagnosis
- Not a substitute for professional medical advice

### ⚠️ SYNTHETIC DATA ONLY
- Current models trained on synthetic data
- Predictions are for demonstration only
- Do not use for actual medical decisions

## Privacy & Security

### Data Protection
- All data encrypted at rest
- Secure transmission (HTTPS/TLS)
- Access controls and authentication
- Audit logging
- HIPAA-compliant architecture (when using real data)

### User Data
- Users control their own data
- Can delete data at any time
- No data sharing without consent
- Transparent data usage

## Questions?

### "Can I use this with real patients?"
No, not without:
- IRB approval
- Clinical validation
- FDA clearance (if in US)
- Proper medical oversight

### "Can I train models on my hospital's data?"
Only if:
- You have proper authorization
- Data is properly de-identified
- You have IRB approval
- You comply with HIPAA/local regulations

### "Is the face recognition trained on real faces?"
No, it uses pre-trained general-purpose face detection models.

### "Where can I get real Alzheimer's data?"
- ADNI: https://adni.loni.usc.edu/
- OASIS: https://www.oasis-brains.org/
- UK Biobank: https://www.ukbiobank.ac.uk/

## Summary

✅ **What This System Has:**
- Synthetic demo data
- HIPAA-compliant architecture
- Privacy-preserving design
- Educational/research framework

❌ **What This System Does NOT Have:**
- Real patient data
- Clinical validation
- FDA approval
- Real medical images

🎯 **Intended Use:**
- Software development
- Research demonstrations
- Educational purposes
- Proof of concept

⚠️ **Not Intended For:**
- Clinical diagnosis
- Treatment decisions
- Real patient care
- Medical advice
