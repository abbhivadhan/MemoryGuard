"""
Simple test to verify logging and monitoring modules
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from ml_pipeline.config.logging_config import main_logger, audit_logger
        print("✓ logging_config imported")
    except Exception as e:
        print(f"✗ logging_config failed: {e}")
        return False
    
    try:
        from ml_pipeline.config.operation_logger import operation_logger
        print("✓ operation_logger imported")
    except Exception as e:
        print(f"✗ operation_logger failed: {e}")
        return False
    
    try:
        from ml_pipeline.config.monitoring_config import (
            performance_monitor,
            resource_monitor,
            processing_time_tracker
        )
        print("✓ monitoring_config imported")
    except Exception as e:
        print(f"✗ monitoring_config failed: {e}")
        return False
    
    try:
        from ml_pipeline.config.alerting import alert_manager
        print("✓ alerting imported")
    except Exception as e:
        print(f"✗ alerting failed: {e}")
        return False
    
    try:
        from ml_pipeline.config.prometheus_metrics import metrics_collector
        print("✓ prometheus_metrics imported")
    except Exception as e:
        print(f"✗ prometheus_metrics failed: {e}")
        return False
    
    try:
        from ml_pipeline.config.data_lineage import lineage_tracker
        print("✓ data_lineage imported")
    except Exception as e:
        print(f"✗ data_lineage failed: {e}")
        return False
    
    print("\n✓ All modules imported successfully!")
    return True


def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    from ml_pipeline.config.logging_config import main_logger, log_operation
    from ml_pipeline.config.operation_logger import operation_logger
    from ml_pipeline.config.monitoring_config import resource_monitor
    from ml_pipeline.config.alerting import alert_manager
    from ml_pipeline.config.data_lineage import lineage_tracker, LineageNodeType
    
    # Test logging
    main_logger.info(
        "Test log message",
        extra=log_operation(operation='test', user_id='test_user')
    )
    print("✓ Logging works")
    
    # Test operation logger
    op_id = operation_logger.log_data_ingestion_start(
        dataset_name="test_dataset",
        source="test_source"
    )
    operation_logger.log_data_ingestion_complete(
        operation_id=op_id,
        dataset_name="test_dataset",
        records_ingested=100
    )
    print("✓ Operation logging works")
    
    # Test resource monitoring
    metrics = resource_monitor.collect_metrics()
    assert 'cpu_percent' in metrics
    assert 'memory_percent' in metrics
    print("✓ Resource monitoring works")
    
    # Test alerting
    alert_manager.send_alert(
        alert_type='test',
        severity='info',
        message='Test alert'
    )
    print("✓ Alerting works")
    
    # Test lineage tracking
    node_id = lineage_tracker.create_node(
        node_type=LineageNodeType.DATA_SOURCE,
        name='test_source'
    )
    assert node_id is not None
    print("✓ Lineage tracking works")
    
    print("\n✓ All basic functionality tests passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Logging and Monitoring System Tests")
    print("=" * 60)
    
    if test_imports():
        test_basic_functionality()
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Tests failed!")
        print("=" * 60)
        sys.exit(1)
