"""
Model Registry for versioning and managing ML models

This module provides a centralized registry for storing, versioning, and
managing machine learning models with their metadata and artifacts.
"""
import os
import uuid
import joblib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ml_pipeline.data_storage.database import get_db_context as get_db_session
from ml_pipeline.data_storage.models import ModelVersion, TrainingJob, AuditLog
from ml_pipeline.config.logging_config import main_logger as logger


class ModelRegistry:
    """
    Centralized registry for model versioning and deployment management
    
    Provides functionality for:
    - Generating unique version identifiers
    - Storing model artifacts with versions
    - Tracking model metadata and performance metrics
    - Managing production deployments
    - Comparing model versions
    - Rolling back to previous versions
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the model registry
        
        Args:
            storage_path: Base path for storing model artifacts
        """
        self.storage_path = Path(storage_path or os.getenv(
            'MODEL_REGISTRY_PATH', 
            'ml_pipeline/data_storage/models'
        ))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Model registry initialized with storage path: {self.storage_path}")
    
    def _generate_version_id(self) -> str:
        """
        Generate a unique version identifier
        
        Format: v{timestamp}_{uuid}
        Example: v20250126_a1b2c3d4
        
        Returns:
            Unique version identifier string
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        version_id = f"v{timestamp}_{unique_id}"
        logger.debug(f"Generated version ID: {version_id}")
        return version_id
    
    def register_model(
        self,
        model: Any,
        model_name: str,
        model_type: str,
        metrics: Dict[str, float],
        dataset_version: str,
        hyperparameters: Dict[str, Any],
        feature_names: List[str] = None,
        training_duration: float = None,
        n_training_samples: int = None,
        n_validation_samples: int = None,
        n_test_samples: int = None,
        notes: str = None,
        user_id: str = "system"
    ) -> str:
        """
        Register a new model version with automatic versioning
        
        Args:
            model: Trained model object (sklearn, xgboost, keras, etc.)
            model_name: Name of the model (e.g., 'random_forest', 'xgboost')
            model_type: Type of model (e.g., 'random_forest', 'xgboost', 'neural_network')
            metrics: Dictionary of performance metrics
            dataset_version: Version of the dataset used for training
            hyperparameters: Model hyperparameters
            feature_names: List of feature names used
            training_duration: Training time in seconds
            n_training_samples: Number of training samples
            n_validation_samples: Number of validation samples
            n_test_samples: Number of test samples
            notes: Additional notes about the model
            user_id: User who registered the model
        
        Returns:
            version_id: Unique version identifier for the registered model
        """
        start_time = datetime.utcnow()
        
        # Generate unique version ID
        version_id = self._generate_version_id()
        
        # Create model directory
        model_dir = self.storage_path / model_name / version_id
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model artifact
        artifact_path = model_dir / 'model.pkl'
        try:
            joblib.dump(model, artifact_path)
            logger.info(f"Model artifact saved to {artifact_path}")
        except Exception as e:
            logger.error(f"Failed to save model artifact: {e}")
            raise
        
        # Save hyperparameters as JSON
        hyperparams_path = model_dir / 'hyperparameters.json'
        with open(hyperparams_path, 'w') as f:
            json.dump(hyperparameters, f, indent=2)
        
        # Save feature names if provided
        if feature_names:
            features_path = model_dir / 'features.json'
            with open(features_path, 'w') as f:
                json.dump(feature_names, f, indent=2)
        
        # Store metadata in database
        with get_db_session() as db:
            model_version = ModelVersion(
                version_id=version_id,
                model_name=model_name,
                model_type=model_type,
                created_at=datetime.utcnow(),
                accuracy=metrics.get('accuracy'),
                balanced_accuracy=metrics.get('balanced_accuracy'),
                precision=metrics.get('precision'),
                recall=metrics.get('recall'),
                f1_score=metrics.get('f1_score'),
                roc_auc=metrics.get('roc_auc'),
                pr_auc=metrics.get('pr_auc'),
                dataset_version=dataset_version,
                n_training_samples=n_training_samples,
                n_validation_samples=n_validation_samples,
                n_test_samples=n_test_samples,
                hyperparameters=hyperparameters,
                feature_names=feature_names,
                status='registered',
                artifact_path=str(artifact_path),
                training_duration_seconds=training_duration,
                notes=notes
            )
            
            db.add(model_version)
            
            # Create audit log entry
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                operation='register_model',
                user_id=user_id,
                resource_type='model',
                resource_id=version_id,
                action='create',
                details={
                    'model_name': model_name,
                    'model_type': model_type,
                    'metrics': metrics,
                    'dataset_version': dataset_version
                },
                success=True
            )
            db.add(audit_log)
            
            db.commit()
            
            logger.info(
                f"Model registered successfully: {model_name} v{version_id} "
                f"with ROC-AUC: {metrics.get('roc_auc', 'N/A')}"
            )
        
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Model registration completed in {elapsed_time:.2f} seconds")
        
        return version_id
    
    def get_model_version(
        self, 
        model_name: str, 
        version_id: str = None
    ) -> Optional[ModelVersion]:
        """
        Get a specific model version or the production version
        
        Args:
            model_name: Name of the model
            version_id: Specific version ID (if None, returns production version)
        
        Returns:
            ModelVersion object or None if not found
        """
        with get_db_session() as db:
            if version_id:
                model_version = db.query(ModelVersion).filter(
                    ModelVersion.version_id == version_id
                ).first()
            else:
                # Get production version
                model_version = db.query(ModelVersion).filter(
                    ModelVersion.model_name == model_name,
                    ModelVersion.status == 'production'
                ).first()
            
            if model_version:
                # Detach from session to avoid lazy loading issues
                db.expunge(model_version)
            
            return model_version
    
    def load_model(
        self, 
        model_name: str, 
        version_id: str = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Load a model and its metadata
        
        Args:
            model_name: Name of the model
            version_id: Specific version ID (if None, loads production version)
        
        Returns:
            Tuple of (model object, metadata dict)
        """
        model_version = self.get_model_version(model_name, version_id)
        
        if not model_version:
            raise ValueError(
                f"Model not found: {model_name}" + 
                (f" version {version_id}" if version_id else " (production)")
            )
        
        # Load model artifact
        artifact_path = Path(model_version.artifact_path)
        if not artifact_path.exists():
            raise FileNotFoundError(f"Model artifact not found: {artifact_path}")
        
        model = joblib.load(artifact_path)
        
        # Prepare metadata
        metadata = {
            'version_id': model_version.version_id,
            'model_name': model_version.model_name,
            'model_type': model_version.model_type,
            'created_at': model_version.created_at,
            'metrics': {
                'accuracy': model_version.accuracy,
                'balanced_accuracy': model_version.balanced_accuracy,
                'precision': model_version.precision,
                'recall': model_version.recall,
                'f1_score': model_version.f1_score,
                'roc_auc': model_version.roc_auc,
                'pr_auc': model_version.pr_auc
            },
            'dataset_version': model_version.dataset_version,
            'hyperparameters': model_version.hyperparameters,
            'feature_names': model_version.feature_names,
            'status': model_version.status
        }
        
        logger.info(f"Loaded model: {model_name} v{model_version.version_id}")
        
        return model, metadata
    
    def list_versions(
        self, 
        model_name: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List all versions of a model
        
        Args:
            model_name: Name of the model
            limit: Maximum number of versions to return
        
        Returns:
            List of version metadata dictionaries
        """
        with get_db_session() as db:
            versions = db.query(ModelVersion).filter(
                ModelVersion.model_name == model_name
            ).order_by(
                desc(ModelVersion.created_at)
            ).limit(limit).all()
            
            version_list = []
            for v in versions:
                version_list.append({
                    'version_id': v.version_id,
                    'model_type': v.model_type,
                    'created_at': v.created_at.isoformat() if v.created_at else None,
                    'status': v.status,
                    'roc_auc': v.roc_auc,
                    'accuracy': v.accuracy,
                    'dataset_version': v.dataset_version
                })
            
            return version_list
    
    def list_all_models(self) -> List[str]:
        """
        List all unique model names in the registry
        
        Returns:
            List of model names
        """
        with get_db_session() as db:
            models = db.query(ModelVersion.model_name).distinct().all()
            return [m[0] for m in models]

    def compare_versions(
        self, 
        model_name: str, 
        version_ids: List[str] = None,
        metric: str = 'roc_auc'
    ) -> List[Dict[str, Any]]:
        """
        Compare metrics across model versions
        
        Args:
            model_name: Name of the model
            version_ids: List of specific version IDs to compare (if None, compares all)
            metric: Primary metric to sort by
        
        Returns:
            List of version comparisons sorted by the specified metric
        """
        with get_db_session() as db:
            query = db.query(ModelVersion).filter(
                ModelVersion.model_name == model_name
            )
            
            if version_ids:
                query = query.filter(ModelVersion.version_id.in_(version_ids))
            
            versions = query.all()
            
            comparisons = []
            for v in versions:
                comparison = {
                    'version_id': v.version_id,
                    'model_type': v.model_type,
                    'created_at': v.created_at.isoformat() if v.created_at else None,
                    'status': v.status,
                    'metrics': {
                        'accuracy': v.accuracy,
                        'balanced_accuracy': v.balanced_accuracy,
                        'precision': v.precision,
                        'recall': v.recall,
                        'f1_score': v.f1_score,
                        'roc_auc': v.roc_auc,
                        'pr_auc': v.pr_auc
                    },
                    'dataset_version': v.dataset_version,
                    'n_training_samples': v.n_training_samples,
                    'training_duration_seconds': v.training_duration_seconds
                }
                comparisons.append(comparison)
            
            # Sort by specified metric (descending)
            comparisons.sort(
                key=lambda x: x['metrics'].get(metric, 0) or 0, 
                reverse=True
            )
            
            logger.info(
                f"Compared {len(comparisons)} versions of {model_name} "
                f"sorted by {metric}"
            )
            
            return comparisons
    
    def promote_to_production(
        self, 
        model_name: str, 
        version_id: str,
        user_id: str = "system"
    ) -> bool:
        """
        Promote a model version to production
        
        This will:
        1. Set the specified version status to 'production'
        2. Demote the current production version to 'archived'
        3. Record deployment timestamp
        4. Create audit log entry
        
        Args:
            model_name: Name of the model
            version_id: Version ID to promote
            user_id: User performing the promotion
        
        Returns:
            True if successful, False otherwise
        """
        with get_db_session() as db:
            # Get the version to promote
            new_prod = db.query(ModelVersion).filter(
                ModelVersion.version_id == version_id
            ).first()
            
            if not new_prod:
                logger.error(f"Version not found: {version_id}")
                return False
            
            if new_prod.model_name != model_name:
                logger.error(
                    f"Version {version_id} does not belong to model {model_name}"
                )
                return False
            
            # Demote current production version
            current_prod = db.query(ModelVersion).filter(
                ModelVersion.model_name == model_name,
                ModelVersion.status == 'production'
            ).first()
            
            if current_prod:
                current_prod.status = 'archived'
                logger.info(
                    f"Demoted previous production version: {current_prod.version_id}"
                )
            
            # Promote new version
            new_prod.status = 'production'
            new_prod.deployed_at = datetime.utcnow()
            
            # Create audit log
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                operation='promote_model',
                user_id=user_id,
                resource_type='model',
                resource_id=version_id,
                action='deploy',
                details={
                    'model_name': model_name,
                    'previous_production': current_prod.version_id if current_prod else None,
                    'new_production': version_id
                },
                success=True
            )
            db.add(audit_log)
            
            db.commit()
            
            logger.info(
                f"Promoted {model_name} v{version_id} to production"
            )
            
            return True
    
    def rollback_to_version(
        self, 
        model_name: str, 
        version_id: str,
        user_id: str = "system"
    ) -> bool:
        """
        Rollback to a previous model version
        
        This is essentially promoting an archived version back to production
        
        Args:
            model_name: Name of the model
            version_id: Version ID to rollback to
            user_id: User performing the rollback
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Rolling back {model_name} to version {version_id}")
        return self.promote_to_production(model_name, version_id, user_id)
    
    def get_production_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the currently deployed production model
        
        Args:
            model_name: Name of the model
        
        Returns:
            Dictionary with production model metadata or None
        """
        model_version = self.get_model_version(model_name, version_id=None)
        
        if not model_version:
            return None
        
        return {
            'version_id': model_version.version_id,
            'model_name': model_version.model_name,
            'model_type': model_version.model_type,
            'deployed_at': model_version.deployed_at.isoformat() if model_version.deployed_at else None,
            'metrics': {
                'accuracy': model_version.accuracy,
                'balanced_accuracy': model_version.balanced_accuracy,
                'precision': model_version.precision,
                'recall': model_version.recall,
                'f1_score': model_version.f1_score,
                'roc_auc': model_version.roc_auc,
                'pr_auc': model_version.pr_auc
            },
            'dataset_version': model_version.dataset_version,
            'artifact_path': model_version.artifact_path
        }
    
    def get_deployment_history(
        self, 
        model_name: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get deployment history for a model
        
        Args:
            model_name: Name of the model
            limit: Maximum number of deployments to return
        
        Returns:
            List of deployment records
        """
        with get_db_session() as db:
            # Query audit logs for deployment actions
            deployments = db.query(AuditLog).filter(
                AuditLog.operation == 'promote_model',
                AuditLog.resource_type == 'model',
                AuditLog.details['model_name'].astext == model_name
            ).order_by(
                desc(AuditLog.timestamp)
            ).limit(limit).all()
            
            history = []
            for d in deployments:
                history.append({
                    'timestamp': d.timestamp.isoformat() if d.timestamp else None,
                    'version_id': d.details.get('new_production'),
                    'previous_version': d.details.get('previous_production'),
                    'user_id': d.user_id,
                    'success': d.success
                })
            
            return history
    
    def delete_version(
        self, 
        version_id: str,
        user_id: str = "system"
    ) -> bool:
        """
        Delete a model version (only if not in production)
        
        Args:
            version_id: Version ID to delete
            user_id: User performing the deletion
        
        Returns:
            True if successful, False otherwise
        """
        with get_db_session() as db:
            model_version = db.query(ModelVersion).filter(
                ModelVersion.version_id == version_id
            ).first()
            
            if not model_version:
                logger.error(f"Version not found: {version_id}")
                return False
            
            if model_version.status == 'production':
                logger.error(
                    f"Cannot delete production version: {version_id}. "
                    "Demote it first."
                )
                return False
            
            # Delete artifact files
            artifact_path = Path(model_version.artifact_path)
            if artifact_path.exists():
                artifact_path.unlink()
                # Delete parent directory if empty
                model_dir = artifact_path.parent
                if model_dir.exists() and not any(model_dir.iterdir()):
                    model_dir.rmdir()
            
            # Create audit log
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                operation='delete_model',
                user_id=user_id,
                resource_type='model',
                resource_id=version_id,
                action='delete',
                details={
                    'model_name': model_version.model_name,
                    'version_id': version_id
                },
                success=True
            )
            db.add(audit_log)
            
            # Delete from database
            db.delete(model_version)
            db.commit()
            
            logger.info(f"Deleted model version: {version_id}")
            
            return True
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics about the model registry
        
        Returns:
            Dictionary with registry statistics
        """
        with get_db_session() as db:
            total_models = db.query(ModelVersion.model_name).distinct().count()
            total_versions = db.query(ModelVersion).count()
            production_models = db.query(ModelVersion).filter(
                ModelVersion.status == 'production'
            ).count()
            
            # Get average metrics for production models
            prod_models = db.query(ModelVersion).filter(
                ModelVersion.status == 'production'
            ).all()
            
            avg_metrics = {
                'accuracy': 0,
                'roc_auc': 0,
                'f1_score': 0
            }
            
            if prod_models:
                for metric in avg_metrics.keys():
                    values = [getattr(m, metric) for m in prod_models if getattr(m, metric) is not None]
                    avg_metrics[metric] = sum(values) / len(values) if values else 0
            
            return {
                'total_models': total_models,
                'total_versions': total_versions,
                'production_models': production_models,
                'archived_models': total_versions - production_models,
                'average_production_metrics': avg_metrics
            }
