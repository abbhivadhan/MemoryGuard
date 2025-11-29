"""
Example demonstrating the logging and monitoring system
"""
import time
import random
from pathlib import Path

from ml_pipeline.config.logging_config import main_logger, audit_logger, log_operation
from ml_pipeline.config.operation_logger import operation_logger, log_operation_decorator
from ml_pipeline.config.monitoring_config import (
    monitor_execution_time,
    monitor_resources,
    resource_monitor,
    processing_time_tracker,
    HealthCheck
)
from ml_pipeline.config.alerting import alert_manager, check_and_alert_on_failure
from ml_pipeline.config.prometheus_metrics import metrics_collector
from ml_pipeline.config.data_lineage import (
    lineage_tracker,
    LineageNodeType,
    LineageOperation
)


def example_basic_logging():
    """Example: Basic structured logging"""
    print("\n=== Example 1: Basic Logging ===")
    
    # Standard logging with context
    main_logger.info(
        "Starting data processing",
        extra=log_operation(
            operation='data_processing',
            user_id='user123',
            dataset='ADNI'
        )
    )
    
    # Warning
    main_logger.warning(
        "Low disk space detected",
        extra=log_operation(
            operation='health_check',
            user_id='system',
            disk_free_gb=15.5
        )
    )
    
    # Error
    main_logger.error(
        "Failed to connect to database",
        extra=log_operation(
            operation='database_connection',
            user_id='system',
            error='Connection timeout'
        )
    )
    
    # Audit logging
    audit_logger.info(
        "User accessed patient data",
        extra={'operation': 'data_access', 'user_id': 'doctor123'}
    )


def example_operation_logging():
    """Example: Operation logging for data ingestion and training"""
    print("\n=== Example 2: Operation Logging ===")
    
    # Data ingestion
    op_id = operation_logger.log_data_ingestion_start(
        dataset_name="ADNI_2024",
        source="ADNI",
        user_id="system",
        file_path="/data/adni_2024.csv"
    )
    
    # Simulate ingestion
    time.sleep(1)
    records = 5000
    
    operation_logger.log_data_ingestion_complete(
        operation_id=op_id,
        dataset_name="ADNI_2024",
        records_ingested=records,
        user_id="system"
    )
    
    # Training
    train_id = operation_logger.log_training_start(
        model_name="alzheimer_classifier",
        model_type="random_forest",
        dataset_version="v1.0",
        n_estimators=200,
        max_depth=15
    )
    
    # Simulate training progress
    for epoch in range(1, 6):
        time.sleep(0.5)
        metrics = {
            'loss': 0.5 - (epoch * 0.08),
            'accuracy': 0.7 + (epoch * 0.03)
        }
        operation_logger.log_training_progress(
            operation_id=train_id,
            model_name="alzheimer_classifier",
            epoch=epoch,
            total_epochs=5,
            metrics=metrics
        )
    
    # Training complete
    final_metrics = {
        'roc_auc': 0.92,
        'accuracy': 0.88,
        'precision': 0.85,
        'recall': 0.90
    }
    operation_logger.log_training_complete(
        operation_id=train_id,
        model_name="alzheimer_classifier",
        model_version="1.0.0",
        metrics=final_metrics
    )


@monitor_execution_time('data_processing')
def process_data_with_monitoring():
    """Example function with execution time monitoring"""
    time.sleep(random.uniform(0.5, 1.5))
    return "processed_data"


@log_operation_decorator('feature_extraction')
def extract_features_with_logging():
    """Example function with automatic operation logging"""
    time.sleep(random.uniform(0.3, 0.8))
    return ["feature1", "feature2", "feature3"]


def example_performance_monitoring():
    """Example: Performance monitoring"""
    print("\n=== Example 3: Performance Monitoring ===")
    
    # Monitor execution time
    for i in range(3):
        result = process_data_with_monitoring()
        print(f"Iteration {i+1} completed")
    
    # Get statistics
    stats = processing_time_tracker.get_statistics('data_processing')
    print(f"\nProcessing statistics:")
    print(f"  Count: {stats['count']}")
    print(f"  Mean: {stats['mean']:.2f}s")
    print(f"  Min: {stats['min']:.2f}s")
    print(f"  Max: {stats['max']:.2f}s")
    
    # Monitor resources
    print("\nMonitoring resources during operation...")
    with monitor_resources('training_simulation'):
        # Simulate resource-intensive operation
        data = [random.random() for _ in range(1000000)]
        time.sleep(1)
    
    # Collect current metrics
    metrics = resource_monitor.collect_metrics()
    print(f"\nCurrent resource usage:")
    print(f"  CPU: {metrics['cpu_percent']:.1f}%")
    print(f"  Memory: {metrics['memory_used_mb']:.1f}MB")
    print(f"  Disk Free: {metrics['disk_free_gb']:.1f}GB")
    
    # Health checks
    print("\nPerforming health checks...")
    disk_ok = HealthCheck.check_disk_space('/', min_gb=10.0)
    memory_ok = HealthCheck.check_memory(min_available_percent=20.0)
    print(f"  Disk space OK: {disk_ok}")
    print(f"  Memory OK: {memory_ok}")
    
    system_status = HealthCheck.get_system_status()
    print(f"\nSystem status:")
    for key, value in system_status.items():
        print(f"  {key}: {value}")


def example_alerting():
    """Example: Alerting system"""
    print("\n=== Example 4: Alerting ===")
    
    # Processing failure alert
    alert_manager.alert_processing_failure(
        operation='data_ingestion',
        error='Connection timeout to ADNI server',
        details={'dataset': 'ADNI', 'retry_count': 3}
    )
    
    # Resource threshold alert
    alert_manager.alert_resource_threshold(
        resource='memory',
        current_value=95.0,
        threshold=90.0,
        unit='%'
    )
    
    # Data quality alert
    alert_manager.alert_data_quality_issue(
        dataset='OASIS',
        issue_type='high_missing_values',
        details={'column': 'csf_ab42', 'missing_percent': 25.0}
    )
    
    # Data drift alert
    alert_manager.alert_data_drift(
        feature='age',
        psi_value=0.25,
        threshold=0.2
    )
    
    # Model performance degradation
    alert_manager.alert_model_performance_degradation(
        model_name='alzheimer_classifier',
        metric='roc_auc',
        current_value=0.78,
        baseline_value=0.92
    )
    
    # Get recent alerts
    recent_alerts = alert_manager.get_recent_alerts(hours=24)
    print(f"\nRecent alerts (last 24h): {len(recent_alerts)}")
    
    # Get alert summary
    summary = alert_manager.get_alert_summary(hours=24)
    print(f"\nAlert summary:")
    print(f"  Total: {summary['total']}")
    print(f"  By severity: {summary['by_severity']}")
    print(f"  By type: {summary['by_type']}")


@check_and_alert_on_failure('risky_operation')
def risky_operation(should_fail=False):
    """Example function with automatic failure alerting"""
    if should_fail:
        raise ValueError("Operation failed!")
    return "success"


def example_alerting_decorator():
    """Example: Automatic alerting on failure"""
    print("\n=== Example 5: Automatic Alerting ===")
    
    # Successful operation
    try:
        result = risky_operation(should_fail=False)
        print(f"Operation succeeded: {result}")
    except Exception as e:
        print(f"Operation failed: {e}")
    
    # Failed operation (will trigger alert)
    try:
        result = risky_operation(should_fail=True)
    except Exception as e:
        print(f"Operation failed and alert sent: {e}")


def example_prometheus_metrics():
    """Example: Recording Prometheus metrics"""
    print("\n=== Example 6: Prometheus Metrics ===")
    
    # Record data ingestion
    metrics_collector.record_data_ingestion(
        dataset='ADNI',
        source='ADNI',
        status='success',
        records=5000,
        duration=120.5
    )
    
    # Record training
    metrics_collector.record_training(
        model_name='alzheimer_classifier',
        model_type='random_forest',
        status='success',
        duration=3600.0,
        metrics={'roc_auc': 0.92, 'accuracy': 0.88}
    )
    
    # Record feature extraction
    metrics_collector.record_feature_extraction(
        dataset='ADNI',
        status='success',
        num_features=45,
        duration=30.2
    )
    
    # Record data quality
    metrics_collector.record_data_quality(
        dataset='ADNI',
        completeness={'mmse_score': 0.95, 'age': 1.0},
        outliers={'csf_ab42': 12},
        issues={'missing_values': 5, 'outliers': 12}
    )
    
    # Record drift
    metrics_collector.record_drift(
        feature='age',
        psi_value=0.15,
        drift_detected=False
    )
    
    # Update resource metrics
    metrics_collector.update_resource_metrics({
        'cpu_percent': 45.2,
        'memory_percent': 62.1,
        'memory_used_mb': 2048.5,
        'disk_percent': 65.0,
        'disk_free_gb': 150.0
    })
    
    print("Metrics recorded for Prometheus scraping")


def example_data_lineage():
    """Example: Data lineage tracking"""
    print("\n=== Example 7: Data Lineage Tracking ===")
    
    # Track data ingestion
    source_id, data_id = lineage_tracker.track_data_ingestion(
        source_name='ADNI',
        dataset_name='ADNI_2024',
        records_count=5000,
        user_id='system'
    )
    print(f"Created data source node: {source_id}")
    print(f"Created raw data node: {data_id}")
    
    # Track validation
    validated_id = lineage_tracker.track_validation(
        input_node_id=data_id,
        output_dataset_name='ADNI_2024_validated',
        validation_results={
            'completeness': 0.95,
            'outliers': 12,
            'duplicates': 0
        },
        user_id='system'
    )
    print(f"Created validated data node: {validated_id}")
    
    # Track feature engineering
    features_id = lineage_tracker.track_feature_engineering(
        input_node_id=validated_id,
        feature_set_name='cognitive_biomarker_features',
        num_features=45,
        feature_names=['mmse_score', 'csf_ab42', 'age', 'apoe_e4'],
        user_id='system'
    )
    print(f"Created features node: {features_id}")
    
    # Track model training
    model_id = lineage_tracker.track_model_training(
        training_data_node_id=features_id,
        model_name='alzheimer_classifier',
        model_version='1.0.0',
        model_type='random_forest',
        metrics={'roc_auc': 0.92, 'accuracy': 0.88},
        user_id='data_scientist'
    )
    print(f"Created model node: {model_id}")
    
    # Track prediction
    pred_id = lineage_tracker.track_prediction(
        model_node_id=model_id,
        prediction_id='pred_12345',
        input_features={'mmse_score': 24, 'age': 72},
        prediction_result={'risk': 0.65, 'class': 'MCI'},
        user_id='clinician'
    )
    print(f"Created prediction node: {pred_id}")
    
    # Get lineage for prediction
    lineage = lineage_tracker.get_lineage_for_node(pred_id)
    print(f"\nLineage for prediction {pred_id}:")
    print(f"  Upstream nodes: {len(lineage['upstream'])}")
    print(f"  Downstream nodes: {len(lineage['downstream'])}")
    
    # Get full path
    path = lineage_tracker.get_full_lineage_path(pred_id)
    print(f"\nFull lineage path:")
    for i, node in enumerate(path):
        print(f"  {i+1}. {node['name']} ({node['node_type']})")
    
    # Export lineage graph
    output_path = Path('lineage_example.dot')
    lineage_tracker.export_lineage_graph(output_path)
    print(f"\nLineage graph exported to {output_path}")
    print("Visualize with: dot -Tpng lineage_example.dot -o lineage_example.png")


def example_complete_pipeline():
    """Example: Complete pipeline with all monitoring"""
    print("\n=== Example 8: Complete Pipeline ===")
    
    # Start training operation
    train_id = operation_logger.log_training_start(
        model_name='alzheimer_classifier',
        model_type='random_forest',
        dataset_version='v1.0',
        n_estimators=200
    )
    
    try:
        # Monitor resources
        with monitor_resources('complete_training'):
            # Create lineage nodes
            data_id = lineage_tracker.create_node(
                LineageNodeType.TRAINING_DATA,
                'training_data_v1.0',
                {'records': 10000, 'features': 45}
            )
            
            # Simulate training
            print("Training model...")
            time.sleep(2)
            
            # Training metrics
            metrics = {
                'roc_auc': 0.92,
                'accuracy': 0.88,
                'precision': 0.85,
                'recall': 0.90
            }
            
            # Track in lineage
            model_id = lineage_tracker.track_model_training(
                training_data_node_id=data_id,
                model_name='alzheimer_classifier',
                model_version='1.0.0',
                model_type='random_forest',
                metrics=metrics,
                user_id='system'
            )
            
            # Record Prometheus metrics
            metrics_collector.record_training(
                model_name='alzheimer_classifier',
                model_type='random_forest',
                status='success',
                duration=2.0,
                metrics=metrics
            )
            
            # Log completion
            operation_logger.log_training_complete(
                operation_id=train_id,
                model_name='alzheimer_classifier',
                model_version='1.0.0',
                metrics=metrics,
                user_id='system'
            )
            
            print("Training completed successfully!")
            print(f"Model ID: {model_id}")
            print(f"Metrics: {metrics}")
            
    except Exception as e:
        # Alert on failure
        alert_manager.alert_processing_failure(
            operation='training',
            error=str(e),
            details={'model': 'alzheimer_classifier'}
        )
        
        # Log error
        operation_logger.log_training_error(
            operation_id=train_id,
            model_name='alzheimer_classifier',
            error=str(e),
            user_id='system'
        )
        
        print(f"Training failed: {e}")
        raise


def main():
    """Run all examples"""
    print("=" * 60)
    print("ML Pipeline Logging and Monitoring Examples")
    print("=" * 60)
    
    example_basic_logging()
    example_operation_logging()
    example_performance_monitoring()
    example_alerting()
    example_alerting_decorator()
    example_prometheus_metrics()
    example_data_lineage()
    example_complete_pipeline()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nCheck logs at: ml_pipeline/logs/")
    print("Check lineage at: ml_pipeline/data_storage/metadata/lineage/")


if __name__ == "__main__":
    main()
