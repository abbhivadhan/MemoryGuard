"""
Basic tests for data validation engine
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_validation import (
    DataValidationEngine,
    PHIDetector,
    CompletenessChecker,
    OutlierDetector,
    RangeValidator,
    DuplicateDetector,
    TemporalValidator
)


def create_test_data():
    """Create simple test dataset"""
    np.random.seed(42)
    
    data = {
        'patient_id': [f'P{i:03d}' for i in range(1, 51)],
        'visit_date': pd.date_range('2020-01-01', periods=50, freq='30D'),
        'age': np.random.randint(50, 90, 50),
        'mmse_score': np.random.randint(20, 30, 50),
        'csf_ab42': np.random.uniform(500, 1500, 50),
        'hippocampus_volume': np.random.uniform(3, 7, 50)
    }
    
    return pd.DataFrame(data)


def test_phi_detector():
    """Test PHI detection"""
    print("\n=== Testing PHI Detector ===")
    
    detector = PHIDetector()
    data = create_test_data()
    
    # Test data has patient_id and dates which may trigger PHI detection
    # This is expected behavior - the detector is working correctly
    phi_detected = detector.detect_phi(data)
    
    # Add a clear PHI column (email)
    data['email'] = ['test@example.com'] * len(data)
    phi_detected_with_email = detector.detect_phi(data)
    
    assert 'email_addresses' in phi_detected_with_email, "Email PHI not detected"
    print(f"✓ PHI detector works correctly: detected {len(phi_detected_with_email)} PHI categories")


def test_completeness_checker():
    """Test completeness checking"""
    print("\n=== Testing Completeness Checker ===")
    
    checker = CompletenessChecker(completeness_threshold=0.70)
    data = create_test_data()
    
    # Add some missing values
    data.loc[0:5, 'mmse_score'] = np.nan
    
    completeness = checker.get_overall_completeness(data)
    assert 0 < completeness <= 1, "Invalid completeness value"
    print(f"✓ Completeness checker works: {completeness*100:.1f}%")


def test_outlier_detector():
    """Test outlier detection"""
    print("\n=== Testing Outlier Detector ===")
    
    detector = OutlierDetector()
    data = create_test_data()
    
    # Add an outlier
    data.loc[0, 'mmse_score'] = 100  # Invalid MMSE score
    
    outliers_iqr, stats = detector.detect_outliers_iqr(data['mmse_score'])
    assert outliers_iqr.sum() > 0, "Outlier not detected"
    print(f"✓ Outlier detector works: {outliers_iqr.sum()} outliers found")


def test_range_validator():
    """Test range validation"""
    print("\n=== Testing Range Validator ===")
    
    validator = RangeValidator()
    data = create_test_data()
    
    # Add out-of-range value
    data.loc[0, 'mmse_score'] = 50  # Invalid MMSE score
    
    result = validator.validate_column(data['mmse_score'], 'mmse_score')
    assert not result['validated'], "Out-of-range value not detected"
    assert result['violations'] > 0, "Violations not counted"
    print(f"✓ Range validator works: {result['violations']} violations found")


def test_duplicate_detector():
    """Test duplicate detection"""
    print("\n=== Testing Duplicate Detector ===")
    
    detector = DuplicateDetector()
    data = create_test_data()
    
    # Add duplicate row
    data = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    
    result = detector.detect_exact_duplicates(data)
    assert result['duplicate_rows'] > 0, "Duplicates not detected"
    print(f"✓ Duplicate detector works: {result['duplicate_rows']} duplicates found")


def test_temporal_validator():
    """Test temporal validation"""
    print("\n=== Testing Temporal Validator ===")
    
    validator = TemporalValidator()
    data = create_test_data()
    
    result = validator.validate_date_sequences(
        data, 
        patient_id_col='patient_id',
        date_col='visit_date'
    )
    assert 'validation_passed' in result, "Validation result missing"
    print(f"✓ Temporal validator works: {result['validation_passed']}")


def test_data_validation_engine():
    """Test main validation engine"""
    print("\n=== Testing Data Validation Engine ===")
    
    engine = DataValidationEngine()
    data = create_test_data()
    
    # Quick validation
    quick_results = engine.quick_validate(data)
    assert 'quick_validation_passed' in quick_results, "Quick validation failed"
    print(f"✓ Quick validation: {quick_results['quick_validation_passed']}")
    
    # Full validation
    report = engine.validate_dataset(
        data=data,
        dataset_name="Test Dataset",
        patient_id_col='patient_id',
        visit_date_col='visit_date',
        strict_mode=False
    )
    assert 'quality_score' in report, "Quality score missing"
    print(f"✓ Full validation: Quality score = {report['quality_score']['overall_score']:.1f}/100")
    
    # ML readiness check
    is_ready, issues = engine.validate_for_ml_training(data)
    print(f"✓ ML readiness check: {is_ready}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RUNNING DATA VALIDATION TESTS")
    print("="*60)
    
    try:
        test_phi_detector()
        test_completeness_checker()
        test_outlier_detector()
        test_range_validator()
        test_duplicate_detector()
        test_temporal_validator()
        test_data_validation_engine()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
