"""
Ensemble model combining Random Forest, XGBoost, and Neural Network predictions.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import stats
import logging
from pathlib import Path

from .random_forest import AlzheimerRandomForest
from .xgboost_model import AlzheimerXGBoost
from .neural_net import AlzheimerNeuralNetwork

logger = logging.getLogger(__name__)


class AlzheimerEnsemble:
    """
    Ensemble model combining multiple classifiers for robust Alzheimer's prediction.
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        random_state: int = 42
    ):
        """
        Initialize ensemble model.
        
        Args:
            weights: Optional weights for each model (rf, xgb, nn)
            random_state: Random seed for reproducibility
        """
        # Default equal weights
        self.weights = weights or {
            'rf': 0.33,
            'xgb': 0.33,
            'nn': 0.34
        }
        
        # Normalize weights
        total_weight = sum(self.weights.values())
        self.weights = {k: v/total_weight for k, v in self.weights.items()}
        
        self.random_state = random_state
        self.models = {}
        self.is_trained = False
        self.feature_names = []
    
    def initialize_models(self, input_dim: int) -> None:
        """
        Initialize all models in the ensemble.
        
        Args:
            input_dim: Number of input features
        """
        self.models['rf'] = AlzheimerRandomForest(
            n_estimators=200,
            random_state=self.random_state
        )
        
        self.models['xgb'] = AlzheimerXGBoost(
            n_estimators=200,
            max_depth=6,
            random_state=self.random_state
        )
        
        self.models['nn'] = AlzheimerNeuralNetwork(
            input_dim=input_dim,
            hidden_layers=[128, 64, 32],
            random_state=self.random_state
        )
        
        logger.info("Ensemble models initialized")
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: List[str],
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> Dict[str, Dict]:
        """
        Train all models in the ensemble.
        
        Args:
            X_train: Training features
            y_train: Training labels
            feature_names: List of feature names
            X_val: Optional validation features
            y_val: Optional validation labels
            
        Returns:
            Dictionary with training metrics for each model
        """
        logger.info(f"Training ensemble on {len(X_train)} samples")
        
        self.feature_names = feature_names
        
        # Initialize models if not already done
        if not self.models:
            self.initialize_models(X_train.shape[1])
        
        metrics = {}
        
        # Train Random Forest
        logger.info("Training Random Forest...")
        metrics['rf'] = self.models['rf'].train(X_train, y_train, feature_names)
        
        # Train XGBoost
        logger.info("Training XGBoost...")
        metrics['xgb'] = self.models['xgb'].train(
            X_train, y_train, feature_names, X_val, y_val
        )
        
        # Train Neural Network
        logger.info("Training Neural Network...")
        metrics['nn'] = self.models['nn'].train(
            X_train, y_train, feature_names
        )
        
        self.is_trained = True
        
        # Calculate ensemble performance
        if X_val is not None and y_val is not None:
            ensemble_accuracy = self._evaluate_ensemble(X_val, y_val)
            metrics['ensemble'] = {
                'val_accuracy': float(ensemble_accuracy),
                'weights': self.weights
            }
        
        logger.info("Ensemble training complete")
        
        return metrics
    
    def _evaluate_ensemble(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Evaluate ensemble accuracy on a dataset.
        
        Args:
            X: Features
            y: True labels
            
        Returns:
            Accuracy score
        """
        predictions = []
        for i in range(len(X)):
            pred = self.predict(X[i])
            predictions.append(pred)
        
        accuracy = np.mean(np.array(predictions) == y)
        return accuracy
    
    def predict(self, X: np.ndarray) -> int:
        """
        Predict class using weighted ensemble voting.
        
        Args:
            X: Feature vector
            
        Returns:
            Predicted class (0 or 1)
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")
        
        # Get probabilities from each model
        _, prob_rf = self.models['rf'].predict_proba(X)
        _, prob_xgb = self.models['xgb'].predict_proba(X)
        _, prob_nn = self.models['nn'].predict_proba(X)
        
        # Weighted average
        weighted_prob = (
            self.weights['rf'] * prob_rf +
            self.weights['xgb'] * prob_xgb +
            self.weights['nn'] * prob_nn
        )
        
        # Threshold at 0.5
        prediction = 1 if weighted_prob >= 0.5 else 0
        
        return int(prediction)
    
    def predict_proba(self, X: np.ndarray) -> Tuple[float, float]:
        """
        Predict probability using weighted ensemble.
        
        Args:
            X: Feature vector
            
        Returns:
            Tuple of (probability_no_alzheimers, probability_alzheimers)
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")
        
        # Get probabilities from each model
        prob_neg_rf, prob_pos_rf = self.models['rf'].predict_proba(X)
        prob_neg_xgb, prob_pos_xgb = self.models['xgb'].predict_proba(X)
        prob_neg_nn, prob_pos_nn = self.models['nn'].predict_proba(X)
        
        # Weighted average for positive class
        weighted_prob_pos = (
            self.weights['rf'] * prob_pos_rf +
            self.weights['xgb'] * prob_pos_xgb +
            self.weights['nn'] * prob_pos_nn
        )
        
        weighted_prob_neg = 1.0 - weighted_prob_pos
        
        return float(weighted_prob_neg), float(weighted_prob_pos)
    
    def predict_with_confidence(
        self, 
        X: np.ndarray
    ) -> Tuple[int, float, Tuple[float, float]]:
        """
        Predict with confidence interval.
        
        Args:
            X: Feature vector
            
        Returns:
            Tuple of (prediction, confidence_score, confidence_interval)
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")
        
        # Get probabilities from each model
        _, prob_rf = self.models['rf'].predict_proba(X)
        _, prob_xgb = self.models['xgb'].predict_proba(X)
        _, prob_nn = self.models['nn'].predict_proba(X)
        
        # Calculate weighted average
        weighted_prob = (
            self.weights['rf'] * prob_rf +
            self.weights['xgb'] * prob_xgb +
            self.weights['nn'] * prob_nn
        )
        
        # Calculate confidence based on agreement between models
        probs = [prob_rf, prob_xgb, prob_nn]
        std_dev = np.std(probs)
        
        # Confidence score (higher when models agree)
        confidence_score = 1.0 - (std_dev / 0.5)  # Normalize by max possible std
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        # Calculate confidence interval (95%)
        z_score = 1.96  # 95% confidence
        margin = z_score * std_dev
        ci_lower = max(0.0, weighted_prob - margin)
        ci_upper = min(1.0, weighted_prob + margin)
        
        prediction = 1 if weighted_prob >= 0.5 else 0
        
        return int(prediction), float(confidence_score), (float(ci_lower), float(ci_upper))
    
    def get_model_predictions(self, X: np.ndarray) -> Dict[str, Tuple[int, float]]:
        """
        Get individual predictions from each model.
        
        Args:
            X: Feature vector
            
        Returns:
            Dictionary with predictions and probabilities for each model
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")
        
        predictions = {}
        
        for model_name, model in self.models.items():
            pred = model.predict(X)
            _, prob = model.predict_proba(X)
            predictions[model_name] = (int(pred), float(prob))
        
        return predictions
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get aggregated feature importance from all models.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before getting feature importance")
        
        # Get importance from each model
        importance_rf = self.models['rf'].get_feature_importance()
        importance_xgb = self.models['xgb'].get_feature_importance()
        importance_nn = self.models['nn'].get_feature_importance()
        
        # Weighted average of importances
        aggregated_importance = {}
        for feature in self.feature_names:
            aggregated_importance[feature] = (
                self.weights['rf'] * importance_rf.get(feature, 0) +
                self.weights['xgb'] * importance_xgb.get(feature, 0) +
                self.weights['nn'] * importance_nn.get(feature, 0)
            )
        
        # Sort by importance
        sorted_importance = dict(
            sorted(aggregated_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_importance
    
    def save(self, directory: str) -> None:
        """
        Save all models in the ensemble.
        
        Args:
            directory: Directory to save models
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained ensemble")
        
        # Create directory
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Save each model
        self.models['rf'].save(str(dir_path / 'random_forest.pkl'))
        self.models['xgb'].save(str(dir_path / 'xgboost.pkl'))
        self.models['nn'].save(str(dir_path / 'neural_network'))
        
        # Save ensemble metadata
        import json
        metadata = {
            'weights': self.weights,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'random_state': self.random_state
        }
        
        with open(dir_path / 'ensemble_metadata.json', 'w') as f:
            json.dump(metadata, f)
        
        logger.info(f"Ensemble saved to {directory}")
    
    def load(self, directory: str) -> None:
        """
        Load all models in the ensemble.
        
        Args:
            directory: Directory to load models from
        """
        import json
        
        dir_path = Path(directory)
        
        # Load metadata
        with open(dir_path / 'ensemble_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        self.weights = metadata['weights']
        self.feature_names = metadata['feature_names']
        self.is_trained = metadata['is_trained']
        self.random_state = metadata['random_state']
        
        # Initialize and load models
        input_dim = len(self.feature_names)
        self.initialize_models(input_dim)
        
        self.models['rf'].load(str(dir_path / 'random_forest.pkl'))
        self.models['xgb'].load(str(dir_path / 'xgboost.pkl'))
        self.models['nn'].load(str(dir_path / 'neural_network'))
        
        logger.info(f"Ensemble loaded from {directory}")
    
    def get_ensemble_info(self) -> Dict:
        """
        Get ensemble information.
        
        Returns:
            Dictionary with ensemble metadata
        """
        info = {
            'ensemble_type': 'WeightedVoting',
            'weights': self.weights,
            'is_trained': self.is_trained,
            'n_features': len(self.feature_names) if self.feature_names else 0,
            'models': {}
        }
        
        if self.models:
            for model_name, model in self.models.items():
                info['models'][model_name] = model.get_model_info()
        
        return info
