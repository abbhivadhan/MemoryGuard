"""
ML Training Pipeline

Main pipeline that orchestrates the complete ML training workflow including:
- Data loading and splitting
- Class imbalance handling
- Model training (Random Forest, XGBoost, Neural Network)
- Ensemble creation
- Cross-validation
- Performance optimization
"""

import logging
import time
from pathlib import Path
from typing import Dict, Optional, Any, List
import pandas as pd
import numpy as np
import joblib
import json

from .data_loader import DataLoader
from .class_balancer import ClassBalancer
from .trainers import RandomForestTrainer, XGBoostTrainer, NeuralNetworkTrainer
from .ensemble import EnsemblePredictor
from .cross_validator import CrossValidator
from .model_evaluator import ModelEvaluator

logger = logging.getLogger(__name__)


class MLTrainingPipeline:
    """
    Complete ML training pipeline for Alzheimer's Disease detection.
    
    Orchestrates data loading, preprocessing, model training, and evaluation
    with performance optimization to meet the 2-hour training requirement.
    """
    
    def __init__(
        self,
        feature_store_path: Path,
        output_dir: Path,
        config: Optional[Dict] = None,
        random_state: int = 42
    ):
        """
        Initialize ML training pipeline.
        
        Args:
            feature_store_path: Path to feature store
            output_dir: Directory for saving models and results
            config: Configuration dictionary for models
            random_state: Random seed for reproducibility
        """
        self.feature_store_path = Path(feature_store_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.random_state = random_state
        
        # Initialize components
        self.data_loader = DataLoader(feature_store_path)
        self.class_balancer = ClassBalancer(random_state=random_state)
        self.cross_validator = CrossValidator(n_splits=5, random_state=random_state)
        self.evaluator = ModelEvaluator(output_dir=output_dir / "evaluation")
        
        # Set default config if not provided
        self.config = config or self._get_default_config()
        
        # Storage for trained models and results
        self.models = {}
        self.results = {}
        self.ensemble = None
        
        logger.info("Initialized MLTrainingPipeline")
        logger.info(f"Feature store: {feature_store_path}")
        logger.info(f"Output directory: {output_dir}")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for models."""
        return {
            'random_forest': {
                'n_estimators': 200,
                'max_depth': 15,
                'min_samples_split': 10,
                'min_samples_leaf': 5,
                'n_jobs': -1
            },
            'xgboost': {
                'n_estimators': 200,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'n_jobs': -1
            },
            'neural_network': {
                'hidden_layers': [128, 64, 32],
                'dropout_rates': [0.3, 0.3, 0.2],
                'batch_size': 32,
                'epochs': 100
            }
        }
    
    def run_full_pipeline(
        self,
        dataset_name: str = "train_features",
        target_column: str = "diagnosis",
        enable_gpu: bool = True,
        save_models: bool = True
    ) -> Dict[str, Any]:
        """
        Run the complete training pipeline.
        
        This method orchestrates all steps and ensures training completes
        within 2 hours as per requirements.
        
        Args:
            dataset_name: Name of the dataset in feature store
            target_column: Name of the target column
            enable_gpu: Whether to use GPU acceleration
            save_models: Whether to save trained models
            
        Returns:
            Dictionary with all training results
        """
        start_time = time.time()
        logger.info("=" * 80)
        logger.info("Starting ML Training Pipeline")
        logger.info("=" * 80)
        
        # Configure GPU if available
        if enable_gpu:
            self._configure_gpu()
        
        # Step 1: Load and split data
        logger.info("\n[Step 1/6] Loading and splitting data")
        step_start = time.time()
        splits = self.data_loader.load_and_split(
            dataset_name=dataset_name,
            target_column=target_column
        )
        logger.info(f"Step completed in {time.time() - step_start:.2f}s")
        
        # Step 2: Handle class imbalance
        logger.info("\n[Step 2/6] Handling class imbalance")
        step_start = time.time()
        balanced_splits, class_weights = self.class_balancer.get_balanced_splits(
            splits,
            balance_train=True,
            balance_val=False
        )
        logger.info(f"Step completed in {time.time() - step_start:.2f}s")
        
        # Step 3: Train Random Forest
        logger.info("\n[Step 3/6] Training Random Forest")
        step_start = time.time()
        rf_result = self._train_random_forest(balanced_splits, class_weights)
        self.models['random_forest'] = rf_result['model']
        self.results['random_forest'] = rf_result
        logger.info(f"Step completed in {time.time() - step_start:.2f}s")
        
        # Step 4: Train XGBoost
        logger.info("\n[Step 4/6] Training XGBoost")
        step_start = time.time()
        xgb_result = self._train_xgboost(balanced_splits, class_weights)
        self.models['xgboost'] = xgb_result['model']
        self.results['xgboost'] = xgb_result
        logger.info(f"Step completed in {time.time() - step_start:.2f}s")
        
        # Step 5: Train Neural Network
        logger.info("\n[Step 5/6] Training Neural Network")
        step_start = time.time()
        nn_result = self._train_neural_network(balanced_splits)
        self.models['neural_network'] = nn_result['model']
        self.results['neural_network'] = nn_result
        logger.info(f"Step completed in {time.time() - step_start:.2f}s")
        
        # Step 6: Create ensemble
        logger.info("\n[Step 6/7] Creating ensemble predictor")
        step_start = time.time()
        ensemble_result = self._create_ensemble(splits)
        self.ensemble = ensemble_result['ensemble']
        self.results['ensemble'] = ensemble_result
        logger.info(f"Step completed in {time.time() - step_start:.2f}s")
        
        # Step 7: Comprehensive evaluation
        logger.info("\n[Step 7/7] Performing comprehensive evaluation")
        step_start = time.time()
        evaluation_results = self._evaluate_all_models(splits)
        self.results['evaluation'] = evaluation_results
        logger.info(f"Step completed in {time.time() - step_start:.2f}s")
        
        # Calculate total time
        total_time = time.time() - start_time
        logger.info("\n" + "=" * 80)
        logger.info(f"Pipeline completed in {total_time:.2f}s ({total_time/60:.2f} minutes)")
        
        # Check if within 2-hour requirement
        if total_time > 7200:  # 2 hours
            logger.warning(
                f"Training time {total_time/3600:.2f}h exceeds 2-hour requirement!"
            )
        else:
            logger.info(
                f"Training completed within requirement "
                f"({total_time/3600:.2f}h < 2h) ✓"
            )
        
        # Save models if requested
        if save_models:
            self._save_all_models()
        
        # Generate summary report
        summary = self._generate_summary(total_time)
        
        return summary
    
    def _train_random_forest(
        self,
        splits: Dict,
        class_weights: Optional[Dict]
    ) -> Dict[str, Any]:
        """Train Random Forest model."""
        config = self.config['random_forest'].copy()
        if class_weights:
            config['class_weight'] = class_weights
        
        trainer = RandomForestTrainer(**config, random_state=self.random_state)
        
        result = trainer.train(
            splits['X_train'],
            splits['y_train'],
            splits['X_val'],
            splits['y_val']
        )
        
        # Evaluate on test set
        test_metrics = trainer.evaluate(splits['X_test'], splits['y_test'])
        result['test_metrics'] = test_metrics
        
        return result
    
    def _train_xgboost(
        self,
        splits: Dict,
        class_weights: Optional[Dict]
    ) -> Dict[str, Any]:
        """Train XGBoost model."""
        config = self.config['xgboost'].copy()
        
        # Calculate scale_pos_weight if class weights provided
        if class_weights and len(class_weights) == 2:
            config['scale_pos_weight'] = class_weights[1] / class_weights[0]
        
        trainer = XGBoostTrainer(**config, random_state=self.random_state)
        
        result = trainer.train(
            splits['X_train'],
            splits['y_train'],
            splits['X_val'],
            splits['y_val'],
            early_stopping_rounds=20
        )
        
        # Evaluate on test set
        test_metrics = trainer.evaluate(splits['X_test'], splits['y_test'])
        result['test_metrics'] = test_metrics
        
        return result
    
    def _train_neural_network(self, splits: Dict) -> Dict[str, Any]:
        """Train Neural Network model."""
        config = self.config['neural_network'].copy()
        
        trainer = NeuralNetworkTrainer(**config, random_state=self.random_state)
        
        result = trainer.train(
            splits['X_train'],
            splits['y_train'],
            splits['X_val'],
            splits['y_val'],
            early_stopping_patience=15
        )
        
        # Evaluate on test set
        test_metrics = trainer.evaluate(splits['X_test'], splits['y_test'])
        result['test_metrics'] = test_metrics
        
        return result
    
    def _create_ensemble(self, splits: Dict) -> Dict[str, Any]:
        """Create ensemble predictor."""
        models = [
            self.models['random_forest'],
            self.models['xgboost'],
            self.models['neural_network']
        ]
        
        model_names = ['random_forest', 'xgboost', 'neural_network']
        
        ensemble = EnsemblePredictor(models, model_names)
        
        # Optimize weights on validation set
        ensemble.optimize_weights(
            splits['X_val'],
            splits['y_val'],
            metric='roc_auc'
        )
        
        # Evaluate ensemble
        test_metrics = ensemble.get_ensemble_metrics(
            splits['X_test'],
            splits['y_test']
        )
        
        # Get predictions with confidence
        test_proba, lower, upper = ensemble.predict_with_confidence(
            splits['X_test']
        )
        
        return {
            'ensemble': ensemble,
            'test_metrics': test_metrics,
            'weights': ensemble.weights.tolist()
        }
    
    def _configure_gpu(self):
        """Configure GPU acceleration if available."""
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            
            if gpus:
                logger.info(f"Found {len(gpus)} GPU(s)")
                # Enable memory growth to avoid OOM
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info("GPU acceleration enabled")
            else:
                logger.info("No GPU found, using CPU")
        except Exception as e:
            logger.warning(f"Error configuring GPU: {e}")
    
    def _save_all_models(self):
        """Save all trained models."""
        logger.info("\nSaving models...")
        
        models_dir = self.output_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Save Random Forest
        rf_path = models_dir / "random_forest.pkl"
        joblib.dump(self.models['random_forest'], rf_path)
        logger.info(f"Saved Random Forest to {rf_path}")
        
        # Save XGBoost
        xgb_path = models_dir / "xgboost.pkl"
        joblib.dump(self.models['xgboost'], xgb_path)
        logger.info(f"Saved XGBoost to {xgb_path}")
        
        # Save Neural Network
        nn_path = models_dir / "neural_network.h5"
        self.models['neural_network'].save(nn_path)
        logger.info(f"Saved Neural Network to {nn_path}")
        
        # Save ensemble
        ensemble_path = models_dir / "ensemble.pkl"
        joblib.dump(self.ensemble, ensemble_path)
        logger.info(f"Saved Ensemble to {ensemble_path}")
    
    def _evaluate_all_models(self, splits: Dict) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation on all trained models.
        
        Args:
            splits: Data splits dictionary
            
        Returns:
            Dictionary with evaluation results for all models
        """
        evaluation_results = {}
        
        # Evaluate each model
        for model_name in ['random_forest', 'xgboost', 'neural_network']:
            if model_name in self.models:
                logger.info(f"\nEvaluating {model_name}...")
                
                model = self.models[model_name]
                
                # Get predictions
                y_pred = model.predict(splits['X_test'])
                y_proba = model.predict_proba(splits['X_test'])[:, 1]
                
                # Calculate all metrics
                metrics = self.evaluator.calculate_classification_metrics(
                    splits['y_test'].values,
                    y_pred,
                    y_proba,
                    model_name
                )
                
                # Generate confusion matrix
                cm, cm_path = self.evaluator.generate_confusion_matrix(
                    splits['y_test'].values,
                    y_pred,
                    model_name
                )
                
                # Calculate ROC and PR curves
                curve_metrics, roc_path, pr_path = self.evaluator.calculate_roc_pr_curves(
                    splits['y_test'].values,
                    y_proba,
                    model_name
                )
                
                # Calculate calibration metrics
                cal_metrics, cal_path = self.evaluator.calculate_calibration_metrics(
                    splits['y_test'].values,
                    y_proba,
                    model_name
                )
                
                # Store results
                evaluation_results[model_name] = {
                    'metrics': {
                        **metrics,
                        'brier_score': cal_metrics['brier_score'],
                        'expected_calibration_error': cal_metrics['expected_calibration_error']
                    }
                }
        
        # Evaluate ensemble
        if self.ensemble:
            logger.info("\nEvaluating ensemble...")
            
            y_proba = self.ensemble.predict_proba(splits['X_test'])
            y_pred = (y_proba >= 0.5).astype(int)
            
            metrics = self.evaluator.calculate_classification_metrics(
                splits['y_test'].values,
                y_pred,
                y_proba,
                'ensemble'
            )
            
            cm, cm_path = self.evaluator.generate_confusion_matrix(
                splits['y_test'].values,
                y_pred,
                'ensemble'
            )
            
            curve_metrics, roc_path, pr_path = self.evaluator.calculate_roc_pr_curves(
                splits['y_test'].values,
                y_proba,
                'ensemble'
            )
            
            cal_metrics, cal_path = self.evaluator.calculate_calibration_metrics(
                splits['y_test'].values,
                y_proba,
                'ensemble'
            )
            
            evaluation_results['ensemble'] = {
                'metrics': {
                    **metrics,
                    'brier_score': cal_metrics['brier_score'],
                    'expected_calibration_error': cal_metrics['expected_calibration_error']
                }
            }
        
        # Generate performance comparison
        comparison_df, report_path = self.evaluator.generate_performance_comparison(
            evaluation_results,
            save_report=True
        )
        
        return evaluation_results
    
    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate training summary report."""
        summary = {
            'training_time_seconds': total_time,
            'training_time_minutes': total_time / 60,
            'models': {}
        }
        
        # Add model results from evaluation
        if 'evaluation' in self.results:
            for model_name, eval_result in self.results['evaluation'].items():
                summary['models'][model_name] = eval_result['metrics']
        else:
            # Fallback to test metrics if evaluation not run
            for model_name in ['random_forest', 'xgboost', 'neural_network', 'ensemble']:
                if model_name in self.results:
                    result = self.results[model_name]
                    if 'test_metrics' in result:
                        summary['models'][model_name] = result['test_metrics']
        
        # Save summary to file
        summary_path = self.output_dir / "training_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\nSummary saved to {summary_path}")
        
        # Log summary
        logger.info("\n" + "=" * 80)
        logger.info("TRAINING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total training time: {total_time/60:.2f} minutes")
        logger.info("\nTest Set Performance:")
        
        for model_name, metrics in summary['models'].items():
            logger.info(f"\n{model_name.upper()}:")
            for metric, value in metrics.items():
                logger.info(f"  {metric}: {value:.4f}")
        
        return summary
    
    def run_cross_validation(
        self,
        dataset_name: str = "train_features",
        target_column: str = "diagnosis"
    ) -> Dict[str, Any]:
        """
        Run cross-validation for all models.
        
        Args:
            dataset_name: Name of the dataset
            target_column: Target column name
            
        Returns:
            Cross-validation results
        """
        logger.info("Running cross-validation")
        
        # Load data
        X, y = self.data_loader.load_features(dataset_name, target_column)
        
        # Balance data
        X_balanced, y_balanced, _ = self.class_balancer.balance_data(
            X, y, method='auto'
        )
        
        # Define models for comparison
        from sklearn.ensemble import RandomForestClassifier
        import xgboost as xgb
        
        models_config = {
            'RandomForest': {
                'class': RandomForestClassifier,
                'params': self.config['random_forest']
            },
            'XGBoost': {
                'class': xgb.XGBClassifier,
                'params': self.config['xgboost']
            }
        }
        
        # Run comparison
        comparison_df = self.cross_validator.compare_models(
            models_config,
            X_balanced,
            y_balanced
        )
        
        # Save results
        cv_path = self.output_dir / "cross_validation_results.csv"
        comparison_df.to_csv(cv_path)
        logger.info(f"Cross-validation results saved to {cv_path}")
        
        return {
            'comparison': comparison_df,
            'best_model': self.cross_validator.get_best_model(comparison_df)
        }
