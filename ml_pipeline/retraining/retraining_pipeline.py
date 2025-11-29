"""
Automated Retraining Pipeline

This module orchestrates the complete automated retraining workflow including:
- Loading new data
- Retraining all models
- Evaluating new models against production
- Managing the retraining process
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import get_logger
from ml_pipeline.training.training_pipeline import MLTrainingPipeline
from ml_pipeline.models.model_registry import ModelRegistry
from ml_pipeline.training.model_evaluator import ModelEvaluator

logger = get_logger(__name__)


class AutomatedRetrainingPipeline:
    """
    Orchestrate automated model retraining
    
    Implements:
    - Automatic model retraining (Requirement 11.1, 11.2, 11.3)
    - Automatic evaluation against production (Requirement 11.4)
    """
    
    def __init__(
        self,
        feature_store_path: Path = None,
        output_dir: Path = None
    ):
        """
        Initialize automated retraining pipeline
        
        Args:
            feature_store_path: Path to feature store
            output_dir: Directory for saving retraining outputs
        """
        self.feature_store_path = feature_store_path or settings.FEATURES_PATH
        self.output_dir = output_dir or (settings.MODELS_PATH / "retraining" / datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_registry = ModelRegistry(storage_path=settings.MODELS_PATH)
        self.evaluator = ModelEvaluator(output_dir=self.output_dir / "evaluation")
        
        logger.info(f"Initialized AutomatedRetrainingPipeline")
        logger.info(f"Output directory: {self.output_dir}")
    
    def retrain_all_models(
        self,
        dataset_name: str = "train_features",
        target_column: str = "diagnosis"
    ) -> Dict[str, Any]:
        """
        Retrain all models with new data
        
        Implements Requirement 11.1: Support scheduled retraining
        
        Args:
            dataset_name: Name of the dataset in feature store
            target_column: Name of the target column
            
        Returns:
            Dictionary with retraining results for all models
        """
        logger.info("=" * 80)
        logger.info("Starting Automated Model Retraining")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # Initialize training pipeline
            training_pipeline = MLTrainingPipeline(
                feature_store_path=self.feature_store_path,
                output_dir=self.output_dir,
                random_state=settings.RANDOM_SEED
            )
            
            # Run full training pipeline
            logger.info("Running full training pipeline...")
            training_results = training_pipeline.run_full_pipeline(
                dataset_name=dataset_name,
                target_column=target_column,
                enable_gpu=True,
                save_models=True
            )
            
            # Register new models in registry
            logger.info("Registering new models in registry...")
            registration_results = self._register_new_models(
                training_pipeline,
                training_results
            )
            
            elapsed_time = time.time() - start_time
            
            results = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'elapsed_time_seconds': elapsed_time,
                'training_results': training_results,
                'registration_results': registration_results,
                'output_dir': str(self.output_dir)
            }
            
            logger.info(f"Retraining completed successfully in {elapsed_time:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during retraining: {e}", exc_info=True)
            
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'output_dir': str(self.output_dir)
            }
    
    def evaluate_new_models(
        self,
        retraining_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate new models against current production models
        
        Implements Requirement 11.4: Automatically evaluate new models vs current production
        
        Args:
            retraining_results: Results from retrain_all_models()
            
        Returns:
            Dictionary with evaluation results comparing new vs production models
        """
        logger.info("=" * 80)
        logger.info("Evaluating New Models vs Production")
        logger.info("=" * 80)
        
        if not retraining_results.get('success'):
            logger.error("Cannot evaluate: retraining failed")
            return {
                'success': False,
                'error': 'Retraining failed'
            }
        
        try:
            evaluation_results = {}
            
            # Get model names
            model_names = ['random_forest', 'xgboost', 'neural_network', 'ensemble']
            
            for model_name in model_names:
                logger.info(f"\nEvaluating {model_name}...")
                
                # Get new model metrics
                new_metrics = self._extract_model_metrics(
                    retraining_results,
                    model_name
                )
                
                if not new_metrics:
                    logger.warning(f"No metrics found for new {model_name}")
                    continue
                
                # Get production model metrics
                prod_model_info = self.model_registry.get_production_model(model_name)
                
                if not prod_model_info:
                    logger.warning(f"No production model found for {model_name}")
                    evaluation_results[model_name] = {
                        'new_metrics': new_metrics,
                        'production_metrics': None,
                        'comparison': 'no_production_model',
                        'recommendation': 'deploy_new'
                    }
                    continue
                
                prod_metrics = prod_model_info.get('metrics', {})
                
                # Compare metrics
                comparison = self._compare_metrics(
                    new_metrics,
                    prod_metrics,
                    model_name
                )
                
                evaluation_results[model_name] = {
                    'new_metrics': new_metrics,
                    'production_metrics': prod_metrics,
                    'production_version': prod_model_info.get('version_id'),
                    'comparison': comparison,
                    'recommendation': self._get_deployment_recommendation(comparison)
                }
                
                logger.info(
                    f"{model_name} evaluation complete: "
                    f"recommendation={evaluation_results[model_name]['recommendation']}"
                )
            
            # Overall summary
            summary = self._generate_evaluation_summary(evaluation_results)
            
            results = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'model_evaluations': evaluation_results,
                'summary': summary
            }
            
            logger.info("\n" + "=" * 80)
            logger.info("Evaluation Summary")
            logger.info("=" * 80)
            logger.info(f"Models evaluated: {summary['models_evaluated']}")
            logger.info(f"Models recommended for deployment: {summary['models_recommended_for_deployment']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}", exc_info=True)
            
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _register_new_models(
        self,
        training_pipeline: MLTrainingPipeline,
        training_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Register newly trained models in the model registry
        
        Args:
            training_pipeline: Training pipeline with trained models
            training_results: Results from training
            
        Returns:
            Dictionary mapping model names to version IDs
        """
        registration_results = {}
        
        model_names = ['random_forest', 'xgboost', 'neural_network']
        
        for model_name in model_names:
            if model_name not in training_pipeline.models:
                logger.warning(f"Model {model_name} not found in training pipeline")
                continue
            
            try:
                model = training_pipeline.models[model_name]
                
                # Extract metrics
                metrics = training_results.get('models', {}).get(model_name, {})
                
                # Get hyperparameters from config
                hyperparameters = training_pipeline.config.get(model_name, {})
                
                # Register model
                version_id = self.model_registry.register_model(
                    model=model,
                    model_name=model_name,
                    model_type=model_name,
                    metrics=metrics,
                    dataset_version='latest',
                    hyperparameters=hyperparameters,
                    training_duration=training_results.get('training_time_seconds'),
                    notes='Automated retraining',
                    user_id='automated_retraining'
                )
                
                registration_results[model_name] = version_id
                
                logger.info(f"Registered {model_name} as version {version_id}")
                
            except Exception as e:
                logger.error(f"Error registering {model_name}: {e}", exc_info=True)
                registration_results[model_name] = f"error: {str(e)}"
        
        # Register ensemble if available
        if training_pipeline.ensemble:
            try:
                ensemble = training_pipeline.ensemble
                metrics = training_results.get('models', {}).get('ensemble', {})
                
                version_id = self.model_registry.register_model(
                    model=ensemble,
                    model_name='ensemble',
                    model_type='ensemble',
                    metrics=metrics,
                    dataset_version='latest',
                    hyperparameters={'weights': ensemble.weights.tolist()},
                    training_duration=training_results.get('training_time_seconds'),
                    notes='Automated retraining - ensemble',
                    user_id='automated_retraining'
                )
                
                registration_results['ensemble'] = version_id
                
                logger.info(f"Registered ensemble as version {version_id}")
                
            except Exception as e:
                logger.error(f"Error registering ensemble: {e}", exc_info=True)
                registration_results['ensemble'] = f"error: {str(e)}"
        
        return registration_results
    
    def _extract_model_metrics(
        self,
        retraining_results: Dict[str, Any],
        model_name: str
    ) -> Optional[Dict[str, float]]:
        """
        Extract metrics for a specific model from retraining results
        
        Args:
            retraining_results: Results from retraining
            model_name: Name of the model
            
        Returns:
            Dictionary of metrics or None
        """
        try:
            training_results = retraining_results.get('training_results', {})
            models = training_results.get('models', {})
            
            if model_name in models:
                return models[model_name]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting metrics for {model_name}: {e}")
            return None
    
    def _compare_metrics(
        self,
        new_metrics: Dict[str, float],
        prod_metrics: Dict[str, float],
        model_name: str
    ) -> Dict[str, Any]:
        """
        Compare new model metrics against production model metrics
        
        Args:
            new_metrics: Metrics from new model
            prod_metrics: Metrics from production model
            model_name: Name of the model
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            'model_name': model_name,
            'metrics_compared': []
        }
        
        # Primary metrics to compare
        primary_metrics = ['roc_auc', 'accuracy', 'f1_score', 'balanced_accuracy']
        
        for metric in primary_metrics:
            new_value = new_metrics.get(metric)
            prod_value = prod_metrics.get(metric)
            
            if new_value is not None and prod_value is not None:
                improvement = new_value - prod_value
                improvement_pct = (improvement / prod_value) * 100 if prod_value > 0 else 0
                
                comparison['metrics_compared'].append({
                    'metric': metric,
                    'new_value': new_value,
                    'production_value': prod_value,
                    'improvement': improvement,
                    'improvement_percent': improvement_pct,
                    'better': new_value > prod_value
                })
        
        # Calculate overall improvement based on primary metric (ROC-AUC)
        if 'roc_auc' in new_metrics and 'roc_auc' in prod_metrics:
            roc_improvement = new_metrics['roc_auc'] - prod_metrics['roc_auc']
            roc_improvement_pct = (roc_improvement / prod_metrics['roc_auc']) * 100
            
            comparison['primary_metric'] = 'roc_auc'
            comparison['primary_metric_improvement'] = roc_improvement
            comparison['primary_metric_improvement_percent'] = roc_improvement_pct
            comparison['is_better'] = roc_improvement > 0
        else:
            comparison['primary_metric'] = None
            comparison['is_better'] = False
        
        return comparison
    
    def _get_deployment_recommendation(
        self,
        comparison: Dict[str, Any]
    ) -> str:
        """
        Get deployment recommendation based on comparison
        
        Implements Requirement 11.5: Promote if new model is 5% better
        
        Args:
            comparison: Comparison results from _compare_metrics
            
        Returns:
            Recommendation string: 'deploy', 'do_not_deploy', or 'manual_review'
        """
        if comparison == 'no_production_model':
            return 'deploy'
        
        # Check if primary metric improved by at least 5%
        improvement_threshold = settings.MODEL_IMPROVEMENT_THRESHOLD  # 0.05 = 5%
        
        if comparison.get('primary_metric_improvement_percent', 0) >= (improvement_threshold * 100):
            return 'deploy'
        elif comparison.get('is_better', False):
            # Improved but not by 5% - recommend manual review
            return 'manual_review'
        else:
            return 'do_not_deploy'
    
    def _generate_evaluation_summary(
        self,
        evaluation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate summary of evaluation results
        
        Args:
            evaluation_results: Results from evaluate_new_models
            
        Returns:
            Summary dictionary
        """
        summary = {
            'models_evaluated': len(evaluation_results),
            'models_recommended_for_deployment': 0,
            'models_requiring_manual_review': 0,
            'models_not_recommended': 0,
            'best_improvements': []
        }
        
        for model_name, result in evaluation_results.items():
            recommendation = result.get('recommendation')
            
            if recommendation == 'deploy':
                summary['models_recommended_for_deployment'] += 1
            elif recommendation == 'manual_review':
                summary['models_requiring_manual_review'] += 1
            elif recommendation == 'do_not_deploy':
                summary['models_not_recommended'] += 1
            
            # Track best improvements
            comparison = result.get('comparison', {})
            if isinstance(comparison, dict) and 'primary_metric_improvement_percent' in comparison:
                summary['best_improvements'].append({
                    'model_name': model_name,
                    'improvement_percent': comparison['primary_metric_improvement_percent']
                })
        
        # Sort by improvement
        summary['best_improvements'].sort(
            key=lambda x: x['improvement_percent'],
            reverse=True
        )
        
        return summary
