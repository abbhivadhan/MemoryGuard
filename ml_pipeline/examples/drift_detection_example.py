"""
Example script demonstrating the data drift detection system
"""
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from ml_pipeline.monitoring import (
    DataDriftMonitor,
    create_drift_monitor
)
from ml_pipeline.config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def generate_sample_data(n_samples: int = 1000, drift: bool = False) -> pd.DataFrame:
    """
    Generate sample biomedical data for testing
    
    Args:
        n_samples: Number of samples to generate
        drift: Whether to introduce drift
        
    Returns:
        DataFrame with sample features
    """
    np.random.seed(42 if not drift else 123)
    
    # Base parameters
    mmse_mean = 24.0 if not drift else 20.0  # Drift in cognitive scores
    csf_ab42_mean = 800.0 if not drift else 600.0  # Drift in biomarkers
    
    data = {
        # Cognitive features
        'mmse_score': np.random.normal(mmse_mean, 4.0, n_samples).clip(0, 30),
        'moca_score': np.random.normal(22.0, 5.0, n_samples).clip(0, 30),
        'cdr_global': np.random.choice([0, 0.5, 1, 2], n_samples, p=[0.4, 0.3, 0.2, 0.1]),
        
        # Biomarker features
        'csf_ab42': np.random.normal(csf_ab42_mean, 200.0, n_samples).clip(100, 2000),
        'csf_tau': np.random.normal(400.0, 150.0, n_samples).clip(50, 1500),
        'csf_ptau': np.random.normal(60.0, 20.0, n_samples).clip(10, 200),
        
        # Imaging features
        'hippocampus_volume': np.random.normal(7000.0, 1000.0, n_samples).clip(3000, 10000),
        'entorhinal_cortex_thickness': np.random.normal(3.5, 0.5, n_samples).clip(2.0, 5.0),
        'ventricular_volume': np.random.normal(40000.0, 10000.0, n_samples).clip(20000, 80000),
        
        # Genetic features
        'apoe_e4_count': np.random.choice([0, 1, 2], n_samples, p=[0.6, 0.3, 0.1]),
        
        # Demographics
        'age': np.random.normal(70.0, 8.0, n_samples).clip(50, 90).astype(int),
        'education_years': np.random.normal(14.0, 3.0, n_samples).clip(8, 20).astype(int),
    }
    
    df = pd.DataFrame(data)
    
    # Add derived features
    df['ab42_tau_ratio'] = df['csf_ab42'] / df['csf_tau']
    df['ptau_tau_ratio'] = df['csf_ptau'] / df['csf_tau']
    
    return df


def example_basic_drift_detection():
    """Example 1: Basic drift detection"""
    print("\n" + "="*80)
    print("Example 1: Basic Drift Detection")
    print("="*80)
    
    # Generate reference data
    print("\n1. Generating reference data...")
    reference_data = generate_sample_data(n_samples=1000, drift=False)
    print(f"   Reference data: {len(reference_data)} samples, {len(reference_data.columns)} features")
    
    # Create drift monitor
    print("\n2. Creating drift monitor...")
    monitor = create_drift_monitor(reference_data, model_name="alzheimer_classifier")
    
    # Generate current data with drift
    print("\n3. Generating current data with drift...")
    current_data = generate_sample_data(n_samples=500, drift=True)
    print(f"   Current data: {len(current_data)} samples")
    
    # Monitor for drift
    print("\n4. Running drift detection...")
    results = monitor.monitor_data(current_data, dataset_name="week_1_data")
    
    # Display results
    print("\n5. Drift Detection Results:")
    print(f"   Drift detected: {results['drift_detected']}")
    print(f"   Retraining recommended: {results['retraining_recommended']}")
    print(f"   Alert triggered: {results['alert_triggered']}")
    
    if results['drift_detected']:
        drift_results = results['drift_results']
        print(f"\n   Features with high PSI:")
        for feature in drift_results.get('features_with_high_psi', []):
            psi_score = drift_results['psi_scores'][feature]
            print(f"     - {feature}: PSI = {psi_score:.4f}")
        
        print(f"\n   Features with KS drift:")
        for feature in drift_results.get('features_with_ks_drift', []):
            ks_result = drift_results['ks_test'][feature]
            print(f"     - {feature}: p-value = {ks_result['p_value']:.4f}")


def example_performance_tracking():
    """Example 2: Performance tracking"""
    print("\n" + "="*80)
    print("Example 2: Performance Tracking")
    print("="*80)
    
    # Generate reference data
    reference_data = generate_sample_data(n_samples=1000, drift=False)
    
    # Create drift monitor
    monitor = create_drift_monitor(reference_data, model_name="alzheimer_classifier")
    
    # Set baseline metrics
    print("\n1. Setting baseline performance metrics...")
    baseline_metrics = {
        'accuracy': 0.85,
        'balanced_accuracy': 0.83,
        'precision': 0.84,
        'recall': 0.82,
        'f1_score': 0.83,
        'roc_auc': 0.90
    }
    monitor.performance_tracker.set_baseline_metrics(baseline_metrics)
    print(f"   Baseline accuracy: {baseline_metrics['accuracy']:.4f}")
    
    # Simulate performance tracking over time
    print("\n2. Tracking performance over time...")
    for week in range(1, 6):
        # Generate predictions (simulating degradation)
        n_samples = 200
        y_true = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        
        # Simulate degrading accuracy
        accuracy = 0.85 - (week * 0.02)  # 2% degradation per week
        y_pred = y_true.copy()
        # Introduce errors
        n_errors = int(n_samples * (1 - accuracy))
        error_indices = np.random.choice(n_samples, n_errors, replace=False)
        y_pred[error_indices] = 1 - y_pred[error_indices]
        
        # Track performance
        performance = monitor.monitor_performance(
            pd.Series(y_true),
            pd.Series(y_pred),
            dataset_name=f"week_{week}_data"
        )
        
        print(f"   Week {week}: accuracy = {performance['metrics']['accuracy']:.4f}")
    
    # Check for degradation
    print("\n3. Checking for performance degradation...")
    degraded, details = monitor.performance_tracker.detect_performance_degradation()
    
    if degraded:
        print(f"   ⚠️  Performance degradation detected!")
        print(f"   Metric: {details['metric']}")
        print(f"   Baseline: {details['baseline_value']:.4f}")
        print(f"   Recent average: {details['recent_average']:.4f}")
        print(f"   Change: {details['relative_change']*100:.2f}%")
    else:
        print(f"   ✅ No significant performance degradation")


def example_weekly_report():
    """Example 3: Generate weekly drift report"""
    print("\n" + "="*80)
    print("Example 3: Weekly Drift Report")
    print("="*80)
    
    # Generate reference data
    reference_data = generate_sample_data(n_samples=1000, drift=False)
    
    # Create drift monitor
    monitor = create_drift_monitor(reference_data, model_name="alzheimer_classifier")
    
    # Track distributions over the week
    print("\n1. Tracking distributions over the week...")
    for day in range(1, 8):
        # Generate daily data with increasing drift
        drift_factor = day > 4  # Introduce drift after day 4
        daily_data = generate_sample_data(n_samples=100, drift=drift_factor)
        
        monitor.distribution_monitor.track_distributions(
            daily_data,
            dataset_name=f"day_{day}_data"
        )
        print(f"   Day {day}: tracked {len(daily_data)} samples")
    
    # Generate current data for drift detection
    current_data = generate_sample_data(n_samples=500, drift=True)
    
    # Generate weekly report
    print("\n2. Generating weekly drift report...")
    report = monitor.generate_weekly_report(current_data)
    
    # Display report summary
    print("\n3. Report Summary:")
    print(f"   Report name: {report['report_name']}")
    print(f"   Generated at: {report['generated_at']}")
    
    if 'drift_summary' in report:
        drift_summary = report['drift_summary']
        print(f"\n   Drift Summary:")
        print(f"     Drift detected: {drift_summary['drift_detected']}")
        print(f"     Retraining recommended: {drift_summary['retraining_recommended']}")
        print(f"     Features with high PSI: {drift_summary['n_features_with_high_psi']}")
        print(f"     Features with KS drift: {drift_summary['n_features_with_ks_drift']}")
    
    print(f"\n   Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"     {i}. {rec}")


def example_historical_statistics():
    """Example 4: Load and analyze historical statistics"""
    print("\n" + "="*80)
    print("Example 4: Historical Statistics")
    print("="*80)
    
    # Generate reference data
    reference_data = generate_sample_data(n_samples=1000, drift=False)
    
    # Create drift monitor
    monitor = create_drift_monitor(reference_data, model_name="alzheimer_classifier")
    
    # Simulate historical tracking
    print("\n1. Simulating historical tracking...")
    for week in range(1, 5):
        weekly_data = generate_sample_data(n_samples=200, drift=(week > 2))
        monitor.distribution_monitor.track_distributions(
            weekly_data,
            dataset_name=f"week_{week}_data"
        )
    
    # Load historical statistics
    print("\n2. Loading historical statistics...")
    stats = monitor.load_historical_statistics(days=90)
    
    print(f"\n3. Historical Statistics Summary:")
    print(f"   Distribution entries: {stats['n_distribution_entries']}")
    print(f"   Performance entries: {stats['n_performance_entries']}")
    print(f"   Alerts: {stats['n_alerts']}")
    
    # Get distribution summary for a specific feature
    print("\n4. Distribution trend for MMSE score:")
    mmse_summary = monitor.distribution_monitor.get_distribution_summary('mmse_score')
    
    if not mmse_summary.empty:
        print(f"   Entries: {len(mmse_summary)}")
        print(f"   Mean range: {mmse_summary['mean'].min():.2f} - {mmse_summary['mean'].max():.2f}")
        print(f"   Std range: {mmse_summary['std'].min():.2f} - {mmse_summary['std'].max():.2f}")


def example_retraining_decision():
    """Example 5: Automated retraining decision"""
    print("\n" + "="*80)
    print("Example 5: Automated Retraining Decision")
    print("="*80)
    
    # Generate reference data
    reference_data = generate_sample_data(n_samples=1000, drift=False)
    
    # Create drift monitor
    monitor = create_drift_monitor(reference_data, model_name="alzheimer_classifier")
    
    # Set baseline performance
    baseline_metrics = {
        'accuracy': 0.85,
        'f1_score': 0.83,
        'roc_auc': 0.90
    }
    monitor.performance_tracker.set_baseline_metrics(baseline_metrics)
    
    # Simulate drift and performance degradation
    print("\n1. Simulating drift and performance degradation...")
    
    # Monitor drift
    drifted_data = generate_sample_data(n_samples=500, drift=True)
    drift_results = monitor.monitor_data(drifted_data, dataset_name="recent_data")
    
    # Monitor performance
    n_samples = 200
    y_true = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    y_pred = y_true.copy()
    # Introduce 20% errors
    error_indices = np.random.choice(n_samples, 40, replace=False)
    y_pred[error_indices] = 1 - y_pred[error_indices]
    
    monitor.monitor_performance(
        pd.Series(y_true),
        pd.Series(y_pred),
        dataset_name="recent_predictions"
    )
    
    # Make retraining decision
    print("\n2. Making retraining decision...")
    should_retrain, reason = monitor.should_retrain_model()
    
    print(f"\n3. Retraining Decision:")
    print(f"   Should retrain: {should_retrain}")
    print(f"   Reason: {reason}")
    
    if should_retrain:
        print("\n   ⚠️  Model retraining is recommended!")
        print("   Next steps:")
        print("     1. Review drift analysis and performance metrics")
        print("     2. Prepare updated training dataset")
        print("     3. Trigger automated retraining pipeline")
        print("     4. Evaluate new model before deployment")
    else:
        print("\n   ✅ Model is performing well, continue monitoring")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("Data Drift Detection System - Examples")
    print("="*80)
    
    try:
        # Run examples
        example_basic_drift_detection()
        example_performance_tracking()
        example_weekly_report()
        example_historical_statistics()
        example_retraining_decision()
        
        print("\n" + "="*80)
        print("All examples completed successfully!")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
