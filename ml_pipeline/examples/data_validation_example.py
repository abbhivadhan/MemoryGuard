"""
Example script demonstrating data validation engine usage
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_validation import DataValidationEngine
from config.logging_config import setup_logging

# Setup logging
logger = setup_logging('data_validation_example')


def create_sample_dataset():
    """Create a sample biomedical dataset for demonstration"""
    np.random.seed(42)
    
    n_patients = 100
    n_visits_per_patient = 3
    
    data = []
    
    for patient_id in range(1, n_patients + 1):
        for visit in range(n_visits_per_patient):
            record = {
                'patient_id': f'P{patient_id:04d}',
                'visit_date': pd.Timestamp('2020-01-01') + pd.Timedelta(days=visit*180 + np.random.randint(-30, 30)),
                'age': 65 + np.random.randint(-10, 20),
                'sex': np.random.choice(['M', 'F']),
                'education_years': np.random.randint(8, 20),
                
                # Cognitive scores
                'mmse_score': np.random.randint(15, 30),
                'moca_score': np.random.randint(12, 28),
                'cdr_global': np.random.choice([0, 0.5, 1, 2]),
                
                # CSF Biomarkers
                'csf_ab42': np.random.uniform(200, 1500),
                'csf_tau': np.random.uniform(100, 800),
                'csf_ptau': np.random.uniform(20, 100),
                
                # Brain volumes
                'hippocampus_volume': np.random.uniform(2.5, 8.0),
                'entorhinal_cortex_thickness': np.random.uniform(2.0, 4.0),
                'ventricular_volume': np.random.uniform(20, 150),
                
                # Genetic
                'apoe_e4_count': np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
            }
            
            # Add some missing values (10% missing rate)
            for key in record.keys():
                if key not in ['patient_id', 'visit_date'] and np.random.random() < 0.1:
                    record[key] = np.nan
            
            data.append(record)
    
    df = pd.DataFrame(data)
    
    # Add some outliers
    df.loc[5, 'mmse_score'] = 50  # Invalid MMSE score
    df.loc[10, 'csf_ab42'] = 3000  # Out of range
    df.loc[15, 'age'] = 150  # Invalid age
    
    # Add some duplicates
    df = pd.concat([df, df.iloc[:5]], ignore_index=True)
    
    logger.info(f"Created sample dataset with {len(df)} records")
    
    return df


def example_basic_validation():
    """Example 1: Basic dataset validation"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Dataset Validation")
    print("="*70)
    
    # Create sample data
    data = create_sample_dataset()
    
    # Initialize validation engine
    engine = DataValidationEngine(
        completeness_threshold=0.70,
        k_anonymity_threshold=5
    )
    
    # Validate dataset
    report = engine.validate_dataset(
        data=data,
        dataset_name="Sample Biomedical Dataset",
        patient_id_col='patient_id',
        visit_date_col='visit_date',
        strict_mode=False  # Use non-strict mode for demo
    )
    
    # Print summary
    engine.print_summary(report)
    
    # Check ML readiness
    is_ready, issues = engine.validate_for_ml_training(data)
    print(f"\nML Training Ready: {'✓ YES' if is_ready else '✗ NO'}")
    if issues:
        print("Blocking Issues:")
        for issue in issues:
            print(f"  - {issue}")


def example_quick_validation():
    """Example 2: Quick validation"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Quick Validation")
    print("="*70)
    
    data = create_sample_dataset()
    engine = DataValidationEngine()
    
    # Quick validation
    results = engine.quick_validate(data)
    
    print(f"Dataset Shape: {results['dataset_shape']}")
    print(f"PHI Detected: {results['phi_detected']}")
    print(f"Completeness: {results['completeness']*100:.1f}%")
    print(f"Duplicate Rows: {results['duplicate_rows']}")
    print(f"Quick Validation: {'✓ PASSED' if results['quick_validation_passed'] else '✗ FAILED'}")


def example_validate_and_clean():
    """Example 3: Validate and automatically clean dataset"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Validate and Clean")
    print("="*70)
    
    data = create_sample_dataset()
    engine = DataValidationEngine()
    
    print(f"Original shape: {data.shape}")
    
    # Validate and clean
    cleaned_data, cleaning_report = engine.validate_and_clean(
        data=data,
        remove_duplicates=True,
        remove_incomplete_columns=False,
        incomplete_threshold=0.50
    )
    
    print(f"Final shape: {cleaned_data.shape}")
    print(f"Rows removed: {cleaning_report['rows_removed']}")
    print(f"Columns removed: {cleaning_report['columns_removed']}")
    
    print("\nCleaning Operations:")
    for op in cleaning_report['operations']:
        print(f"  - {op['operation']}: {op.get('rows_removed', op.get('columns_removed', 0))} items")


def example_individual_validators():
    """Example 4: Using individual validators"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Individual Validators")
    print("="*70)
    
    data = create_sample_dataset()
    engine = DataValidationEngine()
    
    # Completeness check
    print("\n--- Completeness Check ---")
    completeness = engine.completeness_checker.get_overall_completeness(data)
    print(f"Overall Completeness: {completeness*100:.1f}%")
    
    incomplete_cols = engine.completeness_checker.identify_incomplete_columns(data)
    if incomplete_cols:
        print(f"Incomplete Columns: {incomplete_cols}")
    
    # Outlier detection
    print("\n--- Outlier Detection ---")
    outlier_report = engine.outlier_detector.generate_outlier_report(data, method='iqr')
    print(f"Columns with Outliers: {outlier_report['summary']['columns_with_outliers']}")
    print(f"Total Outliers (IQR): {outlier_report['summary']['total_outliers_iqr']}")
    
    # Range validation
    print("\n--- Range Validation ---")
    range_report = engine.range_validator.generate_range_report(data)
    print(f"Validated Columns: {range_report['validation_summary']['validated_columns']}")
    print(f"Columns with Violations: {range_report['validation_summary']['columns_with_violations']}")
    
    if range_report['violations']:
        print("\nTop Violations:")
        for violation in range_report['violations'][:3]:
            print(f"  - {violation['column']}: {violation['violations']} violations")
    
    # Duplicate detection
    print("\n--- Duplicate Detection ---")
    dup_report = engine.duplicate_detector.generate_duplicate_report(
        data, 
        patient_id_col='patient_id',
        visit_date_col='visit_date'
    )
    print(f"Exact Duplicates: {dup_report['exact_duplicates']['duplicate_rows']}")
    print(f"Duplicate Patients: {dup_report.get('patient_duplicates', {}).get('duplicate_patients', 'N/A')}")


def example_generate_reports():
    """Example 5: Generate and save reports"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Generate Reports")
    print("="*70)
    
    data = create_sample_dataset()
    engine = DataValidationEngine()
    
    # Create reports directory
    reports_dir = Path('ml_pipeline/reports')
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate JSON report
    print("Generating JSON report...")
    json_path = reports_dir / 'sample_quality_report.json'
    report = engine.generate_report(
        data=data,
        dataset_name="Sample Dataset",
        patient_id_col='patient_id',
        visit_date_col='visit_date',
        output_path=json_path,
        format='json'
    )
    print(f"✓ JSON report saved to: {json_path}")
    
    # Generate HTML report
    print("Generating HTML report...")
    html_path = reports_dir / 'sample_quality_report.html'
    engine.generate_report(
        data=data,
        dataset_name="Sample Dataset",
        patient_id_col='patient_id',
        visit_date_col='visit_date',
        output_path=html_path,
        format='html'
    )
    print(f"✓ HTML report saved to: {html_path}")
    
    print(f"\nQuality Score: {report['quality_score']['overall_score']:.1f}/100")
    print(f"Grade: {report['quality_score']['grade']}")
    print(f"Status: {report['overall_assessment']['overall_status']}")


def example_custom_ranges():
    """Example 6: Adding custom range definitions"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Custom Range Definitions")
    print("="*70)
    
    data = create_sample_dataset()
    engine = DataValidationEngine()
    
    # Add custom range for a new biomarker
    engine.range_validator.add_custom_range(
        field_name='custom_biomarker',
        min_val=0,
        max_val=100,
        unit='ng/mL',
        field_type='biomarker'
    )
    
    # Add the custom column to data
    data['custom_biomarker'] = np.random.uniform(0, 120, len(data))
    
    # Validate
    range_report = engine.range_validator.generate_range_report(data)
    
    if 'custom_biomarker' in range_report['detailed_results']:
        result = range_report['detailed_results']['custom_biomarker']
        print(f"Custom Biomarker Validation:")
        print(f"  - Validated: {result['validated']}")
        print(f"  - Violations: {result['violations']}")
        print(f"  - Range: {result['range']}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("DATA VALIDATION ENGINE EXAMPLES")
    print("="*70)
    
    try:
        example_basic_validation()
        example_quick_validation()
        example_validate_and_clean()
        example_individual_validators()
        example_generate_reports()
        example_custom_ranges()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
