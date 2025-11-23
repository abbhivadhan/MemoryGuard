"""
Model registry for managing trained ML model versions.

This module provides functionality for:
- Registering new model versions
- Loading specific model versions
- Comparing model performance
- Managing model lifecycle
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime
import logging
import shutil

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Registry for managing ML model versions.
    """
    
    def __init__(self, registry_dir: str = "models"):
        """
        Initialize model registry.
        
        Args:
            registry_dir: Base directory for model storage
        """
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.registry_dir / 'registry.json'
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load registry from disk."""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {
            'models': {},
            'production_version': None,
            'staging_version': None
        }
    
    def _save_registry(self) -> None:
        """Save registry to disk."""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(
        self,
        version: str,
        model_path: str,
        metrics: Dict,
        metadata: Dict = None
    ) -> None:
        """
        Register a new model version.
        
        Args:
            version: Model version identifier
            model_path: Path to model directory
            metrics: Model performance metrics
            metadata: Additional metadata
        """
        model_info = {
            'version': version,
            'path': str(model_path),
            'registered_at': datetime.now().isoformat(),
            'metrics': metrics,
            'metadata': metadata or {},
            'status': 'registered'
        }
        
        self.registry['models'][version] = model_info
        self._save_registry()
        
        logger.info(f"Registered model version: {version}")
    
    def get_model_info(self, version: str) -> Optional[Dict]:
        """
        Get information about a specific model version.
        
        Args:
            version: Model version
            
        Returns:
            Model information dictionary or None
        """
        return self.registry['models'].get(version)
    
    def list_models(self, status: Optional[str] = None) -> List[Dict]:
        """
        List all registered models.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of model information dictionaries
        """
        models = list(self.registry['models'].values())
        
        if status:
            models = [m for m in models if m.get('status') == status]
        
        # Sort by registration date (newest first)
        models.sort(key=lambda x: x['registered_at'], reverse=True)
        
        return models
    
    def get_latest_model(self) -> Optional[Dict]:
        """
        Get the most recently registered model.
        
        Returns:
            Model information dictionary or None
        """
        models = self.list_models()
        return models[0] if models else None
    
    def get_production_model(self) -> Optional[Dict]:
        """
        Get the current production model.
        
        Returns:
            Model information dictionary or None
        """
        version = self.registry.get('production_version')
        if version:
            return self.get_model_info(version)
        return None
    
    def get_staging_model(self) -> Optional[Dict]:
        """
        Get the current staging model.
        
        Returns:
            Model information dictionary or None
        """
        version = self.registry.get('staging_version')
        if version:
            return self.get_model_info(version)
        return None
    
    def promote_to_staging(self, version: str) -> None:
        """
        Promote a model version to staging.
        
        Args:
            version: Model version to promote
        """
        if version not in self.registry['models']:
            raise ValueError(f"Model version {version} not found")
        
        # Update previous staging model
        prev_staging = self.registry.get('staging_version')
        if prev_staging and prev_staging in self.registry['models']:
            self.registry['models'][prev_staging]['status'] = 'registered'
        
        # Promote new model
        self.registry['staging_version'] = version
        self.registry['models'][version]['status'] = 'staging'
        self.registry['models'][version]['promoted_to_staging_at'] = datetime.now().isoformat()
        
        self._save_registry()
        
        logger.info(f"Promoted model {version} to staging")
    
    def promote_to_production(self, version: str) -> None:
        """
        Promote a model version to production.
        
        Args:
            version: Model version to promote
        """
        if version not in self.registry['models']:
            raise ValueError(f"Model version {version} not found")
        
        # Update previous production model
        prev_production = self.registry.get('production_version')
        if prev_production and prev_production in self.registry['models']:
            self.registry['models'][prev_production]['status'] = 'archived'
            self.registry['models'][prev_production]['archived_at'] = datetime.now().isoformat()
        
        # Promote new model
        self.registry['production_version'] = version
        self.registry['models'][version]['status'] = 'production'
        self.registry['models'][version]['promoted_to_production_at'] = datetime.now().isoformat()
        
        self._save_registry()
        
        logger.info(f"Promoted model {version} to production")
    
    def rollback_production(self) -> Optional[str]:
        """
        Rollback to previous production model.
        
        Returns:
            Version of rolled back model or None
        """
        # Find most recent archived model
        archived_models = [
            m for m in self.registry['models'].values()
            if m.get('status') == 'archived'
        ]
        
        if not archived_models:
            logger.warning("No archived models available for rollback")
            return None
        
        # Sort by archived date
        archived_models.sort(
            key=lambda x: x.get('archived_at', ''),
            reverse=True
        )
        
        rollback_version = archived_models[0]['version']
        
        # Demote current production
        current_production = self.registry.get('production_version')
        if current_production and current_production in self.registry['models']:
            self.registry['models'][current_production]['status'] = 'registered'
        
        # Promote rollback version
        self.registry['production_version'] = rollback_version
        self.registry['models'][rollback_version]['status'] = 'production'
        self.registry['models'][rollback_version]['rolled_back_at'] = datetime.now().isoformat()
        
        self._save_registry()
        
        logger.info(f"Rolled back to model version: {rollback_version}")
        
        return rollback_version
    
    def compare_models(self, version1: str, version2: str) -> Dict:
        """
        Compare metrics between two model versions.
        
        Args:
            version1: First model version
            version2: Second model version
            
        Returns:
            Dictionary with comparison results
        """
        model1 = self.get_model_info(version1)
        model2 = self.get_model_info(version2)
        
        if not model1 or not model2:
            raise ValueError("One or both model versions not found")
        
        metrics1 = model1.get('metrics', {})
        metrics2 = model2.get('metrics', {})
        
        comparison = {
            'version1': version1,
            'version2': version2,
            'metrics_comparison': {}
        }
        
        # Compare common metrics
        common_metrics = set(metrics1.keys()) & set(metrics2.keys())
        
        for metric in common_metrics:
            val1 = metrics1[metric]
            val2 = metrics2[metric]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                diff = val2 - val1
                pct_change = (diff / val1 * 100) if val1 != 0 else 0
                
                comparison['metrics_comparison'][metric] = {
                    'version1_value': val1,
                    'version2_value': val2,
                    'difference': diff,
                    'percent_change': pct_change,
                    'improved': diff > 0 if metric != 'loss' else diff < 0
                }
        
        return comparison
    
    def delete_model(self, version: str, delete_files: bool = False) -> None:
        """
        Delete a model version from registry.
        
        Args:
            version: Model version to delete
            delete_files: Whether to delete model files from disk
        """
        if version not in self.registry['models']:
            raise ValueError(f"Model version {version} not found")
        
        # Prevent deletion of production/staging models
        if self.registry.get('production_version') == version:
            raise ValueError("Cannot delete production model")
        if self.registry.get('staging_version') == version:
            raise ValueError("Cannot delete staging model")
        
        model_info = self.registry['models'][version]
        
        # Delete files if requested
        if delete_files:
            model_path = Path(model_info['path'])
            if model_path.exists():
                shutil.rmtree(model_path)
                logger.info(f"Deleted model files at {model_path}")
        
        # Remove from registry
        del self.registry['models'][version]
        self._save_registry()
        
        logger.info(f"Deleted model version: {version}")
    
    def get_model_path(self, version: str) -> Optional[str]:
        """
        Get the file path for a model version.
        
        Args:
            version: Model version
            
        Returns:
            Path to model directory or None
        """
        model_info = self.get_model_info(version)
        if model_info:
            return model_info['path']
        return None
    
    def export_registry(self, output_path: str) -> None:
        """
        Export registry to a file.
        
        Args:
            output_path: Path to export file
        """
        with open(output_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
        
        logger.info(f"Registry exported to {output_path}")
    
    def get_registry_summary(self) -> Dict:
        """
        Get a summary of the registry.
        
        Returns:
            Dictionary with registry statistics
        """
        models = self.registry['models']
        
        summary = {
            'total_models': len(models),
            'production_version': self.registry.get('production_version'),
            'staging_version': self.registry.get('staging_version'),
            'status_counts': {},
            'latest_model': None
        }
        
        # Count by status
        for model in models.values():
            status = model.get('status', 'unknown')
            summary['status_counts'][status] = summary['status_counts'].get(status, 0) + 1
        
        # Get latest model
        latest = self.get_latest_model()
        if latest:
            summary['latest_model'] = {
                'version': latest['version'],
                'registered_at': latest['registered_at'],
                'status': latest['status']
            }
        
        return summary


# Singleton instance
_registry_instance = None


def get_model_registry(registry_dir: str = "models") -> ModelRegistry:
    """
    Get the global model registry instance.
    
    Args:
        registry_dir: Base directory for model storage
        
    Returns:
        ModelRegistry instance
    """
    global _registry_instance
    
    if _registry_instance is None:
        _registry_instance = ModelRegistry(registry_dir)
    
    return _registry_instance
