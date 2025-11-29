"""
Prometheus metrics for ML pipeline monitoring
Exposes metrics for Grafana dashboards
"""
from prometheus_client import Counter, Gauge, Histogram, Summary
from typing import Dict, Any
import time

# Data ingestion metrics
data_ingestion_total = Counter(
    'ml_pipeline_data_ingestion_total',
    'Total number of data ingestion operations',
    ['dataset', 'source', 'status']
)

data_ingestion_records = Counter(
    'ml_pipeline_data_ingestion_records_total',
    'Total number of records ingested',
    ['dataset', 'source']
)

data_ingestion_duration = Histogram(
    'ml_pipeline_data_ingestion_duration_seconds',
    'Duration of data ingestion operations',
    ['dataset', 'source'],
    buckets=[10, 30, 60, 120, 300, 600, 1800, 3600]
)

# Training metrics
training_total = Counter(
    'ml_pipeline_training_total',
    'Total number of training operations',
    ['model_name', 'model_type', 'status']
)

training_duration = Histogram(
    'ml_pipeline_training_duration_seconds',
    'Duration of training operations',
    ['model_name', 'model_type'],
    buckets=[60, 300, 600, 1800, 3600, 7200]
)

model_performance = Gauge(
    'ml_pipeline_model_performance',
    'Model performance metrics',
    ['model_name', 'metric']
)

# Feature engineering metrics
feature_extraction_total = Counter(
    'ml_pipeline_feature_extraction_total',
    'Total number of feature extraction operations',
    ['dataset', 'status']
)

feature_extraction_duration = Histogram(
    'ml_pipeline_feature_extraction_duration_seconds',
    'Duration of feature extraction',
    ['dataset'],
    buckets=[1, 5, 10, 30, 60, 120]
)

features_extracted = Gauge(
    'ml_pipeline_features_extracted',
    'Number of features extracted',
    ['dataset']
)

# Data quality metrics
data_quality_completeness = Gauge(
    'ml_pipeline_data_quality_completeness',
    'Data completeness percentage',
    ['dataset', 'column']
)

data_quality_outliers = Gauge(
    'ml_pipeline_data_quality_outliers',
    'Number of outliers detected',
    ['dataset', 'column']
)

data_quality_issues = Counter(
    'ml_pipeline_data_quality_issues_total',
    'Total data quality issues',
    ['dataset', 'issue_type']
)

# Drift detection metrics
data_drift_psi = Gauge(
    'ml_pipeline_data_drift_psi',
    'Population Stability Index for features',
    ['feature']
)

data_drift_detected = Counter(
    'ml_pipeline_data_drift_detected_total',
    'Total number of drift detections',
    ['feature']
)

# Model registry metrics
models_registered = Gauge(
    'ml_pipeline_models_registered',
    'Number of registered models',
    ['model_name']
)

model_deployments = Counter(
    'ml_pipeline_model_deployments_total',
    'Total model deployments',
    ['model_name', 'environment']
)

# Resource utilization metrics
cpu_usage = Gauge(
    'ml_pipeline_cpu_usage_percent',
    'CPU usage percentage'
)

memory_usage = Gauge(
    'ml_pipeline_memory_usage_percent',
    'Memory usage percentage'
)

memory_used_mb = Gauge(
    'ml_pipeline_memory_used_mb',
    'Memory used in MB'
)

disk_usage = Gauge(
    'ml_pipeline_disk_usage_percent',
    'Disk usage percentage'
)

disk_free_gb = Gauge(
    'ml_pipeline_disk_free_gb',
    'Free disk space in GB'
)

# Processing metrics
processing_queue_size = Gauge(
    'ml_pipeline_processing_queue_size',
    'Number of items in processing queue',
    ['queue_name']
)

processing_errors = Counter(
    'ml_pipeline_processing_errors_total',
    'Total processing errors',
    ['operation', 'error_type']
)

# Alert metrics
alerts_total = Counter(
    'ml_pipeline_alerts_total',
    'Total alerts generated',
    ['alert_type', 'severity']
)

active_alerts = Gauge(
    'ml_pipeline_active_alerts',
    'Number of active alerts',
    ['severity']
)


class MetricsCollector:
    """Collect and expose metrics for Prometheus"""
    
    @staticmethod
    def record_data_ingestion(
        dataset: str,
        source: str,
        status: str,
        records: int,
        duration: float
    ):
        """Record data ingestion metrics"""
        data_ingestion_total.labels(dataset=dataset, source=source, status=status).inc()
        data_ingestion_records.labels(dataset=dataset, source=source).inc(records)
        data_ingestion_duration.labels(dataset=dataset, source=source).observe(duration)
    
    @staticmethod
    def record_training(
        model_name: str,
        model_type: str,
        status: str,
        duration: float,
        metrics: Dict[str, float]
    ):
        """Record training metrics"""
        training_total.labels(
            model_name=model_name,
            model_type=model_type,
            status=status
        ).inc()
        
        training_duration.labels(
            model_name=model_name,
            model_type=model_type
        ).observe(duration)
        
        # Record performance metrics
        for metric_name, value in metrics.items():
            model_performance.labels(
                model_name=model_name,
                metric=metric_name
            ).set(value)
    
    @staticmethod
    def record_feature_extraction(
        dataset: str,
        status: str,
        num_features: int,
        duration: float
    ):
        """Record feature extraction metrics"""
        feature_extraction_total.labels(dataset=dataset, status=status).inc()
        feature_extraction_duration.labels(dataset=dataset).observe(duration)
        features_extracted.labels(dataset=dataset).set(num_features)
    
    @staticmethod
    def record_data_quality(
        dataset: str,
        completeness: Dict[str, float],
        outliers: Dict[str, int],
        issues: Dict[str, int]
    ):
        """Record data quality metrics"""
        for column, value in completeness.items():
            data_quality_completeness.labels(dataset=dataset, column=column).set(value)
        
        for column, count in outliers.items():
            data_quality_outliers.labels(dataset=dataset, column=column).set(count)
        
        for issue_type, count in issues.items():
            data_quality_issues.labels(dataset=dataset, issue_type=issue_type).inc(count)
    
    @staticmethod
    def record_drift(feature: str, psi_value: float, drift_detected: bool):
        """Record drift metrics"""
        data_drift_psi.labels(feature=feature).set(psi_value)
        if drift_detected:
            data_drift_detected.labels(feature=feature).inc()
    
    @staticmethod
    def record_model_registry(model_name: str, version_count: int):
        """Record model registry metrics"""
        models_registered.labels(model_name=model_name).set(version_count)
    
    @staticmethod
    def record_deployment(model_name: str, environment: str):
        """Record model deployment"""
        model_deployments.labels(model_name=model_name, environment=environment).inc()
    
    @staticmethod
    def update_resource_metrics(metrics: Dict[str, float]):
        """Update resource utilization metrics"""
        cpu_usage.set(metrics.get('cpu_percent', 0))
        memory_usage.set(metrics.get('memory_percent', 0))
        memory_used_mb.set(metrics.get('memory_used_mb', 0))
        disk_usage.set(metrics.get('disk_percent', 0))
        disk_free_gb.set(metrics.get('disk_free_gb', 0))
    
    @staticmethod
    def record_processing_error(operation: str, error_type: str):
        """Record processing error"""
        processing_errors.labels(operation=operation, error_type=error_type).inc()
    
    @staticmethod
    def record_alert(alert_type: str, severity: str):
        """Record alert"""
        alerts_total.labels(alert_type=alert_type, severity=severity).inc()
    
    @staticmethod
    def update_active_alerts(severity_counts: Dict[str, int]):
        """Update active alert counts"""
        for severity, count in severity_counts.items():
            active_alerts.labels(severity=severity).set(count)


# Global metrics collector
metrics_collector = MetricsCollector()
