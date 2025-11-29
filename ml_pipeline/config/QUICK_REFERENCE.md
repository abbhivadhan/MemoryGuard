# Logging and Monitoring Quick Reference

## Quick Import

```python
from ml_pipeline.config import (
    main_logger,
    operation_logger,
    alert_manager,
    lineage_tracker,
    metrics_collector,
    monitor_resources
)
```

## Common Patterns

### 1. Log an Operation
```python
from ml_pipeline.config import main_logger, log_operation

main_logger.info(
    "Processing started",
    extra=log_operation(operation='processing', user_id='user123')
)
```

### 2. Track Data Ingestion
```python
from ml_pipeline.config import operation_logger

op_id = operation_logger.log_data_ingestion_start(
    dataset_name="ADNI_2024",
    source="ADNI"
)
# ... ingest data ...
operation_logger.log_data_ingestion_complete(
    operation_id=op_id,
    dataset_name="ADNI_2024",
    records_ingested=5000
)
```

### 3. Track Training
```python
from ml_pipeline.config import operation_logger

train_id = operation_logger.log_training_start(
    model_name="classifier",
    model_type="random_forest",
    dataset_version="v1.0"
)
# ... train model ...
operation_logger.log_training_complete(
    operation_id=train_id,
    model_name="classifier",
    model_version="1.0.0",
    metrics={'roc_auc': 0.92}
)
```

### 4. Monitor Resources
```python
from ml_pipeline.config import monitor_resources

with monitor_resources('training'):
    train_model()  # Automatically logs CPU, memory, disk usage
```

### 5. Send Alert
```python
from ml_pipeline.config import alert_manager

alert_manager.alert_processing_failure(
    operation='data_ingestion',
    error='Connection timeout'
)
```

### 6. Track Lineage
```python
from ml_pipeline.config import lineage_tracker

# Ingestion
source_id, data_id = lineage_tracker.track_data_ingestion(
    source_name='ADNI',
    dataset_name='ADNI_2024',
    records_count=5000
)

# Validation
validated_id = lineage_tracker.track_validation(
    input_node_id=data_id,
    output_dataset_name='ADNI_2024_validated',
    validation_results={'completeness': 0.95}
)

# Features
features_id = lineage_tracker.track_feature_engineering(
    input_node_id=validated_id,
    feature_set_name='features_v1',
    num_features=45,
    feature_names=['age', 'mmse', ...]
)

# Training
model_id = lineage_tracker.track_model_training(
    training_data_node_id=features_id,
    model_name='classifier',
    model_version='1.0.0',
    model_type='random_forest',
    metrics={'roc_auc': 0.92}
)

# Prediction
pred_id = lineage_tracker.track_prediction(
    model_node_id=model_id,
    prediction_id='pred_123',
    input_features={'age': 72},
    prediction_result={'risk': 0.65}
)
```

### 7. Record Metrics
```python
from ml_pipeline.config import metrics_collector

metrics_collector.record_training(
    model_name='classifier',
    model_type='random_forest',
    status='success',
    duration=3600.0,
    metrics={'roc_auc': 0.92}
)
```

## Decorators

### Auto-log Operations
```python
from ml_pipeline.config import log_operation_decorator

@log_operation_decorator('data_processing')
def process_data(data):
    return processed_data
```

### Monitor Execution Time
```python
from ml_pipeline.config import monitor_execution_time

@monitor_execution_time('feature_extraction')
def extract_features(data):
    return features
```

### Alert on Failure
```python
from ml_pipeline.config import check_and_alert_on_failure

@check_and_alert_on_failure('critical_operation')
def critical_operation():
    # Automatically alerts if this fails
    pass
```

## Complete Pipeline Example

```python
from ml_pipeline.config import (
    operation_logger,
    monitor_resources,
    alert_manager,
    lineage_tracker,
    metrics_collector,
    LineageNodeType
)

def run_pipeline():
    # Start logging
    train_id = operation_logger.log_training_start(
        model_name='classifier',
        model_type='random_forest',
        dataset_version='v1.0'
    )
    
    try:
        # Monitor resources
        with monitor_resources('training'):
            # Track lineage
            data_id = lineage_tracker.create_node(
                LineageNodeType.TRAINING_DATA,
                'training_data_v1.0',
                {'records': 10000}
            )
            
            # Train model
            model, metrics = train_model()
            
            # Track model in lineage
            model_id = lineage_tracker.track_model_training(
                training_data_node_id=data_id,
                model_name='classifier',
                model_version='1.0.0',
                model_type='random_forest',
                metrics=metrics
            )
            
            # Record metrics
            metrics_collector.record_training(
                model_name='classifier',
                model_type='random_forest',
                status='success',
                duration=3600.0,
                metrics=metrics
            )
            
            # Log completion
            operation_logger.log_training_complete(
                operation_id=train_id,
                model_name='classifier',
                model_version='1.0.0',
                metrics=metrics
            )
            
    except Exception as e:
        # Alert on failure
        alert_manager.alert_processing_failure(
            operation='training',
            error=str(e)
        )
        
        # Log error
        operation_logger.log_training_error(
            operation_id=train_id,
            model_name='classifier',
            error=str(e)
        )
        
        raise
```

## Configuration

### Settings (ml_pipeline/config/settings.py)
```python
LOG_RETENTION_DAYS = 90
AUDIT_LOG_RETENTION_YEARS = 7
PERFORMANCE_ALERT_EMAIL = "admin@example.com"
```

### Alert Thresholds (ml_pipeline/config/alerting.py)
```python
CPU_THRESHOLD = 90.0  # percent
MEMORY_THRESHOLD = 90.0  # percent
DISK_THRESHOLD = 10.0  # GB free
PSI_THRESHOLD = 0.2  # drift threshold
```

## Log Files

- `ml_pipeline/logs/ml_pipeline.log` - Main logs (90 days)
- `ml_pipeline/logs/audit.log` - Audit logs (7 years)
- `ml_pipeline/logs/alerts.json` - Alert history

## Lineage Files

- `ml_pipeline/data_storage/metadata/lineage/nodes.json` - Lineage nodes
- `ml_pipeline/data_storage/metadata/lineage/edges.json` - Lineage edges

## Monitoring Stack

### Start Services
```bash
docker-compose -f ml_pipeline/docker-compose.infrastructure.yml up -d
```

### Setup Dashboards
```bash
python ml_pipeline/config/setup_dashboards.py
```

### Access Grafana
- URL: http://localhost:3000
- Default: admin/admin

## Testing

```bash
python3 ml_pipeline/config/test_logging_monitoring.py
```

## Examples

```bash
python3 ml_pipeline/examples/logging_monitoring_example.py
```

## Documentation

- Full Guide: `ml_pipeline/config/LOGGING_MONITORING_README.md`
- Implementation Summary: `ml_pipeline/TASK_17_IMPLEMENTATION_SUMMARY.md`
