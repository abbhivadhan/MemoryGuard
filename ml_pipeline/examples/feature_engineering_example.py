"""
Feature Engineering Example

Demonstrates how to use the feature engineering pipeline to transform
raw biomedical data into ML-ready features.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering import FeatureEngineeringPipeline
from config.logging_config import setup_logging

# Setup logging
logger = setup_logging('feature_engineering_example')


def create_sample_data() -> pd.DataFrame:
    """Create sample biomedical data for demonstration"""
    
    np.random.seed(42)
    n_samples = 100
    
    data = pd.DataFrame({
        # Patient identifiers
        'patient_id': [f'P{i:04d}' for i in range(n_samples)],
        'visit_date': pd.date_range('2020-01-01', periods=n_samples, freq='30D'),
        
        # Cognitive assessments
        'MMSE': np.random.randint(15, 30, n_samples),
        'MoCA': np.random.randint(12, 28, n_samples),
        'CDR': np.random.choice([0, 0.5, 1, 2], n_samples),
        'ADAS_Cog': np.random.randint(5, 40, n_samples),
        
        # CSF biomarkers
        'CSF_AB42': np.random.uniform(300, 800, n_samples),
        'CSF_TAU': np.random.uniform(200, 600, n_samples),
        'CSF_PTAU': np.random.uniform(40, 120, n_samples),
        
        # Imaging measurements
        'hippocampus_left': np.random.uniform(2000, 4000, n_samples),
        'hippocampus_right': np.random.uniform(2000, 4000, n_samples),
        'entorhinal_cortex_left': np.random.uniform(1500, 3000, n_samples),
        'entorhinal_cortex_right': np.random.uniform(1500, 3000, n_samples),
        'ventricles': np.random.uniform(20000, 50000, n_samples),
        'whole_brain': np.random.uniform(900000, 1200000, n_samples),
        'intracranial_volume': np.random.uniform(1200000, 1600000, n_samples),
        
        # Genetic data
        'APOE': np.random.choice(['e3/e3', 'e3/e4', 'e4/e4', 'e2/e3'], n_samples),
        'family_history_dementia': np.random.choice([0, 1], n_samples),
        
        # Demographics
        'age': np.random.randint(60, 85, n_samples),
        'sex': np.random.choice([0, 1], n_samples),
        'education': np.random.randint(8, 20, n_samples),
        'race': np.random.choice(['white', 'black', 'asian', 'hispanic'], n_samples),
        
        # Lifestyle
        'bmi': np.random.uniform(18, 35, n_samples),
        'smoking': np.random.choice([0, 1, 2], n_samples),
        'physical_activity': np.random.choice([0, 1, 2, 3], n_samples),
    })
    
    # Add some missing values
    for col in ['MoCA', 'CSF_PTAU', 'entorhinal_cortex_left', 'bmi']:
        missing_idx = np.random.choice(n_samples, size=int(n_samples * 0.1), replace=False)
        data.loc[missing_idx, col] = np.nan
    
    return data


def main():
    """Main example function"""
    
    logger.info("=" * 80)
    logger.info("Feature Engineering Pipeline Example")
    logger.info("=" * 80)
    
    # Create sample data
    logger.info("\n1. Creating sample biomedical data...")
    data = create_sample_data()
    logger.info(f"   Created {len(data)} samples with {len(data.columns)} columns")
    
    # Initialize pipeline
    logger.info("\n2. Initializing feature engineering pipeline...")
    pipeline = FeatureEngineeringPipeline(
        imputation_strategy='iterative',
        normalization_method='standard',
        include_temporal=True
    )
    logger.info("   Pipeline initialized")
    
    # Fit and transform data
    logger.info("\n3. Running feature engineering pipeline...")
    engineered_features = pipeline.fit_transform(
        data,
        patient_id_col='patient_id',
        visit_date_col='visit_date'
    )
    
    logger.info(f"   Engineered {len(engineered_features.columns)} features")
    logger.info(f"   Feature shape: {engineered_features.shape}")
    
    # Get feature report
    logger.info("\n4. Generating feature report...")
    report = pipeline.get_feature_report()
    
    logger.info("\n   Feature Summary:")
    for key, value in report['summary'].items():
        logger.info(f"   - {key}: {value}")
    
    logger.info("\n   Missing Data Analysis:")
    for key, value in report['missing_data'].items():
        if key != 'missing_by_feature':
            logger.info(f"   - {key}: {value}")
    
    logger.info("\n   Feature Categories:")
    for category, features in report['feature_types'].items():
        if features:
            logger.info(f"   - {category}: {len(features)} features")
    
    # Display sample features
    logger.info("\n5. Sample engineered features:")
    logger.info(f"\n{engineered_features.head()}")
    
    # Validate pipeline
    logger.info("\n6. Validating pipeline...")
    validation = pipeline.validate_pipeline(engineered_features)
    
    all_valid = True
    for component, results in validation.items():
        component_valid = all(results.values())
        logger.info(f"   - {component}: {'✓ Valid' if component_valid else '✗ Invalid'}")
        if not component_valid:
            all_valid = False
            for check, result in results.items():
                if not result:
                    logger.warning(f"     Failed: {check}")
    
    if all_valid:
        logger.info("\n✓ All validation checks passed!")
    else:
        logger.warning("\n✗ Some validation checks failed")
    
    # Save feature documentation
    logger.info("\n7. Saving feature documentation...")
    output_path = Path(__file__).parent.parent / 'data_storage' / 'features' / 'feature_report.txt'
    pipeline.save_feature_documentation(output_path)
    logger.info(f"   Documentation saved to {output_path.parent}")
    
    # Transform new data
    logger.info("\n8. Testing transform on new data...")
    new_data = create_sample_data()
    new_features = pipeline.transform(
        new_data,
        patient_id_col='patient_id',
        visit_date_col='visit_date'
    )
    logger.info(f"   Transformed {len(new_features)} samples")
    logger.info(f"   Feature shape: {new_features.shape}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Feature Engineering Pipeline Example Complete!")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
