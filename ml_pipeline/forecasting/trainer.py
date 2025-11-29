"""
Progression Forecasting Trainer

Orchestrates the training of progression forecasting models including
data preparation, model training, and evaluation.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import json
from datetime import datetime

from .progression_forecaster import ProgressionForecaster
from .sequence_builder import SequenceBuilder

logger = logging.getLogger(__name__)


class ProgressionForecastingTrainer:
    """
    Trainer for progression forecasting models.
    
    Handles:
    - Loading and preparing longitudinal data
    - Training LSTM models with early stopping
    - Generating multi-horizon forecasts (6, 12, 24 months)
    - Incorporating baseline features
    - Model evaluation and validation
    """
    
    def __init__(
        self,
        sequence_length: int = 4,
        forecast_horizons: List[int] = [6, 12, 24],
        lstm_units: List[int] = [128, 64],
        dropout_rate: float = 0.3,
        learning_rate: float = 0.001,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize the trainer.
        
        Args:
            sequence_length: Number of historical visits to use
            forecast_horizons: Months ahead to forecast
            lstm_units: LSTM layer sizes
            dropout_rate: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
            output_dir: Directory to save models and results
        """
        self.sequence_length = sequence_length
        self.forecast_horizons = forecast_horizons
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        
        self.output_dir = Path(output_dir) if output_dir else Path('ml_pipeline/models/forecasting')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.sequence_builder = SequenceBuilder(
            sequence_length=sequence_length,
            forecast_horizons=forecast_horizons
        )
        
        self.forecaster = None
        self.training_history = None
        self.feature_columns = None
        
        logger.info(f"Initialized ProgressionForecastingTrainer with output_dir={self.output_dir}")
    
    def prepare_data(
        self,
        data: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        visit_date_col: str = 'visit_date',
        target_col: str = 'mmse_score',
        feature_cols: Optional[List[str]] = None,
        add_temporal_features: bool = True,
        add_rate_features: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Prepare longitudinal data for training.
        
        Args:
            data: DataFrame with longitudinal patient data
            patient_id_col: Column name for patient ID
            visit_date_col: Column name for visit date
            target_col: Column name for target (MMSE score)
            feature_cols: Feature columns to use
            add_temporal_features: Whether to add temporal features
            add_rate_features: Whether to add rate of change features
            
        Returns:
            Dictionary with train/val/test splits
        """
        logger.info(f"Preparing data from {len(data)} records")
        
        # Add temporal features
        if add_temporal_features:
            data = self.sequence_builder.create_temporal_features(
                data,
                visit_date_col=visit_date_col
            )
        
        # Add rate of change features
        if add_rate_features:
            rate_cols = [target_col, 'csf_ab42', 'csf_tau', 'hippocampus_volume'] \
                if all(col in data.columns for col in ['csf_ab42', 'csf_tau', 'hippocampus_volume']) \
                else [target_col]
            
            data = self.sequence_builder.calculate_rate_of_change(
                data,
                patient_id_col=patient_id_col,
                visit_date_col=visit_date_col,
                value_cols=rate_cols
            )
        
        # Prepare sequences
        X, y, patient_ids = self.sequence_builder.prepare_sequences(
            data,
            patient_id_col=patient_id_col,
            visit_date_col=visit_date_col,
            target_col=target_col,
            feature_cols=feature_cols
        )
        
        self.feature_columns = self.sequence_builder.feature_columns
        
        # Normalize sequences
        X_normalized = self.sequence_builder.normalize_sequences(X, fit=True)
        
        # Split into train/val/test
        splits = self.sequence_builder.split_sequences(
            X_normalized,
            y,
            patient_ids,
            train_ratio=0.7,
            val_ratio=0.15,
            test_ratio=0.15
        )
        
        logger.info(f"Data preparation complete. Using {len(self.feature_columns)} features.")
        
        return splits
    
    def train(
        self,
        data_splits: Dict[str, np.ndarray],
        epochs: int = 100,
        batch_size: int = 32,
        early_stopping_patience: int = 15,
        save_best_model: bool = True
    ) -> Dict:
        """
        Train the progression forecasting model.
        
        Args:
            data_splits: Dictionary with train/val/test data
            epochs: Maximum training epochs
            batch_size: Batch size for training
            early_stopping_patience: Patience for early stopping
            save_best_model: Whether to save the best model
            
        Returns:
            Dictionary with training results and metrics
        """
        logger.info("Starting model training")
        
        # Extract data
        X_train = data_splits['X_train']
        y_train = data_splits['y_train']
        X_val = data_splits['X_val']
        y_val = data_splits['y_val']
        
        # Initialize forecaster
        n_features = X_train.shape[2]
        
        self.forecaster = ProgressionForecaster(
            sequence_length=self.sequence_length,
            n_features=n_features,
            lstm_units=self.lstm_units,
            dropout_rate=self.dropout_rate,
            learning_rate=self.learning_rate,
            forecast_horizons=self.forecast_horizons
        )
        
        # Build model
        self.forecaster.build_model()
        
        # Train model
        model_save_path = self.output_dir / 'best_model.h5' if save_best_model else None
        
        training_result = self.forecaster.train(
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
            epochs=epochs,
            batch_size=batch_size,
            early_stopping_patience=early_stopping_patience,
            model_save_path=model_save_path
        )
        
        self.training_history = training_result
        
        # Evaluate on test set
        if 'X_test' in data_splits and 'y_test' in data_splits:
            test_metrics = self.evaluate(
                data_splits['X_test'],
                data_splits['y_test']
            )
            training_result['test_metrics'] = test_metrics
        
        # Save training metadata
        self._save_training_metadata(training_result)
        
        logger.info("Training complete")
        
        return training_result
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate the trained model on test data.
        
        Args:
            X_test: Test sequences
            y_test: Test targets
            
        Returns:
            Dictionary with evaluation metrics
        """
        if self.forecaster is None or self.forecaster.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        logger.info(f"Evaluating model on {len(X_test)} test samples")
        
        # Generate predictions
        predictions = self.forecaster.predict(X_test, return_dict=False)
        
        # Calculate metrics for each horizon
        metrics = {}
        
        for i, horizon in enumerate(self.forecast_horizons):
            y_true = y_test[:, i]
            y_pred = predictions[:, i]
            
            # Mean Absolute Error
            mae = np.mean(np.abs(y_true - y_pred))
            
            # Mean Squared Error
            mse = np.mean((y_true - y_pred) ** 2)
            
            # Root Mean Squared Error
            rmse = np.sqrt(mse)
            
            # Mean Absolute Percentage Error
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            
            # R-squared
            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            metrics[f'{horizon}_month_mae'] = float(mae)
            metrics[f'{horizon}_month_mse'] = float(mse)
            metrics[f'{horizon}_month_rmse'] = float(rmse)
            metrics[f'{horizon}_month_mape'] = float(mape)
            metrics[f'{horizon}_month_r2'] = float(r2)
        
        # Overall metrics
        overall_mae = np.mean([metrics[f'{h}_month_mae'] for h in self.forecast_horizons])
        overall_rmse = np.mean([metrics[f'{h}_month_rmse'] for h in self.forecast_horizons])
        
        metrics['overall_mae'] = float(overall_mae)
        metrics['overall_rmse'] = float(overall_rmse)
        
        logger.info(f"Evaluation complete. Overall MAE: {overall_mae:.3f}")
        
        return metrics
    
    def forecast_patient(
        self,
        patient_history: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        visit_date_col: str = 'visit_date'
    ) -> Dict[str, float]:
        """
        Generate forecast for a single patient.
        
        Args:
            patient_history: DataFrame with patient's visit history
            patient_id_col: Column name for patient ID
            visit_date_col: Column name for visit date
            
        Returns:
            Dictionary with forecasted MMSE scores at 6, 12, 24 months
        """
        if self.forecaster is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if self.feature_columns is None:
            raise ValueError("Feature columns not set. Train model first.")
        
        # Ensure patient has enough visits
        if len(patient_history) < self.sequence_length:
            raise ValueError(
                f"Patient has {len(patient_history)} visits, "
                f"but {self.sequence_length} required"
            )
        
        # Sort by date
        patient_history = patient_history.sort_values(visit_date_col)
        
        # Generate forecast
        forecast = self.forecaster.forecast_single_patient(
            patient_history,
            self.feature_columns
        )
        
        return forecast
    
    def update_forecast(
        self,
        patient_history: pd.DataFrame,
        new_assessment: pd.DataFrame,
        visit_date_col: str = 'visit_date'
    ) -> Dict[str, float]:
        """
        Update forecast with new assessment data.
        
        Args:
            patient_history: DataFrame with patient's historical visits
            new_assessment: DataFrame with new assessment data
            visit_date_col: Column name for visit date
            
        Returns:
            Updated forecast dictionary
        """
        # Combine history with new assessment
        updated_history = pd.concat([patient_history, new_assessment], ignore_index=True)
        
        # Sort by date
        updated_history = updated_history.sort_values(visit_date_col)
        
        # Generate updated forecast
        updated_forecast = self.forecast_patient(updated_history)
        
        logger.info("Forecast updated with new assessment data")
        
        return updated_forecast
    
    def save_model(self, path: Optional[Path] = None):
        """Save the trained model."""
        if self.forecaster is None:
            raise ValueError("No model to save")
        
        save_path = path if path else self.output_dir / 'final_model.h5'
        self.forecaster.save_model(save_path)
        
        # Save feature columns
        feature_path = save_path.parent / 'feature_columns.json'
        with open(feature_path, 'w') as f:
            json.dump({
                'feature_columns': self.feature_columns,
                'sequence_length': self.sequence_length,
                'forecast_horizons': self.forecast_horizons
            }, f, indent=2)
        
        logger.info(f"Model and metadata saved to {save_path.parent}")
    
    def load_model(self, path: Path):
        """Load a trained model."""
        model_path = Path(path)
        
        # Load model
        self.forecaster = ProgressionForecaster(
            sequence_length=self.sequence_length,
            n_features=len(self.feature_columns) if self.feature_columns else 20,
            lstm_units=self.lstm_units,
            dropout_rate=self.dropout_rate,
            learning_rate=self.learning_rate,
            forecast_horizons=self.forecast_horizons
        )
        
        self.forecaster.load_model(model_path)
        
        # Load feature columns
        feature_path = model_path.parent / 'feature_columns.json'
        if feature_path.exists():
            with open(feature_path, 'r') as f:
                metadata = json.load(f)
                self.feature_columns = metadata['feature_columns']
                self.sequence_length = metadata['sequence_length']
                self.forecast_horizons = metadata['forecast_horizons']
        
        logger.info(f"Model loaded from {model_path}")
    
    def _save_training_metadata(self, training_result: Dict):
        """Save training metadata to JSON file."""
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'sequence_length': self.sequence_length,
            'forecast_horizons': self.forecast_horizons,
            'lstm_units': self.lstm_units,
            'dropout_rate': self.dropout_rate,
            'learning_rate': self.learning_rate,
            'n_features': len(self.feature_columns) if self.feature_columns else None,
            'feature_columns': self.feature_columns,
            'metrics': training_result.get('metrics', {}),
            'test_metrics': training_result.get('test_metrics', {})
        }
        
        metadata_path = self.output_dir / 'training_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Training metadata saved to {metadata_path}")
