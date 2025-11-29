# Data Drift Detection System

Comprehensive monitoring system for detecting data drift and model performance degradation in the ML pipeline.

## Overview

The data drift detection system monitors feature distributions over time, detects statistical drift, tracks model performance, and generates alerts when retraining is recommended.

## Components

### 1. DistributionMonitor
Tracks feature distributions over time and stores reference distributions for comparison.

**Key Features:**
- Compute distribution statistics (mean, std, quantiles, skewness, kurtosis)
- Track distributions over time
- Store and load reference distributions
- Compare current vs reference distributions
- Maintain historical distribution data

**Usage:**
```python
from ml_pipeline.monitoring import DistributionMonitor

# Initialize with reference data
monitor = DistributionMonitor(reference_data)

# Track current distributions
current_distributions = monitor.track_distributions(
    current_data,
    dataset_name="week_1_data"
)

# Get distribution summary for a feature
summary = monitor.get_distribution_summary('mmse_score')
```

### 2. DriftDetector
Detects statistical drift using Kolmogorov-Smirnov test and Population Stability Index (PSI).

**Key Features:**
- Kolmogorov-Smirnov (KS) test for distribution comparison
- Population Stability Index (PSI) calculation
- Configurable thresholds
- Comprehensive drift detection across all features
- Drift summary reports

**Usage:**
```python
from ml_pipeline.monitoring import DriftDetector

# Initialize
detector = DriftDetector(
    reference_data,
    ks_threshold=0.05,
    psi_threshold=0.2
)

# Detect drift
drift_results = detector.detect_drift(current_data)

# Check if retraining is needed
should_retrain = detector.should_retrain(drift_results)
```

**Interpretation:**
- **KS Test**: p-value < 0.05 indicates significant distribution difference
- **PSI Scores**:
  - PSI < 0.1: No significant change
  - 0.1 ≤ PSI < 0.2: Moderate change
  - PSI ≥ 0.2: Significant change (retraining recommended)

### 3. DriftAlerter
Triggers alerts when drift exceeds thresholds and sends notifications.

**Key Features:**
- Automatic alert triggering based on drift detection
- Email notifications (configurable)
- Alert severity levels (low, medium, high, critical)
- Alert history storage
- Formatted alert messages with actionable recommendations

**Usage:**
```python
from ml_pipeline.monitoring import DriftAlerter

# Initialize
alerter = DriftAlerter(
    alert_email="ml-team@example.com",
    psi_threshold=0.2
)

# Check and alert
alert_triggered = alerter.check_and_alert(
    drift_results,
    dataset_name="production_data"
)

# Load alert history
alerts = alerter.load_alert_history()
```

### 4. PerformanceTracker
Tracks model performance on recent data and detects degradation.

**Key Features:**
- Calculate performance metrics (accuracy, precision, recall, F1, AUC)
- Compare with baseline metrics
- Detect performance degradation
- Track performance trends over time
- Generate performance reports

**Usage:**
```python
from ml_pipeline.monitoring import PerformanceTracker

# Initialize
tracker = PerformanceTracker(model_name="alzheimer_classifier")

# Set baseline
tracker.set_baseline_metrics({
    'accuracy': 0.85,
    'f1_score': 0.83,
    'roc_auc': 0.90
})

# Track performance
performance = tracker.track_performance(
    y_true, y_pred, y_proba,
    dataset_name="week_1_data"
)

# Check for degradation
degraded, details = tracker.detect_performance_degradation()
```

### 5. DriftReporter
Generates comprehensive weekly drift reports with visualizations.

**Key Features:**
- Weekly drift reports
- Distribution summaries
- Performance summaries
- Visualizations (PSI scores, distribution trends)
- Actionable recommendations
- Report history management

**Usage:**
```python
from ml_pipeline.monitoring import DriftReporter

# Initialize
reporter = DriftReporter()

# Generate weekly report
report = reporter.generate_weekly_report(
    distribution_monitor,
    drift_detector,
    performance_tracker,
    current_data
)

# Load previous reports
reports = reporter.list_reports()
```

### 6. DataDriftMonitor
Comprehensive monitoring system that integrates all components.

**Key Features:**
- Unified interface for all monitoring components
- Database persistence
- Historical statistics management
- Automated retraining decisions
- Complete monitoring workflow

**Usage:**
```python
from ml_pipeline.monitoring import create_drift_monitor

# Create monitor
monitor = create_drift_monitor(
    reference_data,
    model_name="alzheimer_classifier"
)

# Monitor data
results = monitor.monitor_data(current_data)

# Monitor performance
performance = monitor.monitor_performance(y_true, y_pred)

# Generate weekly report
report = monitor.generate_weekly_report(current_data)

# Make retraining decision
should_retrain, reason = monitor.should_retrain_model()
```

## Workflow

### 1. Initial Setup
```python
# Load reference data (training data)
reference_data = load_training_data()

# Create drift monitor
monitor = create_drift_monitor(reference_data, model_name="my_model")

# Set baseline performance
monitor.performance_tracker.set_baseline_metrics({
    'accuracy': 0.85,
    'roc_auc': 0.90
})
```

### 2. Regular Monitoring
```python
# Monitor new data (e.g., weekly)
current_data = load_recent_data()

# Run drift detection
results = monitor.monitor_data(
    current_data,
    dataset_name=f"week_{week_number}"
)

# Monitor predictions
performance = monitor.monitor_performance(
    y_true, y_pred, y_proba,
    dataset_name=f"week_{week_number}_predictions"
)
```

### 3. Weekly Reporting
```python
# Generate weekly report
report = monitor.generate_weekly_report(current_data)

# Review recommendations
for rec in report['recommendations']:
    print(rec)
```

### 4. Retraining Decision
```python
# Check if retraining is needed
should_retrain, reason = monitor.should_retrain_model()

if should_retrain:
    print(f"Retraining recommended: {reason}")
    # Trigger retraining pipeline
    trigger_retraining()
```

## Configuration

Configure monitoring thresholds in `ml_pipeline/config/settings.py`:

```python
# Data quality thresholds
DRIFT_THRESHOLD: float = 0.2
PSI_THRESHOLD: float = 0.2

# Monitoring
DRIFT_CHECK_INTERVAL_DAYS: int = 7
PERFORMANCE_ALERT_EMAIL: Optional[str] = "ml-team@example.com"
```

## Database Schema

Drift reports are stored in the `data_drift_reports` table:

```sql
CREATE TABLE data_drift_reports (
    id INTEGER PRIMARY KEY,
    report_id VARCHAR(50) UNIQUE,
    reference_dataset VARCHAR(100),
    comparison_dataset VARCHAR(100),
    drift_detected BOOLEAN,
    features_with_drift JSON,
    ks_test_results JSON,
    psi_scores JSON,
    retraining_recommended BOOLEAN,
    created_at TIMESTAMP
);
```

## Examples

See `ml_pipeline/examples/drift_detection_example.py` for comprehensive examples:

1. Basic drift detection
2. Performance tracking
3. Weekly report generation
4. Historical statistics analysis
5. Automated retraining decisions

Run examples:
```bash
cd ml_pipeline
python examples/drift_detection_example.py
```

## Best Practices

### 1. Reference Data Selection
- Use training data as reference
- Ensure reference data is representative
- Update reference periodically (e.g., after retraining)

### 2. Monitoring Frequency
- Monitor weekly for production systems
- More frequent monitoring for critical applications
- Balance between detection speed and computational cost

### 3. Threshold Tuning
- Start with default thresholds (KS: 0.05, PSI: 0.2)
- Adjust based on false positive/negative rates
- Consider domain-specific requirements

### 4. Alert Management
- Configure email notifications for critical alerts
- Review alerts regularly
- Document investigation and resolution

### 5. Historical Data
- Retain distribution history for trend analysis
- Clean up old data periodically (default: 90 days)
- Archive important reports for compliance

## Troubleshooting

### High False Positive Rate
- Increase PSI threshold (e.g., 0.25)
- Increase KS p-value threshold (e.g., 0.01)
- Review feature selection

### Missed Drift Detection
- Decrease thresholds
- Increase monitoring frequency
- Add more sensitive features

### Performance Issues
- Reduce number of features monitored
- Increase monitoring interval
- Optimize data loading

## Integration with Retraining Pipeline

The drift detection system integrates with the automated retraining pipeline:

```python
# In retraining pipeline
monitor = create_drift_monitor(reference_data, model_name)

# Check if retraining needed
should_retrain, reason = monitor.should_retrain_model()

if should_retrain:
    logger.info(f"Triggering retraining: {reason}")
    
    # Load new data
    new_data = load_recent_data()
    
    # Retrain models
    new_model = train_model(new_data)
    
    # Evaluate
    if new_model.performance > current_model.performance * 1.05:
        # Deploy new model
        deploy_model(new_model)
        
        # Update reference data
        monitor.set_reference_data(new_data)
```

## Metrics and KPIs

Track these KPIs for monitoring system health:

1. **Drift Detection Rate**: % of monitoring runs with drift detected
2. **Alert Response Time**: Time from alert to investigation
3. **False Positive Rate**: % of alerts that don't require action
4. **Retraining Frequency**: Number of retraining events per month
5. **Model Performance Stability**: Variance in performance metrics

## References

- Kolmogorov-Smirnov Test: [Wikipedia](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test)
- Population Stability Index: [PSI Guide](https://www.listendata.com/2015/05/population-stability-index.html)
- Data Drift in ML: [Google MLOps](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
