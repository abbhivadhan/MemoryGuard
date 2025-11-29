"""
Model Trainers Module

Provides trainer classes for different ML models:
- Random Forest
- XGBoost
- Deep Neural Network
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Any
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, balanced_accuracy_score
)
import xgboost as xgb
from tensorflow import keras
from tensorflow.keras import layers, callbacks

logger = logging.getLogger(__name__)


class BaseTrainer:
    """Base class for model trainers."""
    
    def __init__(self, model_name: str, random_state: int = 42):
        """
        Initialize base trainer.
        
        Args:
            model_name: Name of the model
            random_state: Random seed for reproducibility
        """
        self.model_name = model_name
        self.random_state = random_state
        self.model = None
        self.training_history = {}
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            X: Feature DataFrame
            y: True labels
            
        Returns:
            Dictionary of evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        y_pred = self.model.predict(X)
        y_proba = self.model.predict_proba(X)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'balanced_accuracy': balanced_accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, average='binary', zero_division=0),
            'recall': recall_score(y, y_pred, average='binary', zero_division=0),
            'f1_score': f1_score(y, y_pred, average='binary', zero_division=0),
            'roc_auc': roc_auc_score(y, y_proba),
            'pr_auc': average_precision_score(y, y_proba)
        }
        
        logger.info(f"{self.model_name} evaluation metrics:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        return metrics
    
    def save_model(self, output_path: Path):
        """
        Save trained model to disk.
        
        Args:
            output_path: Path to save the model
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, output_path)
        logger.info(f"Model saved to {output_path}")
    
    def load_model(self, model_path: Path):
        """
        Load trained model from disk.
        
        Args:
            model_path: Path to the saved model
        """
        self.model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")


class RandomForestTrainer(BaseTrainer):
    """
    Trainer for Random Forest classifier.
    
    Implements training with configurable hyperparameters and cross-validation.
    """
    
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: Optional[int] = 15,
        min_samples_split: int = 10,
        min_samples_leaf: int = 5,
        max_features: str = 'sqrt',
        class_weight: Optional[Dict] = None,
        random_state: int = 42,
        n_jobs: int = -1
    ):
        """
        Initialize Random Forest trainer.
        
        Args:
            n_estimators: Number of trees (minimum 200 per requirements)
            max_depth: Maximum tree depth
            min_samples_split: Minimum samples to split node
            min_samples_leaf: Minimum samples in leaf node
            max_features: Number of features for best split
            class_weight: Class weights for imbalanced data
            random_state: Random seed
            n_jobs: Number of parallel jobs (-1 for all cores)
        """
        super().__init__("RandomForest", random_state)
        
        if n_estimators < 200:
            logger.warning(
                f"n_estimators={n_estimators} is below requirement of 200. "
                "Setting to 200."
            )
            n_estimators = 200
        
        self.params = {
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'min_samples_split': min_samples_split,
            'min_samples_leaf': min_samples_leaf,
            'max_features': max_features,
            'class_weight': class_weight or 'balanced',
            'random_state': random_state,
            'n_jobs': n_jobs,
            'verbose': 1
        }
        
        logger.info(f"Initialized RandomForestTrainer with params: {self.params}")
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Train Random Forest model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            
        Returns:
            Dictionary with model and training metrics
        """
        logger.info(f"Training Random Forest with {len(X_train)} samples")
        
        # Create and train model
        self.model = RandomForestClassifier(**self.params)
        self.model.fit(X_train, y_train)
        
        # Evaluate on training set
        train_metrics = self.evaluate(X_train, y_train)
        train_metrics = {f'train_{k}': v for k, v in train_metrics.items()}
        
        # Evaluate on validation set if provided
        val_metrics = {}
        if X_val is not None and y_val is not None:
            val_metrics = self.evaluate(X_val, y_val)
            val_metrics = {f'val_{k}': v for k, v in val_metrics.items()}
        
        # Store training history
        self.training_history = {**train_metrics, **val_metrics}
        
        # Get feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Top 10 important features:")
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        return {
            'model': self.model,
            'metrics': self.training_history,
            'feature_importance': feature_importance
        }


class XGBoostTrainer(BaseTrainer):
    """
    Trainer for XGBoost classifier.
    
    Implements training with early stopping and hyperparameter optimization.
    """
    
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        scale_pos_weight: Optional[float] = None,
        random_state: int = 42,
        n_jobs: int = -1
    ):
        """
        Initialize XGBoost trainer.
        
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate
            subsample: Subsample ratio of training instances
            colsample_bytree: Subsample ratio of columns
            scale_pos_weight: Balancing of positive/negative weights
            random_state: Random seed
            n_jobs: Number of parallel jobs
        """
        super().__init__("XGBoost", random_state)
        
        self.params = {
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'learning_rate': learning_rate,
            'subsample': subsample,
            'colsample_bytree': colsample_bytree,
            'scale_pos_weight': scale_pos_weight,
            'random_state': random_state,
            'n_jobs': n_jobs,
            'eval_metric': 'auc',
            'use_label_encoder': False
        }
        
        logger.info(f"Initialized XGBoostTrainer with params: {self.params}")
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        early_stopping_rounds: int = 20
    ) -> Dict[str, Any]:
        """
        Train XGBoost model with early stopping.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            early_stopping_rounds: Rounds for early stopping
            
        Returns:
            Dictionary with model and training metrics
        """
        logger.info(f"Training XGBoost with {len(X_train)} samples")
        
        # Create model
        self.model = xgb.XGBClassifier(**self.params)
        
        # Train with early stopping if validation set provided
        if X_val is not None and y_val is not None:
            eval_set = [(X_train, y_train), (X_val, y_val)]
            self.model.fit(
                X_train, y_train,
                eval_set=eval_set,
                early_stopping_rounds=early_stopping_rounds,
                verbose=True
            )
            
            # Get best iteration
            best_iteration = self.model.best_iteration
            logger.info(f"Best iteration: {best_iteration}")
        else:
            self.model.fit(X_train, y_train, verbose=True)
        
        # Evaluate on training set
        train_metrics = self.evaluate(X_train, y_train)
        train_metrics = {f'train_{k}': v for k, v in train_metrics.items()}
        
        # Evaluate on validation set
        val_metrics = {}
        if X_val is not None and y_val is not None:
            val_metrics = self.evaluate(X_val, y_val)
            val_metrics = {f'val_{k}': v for k, v in val_metrics.items()}
        
        # Store training history
        self.training_history = {**train_metrics, **val_metrics}
        
        # Get feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Top 10 important features:")
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        return {
            'model': self.model,
            'metrics': self.training_history,
            'feature_importance': feature_importance
        }


class NeuralNetworkTrainer(BaseTrainer):
    """
    Trainer for Deep Neural Network classifier.
    
    Implements training with dropout regularization and early stopping.
    """
    
    def __init__(
        self,
        hidden_layers: list = [128, 64, 32],
        dropout_rates: list = [0.3, 0.3, 0.2],
        learning_rate: float = 0.001,
        batch_size: int = 32,
        epochs: int = 100,
        random_state: int = 42
    ):
        """
        Initialize Neural Network trainer.
        
        Args:
            hidden_layers: List of hidden layer sizes (minimum 3 layers)
            dropout_rates: Dropout rates for each hidden layer
            learning_rate: Learning rate for optimizer
            batch_size: Training batch size
            epochs: Maximum training epochs
            random_state: Random seed
        """
        super().__init__("NeuralNetwork", random_state)
        
        if len(hidden_layers) < 3:
            logger.warning(
                f"hidden_layers has {len(hidden_layers)} layers, "
                "requirement is minimum 3. Adding layers."
            )
            hidden_layers = [128, 64, 32]
        
        self.hidden_layers = hidden_layers
        self.dropout_rates = dropout_rates
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        
        # Set random seeds
        np.random.seed(random_state)
        import tensorflow as tf
        tf.random.set_seed(random_state)
        
        logger.info(
            f"Initialized NeuralNetworkTrainer with "
            f"{len(hidden_layers)} hidden layers: {hidden_layers}"
        )
    
    def build_model(self, input_dim: int) -> keras.Model:
        """
        Build neural network architecture.
        
        Args:
            input_dim: Number of input features
            
        Returns:
            Compiled Keras model
        """
        model = keras.Sequential()
        
        # Input layer
        model.add(layers.Input(shape=(input_dim,)))
        
        # Hidden layers with dropout
        for i, (units, dropout) in enumerate(zip(self.hidden_layers, self.dropout_rates)):
            model.add(layers.Dense(units, activation='relu', name=f'hidden_{i+1}'))
            model.add(layers.Dropout(dropout, name=f'dropout_{i+1}'))
        
        # Output layer
        model.add(layers.Dense(1, activation='sigmoid', name='output'))
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        
        logger.info("Neural network architecture:")
        model.summary(print_fn=logger.info)
        
        return model
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        early_stopping_patience: int = 15
    ) -> Dict[str, Any]:
        """
        Train neural network model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            early_stopping_patience: Patience for early stopping
            
        Returns:
            Dictionary with model and training metrics
        """
        logger.info(f"Training Neural Network with {len(X_train)} samples")
        
        # Build model
        self.model = self.build_model(X_train.shape[1])
        
        # Setup callbacks
        callback_list = []
        
        # Early stopping
        if X_val is not None and y_val is not None:
            early_stop = callbacks.EarlyStopping(
                monitor='val_loss',
                patience=early_stopping_patience,
                restore_best_weights=True,
                verbose=1
            )
            callback_list.append(early_stop)
        
        # Train model
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=self.epochs,
            batch_size=self.batch_size,
            callbacks=callback_list,
            verbose=1
        )
        
        # Store training history
        self.training_history = {
            'train_loss': history.history['loss'][-1],
            'train_accuracy': history.history['accuracy'][-1],
            'train_auc': history.history['auc'][-1]
        }
        
        if validation_data is not None:
            self.training_history.update({
                'val_loss': history.history['val_loss'][-1],
                'val_accuracy': history.history['val_accuracy'][-1],
                'val_auc': history.history['val_auc'][-1]
            })
        
        # Evaluate with sklearn metrics
        train_metrics = self.evaluate(X_train, y_train)
        train_metrics = {f'train_{k}': v for k, v in train_metrics.items()}
        
        val_metrics = {}
        if X_val is not None and y_val is not None:
            val_metrics = self.evaluate(X_val, y_val)
            val_metrics = {f'val_{k}': v for k, v in val_metrics.items()}
        
        all_metrics = {**train_metrics, **val_metrics}
        
        return {
            'model': self.model,
            'metrics': all_metrics,
            'history': history.history
        }
    
    def save_model(self, output_path: Path):
        """Save Keras model."""
        if self.model is None:
            raise ValueError("No model to save")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.model.save(output_path)
        logger.info(f"Model saved to {output_path}")
    
    def load_model(self, model_path: Path):
        """Load Keras model."""
        self.model = keras.models.load_model(model_path)
        logger.info(f"Model loaded from {model_path}")
