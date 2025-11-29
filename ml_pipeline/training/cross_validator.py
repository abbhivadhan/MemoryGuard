"""
Cross-Validation Module

Implements stratified k-fold cross-validation for model evaluation.
"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, balanced_accuracy_score
)

logger = logging.getLogger(__name__)


class CrossValidator:
    """
    Perform stratified k-fold cross-validation.
    
    Evaluates model performance across multiple folds to assess
    generalization and stability.
    """
    
    def __init__(self, n_splits: int = 5, random_state: int = 42):
        """
        Initialize cross-validator.
        
        Args:
            n_splits: Number of folds (default: 5 per requirements)
            random_state: Random seed for reproducibility
        """
        if n_splits < 2:
            raise ValueError("n_splits must be at least 2")
        
        self.n_splits = n_splits
        self.random_state = random_state
        self.cv = StratifiedKFold(
            n_splits=n_splits,
            shuffle=True,
            random_state=random_state
        )
        
        logger.info(f"Initialized CrossValidator with {n_splits} folds")
    
    def evaluate_model(
        self,
        model_class,
        model_params: Dict,
        X: pd.DataFrame,
        y: pd.Series,
        scoring_metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform cross-validation for a model.
        
        Args:
            model_class: Model class to instantiate
            model_params: Parameters for model initialization
            X: Feature DataFrame
            y: Target Series
            scoring_metrics: List of metrics to compute
            
        Returns:
            Dictionary with cross-validation results
        """
        if scoring_metrics is None:
            scoring_metrics = [
                'accuracy', 'balanced_accuracy', 'precision', 'recall',
                'f1_score', 'roc_auc', 'pr_auc'
            ]
        
        logger.info(f"Starting {self.n_splits}-fold cross-validation")
        logger.info(f"Dataset size: {len(X)} samples, {X.shape[1]} features")
        
        # Store results for each fold
        fold_results = []
        fold_predictions = []
        
        for fold_idx, (train_idx, val_idx) in enumerate(self.cv.split(X, y), 1):
            logger.info(f"Processing fold {fold_idx}/{self.n_splits}")
            
            # Split data
            X_train_fold = X.iloc[train_idx]
            y_train_fold = y.iloc[train_idx]
            X_val_fold = X.iloc[val_idx]
            y_val_fold = y.iloc[val_idx]
            
            logger.info(
                f"  Train: {len(X_train_fold)} samples, "
                f"Val: {len(X_val_fold)} samples"
            )
            
            # Train model
            model = model_class(**model_params)
            
            # Handle different model types
            if hasattr(model, 'fit'):
                # Check if model supports validation set (like XGBoost)
                if 'XGB' in str(model_class):
                    model.fit(
                        X_train_fold, y_train_fold,
                        eval_set=[(X_val_fold, y_val_fold)],
                        verbose=False
                    )
                else:
                    model.fit(X_train_fold, y_train_fold)
            else:
                raise ValueError(f"Model {model_class} doesn't have fit method")
            
            # Make predictions
            y_pred = model.predict(X_val_fold)
            y_proba = model.predict_proba(X_val_fold)[:, 1]
            
            # Calculate metrics
            fold_metrics = self._calculate_metrics(
                y_val_fold, y_pred, y_proba, scoring_metrics
            )
            
            fold_results.append(fold_metrics)
            fold_predictions.append({
                'y_true': y_val_fold.values,
                'y_pred': y_pred,
                'y_proba': y_proba
            })
            
            # Log fold results
            logger.info(f"  Fold {fold_idx} results:")
            for metric, value in fold_metrics.items():
                logger.info(f"    {metric}: {value:.4f}")
        
        # Aggregate results across folds
        cv_results = self._aggregate_results(fold_results, scoring_metrics)
        
        # Log summary
        logger.info("Cross-validation summary:")
        for metric in scoring_metrics:
            mean = cv_results[f'{metric}_mean']
            std = cv_results[f'{metric}_std']
            logger.info(f"  {metric}: {mean:.4f} (+/- {std:.4f})")
        
        return {
            'cv_results': cv_results,
            'fold_results': fold_results,
            'fold_predictions': fold_predictions
        }
    
    def _calculate_metrics(
        self,
        y_true: pd.Series,
        y_pred: np.ndarray,
        y_proba: np.ndarray,
        metrics: List[str]
    ) -> Dict[str, float]:
        """
        Calculate evaluation metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities
            metrics: List of metrics to calculate
            
        Returns:
            Dictionary of metric values
        """
        results = {}
        
        for metric in metrics:
            try:
                if metric == 'accuracy':
                    results[metric] = accuracy_score(y_true, y_pred)
                elif metric == 'balanced_accuracy':
                    results[metric] = balanced_accuracy_score(y_true, y_pred)
                elif metric == 'precision':
                    results[metric] = precision_score(
                        y_true, y_pred, average='binary', zero_division=0
                    )
                elif metric == 'recall':
                    results[metric] = recall_score(
                        y_true, y_pred, average='binary', zero_division=0
                    )
                elif metric == 'f1_score':
                    results[metric] = f1_score(
                        y_true, y_pred, average='binary', zero_division=0
                    )
                elif metric == 'roc_auc':
                    results[metric] = roc_auc_score(y_true, y_proba)
                elif metric == 'pr_auc':
                    results[metric] = average_precision_score(y_true, y_proba)
                else:
                    logger.warning(f"Unknown metric: {metric}")
            except Exception as e:
                logger.error(f"Error calculating {metric}: {e}")
                results[metric] = np.nan
        
        return results
    
    def _aggregate_results(
        self,
        fold_results: List[Dict],
        metrics: List[str]
    ) -> Dict[str, float]:
        """
        Aggregate results across folds.
        
        Args:
            fold_results: List of metric dictionaries from each fold
            metrics: List of metric names
            
        Returns:
            Dictionary with mean and std for each metric
        """
        aggregated = {}
        
        for metric in metrics:
            values = [fold[metric] for fold in fold_results if metric in fold]
            
            if values:
                aggregated[f'{metric}_mean'] = np.mean(values)
                aggregated[f'{metric}_std'] = np.std(values)
                aggregated[f'{metric}_min'] = np.min(values)
                aggregated[f'{metric}_max'] = np.max(values)
                aggregated[f'{metric}_values'] = values
            else:
                aggregated[f'{metric}_mean'] = np.nan
                aggregated[f'{metric}_std'] = np.nan
        
        return aggregated
    
    def compare_models(
        self,
        models_config: Dict[str, Dict],
        X: pd.DataFrame,
        y: pd.Series
    ) -> pd.DataFrame:
        """
        Compare multiple models using cross-validation.
        
        Args:
            models_config: Dictionary mapping model names to
                          {'class': ModelClass, 'params': {...}}
            X: Feature DataFrame
            y: Target Series
            
        Returns:
            DataFrame with comparison results
        """
        logger.info(f"Comparing {len(models_config)} models")
        
        comparison_results = []
        
        for model_name, config in models_config.items():
            logger.info(f"\nEvaluating {model_name}")
            
            results = self.evaluate_model(
                config['class'],
                config['params'],
                X, y
            )
            
            # Extract mean scores
            cv_results = results['cv_results']
            model_scores = {'model': model_name}
            
            for key, value in cv_results.items():
                if key.endswith('_mean'):
                    metric_name = key.replace('_mean', '')
                    model_scores[metric_name] = value
                elif key.endswith('_std'):
                    metric_name = key.replace('_std', '')
                    model_scores[f'{metric_name}_std'] = value
            
            comparison_results.append(model_scores)
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(comparison_results)
        comparison_df = comparison_df.set_index('model')
        
        logger.info("\nModel comparison results:")
        logger.info(f"\n{comparison_df.to_string()}")
        
        return comparison_df
    
    def get_best_model(
        self,
        comparison_df: pd.DataFrame,
        metric: str = 'roc_auc'
    ) -> str:
        """
        Get the best performing model based on a metric.
        
        Args:
            comparison_df: DataFrame from compare_models
            metric: Metric to use for comparison
            
        Returns:
            Name of the best model
        """
        if metric not in comparison_df.columns:
            raise ValueError(
                f"Metric '{metric}' not found. "
                f"Available: {list(comparison_df.columns)}"
            )
        
        best_model = comparison_df[metric].idxmax()
        best_score = comparison_df.loc[best_model, metric]
        
        logger.info(f"Best model: {best_model} ({metric}={best_score:.4f})")
        
        return best_model
