"""
Monitoring configuration for the ML pipeline
Tracks processing times, resource utilization, and system health
"""
import time
import psutil
from typing import Dict, Optional, Callable
from functools import wraps
from contextlib import contextmanager

from ml_pipeline.config.logging_config import main_logger


class PerformanceMonitor:
    """Monitor performance metrics for pipeline operations"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
    
    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': time.time()
        })
    
    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}
        
        values = [m['value'] for m in self.metrics[metric_name]]
        return {
            'count': len(values),
            'mean': sum(values) / len(values),
            'min': min(values),
            'max': max(values)
        }
    
    def clear_metrics(self):
        """Clear all recorded metrics"""
        self.metrics.clear()


# Global performance monitor
performance_monitor = PerformanceMonitor()


def monitor_execution_time(operation_name: str):
    """
    Decorator to monitor execution time of functions
    
    Args:
        operation_name: Name of the operation being monitored
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record metric
                performance_monitor.record_metric(
                    f"{operation_name}_execution_time",
                    execution_time
                )
                
                # Log execution time
                main_logger.info(
                    f"{operation_name} completed in {execution_time:.2f} seconds",
                    extra={'operation': operation_name, 'user_id': 'system'}
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                main_logger.error(
                    f"{operation_name} failed after {execution_time:.2f} seconds: {str(e)}",
                    extra={'operation': operation_name, 'user_id': 'system'}
                )
                raise
        return wrapper
    return decorator


@contextmanager
def monitor_resources(operation_name: str):
    """
    Context manager to monitor resource utilization
    
    Args:
        operation_name: Name of the operation being monitored
    """
    # Get initial resource usage
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    initial_cpu = process.cpu_percent()
    start_time = time.time()
    
    try:
        yield
    finally:
        # Get final resource usage
        execution_time = time.time() - start_time
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = final_memory - initial_memory
        cpu_usage = process.cpu_percent()
        
        # Record metrics
        performance_monitor.record_metric(f"{operation_name}_memory_mb", memory_delta)
        performance_monitor.record_metric(f"{operation_name}_cpu_percent", cpu_usage)
        performance_monitor.record_metric(f"{operation_name}_time_seconds", execution_time)
        
        # Log resource usage
        main_logger.info(
            f"{operation_name} - Time: {execution_time:.2f}s, "
            f"Memory: {memory_delta:.2f}MB, CPU: {cpu_usage:.1f}%",
            extra={'operation': operation_name, 'user_id': 'system'}
        )


class HealthCheck:
    """System health check utilities"""
    
    @staticmethod
    def check_disk_space(path: str, min_gb: float = 10.0) -> bool:
        """
        Check if sufficient disk space is available
        
        Args:
            path: Path to check
            min_gb: Minimum required space in GB
            
        Returns:
            True if sufficient space available
        """
        usage = psutil.disk_usage(path)
        available_gb = usage.free / (1024 ** 3)
        
        if available_gb < min_gb:
            main_logger.warning(
                f"Low disk space: {available_gb:.2f}GB available (minimum: {min_gb}GB)",
                extra={'operation': 'health_check', 'user_id': 'system'}
            )
            return False
        return True
    
    @staticmethod
    def check_memory(min_available_percent: float = 20.0) -> bool:
        """
        Check if sufficient memory is available
        
        Args:
            min_available_percent: Minimum required available memory percentage
            
        Returns:
            True if sufficient memory available
        """
        memory = psutil.virtual_memory()
        available_percent = memory.available / memory.total * 100
        
        if available_percent < min_available_percent:
            main_logger.warning(
                f"Low memory: {available_percent:.1f}% available "
                f"(minimum: {min_available_percent}%)",
                extra={'operation': 'health_check', 'user_id': 'system'}
            )
            return False
        return True
    
    @staticmethod
    def get_system_status() -> Dict[str, any]:
        """Get current system status"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024 ** 3),
            'disk_percent': disk.percent,
            'disk_available_gb': disk.free / (1024 ** 3)
        }
