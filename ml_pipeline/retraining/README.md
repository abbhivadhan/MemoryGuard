# Automated Retraining Pipeline

This module provides automated model retraining capabilities for the ML pipeline, including drift detection, automatic evaluation, model promotion, and A/B testing.

## Features

### 1. Apache Airflow DAG
- Scheduled monthly retraining
- Drift-triggered retraining
- Data volume-triggered retraining
- Complete workflow orchestration

### 2. Retraining Triggers
- **Data Drift Detection**: Monitors feature distributions using KS test and PSI
- **Data Volume Threshold**: Triggers when new data exceeds 1000 records
- **Performance Degradation**: Monitors model performance over time

### 3. Automated Evaluation
- Compares new models against production models
- Calculates performance improvements
- Generates evaluation reports

### 4. Model Promotion Logic
- Promotes models if they are 5% better than production
- Automatic deployment decisions
- Rollback capabilities
- Manual approval workflow

### 5. Notification System
- Email notifications for retraining events
- Drift detection alerts
- Model promotion notifications
- Failure alerts

### 6. A/B Testing
- Gradual rollout strategies (canary, gradual, immediate)
- Traffic splitting between model versions
- Performance tracking
- Automatic winner selection

## Requirements

All requirements are implemented according to the design specification:

- **Requirement 11.1**: Scheduled monthly retraining ✓
- **Requirement 11.2**: Drift-triggered retraining ✓
- **Requirement 11.3**: Data volume trigger (>1000 records) ✓
- **Requirement 11.4**: Automatic evaluation vs production ✓
- **Requirement 11.5**: Promote if 5% better ✓
- **Requirement 11.6**: Notifications before updates ✓
- **Requirement 11.7**: A/B testing for gradual rollout ✓

## Usage

### Setting up Airflow

1. Install Apache Airflow (already in requirements.txt):
```bash
pip install apache-airflow>=2.7.0
```

2. Initialize Airflow database:
```bash
airflow db init
```

3. Copy the DAG file to Airflow's DAG folder:
```bash
cp ml_pipeline/retraining/airflow_dag.py ~/airflow/dags/
```

4. Start Airflow:
```bash
airflow webserver --port 8080
airflow scheduler
```

5. The `model_retraining` DAG will appear in the Airflow UI and run monthly.

### Manual Retraining

```python
from ml_pipeline.retraining import AutomatedRetrainingPipeline

# Initialize pipeline
pipeline = AutomatedRetrainingPipeline()

# Retrain all models
results = pipeline.retrain_all_models()

# Evaluate new models
evaluation = pipeline.evaluate_new_models(results)

print(f"Retraining completed: {results['success']}")
print(f"Models evaluated: {evaluation['summary']['models_evaluated']}")
```

### Checking Retraining Triggers

```python
from ml_pipeline.retraining import RetrainingTriggers

# Initialize triggers
triggers = RetrainingTriggers()

# Check if retraining should be triggered
should_retrain, trigger_info = triggers.should_retrain(
    check_drift=True,
    check_volume=True,
    check_performance=False
)

if should_retrain:
    print(f"Retraining triggered: {trigger_info['trigger_reason']}")
else:
    print("No retraining needed")
```

### Model Promotion

```python
from ml_pipeline.retraining import ModelPromoter

# Initialize promoter
promoter = ModelPromoter(improvement_threshold=0.05)  # 5% improvement

# Promote models if they meet criteria
promotion_results = promoter.promote_if_better(evaluation_results)

print(f"Models promoted: {promotion_results['summary']['models_promoted']}")
```

### A/B Testing

```python
from ml_pipeline.retraining import ABTestingManager

# Initialize A/B testing manager
ab_manager = ABTestingManager()

# Create A/B test
test = ab_manager.create_ab_test(
    model_name='random_forest',
    version_a='v20250126_prod',
    version_b='v20250126_new',
    traffic_split=0.5,  # 50% to each version
    duration_days=7
)

# Route predictions
version_id, variant = ab_manager.route_prediction(
    model_name='random_forest',
    request_id='user_123_request_456'
)

# Check test status
status = ab_manager.check_test_status(test['test_id'])
print(f"Test status: {status['status']}")
print(f"Winner: {status['winner']}")

# End test and promote winner
result = ab_manager.end_test(test['test_id'], promote_winner=True)
```

### Gradual Rollout

```python
from ml_pipeline.retraining import ABTestingManager, RolloutStrategy

ab_manager = ABTestingManager()

# Create gradual rollout plan
rollout = ab_manager.create_gradual_rollout(
    model_name='xgboost',
    new_version='v20250126_new',
    strategy=RolloutStrategy.CANARY,
    initial_traffic=0.1,  # Start with 10%
    increment=0.2,  # Increase by 20% each step
    increment_interval_hours=24  # Every 24 hours
)

print(f"Rollout schedule: {len(rollout['schedule'])} steps")
for step in rollout['schedule']:
    print(f"Step {step['step']}: {step['traffic_percentage']}% after {step['delay_hours']}h")
```

### Notifications

```python
from ml_pipeline.retraining import NotificationService

# Initialize notification service
notifier = NotificationService(
    email_recipients=['ml-team@example.com']
)

# Send retraining summary
notifier.send_retraining_summary(
    drift_detected=True,
    volume_threshold_met=False,
    deployment_results=promotion_results
)

# Send drift alert
notifier.send_drift_alert(drift_results)

# Send promotion notification
notifier.send_promotion_notification(
    model_name='random_forest',
    version_id='v20250126_new',
    improvement_percent=7.5,
    new_metrics={'roc_auc': 0.87, 'accuracy': 0.82}
)
```

## Configuration

Configure the retraining pipeline through environment variables or `ml_pipeline/config/settings.py`:

```python
# Drift detection
DRIFT_THRESHOLD = 0.2  # PSI threshold
PSI_THRESHOLD = 0.2

# Model promotion
MODEL_IMPROVEMENT_THRESHOLD = 0.05  # 5% improvement required

# Retraining schedule
RETRAINING_SCHEDULE = "monthly"

# Notifications
PERFORMANCE_ALERT_EMAIL = "ml-team@example.com"

# Data volume trigger
# (hardcoded to 1000 as per Requirement 11.3)
```

## Airflow DAG Structure

The automated retraining DAG follows this workflow:

```
start
  ↓
check_drift
  ↓
check_data_volume
  ↓
[skip_retrain] OR [load_new_data]
                      ↓
                  retrain_models
                      ↓
                  evaluate_models
                      ↓
                  deploy_models
                      ↓
                  send_notifications
                      ↓
                    end
```

## Monitoring

Monitor the retraining pipeline through:

1. **Airflow UI**: View DAG runs, task status, and logs
2. **Email Notifications**: Receive alerts for important events
3. **Audit Logs**: All operations are logged to the database
4. **Model Registry**: Track model versions and deployments

## Troubleshooting

### Retraining Fails

1. Check Airflow logs in the UI
2. Verify data availability in feature store
3. Check database connectivity
4. Review error notifications

### Models Not Promoted

1. Check if improvement threshold is met (5%)
2. Review evaluation results
3. Verify model metrics are calculated correctly
4. Check audit logs for promotion attempts

### Notifications Not Sent

1. Verify SMTP configuration
2. Check email recipients are configured
3. Review notification service logs
4. Notifications are logged even if email fails

## Testing

Run the example script to test the retraining pipeline:

```bash
python ml_pipeline/examples/automated_retraining_example.py
```

## Architecture

The retraining module consists of:

- **airflow_dag.py**: Airflow DAG definition
- **retraining_pipeline.py**: Core retraining orchestration
- **retraining_triggers.py**: Trigger detection logic
- **model_promoter.py**: Model promotion logic
- **notification_service.py**: Email notifications
- **ab_testing.py**: A/B testing and gradual rollout

All components integrate with the existing ML pipeline infrastructure including the model registry, drift detector, and training pipeline.
