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



class ResourceMonitor:
    """Monitor system resource utilization over time"""
    
    def __init__(self):
        self.resource_history: list = []
        self.max_history_size = 1000
    
    def collect_metrics(self) -> Dict[str, float]:
        """
        Collect current resource metrics
        
        Returns:
            Dictionary of resource metrics
        """
        process = psutil.Process()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': memory.percent,
            'memory_used_mb': process.memory_info().rss / 1024 / 1024,
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024 ** 3),
            'num_threads': process.num_threads(),
            'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
        }
        
        # Add to history
        self.resource_history.append(metrics)
        
        # Trim history if too large
        if len(self.resource_history) > self.max_history_size:
            self.resource_history = self.resource_history[-self.max_history_size:]
        
        return metrics
    
    def get_average_metrics(self, window_seconds: int = 60) -> Dict[str, float]:
        """
        Get average metrics over a time window
        
        Args:
            window_seconds: Time window in seconds
            
        Returns:
            Dictionary of average metrics
        """
        if not self.resource_history:
            return {}
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Filter to window
        recent_metrics = [
            m for m in self.resource_history 
            if m['timestamp'] >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        # Calculate averages
        avg_metrics = {}
        for key in recent_metrics[0].keys():
            if key != 'timestamp':
                values = [m[key] for m in recent_metrics]
                avg_metrics[f'avg_{key}'] = sum(values) / len(values)
                avg_metrics[f'max_{key}'] = max(values)
                avg_metrics[f'min_{key}'] = min(values)
        
        return avg_metrics
    
    def check_resource_thresholds(self) -> Dict[str, bool]:
        """
        Check if resource usage exceeds thresholds
        
        Returns:
            Dictionary of threshold violations
        """
        metrics = self.collect_metrics()
        
        violations = {
            'high_cpu': metrics['cpu_percent'] > 90,
            'high_memory': metrics['memory_percent'] > 90,
            'low_disk': metrics['disk_free_gb'] < 10,
            'high_threads': metrics['num_threads'] > 100
        }
        
        # Log warnings
        for violation, is_violated in violations.items():
            if is_violated:
                main_logger.warning(
                    f"Resource threshold exceeded: {violation}",
                    extra={'operation': 'resource_monitoring', 'user_id': 'system'}
                )
        
        return violations


class ProcessingTimeTracker:
    """Track processing times for different operations"""
    
    def __init__(self):
        self.operation_times: Dict[str, list] = {}
    
    def record_time(self, operation: str, duration_seconds: float):
        """
        Record processing time for an operation
        
        Args:
            operation: Operation name
            duration_seconds: Duration in seconds
        """
        if operation not in self.operation_times:
            self.operation_times[operation] = []
        
        self.operation_times[operation].append({
            'duration': duration_seconds,
            'timestamp': time.time()
        })
        
        # Keep only last 100 entries per operation
        if len(self.operation_times[operation]) > 100:
            self.operation_times[operation] = self.operation_times[operation][-100:]
    
    def get_statistics(self, operation: str) -> Dict[str, float]:
        """
        Get statistics for an operation
        
        Args:
            operation: Operation name
            
        Returns:
            Dictionary of statistics
        """
        if operation not in self.operation_times or not self.operation_times[operation]:
            return {}
        
        durations = [entry['duration'] for entry in self.operation_times[operation]]
        
        return {
            'count': len(durations),
            'mean': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'median': sorted(durations)[len(durations) // 2]
        }
    
    def get_all_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for all operations
        
        Returns:
            Dictionary mapping operation names to statistics
        """
        return {
            operation: self.get_statistics(operation)
            for operation in self.operation_times.keys()
        }


# Global monitoring instances
resource_monitor = ResourceMonitor()
processing_time_tracker = ProcessingTimeTracker()


def monitor_processing_time(operation_name: str):
    """
    Decorator to monitor and record processing time
    
    Args:
        operation_name: Name of the operation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record processing time
                processing_time_tracker.record_time(operation_name, duration)
                
                # Log
                main_logger.info(
                    f"{operation_name} completed in {duration:.2f}s",
                    extra={'operation': operation_name, 'user_id': 'system'}
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                processing_time_tracker.record_time(f"{operation_name}_failed", duration)
                raise
        
        return wrapper
    return decorator
