"""
Model Promoter

This module handles the logic for promoting models to production based on
performance improvements and other criteria.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import get_logger
from ml_pipeline.models.model_registry import ModelRegistry
from ml_pipeline.data_storage.database import get_db_session
from ml_pipeline.data_storage.models import AuditLog

logger = get_logger(__name__)


class ModelPromoter:
    """
    Handle model promotion logic
    
    Implements:
    - Promotion if new model is 5% better (Requirement 11.5)
    - Automatic deployment decisions
    - Rollback capabilities
    """
    
    def __init__(
        self,
        improvement_threshold: float = None,
        require_approval: bool = False
    ):
        """
        Initialize model promoter
        
        Args:
            improvement_threshold: Minimum improvement required for promotion (default: 5%)
            require_approval: Whether to require manual approval before promotion
        """
        self.improvement_threshold = improvement_threshold or settings.MODEL_IMPROVEMENT_THRESHOLD
        self.require_approval = require_approval
        self.model_registry = ModelRegistry(storage_path=settings.MODELS_PATH)
        
        logger.info(
            f"Initialized ModelPromoter: "
            f"improvement_threshold={self.improvement_threshold * 100}%, "
            f"require_approval={require_approval}"
        )
    
    def promote_if_better(
        self,
        evaluation_results: Dict[str, Any],
        user_id: str = "automated_retraining"
    ) -> Dict[str, Any]:
        """
        Promote models to production if they meet improvement criteria
        
        Implements Requirement 11.5: Promote if new model is 5% better
        
        Args:
            evaluation_results: Results from AutomatedRetrainingPipeline.evaluate_new_models()
            user_id: User ID for audit logging
            
        Returns:
            Dictionary with promotion results for each model
        """
        logger.info("=" * 80)
        logger.info("Checking Models for Promotion")
        logger.info("=" * 80)
        
        if not evaluation_results.get('success'):
            logger.error("Cannot promote: evaluation failed")
            return {
                'success': False,
                'error': 'Evaluation failed'
            }
        
        promotion_results = {}
        
        model_evaluations = evaluation_results.get('model_evaluations', {})
        
        for model_name, eval_result in model_evaluations.items():
            logger.info(f"\nChecking {model_name} for promotion...")
            
            recommendation = eval_result.get('recommendation')
            
            if recommendation == 'deploy':
                # Model meets criteria for automatic deployment
                promotion_result = self._promote_model(
                    model_name=model_name,
                    eval_result=eval_result,
                    user_id=user_id
                )
                promotion_results[model_name] = promotion_result
                
            elif recommendation == 'manual_review':
                # Model improved but not by threshold - flag for manual review
                logger.info(
                    f"{model_name} improved but below {self.improvement_threshold * 100}% threshold. "
                    "Flagged for manual review."
                )
                promotion_results[model_name] = {
                    'promoted': False,
                    'reason': 'requires_manual_review',
                    'improvement_percent': eval_result.get('comparison', {}).get(
                        'primary_metric_improvement_percent', 0
                    )
                }
                
            else:
                # Model did not improve - do not promote
                logger.info(f"{model_name} did not improve. Not promoting.")
                promotion_results[model_name] = {
                    'promoted': False,
                    'reason': 'no_improvement'
                }
        
        # Generate summary
        summary = self._generate_promotion_summary(promotion_results)
        
        results = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'promotion_results': promotion_results,
            'summary': summary
        }
        
        logger.info("\n" + "=" * 80)
        logger.info("Promotion Summary")
        logger.info("=" * 80)
        logger.info(f"Models promoted: {summary['models_promoted']}")
        logger.info(f"Models requiring manual review: {summary['models_requiring_review']}")
        logger.info(f"Models not promoted: {summary['models_not_promoted']}")
        
        return results
    
    def _promote_model(
        self,
        model_name: str,
        eval_result: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Promote a specific model to production
        
        Args:
            model_name: Name of the model
            eval_result: Evaluation result for the model
            user_id: User ID for audit logging
            
        Returns:
            Dictionary with promotion result
        """
        try:
            # Get the new model version from registration results
            # We need to find the latest registered version for this model
            versions = self.model_registry.list_versions(model_name, limit=5)
            
            if not versions:
                logger.error(f"No versions found for {model_name}")
                return {
                    'promoted': False,
                    'error': 'No versions found'
                }
            
            # Get the most recent version (should be the newly trained one)
            new_version_id = versions[0]['version_id']
            
            # Check if this version is already in production
            if versions[0]['status'] == 'production':
                logger.warning(f"{model_name} v{new_version_id} is already in production")
                return {
                    'promoted': False,
                    'reason': 'already_in_production',
                    'version_id': new_version_id
                }
            
            # Promote to production
            success = self.model_registry.promote_to_production(
                model_name=model_name,
                version_id=new_version_id,
                user_id=user_id
            )
            
            if success:
                logger.info(f"Successfully promoted {model_name} v{new_version_id} to production")
                
                # Log promotion details
                comparison = eval_result.get('comparison', {})
                improvement_pct = comparison.get('primary_metric_improvement_percent', 0)
                
                return {
                    'promoted': True,
                    'version_id': new_version_id,
                    'previous_version': eval_result.get('production_version'),
                    'improvement_percent': improvement_pct,
                    'new_metrics': eval_result.get('new_metrics'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to promote {model_name} v{new_version_id}")
                return {
                    'promoted': False,
                    'error': 'Promotion failed',
                    'version_id': new_version_id
                }
                
        except Exception as e:
            logger.error(f"Error promoting {model_name}: {e}", exc_info=True)
            return {
                'promoted': False,
                'error': str(e)
            }
    
    def rollback_model(
        self,
        model_name: str,
        target_version_id: Optional[str] = None,
        user_id: str = "manual"
    ) -> Dict[str, Any]:
        """
        Rollback a model to a previous version
        
        Args:
            model_name: Name of the model
            target_version_id: Specific version to rollback to (if None, uses previous production)
            user_id: User ID for audit logging
            
        Returns:
            Dictionary with rollback result
        """
        logger.info(f"Rolling back {model_name}...")
        
        try:
            if target_version_id is None:
                # Get deployment history to find previous production version
                history = self.model_registry.get_deployment_history(model_name, limit=5)
                
                if len(history) < 2:
                    logger.error("No previous production version found")
                    return {
                        'success': False,
                        'error': 'No previous production version'
                    }
                
                # Get the second most recent deployment (previous production)
                target_version_id = history[1]['version_id']
            
            # Rollback
            success = self.model_registry.rollback_to_version(
                model_name=model_name,
                version_id=target_version_id,
                user_id=user_id
            )
            
            if success:
                logger.info(f"Successfully rolled back {model_name} to v{target_version_id}")
                
                return {
                    'success': True,
                    'model_name': model_name,
                    'version_id': target_version_id,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to rollback {model_name}")
                return {
                    'success': False,
                    'error': 'Rollback failed'
                }
                
        except Exception as e:
            logger.error(f"Error rolling back {model_name}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def approve_pending_promotion(
        self,
        model_name: str,
        version_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Manually approve a pending model promotion
        
        Args:
            model_name: Name of the model
            version_id: Version ID to promote
            user_id: User ID approving the promotion
            
        Returns:
            Dictionary with approval result
        """
        logger.info(f"Manually approving promotion of {model_name} v{version_id}")
        
        try:
            success = self.model_registry.promote_to_production(
                model_name=model_name,
                version_id=version_id,
                user_id=user_id
            )
            
            if success:
                logger.info(f"Successfully approved and promoted {model_name} v{version_id}")
                
                # Create audit log for manual approval
                with get_db_session() as db:
                    audit_log = AuditLog(
                        timestamp=datetime.now(),
                        operation='manual_promotion_approval',
                        user_id=user_id,
                        resource_type='model',
                        resource_id=version_id,
                        action='approve',
                        details={
                            'model_name': model_name,
                            'version_id': version_id,
                            'approval_type': 'manual'
                        },
                        success=True
                    )
                    db.add(audit_log)
                    db.commit()
                
                return {
                    'success': True,
                    'model_name': model_name,
                    'version_id': version_id,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to approve promotion of {model_name}")
                return {
                    'success': False,
                    'error': 'Promotion failed'
                }
                
        except Exception as e:
            logger.error(f"Error approving promotion: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_promotion_candidates(self) -> List[Dict[str, Any]]:
        """
        Get list of models that are candidates for promotion
        
        Returns:
            List of model versions requiring manual review
        """
        # This would query a database table of pending promotions
        # For now, return empty list as placeholder
        logger.info("Getting promotion candidates...")
        
        # TODO: Implement database query for pending promotions
        # This would be populated by the evaluation process when
        # models are flagged for manual review
        
        return []
    
    def _generate_promotion_summary(
        self,
        promotion_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate summary of promotion results
        
        Args:
            promotion_results: Results from promote_if_better
            
        Returns:
            Summary dictionary
        """
        summary = {
            'models_promoted': 0,
            'models_requiring_review': 0,
            'models_not_promoted': 0,
            'promoted_models': [],
            'review_required_models': []
        }
        
        for model_name, result in promotion_results.items():
            if result.get('promoted'):
                summary['models_promoted'] += 1
                summary['promoted_models'].append({
                    'model_name': model_name,
                    'version_id': result.get('version_id'),
                    'improvement_percent': result.get('improvement_percent', 0)
                })
            elif result.get('reason') == 'requires_manual_review':
                summary['models_requiring_review'] += 1
                summary['review_required_models'].append({
                    'model_name': model_name,
                    'improvement_percent': result.get('improvement_percent', 0)
                })
            else:
                summary['models_not_promoted'] += 1
        
        return summary
    
    def check_promotion_criteria(
        self,
        model_name: str,
        new_metrics: Dict[str, float],
        production_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Check if a model meets promotion criteria
        
        Args:
            model_name: Name of the model
            new_metrics: Metrics from new model
            production_metrics: Metrics from production model
            
        Returns:
            Dictionary with criteria check results
        """
        # Primary metric for comparison
        primary_metric = 'roc_auc'
        
        if primary_metric not in new_metrics or primary_metric not in production_metrics:
            return {
                'meets_criteria': False,
                'reason': f'Missing {primary_metric} metric'
            }
        
        new_value = new_metrics[primary_metric]
        prod_value = production_metrics[primary_metric]
        
        improvement = new_value - prod_value
        improvement_pct = (improvement / prod_value) * 100 if prod_value > 0 else 0
        
        meets_criteria = improvement_pct >= (self.improvement_threshold * 100)
        
        return {
            'meets_criteria': meets_criteria,
            'primary_metric': primary_metric,
            'new_value': new_value,
            'production_value': prod_value,
            'improvement': improvement,
            'improvement_percent': improvement_pct,
            'threshold_percent': self.improvement_threshold * 100,
            'recommendation': 'promote' if meets_criteria else 'do_not_promote'
        }
