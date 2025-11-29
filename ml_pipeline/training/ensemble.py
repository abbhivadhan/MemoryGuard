"""
Ensemble Predictor Module

Combines predictions from multiple models using weighted averaging
and provides confidence intervals.
"""

import logging
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """
    Ensemble model combining multiple classifiers.
    
    Uses weighted averaging of probability predictions and provides
    confidence intervals for predictions.
    """
    
    def __init__(
        self,
        models: List,
        model_names: List[str],
        weights: Optional[List[float]] = None
    ):
        """
        Initialize ensemble predictor.
        
        Args:
            models: List of trained models
            model_names: Names of the models
            weights: Optional weights for each model (default: equal weights)
        """
        if len(models) != len(model_names):
            raise ValueError("Number of models must match number of model names")
        
        self.models = models
        self.model_names = model_names
        
        # Set weights (equal if not provided)
        if weights is None:
            self.weights = np.array([1.0 / len(models)] * len(models))
        else:
            if len(weights) != len(models):
                raise ValueError("Number of weights must match number of models")
            # Normalize weights to sum to 1
            self.weights = np.array(weights) / np.sum(weights)
        
        logger.info(f"Initialized EnsemblePredictor with {len(models)} models")
        logger.info(f"Model names: {model_names}")
        logger.info(f"Weights: {self.weights}")
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Generate ensemble probability predictions using weighted averaging.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Array of probability predictions for positive class
        """
        predictions = []
        
        for model, name, weight in zip(self.models, self.model_names, self.weights):
            try:
                # Get probability for positive class
                proba = model.predict_proba(X)[:, 1]
                predictions.append(proba)
                logger.debug(f"{name} predictions shape: {proba.shape}")
            except Exception as e:
                logger.error(f"Error getting predictions from {name}: {e}")
                raise
        
        # Stack predictions and compute weighted average
        predictions = np.array(predictions)  # Shape: (n_models, n_samples)
        ensemble_proba = np.average(predictions, axis=0, weights=self.weights)
        
        logger.debug(f"Ensemble predictions shape: {ensemble_proba.shape}")
        
        return ensemble_proba
    
    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """
        Generate binary predictions.
        
        Args:
            X: Feature DataFrame
            threshold: Classification threshold
            
        Returns:
            Array of binary predictions
        """
        proba = self.predict_proba(X)
        predictions = (proba >= threshold).astype(int)
        
        return predictions
    
    def predict_with_confidence(
        self,
        X: pd.DataFrame,
        confidence_level: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate predictions with confidence intervals.
        
        Args:
            X: Feature DataFrame
            confidence_level: Confidence level for intervals (default: 0.95)
            
        Returns:
            Tuple of (predictions, lower_bounds, upper_bounds)
        """
        # Get predictions from all models
        all_predictions = []
        
        for model in self.models:
            proba = model.predict_proba(X)[:, 1]
            all_predictions.append(proba)
        
        all_predictions = np.array(all_predictions)  # Shape: (n_models, n_samples)
        
        # Calculate ensemble prediction (weighted average)
        ensemble_proba = np.average(all_predictions, axis=0, weights=self.weights)
        
        # Calculate confidence intervals using standard error
        # Standard error of the mean
        std_error = np.std(all_predictions, axis=0) / np.sqrt(len(self.models))
        
        # Z-score for confidence level
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        # Confidence intervals
        margin = z_score * std_error
        lower_bound = np.clip(ensemble_proba - margin, 0, 1)
        upper_bound = np.clip(ensemble_proba + margin, 0, 1)
        
        logger.debug(
            f"Generated predictions with {confidence_level*100}% confidence intervals"
        )
        
        return ensemble_proba, lower_bound, upper_bound
    
    def get_model_predictions(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Get individual predictions from each model.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Dictionary mapping model names to their predictions
        """
        model_predictions = {}
        
        for model, name in zip(self.models, self.model_names):
            proba = model.predict_proba(X)[:, 1]
            model_predictions[name] = proba
        
        return model_predictions
    
    def get_prediction_agreement(self, X: pd.DataFrame, threshold: float = 0.5) -> float:
        """
        Calculate agreement rate between models.
        
        Args:
            X: Feature DataFrame
            threshold: Classification threshold
            
        Returns:
            Agreement rate (0 to 1)
        """
        # Get binary predictions from each model
        binary_predictions = []
        
        for model in self.models:
            proba = model.predict_proba(X)[:, 1]
            binary_pred = (proba >= threshold).astype(int)
            binary_predictions.append(binary_pred)
        
        binary_predictions = np.array(binary_predictions)  # Shape: (n_models, n_samples)
        
        # Calculate agreement: all models agree on each sample
        all_agree = np.all(binary_predictions == binary_predictions[0], axis=0)
        agreement_rate = np.mean(all_agree)
        
        logger.info(f"Model agreement rate: {agreement_rate:.2%}")
        
        return agreement_rate
    
    def get_prediction_variance(self, X: pd.DataFrame) -> np.ndarray:
        """
        Calculate variance in predictions across models.
        
        Higher variance indicates more disagreement between models.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Array of prediction variances for each sample
        """
        all_predictions = []
        
        for model in self.models:
            proba = model.predict_proba(X)[:, 1]
            all_predictions.append(proba)
        
        all_predictions = np.array(all_predictions)
        variance = np.var(all_predictions, axis=0)
        
        return variance
    
    def get_ensemble_metrics(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate ensemble performance metrics.
        
        Args:
            X: Feature DataFrame
            y: True labels
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            roc_auc_score, average_precision_score, balanced_accuracy_score
        )
        
        # Get predictions
        y_proba = self.predict_proba(X)
        y_pred = self.predict(X)
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'balanced_accuracy': balanced_accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, zero_division=0),
            'recall': recall_score(y, y_pred, zero_division=0),
            'f1_score': f1_score(y, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y, y_proba),
            'pr_auc': average_precision_score(y, y_proba)
        }
        
        logger.info("Ensemble metrics:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        return metrics
    
    def optimize_weights(
        self,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        metric: str = 'roc_auc'
    ) -> np.ndarray:
        """
        Optimize ensemble weights based on validation performance.
        
        Args:
            X_val: Validation features
            y_val: Validation labels
            metric: Metric to optimize ('roc_auc', 'accuracy', etc.)
            
        Returns:
            Optimized weights
        """
        from scipy.optimize import minimize
        from sklearn.metrics import roc_auc_score, accuracy_score
        
        # Get predictions from all models
        all_predictions = []
        for model in self.models:
            proba = model.predict_proba(X_val)[:, 1]
            all_predictions.append(proba)
        
        all_predictions = np.array(all_predictions)
        
        # Define objective function
        def objective(weights):
            weights = weights / np.sum(weights)  # Normalize
            ensemble_proba = np.average(all_predictions, axis=0, weights=weights)
            
            if metric == 'roc_auc':
                score = roc_auc_score(y_val, ensemble_proba)
            elif metric == 'accuracy':
                ensemble_pred = (ensemble_proba >= 0.5).astype(int)
                score = accuracy_score(y_val, ensemble_pred)
            else:
                raise ValueError(f"Unknown metric: {metric}")
            
            return -score  # Minimize negative score
        
        # Optimize weights
        initial_weights = np.ones(len(self.models)) / len(self.models)
        bounds = [(0, 1) for _ in range(len(self.models))]
        
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints={'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        )
        
        optimized_weights = result.x / np.sum(result.x)
        
        logger.info(f"Optimized weights: {optimized_weights}")
        logger.info(f"Original weights: {self.weights}")
        
        # Update weights
        self.weights = optimized_weights
        
        return optimized_weights
