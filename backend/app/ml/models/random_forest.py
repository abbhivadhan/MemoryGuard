"""
Random Forest classifier for Alzheimer's disease prediction.
"""

from typing import Dict, Optional, Tuple
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AlzheimerRandomForest:
    """
    Random Forest classifier for Alzheimer's disease risk prediction.
    """
    
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: Optional[int] = None,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42
    ):
        """
        Initialize Random Forest model.
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples required to split
            min_samples_leaf: Minimum samples required at leaf node
            random_state: Random seed for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1,  # Use all CPU cores
            class_weight='balanced'  # Handle class imbalance
        )
        self.is_trained = False
        self.feature_names = []
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: list
    ) -> Dict[str, float]:
        """
        Train the Random Forest model.
        
        Args:
            X_train: Training features
            y_train: Training labels (0: no Alzheimer's, 1: Alzheimer's)
            feature_names: List of feature names
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training Random Forest on {len(X_train)} samples")
        
        # Train model
        self.model.fit(X_train, y_train)
        self.feature_names = feature_names
        self.is_trained = True
        
        # Calculate training accuracy
        train_accuracy = self.model.score(X_train, y_train)
        
        # Perform cross-validation
        cv_scores = cross_val_score(
            self.model, X_train, y_train, cv=5, scoring='accuracy'
        )
        
        metrics = {
            'train_accuracy': float(train_accuracy),
            'cv_mean_accuracy': float(cv_scores.mean()),
            'cv_std_accuracy': float(cv_scores.std()),
            'n_estimators': self.model.n_estimators,
            'n_features': X_train.shape[1]
        }
        
        logger.info(
            f"Random Forest trained - "
            f"Train Acc: {train_accuracy:.3f}, "
            f"CV Acc: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})"
        )
        
        return metrics
    
    def predict(self, X: np.ndarray) -> int:
        """
        Predict class for a single sample.
        
        Args:
            X: Feature vector
            
        Returns:
            Predicted class (0 or 1)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        prediction = self.model.predict(X)
        return int(prediction[0])
    
    def predict_proba(self, X: np.ndarray) -> Tuple[float, float]:
        """
        Predict probability for each class.
        
        Args:
            X: Feature vector
            
        Returns:
            Tuple of (probability_no_alzheimers, probability_alzheimers)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        probabilities = self.model.predict_proba(X)[0]
        return float(probabilities[0]), float(probabilities[1])
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before getting feature importance")
        
        importances = self.model.feature_importances_
        
        # Sort by importance
        importance_dict = dict(zip(self.feature_names, importances))
        sorted_importance = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_importance
    
    def save(self, filepath: str) -> None:
        """
        Save model to disk.
        
        Args:
            filepath: Path to save model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save model and metadata
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Random Forest model saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """
        Load model from disk.
        
        Args:
            filepath: Path to load model from
        """
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Random Forest model loaded from {filepath}")
    
    def get_model_info(self) -> Dict:
        """
        Get model information.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            'model_type': 'RandomForest',
            'n_estimators': self.model.n_estimators,
            'max_depth': self.model.max_depth,
            'is_trained': self.is_trained,
            'n_features': len(self.feature_names) if self.feature_names else 0
        }
