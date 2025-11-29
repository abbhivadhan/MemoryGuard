"""
Progression Forecaster

Implements LSTM-based time-series forecasting for Alzheimer's Disease progression.
Predicts future cognitive scores (MMSE) at 6, 12, and 24 month horizons.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Bidirectional
    from tensorflow.keras.models import Model
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
    from tensorflow.keras.optimizers import Adam
except ImportError:
    raise ImportError("TensorFlow is required for progression forecasting. Install with: pip install tensorflow")

logger = logging.getLogger(__name__)


class ProgressionForecaster:
    """
    LSTM-based forecaster for disease progression prediction.
    
    Predicts future MMSE scores at multiple time horizons (6, 12, 24 months)
    using longitudinal patient data including cognitive scores, biomarkers,
    and imaging features.
    """
    
    def __init__(
        self,
        sequence_length: int = 4,
        n_features: int = 20,
        lstm_units: List[int] = [128, 64],
        dropout_rate: float = 0.3,
        learning_rate: float = 0.001,
        forecast_horizons: List[int] = [6, 12, 24]
    ):
        """
        Initialize the progression forecaster.
        
        Args:
            sequence_length: Number of historical visits to use
            n_features: Number of input features per visit
            lstm_units: List of LSTM layer sizes
            dropout_rate: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
            forecast_horizons: Months ahead to forecast (default: 6, 12, 24)
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.forecast_horizons = forecast_horizons
        self.n_horizons = len(forecast_horizons)
        
        self.model = None
        self.history = None
        self.feature_names = None
        
        logger.info(
            f"Initialized ProgressionForecaster with sequence_length={sequence_length}, "
            f"n_features={n_features}, lstm_units={lstm_units}"
        )
    
    def build_model(self) -> Model:
        """
        Build LSTM model architecture with multiple layers and dropout.
        
        Architecture:
        - Input: (sequence_length, n_features)
        - Multiple LSTM layers with dropout
        - Dense layers for multi-horizon forecasting
        - Output: 3 values (6, 12, 24 month MMSE predictions)
        
        Returns:
            Compiled Keras model
        """
        # Input layer
        inputs = Input(shape=(self.sequence_length, self.n_features), name='sequence_input')
        
        # First LSTM layer (return sequences for stacking)
        x = LSTM(
            self.lstm_units[0],
            return_sequences=len(self.lstm_units) > 1,
            name='lstm_1'
        )(inputs)
        x = Dropout(self.dropout_rate, name='dropout_1')(x)
        
        # Additional LSTM layers
        for i, units in enumerate(self.lstm_units[1:], start=2):
            return_seq = i < len(self.lstm_units)
            x = LSTM(
                units,
                return_sequences=return_seq,
                name=f'lstm_{i}'
            )(x)
            x = Dropout(self.dropout_rate, name=f'dropout_{i}')(x)
        
        # Dense layers for forecasting
        x = Dense(64, activation='relu', name='dense_1')(x)
        x = Dropout(self.dropout_rate / 2, name='dropout_dense')(x)
        x = Dense(32, activation='relu', name='dense_2')(x)
        
        # Output layer: predict MMSE scores at multiple horizons
        outputs = Dense(
            self.n_horizons,
            activation='linear',
            name='forecast_output'
        )(x)
        
        # Create model
        model = Model(inputs=inputs, outputs=outputs, name='progression_forecaster')
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae', 'mse']
        )
        
        self.model = model
        
        logger.info(f"Built LSTM model with {model.count_params()} parameters")
        logger.info(f"Model architecture:\n{model.summary()}")
        
        return model
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 100,
        batch_size: int = 32,
        early_stopping_patience: int = 15,
        model_save_path: Optional[Path] = None
    ) -> Dict:
        """
        Train the LSTM forecasting model.
        
        Args:
            X_train: Training sequences (n_samples, sequence_length, n_features)
            y_train: Training targets (n_samples, n_horizons)
            X_val: Validation sequences
            y_val: Validation targets
            epochs: Maximum number of training epochs
            batch_size: Batch size for training
            early_stopping_patience: Patience for early stopping
            model_save_path: Path to save best model
            
        Returns:
            Dictionary with training history and metrics
        """
        if self.model is None:
            self.build_model()
        
        logger.info(
            f"Training progression forecaster on {len(X_train)} samples "
            f"for {epochs} epochs with batch_size={batch_size}"
        )
        
        # Prepare callbacks
        callbacks = []
        
        # Early stopping
        early_stop = EarlyStopping(
            monitor='val_loss' if X_val is not None else 'loss',
            patience=early_stopping_patience,
            restore_best_weights=True,
            verbose=1
        )
        callbacks.append(early_stop)
        
        # Model checkpoint
        if model_save_path:
            model_save_path = Path(model_save_path)
            model_save_path.parent.mkdir(parents=True, exist_ok=True)
            
            checkpoint = ModelCheckpoint(
                str(model_save_path),
                monitor='val_loss' if X_val is not None else 'loss',
                save_best_only=True,
                verbose=1
            )
            callbacks.append(checkpoint)
        
        # Learning rate reduction
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss' if X_val is not None else 'loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        )
        callbacks.append(reduce_lr)
        
        # Train model
        validation_data = (X_val, y_val) if X_val is not None and y_val is not None else None
        
        history = self.model.fit(
            X_train,
            y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        self.history = history.history
        
        # Calculate final metrics
        train_loss, train_mae, train_mse = self.model.evaluate(X_train, y_train, verbose=0)
        
        metrics = {
            'train_loss': float(train_loss),
            'train_mae': float(train_mae),
            'train_mse': float(train_mse),
            'epochs_trained': len(history.history['loss'])
        }
        
        if validation_data:
            val_loss, val_mae, val_mse = self.model.evaluate(X_val, y_val, verbose=0)
            metrics.update({
                'val_loss': float(val_loss),
                'val_mae': float(val_mae),
                'val_mse': float(val_mse)
            })
        
        logger.info(f"Training complete. Final metrics: {metrics}")
        
        return {
            'history': self.history,
            'metrics': metrics
        }
    
    def predict(
        self,
        X: np.ndarray,
        return_dict: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Generate progression forecasts for input sequences.
        
        Args:
            X: Input sequences (n_samples, sequence_length, n_features)
            return_dict: If True, return dict with horizon labels
            
        Returns:
            Dictionary mapping horizon (e.g., '6_month') to predictions
            or raw numpy array if return_dict=False
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = self.model.predict(X, verbose=0)
        
        if not return_dict:
            return predictions
        
        # Format as dictionary
        result = {}
        for i, horizon in enumerate(self.forecast_horizons):
            result[f'{horizon}_month_mmse'] = predictions[:, i]
        
        return result
    
    def forecast_single_patient(
        self,
        patient_history: pd.DataFrame,
        feature_columns: List[str]
    ) -> Dict[str, float]:
        """
        Generate forecast for a single patient.
        
        Args:
            patient_history: DataFrame with patient's visit history
            feature_columns: List of feature column names
            
        Returns:
            Dictionary with forecasted MMSE scores
        """
        # Extract last sequence_length visits
        if len(patient_history) < self.sequence_length:
            raise ValueError(
                f"Patient history has {len(patient_history)} visits, "
                f"but {self.sequence_length} required"
            )
        
        # Get most recent visits
        recent_visits = patient_history.tail(self.sequence_length)
        
        # Extract features
        sequence = recent_visits[feature_columns].values
        
        # Reshape for model input
        sequence = sequence.reshape(1, self.sequence_length, -1)
        
        # Generate forecast
        predictions = self.predict(sequence, return_dict=True)
        
        # Extract single values
        result = {k: float(v[0]) for k, v in predictions.items()}
        
        logger.info(f"Generated forecast: {result}")
        
        return result
    
    def save_model(self, path: Path):
        """Save the trained model."""
        if self.model is None:
            raise ValueError("No model to save")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        self.model.save(str(path))
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: Path):
        """Load a trained model."""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        self.model = keras.models.load_model(str(path))
        logger.info(f"Model loaded from {path}")
    
    def get_model_summary(self) -> str:
        """Get model architecture summary."""
        if self.model is None:
            return "Model not built yet"
        
        from io import StringIO
        stream = StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
        return stream.getvalue()
