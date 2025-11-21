"""
Neural Network classifier for Alzheimer's disease prediction using TensorFlow/Keras.
"""

from typing import Dict, Optional, Tuple
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, callbacks
from sklearn.model_selection import train_test_split
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AlzheimerNeuralNetwork:
    """
    Deep Neural Network classifier for Alzheimer's disease risk prediction.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_layers: list = [128, 64, 32],
        dropout_rate: float = 0.3,
        learning_rate: float = 0.001,
        random_state: int = 42
    ):
        """
        Initialize Neural Network model.
        
        Args:
            input_dim: Number of input features
            hidden_layers: List of hidden layer sizes
            dropout_rate: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
            random_state: Random seed for reproducibility
        """
        tf.random.set_seed(random_state)
        np.random.seed(random_state)
        
        self.input_dim = input_dim
        self.hidden_layers = hidden_layers
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.model = None
        self.is_trained = False
        self.feature_names = []
        self.history = None
        
        self._build_model()
    
    def _build_model(self) -> None:
        """Build the neural network architecture."""
        model = keras.Sequential()
        
        # Input layer
        model.add(layers.Input(shape=(self.input_dim,)))
        
        # Hidden layers with batch normalization and dropout
        for i, units in enumerate(self.hidden_layers):
            model.add(layers.Dense(
                units,
                activation='relu',
                kernel_regularizer=keras.regularizers.l2(0.001),
                name=f'hidden_{i+1}'
            ))
            model.add(layers.BatchNormalization())
            model.add(layers.Dropout(self.dropout_rate))
        
        # Output layer (binary classification)
        model.add(layers.Dense(1, activation='sigmoid', name='output'))
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        
        self.model = model
        logger.info(f"Neural Network built with architecture: {self.hidden_layers}")
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: list,
        epochs: int = 100,
        batch_size: int = 32,
        validation_split: float = 0.2,
        early_stopping_patience: int = 15
    ) -> Dict[str, float]:
        """
        Train the Neural Network model.
        
        Args:
            X_train: Training features
            y_train: Training labels (0: no Alzheimer's, 1: Alzheimer's)
            feature_names: List of feature names
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data to use for validation
            early_stopping_patience: Patience for early stopping
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training Neural Network on {len(X_train)} samples")
        
        self.feature_names = feature_names
        
        # Callbacks
        callback_list = [
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=early_stopping_patience,
                restore_best_weights=True,
                verbose=0
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=0
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            X_train,
            y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callback_list,
            verbose=0
        )
        
        self.is_trained = True
        
        # Get final metrics
        train_loss, train_accuracy, train_auc = self.model.evaluate(
            X_train, y_train, verbose=0
        )
        
        metrics = {
            'train_accuracy': float(train_accuracy),
            'train_loss': float(train_loss),
            'train_auc': float(train_auc),
            'epochs_trained': len(self.history.history['loss']),
            'n_features': X_train.shape[1]
        }
        
        # Add validation metrics if available
        if 'val_accuracy' in self.history.history:
            metrics['val_accuracy'] = float(self.history.history['val_accuracy'][-1])
            metrics['val_loss'] = float(self.history.history['val_loss'][-1])
            metrics['val_auc'] = float(self.history.history['val_auc'][-1])
        
        logger.info(
            f"Neural Network trained - "
            f"Train Acc: {train_accuracy:.3f}, "
            f"Train AUC: {train_auc:.3f}, "
            f"Epochs: {metrics['epochs_trained']}"
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
        
        # Get probability and threshold at 0.5
        probability = self.model.predict(X, verbose=0)[0][0]
        prediction = 1 if probability >= 0.5 else 0
        
        return int(prediction)
    
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
        
        # Get probability for positive class
        prob_positive = float(self.model.predict(X, verbose=0)[0][0])
        prob_negative = 1.0 - prob_positive
        
        return prob_negative, prob_positive
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance using gradient-based method.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before getting feature importance")
        
        # Use gradient-based importance
        # Create a batch of zeros
        X_baseline = np.zeros((1, self.input_dim))
        
        with tf.GradientTape() as tape:
            X_tensor = tf.Variable(X_baseline, dtype=tf.float32)
            predictions = self.model(X_tensor)
        
        # Get gradients
        gradients = tape.gradient(predictions, X_tensor)
        importance_scores = np.abs(gradients.numpy()[0])
        
        # Normalize
        if importance_scores.sum() > 0:
            importance_scores = importance_scores / importance_scores.sum()
        
        # Create dictionary
        importance_dict = dict(zip(self.feature_names, importance_scores))
        sorted_importance = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_importance
    
    def save(self, filepath: str) -> None:
        """
        Save model to disk.
        
        Args:
            filepath: Path to save model (without extension)
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save Keras model
        model_path = f"{filepath}.keras"
        self.model.save(model_path)
        
        # Save metadata
        import json
        metadata = {
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'input_dim': self.input_dim,
            'hidden_layers': self.hidden_layers,
            'dropout_rate': self.dropout_rate,
            'learning_rate': self.learning_rate
        }
        
        metadata_path = f"{filepath}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        logger.info(f"Neural Network model saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """
        Load model from disk.
        
        Args:
            filepath: Path to load model from (without extension)
        """
        import json
        
        # Load Keras model
        model_path = f"{filepath}.keras"
        self.model = keras.models.load_model(model_path)
        
        # Load metadata
        metadata_path = f"{filepath}_metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.feature_names = metadata['feature_names']
        self.is_trained = metadata['is_trained']
        self.input_dim = metadata['input_dim']
        self.hidden_layers = metadata['hidden_layers']
        self.dropout_rate = metadata['dropout_rate']
        self.learning_rate = metadata['learning_rate']
        
        logger.info(f"Neural Network model loaded from {filepath}")
    
    def get_model_info(self) -> Dict:
        """
        Get model information.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            'model_type': 'NeuralNetwork',
            'hidden_layers': self.hidden_layers,
            'dropout_rate': self.dropout_rate,
            'learning_rate': self.learning_rate,
            'is_trained': self.is_trained,
            'n_features': len(self.feature_names) if self.feature_names else 0,
            'total_parameters': self.model.count_params() if self.model else 0
        }
