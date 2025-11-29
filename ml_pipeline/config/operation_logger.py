"""
Operation logging for ML pipeline
Logs data ingestion operations and training progress
"""
import time
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps

from ml_pipeline.config.logging_config import main_logger, audit_logger, log_operation


class OperationLogger:
    """Logger for pipeline operations"""
    
    def __init__(self):
        self.operation_start_times: Dict[str, float] = {}
    
    def log_data_ingestion_start(
        self,
        dataset_name: str,
        source: str,
        user_id: str = "system",
        **metadata
    ):
        """
        Log the start of a data ingestion operation
        
        Args:
            dataset_name: Name of the dataset being ingested
            source: Data source (ADNI, OASIS, NACC)
            user_id: User performing the operation
            **metadata: Additional metadata
        """
        operation_id = f"ingest_{dataset_name}_{int(time.time())}"
        self.operation_start_times[operation_id] = time.time()
        
        main_logger.info(
            f"Starting data ingestion: {dataset_name} from {source}",
            extra=log_operation(
                operation='data_ingestion_start',
                user_id=user_id,
                dataset_name=dataset_name,
                source=source,
                operation_id=operation_id,
                **metadata
            )
        )
        
        # Audit log
        audit_logger.info(
            f"Data ingestion started: {dataset_name} from {source}",
            extra={'operation': 'data_ingestion', 'user_id': user_id}
        )
        
        return operation_id
    
    def log_data_ingestion_complete(
        self,
        operation_id: str,
        dataset_name: str,
        records_ingested: int,
        user_id: str = "system",
        **metadata
    ):
        """
        Log the completion of a data ingestion operation
        
        Args:
            operation_id: Operation identifier from start
            dataset_name: Name of the dataset
            records_ingested: Number of records ingested
            user_id: User performing the operation
            **metadata: Additional metadata
        """
        duration = None
        if operation_id in self.operation_start_times:
            duration = time.time() - self.operation_start_times[operation_id]
            del self.operation_start_times[operation_id]
        
        main_logger.info(
            f"Data ingestion completed: {dataset_name} - {records_ingested} records "
            f"in {duration:.2f}s" if duration else f"Data ingestion completed: {dataset_name}",
            extra=log_operation(
                operation='data_ingestion_complete',
                user_id=user_id,
                dataset_name=dataset_name,
                records_ingested=records_ingested,
                duration_seconds=duration,
                operation_id=operation_id,
                **metadata
            )
        )
        
        # Audit log
        audit_logger.info(
            f"Data ingestion completed: {dataset_name} - {records_ingested} records",
            extra={'operation': 'data_ingestion', 'user_id': user_id}
        )
    
    def log_data_ingestion_error(
        self,
        operation_id: str,
        dataset_name: str,
        error: str,
        user_id: str = "system",
        **metadata
    ):
        """
        Log a data ingestion error
        
        Args:
            operation_id: Operation identifier from start
            dataset_name: Name of the dataset
            error: Error message
            user_id: User performing the operation
            **metadata: Additional metadata
        """
        duration = None
        if operation_id in self.operation_start_times:
            duration = time.time() - self.operation_start_times[operation_id]
            del self.operation_start_times[operation_id]
        
        main_logger.error(
            f"Data ingestion failed: {dataset_name} - {error}",
            extra=log_operation(
                operation='data_ingestion_error',
                user_id=user_id,
                dataset_name=dataset_name,
                error=error,
                duration_seconds=duration,
                operation_id=operation_id,
                **metadata
            )
        )
        
        # Audit log
        audit_logger.error(
            f"Data ingestion failed: {dataset_name} - {error}",
            extra={'operation': 'data_ingestion', 'user_id': user_id}
        )
    
    def log_training_start(
        self,
        model_name: str,
        model_type: str,
        dataset_version: str,
        user_id: str = "system",
        **hyperparameters
    ):
        """
        Log the start of model training
        
        Args:
            model_name: Name of the model
            model_type: Type of model (random_forest, xgboost, neural_network)
            dataset_version: Version of the dataset
            user_id: User performing the operation
            **hyperparameters: Model hyperparameters
        """
        operation_id = f"train_{model_name}_{int(time.time())}"
        self.operation_start_times[operation_id] = time.time()
        
        main_logger.info(
            f"Starting model training: {model_name} ({model_type})",
            extra=log_operation(
                operation='training_start',
                user_id=user_id,
                model_name=model_name,
                model_type=model_type,
                dataset_version=dataset_version,
                operation_id=operation_id,
                **hyperparameters
            )
        )
        
        # Audit log
        audit_logger.info(
            f"Model training started: {model_name} ({model_type}) on dataset {dataset_version}",
            extra={'operation': 'model_training', 'user_id': user_id}
        )
        
        return operation_id
    
    def log_training_progress(
        self,
        operation_id: str,
        model_name: str,
        epoch: int,
        total_epochs: int,
        metrics: Dict[str, float],
        user_id: str = "system"
    ):
        """
        Log training progress
        
        Args:
            operation_id: Operation identifier from start
            model_name: Name of the model
            epoch: Current epoch
            total_epochs: Total number of epochs
            metrics: Training metrics
            user_id: User performing the operation
        """
        progress_percent = (epoch / total_epochs) * 100
        
        main_logger.info(
            f"Training progress: {model_name} - Epoch {epoch}/{total_epochs} "
            f"({progress_percent:.1f}%) - Metrics: {metrics}",
            extra=log_operation(
                operation='training_progress',
                user_id=user_id,
                model_name=model_name,
                epoch=epoch,
                total_epochs=total_epochs,
                progress_percent=progress_percent,
                operation_id=operation_id,
                **metrics
            )
        )
    
    def log_training_complete(
        self,
        operation_id: str,
        model_name: str,
        model_version: str,
        metrics: Dict[str, float],
        user_id: str = "system",
        **metadata
    ):
        """
        Log the completion of model training
        
        Args:
            operation_id: Operation identifier from start
            model_name: Name of the model
            model_version: Version of the trained model
            metrics: Final evaluation metrics
            user_id: User performing the operation
            **metadata: Additional metadata
        """
        duration = None
        if operation_id in self.operation_start_times:
            duration = time.time() - self.operation_start_times[operation_id]
            del self.operation_start_times[operation_id]
        
        main_logger.info(
            f"Training completed: {model_name} v{model_version} - "
            f"Duration: {duration:.2f}s - Metrics: {metrics}" if duration 
            else f"Training completed: {model_name} v{model_version}",
            extra=log_operation(
                operation='training_complete',
                user_id=user_id,
                model_name=model_name,
                model_version=model_version,
                duration_seconds=duration,
                operation_id=operation_id,
                **metrics,
                **metadata
            )
        )
        
        # Audit log
        audit_logger.info(
            f"Model training completed: {model_name} v{model_version} - "
            f"AUC-ROC: {metrics.get('roc_auc', 'N/A')}",
            extra={'operation': 'model_training', 'user_id': user_id}
        )
    
    def log_training_error(
        self,
        operation_id: str,
        model_name: str,
        error: str,
        user_id: str = "system",
        **metadata
    ):
        """
        Log a training error
        
        Args:
            operation_id: Operation identifier from start
            model_name: Name of the model
            error: Error message
            user_id: User performing the operation
            **metadata: Additional metadata
        """
        duration = None
        if operation_id in self.operation_start_times:
            duration = time.time() - self.operation_start_times[operation_id]
            del self.operation_start_times[operation_id]
        
        main_logger.error(
            f"Training failed: {model_name} - {error}",
            extra=log_operation(
                operation='training_error',
                user_id=user_id,
                model_name=model_name,
                error=error,
                duration_seconds=duration,
                operation_id=operation_id,
                **metadata
            )
        )
        
        # Audit log
        audit_logger.error(
            f"Model training failed: {model_name} - {error}",
            extra={'operation': 'model_training', 'user_id': user_id}
        )
    
    def log_feature_extraction(
        self,
        dataset_name: str,
        num_features: int,
        num_records: int,
        duration_seconds: float,
        user_id: str = "system"
    ):
        """
        Log feature extraction operation
        
        Args:
            dataset_name: Name of the dataset
            num_features: Number of features extracted
            num_records: Number of records processed
            duration_seconds: Time taken
            user_id: User performing the operation
        """
        main_logger.info(
            f"Feature extraction completed: {dataset_name} - "
            f"{num_features} features from {num_records} records in {duration_seconds:.2f}s",
            extra=log_operation(
                operation='feature_extraction',
                user_id=user_id,
                dataset_name=dataset_name,
                num_features=num_features,
                num_records=num_records,
                duration_seconds=duration_seconds
            )
        )
        
        # Audit log
        audit_logger.info(
            f"Feature extraction: {dataset_name} - {num_features} features",
            extra={'operation': 'feature_extraction', 'user_id': user_id}
        )
    
    def log_model_deployment(
        self,
        model_name: str,
        model_version: str,
        environment: str,
        user_id: str = "system"
    ):
        """
        Log model deployment
        
        Args:
            model_name: Name of the model
            model_version: Version being deployed
            environment: Deployment environment (production, staging)
            user_id: User performing the operation
        """
        main_logger.info(
            f"Model deployed: {model_name} v{model_version} to {environment}",
            extra=log_operation(
                operation='model_deployment',
                user_id=user_id,
                model_name=model_name,
                model_version=model_version,
                environment=environment
            )
        )
        
        # Audit log
        audit_logger.info(
            f"Model deployed: {model_name} v{model_version} to {environment}",
            extra={'operation': 'model_deployment', 'user_id': user_id}
        )
    
    def log_data_access(
        self,
        dataset_name: str,
        access_type: str,
        user_id: str,
        records_accessed: Optional[int] = None
    ):
        """
        Log data access for audit purposes
        
        Args:
            dataset_name: Name of the dataset accessed
            access_type: Type of access (read, write, delete)
            user_id: User accessing the data
            records_accessed: Number of records accessed
        """
        message = f"Data access: {dataset_name} - {access_type}"
        if records_accessed:
            message += f" - {records_accessed} records"
        
        # Audit log only (sensitive operation)
        audit_logger.info(
            message,
            extra={
                'operation': 'data_access',
                'user_id': user_id,
                'dataset_name': dataset_name,
                'access_type': access_type,
                'records_accessed': records_accessed
            }
        )


# Global operation logger instance
operation_logger = OperationLogger()


def log_operation_decorator(operation_type: str):
    """
    Decorator to automatically log operations
    
    Args:
        operation_type: Type of operation (data_ingestion, training, etc.)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract operation name from function
            operation_name = func.__name__
            
            main_logger.info(
                f"Starting operation: {operation_name}",
                extra=log_operation(
                    operation=operation_type,
                    user_id='system',
                    function=operation_name
                )
            )
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                main_logger.info(
                    f"Operation completed: {operation_name} in {duration:.2f}s",
                    extra=log_operation(
                        operation=operation_type,
                        user_id='system',
                        function=operation_name,
                        duration_seconds=duration,
                        status='success'
                    )
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                main_logger.error(
                    f"Operation failed: {operation_name} after {duration:.2f}s - {str(e)}",
                    extra=log_operation(
                        operation=operation_type,
                        user_id='system',
                        function=operation_name,
                        duration_seconds=duration,
                        status='error',
                        error=str(e)
                    )
                )
                raise
        
        return wrapper
    return decorator
