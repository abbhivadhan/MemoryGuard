"""
SHAP Explainer Module

Implements SHAP (SHapley Additive exPlanations) for model interpretability.
Supports tree-based models (Random Forest, XGBoost) and neural networks.

Implements Requirements 7.1:
- Generate SHAP values for all predictions
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
import shap
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class SHAPExplainer:
    """
    Base SHAP explainer for model interpretability.
    
    Generates SHAP values to explain individual predictions and
    identify feature contributions.
    """
    
    def __init__(
        self,
        model,
        model_type: str,
        feature_names: List[str],
        max_background_samples: int = 100
    ):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model
            model_type: Type of model ('tree', 'deep', 'kernel')
            feature_names: List of feature names
            max_background_samples: Maximum samples for background data
        """
        self.model = model
        self.model_type = model_type
        self.feature_names = feature_names
        self.max_background_samples = max_background_samples
        self.explainer = None
        self.background_data = None
        self.expected_value = None
        
        logger.info(f"Initialized SHAPExplainer for {model_type} model")
    
    def initialize(self, background_data: np.ndarray):
        """
        Initialize the SHAP explainer with background data.
        
        Args:
            background_data: Background dataset for SHAP calculations
        """
        raise NotImplementedError("Subclasses must implement initialize()")
    
    def explain_prediction(
        self,
        X: np.ndarray,
        return_dict: bool = True
    ) -> Dict[str, Any]:
        """
        Generate SHAP explanation for a single prediction.
        
        Implements Requirement 7.1: Generate SHAP values for predictions
        
        Args:
            X: Feature vector (1D or 2D array)
            return_dict: Whether to return as dictionary
            
        Returns:
            Dictionary with SHAP values and explanation details
        """
        if self.explainer is None:
            raise ValueError("Explainer must be initialized first with background data")
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Time the SHAP calculation (Requirement 7.7: within 2 seconds)
        start_time = time.time()
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)
        
        elapsed_time = time.time() - start_time
        logger.debug(f"SHAP calculation took {elapsed_time:.3f} seconds")
        
        # Handle different SHAP value formats
        if isinstance(shap_values, list):
            # For binary classification, use positive class (index 1)
            shap_values = shap_values[1]
        
        # Get SHAP values for the single prediction
        if shap_values.ndim > 1:
            shap_values = shap_values[0]
        
        if not return_dict:
            return shap_values
        
        # Create feature-value mapping
        feature_shap_dict = {
            feature: float(shap_values[i])
            for i, feature in enumerate(self.feature_names)
        }
        
        # Sort by absolute importance
        sorted_features = sorted(
            feature_shap_dict.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        explanation = {
            'shap_values': feature_shap_dict,
            'sorted_features': sorted_features,
            'base_value': float(self.expected_value),
            'computation_time': elapsed_time
        }
        
        return explanation
    
    def explain_batch(
        self,
        X_batch: np.ndarray
    ) -> np.ndarray:
        """
        Generate SHAP values for a batch of predictions.
        
        Args:
            X_batch: Batch of feature vectors
            
        Returns:
            Array of SHAP values (n_samples, n_features)
        """
        if self.explainer is None:
            raise ValueError("Explainer must be initialized first")
        
        logger.info(f"Calculating SHAP values for {len(X_batch)} samples")
        
        start_time = time.time()
        shap_values = self.explainer.shap_values(X_batch)
        elapsed_time = time.time() - start_time
        
        logger.info(f"Batch SHAP calculation took {elapsed_time:.3f} seconds")
        
        # Handle different formats
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        return shap_values
    
    def get_top_features(
        self,
        X: np.ndarray,
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get top N most important features for a prediction.
        
        Implements Requirement 7.4: Identify top 5 contributing features
        
        Args:
            X: Feature vector
            top_n: Number of top features to return (default 5)
            
        Returns:
            List of (feature_name, shap_value) tuples
        """
        explanation = self.explain_prediction(X)
        sorted_features = explanation['sorted_features']
        
        return sorted_features[:top_n]
    
    def get_feature_contributions(
        self,
        X: np.ndarray
    ) -> Dict[str, Dict[str, List[Tuple[str, float]]]]:
        """
        Get positive and negative feature contributions.
        
        Args:
            X: Feature vector
            
        Returns:
            Dictionary with positive and negative contributions
        """
        explanation = self.explain_prediction(X)
        shap_values = explanation['shap_values']
        
        positive = []
        negative = []
        
        for feature, value in shap_values.items():
            if value > 0:
                positive.append((feature, value))
            elif value < 0:
                negative.append((feature, abs(value)))
        
        # Sort by magnitude
        positive.sort(key=lambda x: x[1], reverse=True)
        negative.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'positive': positive,
            'negative': negative
        }


class TreeSHAPExplainer(SHAPExplainer):
    """
    SHAP explainer for tree-based models (Random Forest, XGBoost).
    
    Uses TreeExplainer for fast, exact SHAP value computation.
    """
    
    def __init__(
        self,
        model,
        feature_names: List[str],
        max_background_samples: int = 100
    ):
        """
        Initialize Tree SHAP explainer.
        
        Args:
            model: Trained tree-based model (RandomForest or XGBoost)
            feature_names: List of feature names
            max_background_samples: Not used for TreeExplainer
        """
        super().__init__(model, 'tree', feature_names, max_background_samples)
    
    def initialize(self, background_data: Optional[np.ndarray] = None):
        """
        Initialize TreeExplainer.
        
        TreeExplainer doesn't require background data but we accept it
        for API consistency.
        
        Args:
            background_data: Optional background data (not used)
        """
        logger.info("Initializing TreeExplainer for tree-based model")
        
        try:
            # Create TreeExplainer
            self.explainer = shap.TreeExplainer(self.model)
            
            # Get expected value
            if isinstance(self.explainer.expected_value, (list, np.ndarray)):
                # For binary classification, use positive class
                self.expected_value = self.explainer.expected_value[1]
            else:
                self.expected_value = self.explainer.expected_value
            
            logger.info(f"TreeExplainer initialized successfully")
            logger.info(f"Expected value (base prediction): {self.expected_value:.4f}")
            
        except Exception as e:
            logger.error(f"Error initializing TreeExplainer: {e}")
            raise


class DeepSHAPExplainer(SHAPExplainer):
    """
    SHAP explainer for deep neural networks.
    
    Uses DeepExplainer for neural network models.
    """
    
    def __init__(
        self,
        model,
        feature_names: List[str],
        max_background_samples: int = 100
    ):
        """
        Initialize Deep SHAP explainer.
        
        Args:
            model: Trained neural network model
            feature_names: List of feature names
            max_background_samples: Maximum samples for background data
        """
        super().__init__(model, 'deep', feature_names, max_background_samples)
    
    def initialize(self, background_data: np.ndarray):
        """
        Initialize DeepExplainer with background data.
        
        Args:
            background_data: Background dataset for SHAP calculations
        """
        if background_data is None:
            raise ValueError("DeepExplainer requires background data")
        
        logger.info("Initializing DeepExplainer for neural network")
        
        # Limit background data size for performance
        if len(background_data) > self.max_background_samples:
            logger.info(
                f"Sampling {self.max_background_samples} from "
                f"{len(background_data)} background samples"
            )
            indices = np.random.choice(
                len(background_data),
                self.max_background_samples,
                replace=False
            )
            background_data = background_data[indices]
        
        self.background_data = background_data
        
        try:
            # Create DeepExplainer
            self.explainer = shap.DeepExplainer(self.model, background_data)
            
            # Calculate expected value
            self.expected_value = np.mean(
                self.model.predict(background_data)
            )
            
            logger.info(f"DeepExplainer initialized successfully")
            logger.info(f"Background samples: {len(background_data)}")
            logger.info(f"Expected value: {self.expected_value:.4f}")
            
        except Exception as e:
            logger.error(f"Error initializing DeepExplainer: {e}")
            raise


class EnsembleSHAPExplainer:
    """
    SHAP explainer for ensemble models.
    
    Aggregates SHAP explanations from multiple models using ensemble weights.
    """
    
    def __init__(
        self,
        models: Dict[str, Any],
        model_types: Dict[str, str],
        feature_names: List[str],
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize ensemble SHAP explainer.
        
        Args:
            models: Dictionary of trained models {name: model}
            model_types: Dictionary of model types {name: type}
            feature_names: List of feature names
            weights: Optional weights for each model
        """
        self.models = models
        self.model_types = model_types
        self.feature_names = feature_names
        
        # Set equal weights if not provided
        if weights is None:
            n_models = len(models)
            self.weights = {name: 1.0 / n_models for name in models.keys()}
        else:
            # Normalize weights
            total = sum(weights.values())
            self.weights = {k: v / total for k, v in weights.items()}
        
        self.explainers = {}
        
        logger.info(f"Initialized EnsembleSHAPExplainer with {len(models)} models")
        logger.info(f"Weights: {self.weights}")
    
    def initialize(self, background_data: np.ndarray):
        """
        Initialize SHAP explainers for all models in ensemble.
        
        Args:
            background_data: Background dataset for SHAP calculations
        """
        logger.info("Initializing explainers for ensemble models")
        
        for model_name, model in self.models.items():
            model_type = self.model_types[model_name]
            
            if model_type == 'tree':
                explainer = TreeSHAPExplainer(model, self.feature_names)
                explainer.initialize()
            elif model_type == 'deep':
                explainer = DeepSHAPExplainer(model, self.feature_names)
                explainer.initialize(background_data)
            else:
                logger.warning(f"Unknown model type for {model_name}: {model_type}")
                continue
            
            self.explainers[model_name] = explainer
            logger.info(f"  ✓ {model_name} explainer initialized")
        
        logger.info(f"All {len(self.explainers)} explainers initialized")
    
    def explain_prediction(
        self,
        X: np.ndarray,
        aggregate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate SHAP explanation from ensemble.
        
        Args:
            X: Feature vector
            aggregate: Whether to aggregate explanations (default True)
            
        Returns:
            Dictionary with aggregated or individual explanations
        """
        individual_explanations = {}
        
        # Get explanations from each model
        for model_name, explainer in self.explainers.items():
            explanation = explainer.explain_prediction(X)
            individual_explanations[model_name] = explanation
        
        if not aggregate:
            return {'individual_explanations': individual_explanations}
        
        # Aggregate SHAP values using ensemble weights
        aggregated_shap = {feature: 0.0 for feature in self.feature_names}
        aggregated_base = 0.0
        
        for model_name, explanation in individual_explanations.items():
            weight = self.weights[model_name]
            
            for feature, value in explanation['shap_values'].items():
                aggregated_shap[feature] += weight * value
            
            aggregated_base += weight * explanation['base_value']
        
        # Sort by absolute importance
        sorted_features = sorted(
            aggregated_shap.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        return {
            'shap_values': aggregated_shap,
            'sorted_features': sorted_features,
            'base_value': aggregated_base,
            'individual_explanations': individual_explanations
        }
    
    def get_top_features(
        self,
        X: np.ndarray,
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get top N features from aggregated ensemble explanation.
        
        Args:
            X: Feature vector
            top_n: Number of top features
            
        Returns:
            List of (feature_name, aggregated_shap_value) tuples
        """
        explanation = self.explain_prediction(X, aggregate=True)
        return explanation['sorted_features'][:top_n]
