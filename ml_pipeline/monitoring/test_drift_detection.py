"""
Simple test script for drift detection system
Tests core functionality without requiring full environment setup
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
import pandas as pd
from datetime import datetime

# Test imports
try:
    from ml_pipeline.monitoring.distribution_monitor import DistributionMonitor
    from ml_pipeline.monitoring.drift_detector import DriftDetector
    from ml_pipeline.monitoring.drift_alerting import DriftAlerter
    from ml_pipeline.monitoring.performance_tracker import PerformanceTracker
    print("✓ All monitoring modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def generate_test_data(n_samples=100, drift=False):
    """Generate simple test data"""
    np.random.seed(42 if not drift else 123)
    
    mean_shift = 5.0 if drift else 0.0
    
    data = {
        'feature_1': np.random.normal(10.0 + mean_shift, 2.0, n_samples),
        'feature_2': np.random.normal(20.0 + mean_shift, 3.0, n_samples),
        'feature_3': np.random.normal(30.0, 4.0, n_samples),
    }
    
    return pd.DataFrame(data)


def test_distribution_monitor():
    """Test DistributionMonitor"""
    print("\n" + "="*60)
    print("Testing DistributionMonitor")
    print("="*60)
    
    # Generate reference data
    reference_data = generate_test_data(n_samples=200, drift=False)
    
    # Initialize monitor
    monitor = DistributionMonitor(reference_data)
    
    # Test distribution computation
    distributions = monitor.reference_distributions
    assert distributions is not None, "Reference distributions should be computed"
    assert 'feature_1' in distributions, "Feature_1 should be in distributions"
    
    print(f"✓ Reference distributions computed: {len(distributions)} features")
    
    # Test tracking
    current_data = generate_test_data(n_samples=100, drift=False)
    tracked = monitor.track_distributions(current_data, "test_data")
    
    assert tracked is not None, "Tracking should return distributions"
    print(f"✓ Distribution tracking works")
    
    # Test comparison
    comparison = monitor.compare_distributions(current_data)
    assert comparison is not None, "Comparison should return results"
    print(f"✓ Distribution comparison works")
    
    print("\n✅ DistributionMonitor tests passed")


def test_drift_detector():
    """Test DriftDetector"""
    print("\n" + "="*60)
    print("Testing DriftDetector")
    print("="*60)
    
    # Generate data
    reference_data = generate_test_data(n_samples=200, drift=False)
    current_data_no_drift = generate_test_data(n_samples=100, drift=False)
    current_data_with_drift = generate_test_data(n_samples=100, drift=True)
    
    # Initialize detector
    detector = DriftDetector(reference_data)
    
    # Test KS test - no drift
    ks_results_no_drift = detector.kolmogorov_smirnov_test(current_data_no_drift)
    assert ks_results_no_drift is not None, "KS test should return results"
    print(f"✓ KS test works (no drift): {len(ks_results_no_drift)} features tested")
    
    # Test KS test - with drift
    ks_results_drift = detector.kolmogorov_smirnov_test(current_data_with_drift)
    drift_detected = any(r['drift_detected'] for r in ks_results_drift.values())
    print(f"✓ KS test works (with drift): drift_detected={drift_detected}")
    
    # Test PSI calculation
    psi_scores = detector.calculate_psi(current_data_with_drift)
    assert psi_scores is not None, "PSI calculation should return scores"
    print(f"✓ PSI calculation works: {len(psi_scores)} features")
    
    # Test comprehensive drift detection
    drift_results = detector.detect_drift(current_data_with_drift)
    assert 'drift_detected' in drift_results, "Drift results should include drift_detected"
    assert 'retraining_recommended' in drift_results, "Drift results should include retraining_recommended"
    print(f"✓ Comprehensive drift detection works")
    print(f"  - Drift detected: {drift_results['drift_detected']}")
    print(f"  - Retraining recommended: {drift_results['retraining_recommended']}")
    
    print("\n✅ DriftDetector tests passed")


def test_drift_alerter():
    """Test DriftAlerter"""
    print("\n" + "="*60)
    print("Testing DriftAlerter")
    print("="*60)
    
    # Initialize alerter
    alerter = DriftAlerter(alert_email="test@example.com")
    
    # Create mock drift results
    drift_results = {
        'drift_detected': True,
        'retraining_recommended': True,
        'features_with_high_psi': ['feature_1', 'feature_2'],
        'features_with_ks_drift': ['feature_1'],
        'psi_scores': {'feature_1': 0.25, 'feature_2': 0.22},
        'ks_test': {
            'feature_1': {'p_value': 0.01, 'drift_detected': True}
        },
        'n_reference_samples': 200,
        'n_current_samples': 100
    }
    
    # Test alert checking
    alert_triggered = alerter.check_and_alert(drift_results, "test_dataset")
    assert alert_triggered, "Alert should be triggered for drift"
    print(f"✓ Alert triggering works: alert_triggered={alert_triggered}")
    
    # Test alert history
    assert len(alerter.alert_history) > 0, "Alert history should contain alerts"
    print(f"✓ Alert history works: {len(alerter.alert_history)} alerts")
    
    print("\n✅ DriftAlerter tests passed")


def test_performance_tracker():
    """Test PerformanceTracker"""
    print("\n" + "="*60)
    print("Testing PerformanceTracker")
    print("="*60)
    
    # Initialize tracker
    tracker = PerformanceTracker(model_name="test_model")
    
    # Set baseline
    baseline_metrics = {
        'accuracy': 0.85,
        'f1_score': 0.83
    }
    tracker.set_baseline_metrics(baseline_metrics)
    print(f"✓ Baseline metrics set")
    
    # Generate mock predictions
    n_samples = 100
    y_true = np.random.choice([0, 1], n_samples)
    y_pred = y_true.copy()
    # Introduce some errors
    error_indices = np.random.choice(n_samples, 15, replace=False)
    y_pred[error_indices] = 1 - y_pred[error_indices]
    
    # Track performance
    performance = tracker.track_performance(y_true, y_pred, dataset_name="test_data")
    assert 'metrics' in performance, "Performance should include metrics"
    print(f"✓ Performance tracking works: accuracy={performance['metrics']['accuracy']:.4f}")
    
    # Test degradation detection
    degraded, details = tracker.detect_performance_degradation()
    print(f"✓ Degradation detection works: degraded={degraded}")
    
    print("\n✅ PerformanceTracker tests passed")


def test_integration():
    """Test integration of all components"""
    print("\n" + "="*60)
    print("Testing Integration")
    print("="*60)
    
    # Generate data
    reference_data = generate_test_data(n_samples=200, drift=False)
    current_data = generate_test_data(n_samples=100, drift=True)
    
    # Initialize all components
    dist_monitor = DistributionMonitor(reference_data)
    drift_detector = DriftDetector(reference_data)
    alerter = DriftAlerter()
    
    # Run full workflow
    print("\n1. Tracking distributions...")
    dist_monitor.track_distributions(current_data, "integration_test")
    
    print("2. Detecting drift...")
    drift_results = drift_detector.detect_drift(current_data)
    
    print("3. Checking alerts...")
    alert_triggered = alerter.check_and_alert(drift_results, "integration_test")
    
    print(f"\n✓ Integration test complete:")
    print(f"  - Drift detected: {drift_results['drift_detected']}")
    print(f"  - Alert triggered: {alert_triggered}")
    print(f"  - Retraining recommended: {drift_results['retraining_recommended']}")
    
    print("\n✅ Integration tests passed")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Data Drift Detection System - Unit Tests")
    print("="*60)
    
    try:
        test_distribution_monitor()
        test_drift_detector()
        test_drift_alerter()
        test_performance_tracker()
        test_integration()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
