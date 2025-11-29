# Logging and Monitoring System

## Overview

The ML Pipeline includes a comprehensive logging and monitoring system that tracks all operations, monitors system health, and provides alerting capabilities.

## Components

### 1. Structured Logging (`logging_config.py`)

**Features:**
- Structured log format with timestamps
- Separate audit logging for compliance (7-year retention)
- Log rotation with configurable retention (default: 90 days)
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Usage:**
```python
from ml_pipeline.config.logging_config import main_logger, audit_logger, log_operation

# Standard logging
main_logger.info(
    "Processing data",
    extra=log_operation(
        operation='data_processing',
        user_id='user123',
        dataset='ADNI'
    )
)

# Audit logging
audit_logger.info(
    "Model deployed to production",
    extra={'operation': 'deployment', 'user_id': 'admin'}
)
```

### 2. Operation Logging (`operation_logger.py`)

**Features:**
- Tracks data ingestion operations
- Monitors training progress
- Records feature extraction
- Logs model deployments
- Tracks data access for audit

**Usage:**
```python
from ml_pipeline.config.operation_logger import operation_logger

# Log data ingestion
op_id = operation_logger.log_data_ingestion_start(
    dataset_name="ADNI_2024",
    source="ADNI",
    user_id="system"
)

# ... perform ingestion ...

operation_logger.log_data_ingestion_complete(
    operation_id=op_id,
    dataset_name="ADNI_2024",
    records_ingested=5000,
    user_id="system"
)

# Log training
train_id = operation_logger.log_training_start(
    model_name="alzheimer_classifier",
    model_type="random_forest",
    dataset_version="v1.0",
    n_estimators=200
)

# ... during training ...
operation_logger.log_training_progress(
    operation_id=train_id,
    model_name="alzheimer_classifier",
    epoch=5,
    total_epochs=10,
    metrics={'loss': 0.25, 'accuracy': 0.85}
)

# ... after training ...
operation_logger.log_training_complete(
    operation_id=train_id,
    model_name="alzheimer_classifier",
    model_version="1.0.0",
    metrics={'roc_auc': 0.92, 'accuracy': 0.88}
)
```

**Decorator Usage:**
```python
from ml_pipeline.config.operation_logger import log_operation_decorator

@log_operation_decorator('data_processing')
def process_data(data):
    # Function automatically logged
    return processed_data
```

### 3. Performance Monitoring (`monitoring_config.py`)

**Features:**
- Execution time tracking
- Resource utilization monitoring (CPU, memory, disk)
- Processing time statistics
- Health checks

**Usage:**
```python
from ml_pipeline.config.monitoring_config import (
    monitor_execution_time,
    monitor_resources,
    resource_monitor,
    processing_time_tracker
)

# Monitor execution time
@monitor_execution_time('data_processing')
def process_data(data):
    return processed_data

# Monitor resources
with monitor_resources('training'):
    train_model()

# Collect resource metrics
metrics = resource_monitor.collect_metrics()
print(f"CPU: {metrics['cpu_percent']}%")
print(f"Memory: {metrics['memory_used_mb']}MB")

# Get processing statistics
stats = processing_time_tracker.get_statistics('data_processing')
print(f"Average time: {stats['mean']:.2f}s")
```

### 4. Alerting System (`alerting.py`)

**Features:**
- Alert on processing failures
- Resource threshold violations
- Data quality issues
- Model performance degradation
- Data drift detection
- Alert cooldown to prevent spam
- Email notifications (configurable)

**Usage:**
```python
from ml_pipeline.config.alerting import alert_manager, check_and_alert_on_failure

# Manual alerts
alert_manager.alert_processing_failure(
    operation='data_ingestion',
    error='Connection timeout',
    details={'dataset': 'ADNI'}
)

alert_manager.alert_resource_threshold(
    resource='memory',
    current_value=95.0,
    threshold=90.0,
    unit='%'
)

alert_manager.alert_data_drift(
    feature='age',
    psi_value=0.25,
    threshold=0.2
)

# Automatic alerting with decorator
@check_and_alert_on_failure('data_processing')
def process_data(data):
    # Automatically alerts on failure
    return processed_data

# Get recent alerts
recent = alert_manager.get_recent_alerts(hours=24, severity='error')
summary = alert_manager.get_alert_summary(hours=24)
```

### 5. Prometheus Metrics (`prometheus_metrics.py`)

**Features:**
- Exposes metrics for Prometheus scraping
- Counters, gauges, and histograms
- Metrics for all pipeline operations

**Metrics Categories:**
- Data ingestion metrics
- Training metrics
- Feature engineering metrics
- Data quality metrics
- Drift detection metrics
- Resource utilization metrics
- Alert metrics

**Usage:**
```python
from ml_pipeline.config.prometheus_metrics import metrics_collector

# Record metrics
metrics_collector.record_data_ingestion(
    dataset='ADNI',
    source='ADNI',
    status='success',
    records=5000,
    duration=120.5
)

metrics_collector.record_training(
    model_name='alzheimer_classifier',
    model_type='random_forest',
    status='success',
    duration=3600.0,
    metrics={'roc_auc': 0.92, 'accuracy': 0.88}
)

metrics_collector.update_resource_metrics({
    'cpu_percent': 45.2,
    'memory_percent': 62.1,
    'disk_free_gb': 150.0
})
```

### 6. Grafana Dashboards (`grafana_dashboards.json`, `setup_dashboards.py`)

**Dashboards:**
1. **ML Pipeline Overview** - High-level system health
2. **Data Ingestion Dashboard** - Ingestion metrics and quality
3. **Training Dashboard** - Model training performance
4. **Data Drift Dashboard** - Drift detection and monitoring
5. **Resource Monitoring Dashboard** - System resources
6. **Alerts Dashboard** - Alert history and status

**Setup:**
```bash
# Setup Grafana dashboards
python ml_pipeline/config/setup_dashboards.py
```

Or programmatically:
```python
from ml_pipeline.config.setup_dashboards import setup_monitoring_stack

setup_monitoring_stack()
```

### 7. Data Lineage Tracking (`data_lineage.py`)

**Features:**
- Track data from source to predictions
- Graph-based lineage representation
- Audit trail for all transformations
- Export to DOT format for visualization

**Usage:**
```python
from ml_pipeline.config.data_lineage import lineage_tracker, LineageNodeType, LineageOperation

# Track data ingestion
source_id, data_id = lineage_tracker.track_data_ingestion(
    source_name='ADNI',
    dataset_name='ADNI_2024',
    records_count=5000
)

# Track validation
validated_id = lineage_tracker.track_validation(
    input_node_id=data_id,
    output_dataset_name='ADNI_2024_validated',
    validation_results={'completeness': 0.95, 'outliers': 12}
)

# Track feature engineering
features_id = lineage_tracker.track_feature_engineering(
    input_node_id=validated_id,
    feature_set_name='cognitive_biomarker_features',
    num_features=45,
    feature_names=['mmse_score', 'csf_ab42', ...]
)

# Track model training
model_id = lineage_tracker.track_model_training(
    training_data_node_id=features_id,
    model_name='alzheimer_classifier',
    model_version='1.0.0',
    model_type='random_forest',
    metrics={'roc_auc': 0.92}
)

# Track prediction
pred_id = lineage_tracker.track_prediction(
    model_node_id=model_id,
    prediction_id='pred_12345',
    input_features={'mmse_score': 24, 'age': 72},
    prediction_result={'risk': 0.65, 'class': 'MCI'}
)

# Get lineage for a node
lineage = lineage_tracker.get_lineage_for_node(pred_id)
print(f"Upstream nodes: {lineage['upstream']}")
print(f"Downstream nodes: {lineage['downstream']}")

# Get full path
path = lineage_tracker.get_full_lineage_path(pred_id)
for node in path:
    print(f"{node['name']} ({node['node_type']})")

# Export lineage graph
from pathlib import Path
lineage_tracker.export_lineage_graph(Path('lineage.dot'))
# Visualize with: dot -Tpng lineage.dot -o lineage.png
```

## Configuration

### Environment Variables

Set in `.env` or `ml_pipeline/config/settings.py`:

```bash
# Logging
LOG_RETENTION_DAYS=90
AUDIT_LOG_RETENTION_YEARS=7

# Alerting
PERFORMANCE_ALERT_EMAIL=admin@example.com

# Monitoring
DRIFT_CHECK_INTERVAL_DAYS=7
```

### Alert Thresholds

Defined in `alerting.py`:

```python
CPU_THRESHOLD = 90.0  # percent
MEMORY_THRESHOLD = 90.0  # percent
DISK_THRESHOLD = 10.0  # GB free
PSI_THRESHOLD = 0.2  # drift threshold
```

## Integration with Pipeline

### Example: Complete Pipeline with Monitoring

```python
from ml_pipeline.config.operation_logger import operation_logger
from ml_pipeline.config.monitoring_config import monitor_resources
from ml_pipeline.config.alerting import alert_manager
from ml_pipeline.config.prometheus_metrics import metrics_collector
from ml_pipeline.config.data_lineage import lineage_tracker

def run_training_pipeline():
    # Start operation logging
    train_id = operation_logger.log_training_start(
        model_name='alzheimer_classifier',
        model_type='random_forest',
        dataset_version='v1.0'
    )
    
    try:
        # Monitor resources during training
        with monitor_resources('training'):
            # Load data
            data_id = lineage_tracker.create_node(
                LineageNodeType.TRAINING_DATA,
                'training_data_v1.0',
                {'records': 10000}
            )
            
            # Train model
            model, metrics = train_model()
            
            # Track in lineage
            model_id = lineage_tracker.track_model_training(
                training_data_node_id=data_id,
                model_name='alzheimer_classifier',
                model_version='1.0.0',
                model_type='random_forest',
                metrics=metrics
            )
            
            # Record metrics
            metrics_collector.record_training(
                model_name='alzheimer_classifier',
                model_type='random_forest',
                status='success',
                duration=3600.0,
                metrics=metrics
            )
            
            # Log completion
            operation_logger.log_training_complete(
                operation_id=train_id,
                model_name='alzheimer_classifier',
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
            model_name='alzheimer_classifier',
            error=str(e)
        )
        
        raise
```

## Monitoring Stack Setup

### Prerequisites

1. **Prometheus** - Metrics collection
2. **Grafana** - Visualization
3. **Docker** (optional) - For containerized deployment

### Quick Start

1. Start Prometheus:
```bash
# Using docker-compose
docker-compose -f ml_pipeline/docker-compose.infrastructure.yml up -d prometheus
```

2. Start Grafana:
```bash
docker-compose -f ml_pipeline/docker-compose.infrastructure.yml up -d grafana
```

3. Setup dashboards:
```bash
python ml_pipeline/config/setup_dashboards.py
```

4. Access Grafana:
- URL: http://localhost:3000
- Default credentials: admin/admin

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'ml_pipeline'
    static_configs:
      - targets: ['localhost:8000']  # Your API endpoint
    scrape_interval: 15s
```

## Log Files

Logs are stored in `ml_pipeline/logs/`:

- `ml_pipeline.log` - Main application logs (90-day retention)
- `audit.log` - Audit logs (7-year retention)
- `alerts.json` - Alert history

## Best Practices

1. **Always use structured logging** with operation context
2. **Track lineage** for all data transformations
3. **Monitor resource usage** during long-running operations
4. **Set up alerts** for critical failures
5. **Review dashboards** regularly for system health
6. **Maintain audit logs** for compliance
7. **Export lineage graphs** for documentation

## Troubleshooting

### High Memory Usage
```python
from ml_pipeline.config.monitoring_config import resource_monitor

# Check current usage
metrics = resource_monitor.collect_metrics()
if metrics['memory_percent'] > 90:
    # Take action
    pass
```

### Missing Metrics
- Ensure Prometheus is scraping the correct endpoint
- Check that metrics are being recorded in code
- Verify Prometheus configuration

### Alert Spam
- Alerts have a 5-minute cooldown by default
- Adjust `cooldown_period` in `AlertManager` if needed

### Lineage Not Tracking
- Ensure lineage tracker is imported and used
- Check that metadata directory exists and is writable
- Review logs for lineage-related errors

## Requirements

Satisfied by task 17:
- ✅ 16.1: Log all operations with timestamps
- ✅ 16.2: Log data ingestion and training operations
- ✅ 16.3: Monitor processing times and resource utilization
- ✅ 16.4: Alert on failures within 1 minute
- ✅ 16.5: Maintain logs for 90 days
- ✅ 16.6: Provide monitoring dashboards
- ✅ 16.7: Track data lineage from source to predictions
