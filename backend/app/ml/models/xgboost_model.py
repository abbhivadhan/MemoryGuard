"""
XGBoost classifier for Alzheimer's disease prediction.
"""

from typing import Dict, Optional, Tuple
import numpy as np
import joblib
import xgboost as xgb
from sklearn.model_selection import cross_val_score
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AlzheimerXGBoost:
    """
    XGBoost classifier for Alzheimer's disease risk prediction.
    """
    
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42
    ):
        """
        Initialize XGBoost model.
        
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate (eta)
            subsample: Subsample ratio of training instances
            colsample_bytree: Subsample ratio of columns
            random_state: Random seed for reproducibility
        """
        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=random_state,
            n_jobs=-1,  # Use all CPU cores
            eval_metric='logloss',
            use_label_encoder=False
        )
        self.is_trained = False
        self.feature_names = []
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: list,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Train the XGBoost model.
        
        Args:
            X_train: Training features
            y_train: Training labels (0: no Alzheimer's, 1: Alzheimer's)
            feature_names: List of feature names
            X_val: Optional validation features
            y_val: Optional validation labels
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training XGBoost on {len(X_train)} samples")
        
        # Prepare evaluation set if validation data provided
        eval_set = None
        if X_val is not None and y_val is not None:
            eval_set = [(X_train, y_train), (X_val, y_val)]
        
        # Train model
        self.model.fit(
            X_train, 
            y_train,
            eval_set=eval_set,
            verbose=False
        )
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
        
        # Add validation accuracy if available
        if X_val is not None and y_val is not None:
            val_accuracy = self.model.score(X_val, y_val)
            metrics['val_accuracy'] = float(val_accuracy)
        
        logger.info(
            f"XGBoost trained - "
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
        logger.info(f"XGBoost model saved to {filepath}")
    
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
        
        logger.info(f"XGBoost model loaded from {filepath}")
    
    def get_model_info(self) -> Dict:
        """
        Get model information.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            'model_type': 'XGBoost',
            'n_estimators': self.model.n_estimators,
            'max_depth': self.model.max_depth,
            'learning_rate': self.model.learning_rate,
            'is_trained': self.is_trained,
            'n_features': len(self.feature_names) if self.feature_names else 0
        }
