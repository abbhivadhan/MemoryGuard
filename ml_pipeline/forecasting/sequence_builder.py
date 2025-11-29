"""
Sequence Builder

Prepares longitudinal patient data into time-series sequences for LSTM training.
Extracts patient visit sequences and creates time-series features.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SequenceBuilder:
    """
    Builds time-series sequences from longitudinal patient data.
    
    Handles:
    - Extracting patient visit sequences
    - Creating time-series features
    - Handling variable-length patient histories
    - Data normalization and preprocessing
    """
    
    def __init__(
        self,
        sequence_length: int = 4,
        forecast_horizons: List[int] = [6, 12, 24],
        min_visits_required: int = 5
    ):
        """
        Initialize the sequence builder.
        
        Args:
            sequence_length: Number of historical visits to use as input
            forecast_horizons: Months ahead to forecast (for target creation)
            min_visits_required: Minimum visits needed for a patient
        """
        self.sequence_length = sequence_length
        self.forecast_horizons = forecast_horizons
        self.min_visits_required = min_visits_required
        
        self.feature_columns = None
        self.scaler_params = None
        
        logger.info(
            f"Initialized SequenceBuilder with sequence_length={sequence_length}, "
            f"forecast_horizons={forecast_horizons}"
        )
    
    def prepare_sequences(
        self,
        data: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        visit_date_col: str = 'visit_date',
        target_col: str = 'mmse_score',
        feature_cols: Optional[List[str]] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare time-series sequences from longitudinal data.
        
        Args:
            data: DataFrame with longitudinal patient data
            patient_id_col: Column name for patient ID
            visit_date_col: Column name for visit date
            target_col: Column name for target variable (MMSE score)
            feature_cols: List of feature columns to use (if None, auto-detect)
            
        Returns:
            Tuple of (X, y, patient_ids) where:
            - X: Input sequences (n_samples, sequence_length, n_features)
            - y: Target values (n_samples, n_horizons)
            - patient_ids: List of patient IDs for each sequence
        """
        logger.info(f"Preparing sequences from {len(data)} records")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(data[visit_date_col]):
            data[visit_date_col] = pd.to_datetime(data[visit_date_col])
        
        # Auto-detect feature columns if not provided
        if feature_cols is None:
            exclude_cols = [patient_id_col, visit_date_col, target_col]
            feature_cols = [col for col in data.columns if col not in exclude_cols]
        
        self.feature_columns = feature_cols
        n_features = len(feature_cols)
        
        logger.info(f"Using {n_features} features: {feature_cols}")
        
        sequences = []
        targets = []
        sequence_patient_ids = []
        
        # Group by patient
        grouped = data.groupby(patient_id_col)
        
        patients_processed = 0
        patients_skipped = 0
        
        for patient_id, patient_data in grouped:
            # Sort by visit date
            patient_data = patient_data.sort_values(visit_date_col).reset_index(drop=True)
            
            # Skip if insufficient visits
            if len(patient_data) < self.min_visits_required:
                patients_skipped += 1
                continue
            
            # Extract sequences for this patient
            patient_sequences, patient_targets = self._extract_patient_sequences(
                patient_data,
                visit_date_col,
                target_col,
                feature_cols
            )
            
            if len(patient_sequences) > 0:
                sequences.extend(patient_sequences)
                targets.extend(patient_targets)
                sequence_patient_ids.extend([patient_id] * len(patient_sequences))
                patients_processed += 1
        
        logger.info(
            f"Processed {patients_processed} patients, skipped {patients_skipped} "
            f"(insufficient visits). Generated {len(sequences)} sequences."
        )
        
        if len(sequences) == 0:
            raise ValueError("No valid sequences generated from data")
        
        # Convert to numpy arrays
        X = np.array(sequences)
        y = np.array(targets)
        
        logger.info(f"Final shapes: X={X.shape}, y={y.shape}")
        
        return X, y, sequence_patient_ids
    
    def _extract_patient_sequences(
        self,
        patient_data: pd.DataFrame,
        visit_date_col: str,
        target_col: str,
        feature_cols: List[str]
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Extract all valid sequences from a single patient's data.
        
        Args:
            patient_data: DataFrame with single patient's visits
            visit_date_col: Column name for visit date
            target_col: Column name for target variable
            feature_cols: List of feature columns
            
        Returns:
            Tuple of (sequences, targets) for this patient
        """
        sequences = []
        targets = []
        
        n_visits = len(patient_data)
        
        # Slide window through patient history
        for i in range(n_visits - self.sequence_length):
            # Extract input sequence
            sequence_data = patient_data.iloc[i:i + self.sequence_length]
            sequence = sequence_data[feature_cols].values
            
            # Check for missing values in sequence
            if np.isnan(sequence).any():
                continue
            
            # Extract target values at future time points
            current_date = patient_data.iloc[i + self.sequence_length - 1][visit_date_col]
            
            target_values = []
            valid_target = True
            
            for horizon_months in self.forecast_horizons:
                # Find visit closest to target date
                target_date = current_date + pd.DateOffset(months=horizon_months)
                
                # Look for visits within ±2 months of target date
                future_visits = patient_data[patient_data[visit_date_col] > current_date]
                
                if len(future_visits) == 0:
                    valid_target = False
                    break
                
                # Find closest visit to target date
                time_diffs = abs((future_visits[visit_date_col] - target_date).dt.days)
                closest_idx = time_diffs.idxmin()
                
                # Only use if within 60 days (2 months) of target
                if time_diffs[closest_idx] > 60:
                    valid_target = False
                    break
                
                target_value = future_visits.loc[closest_idx, target_col]
                
                if pd.isna(target_value):
                    valid_target = False
                    break
                
                target_values.append(target_value)
            
            # Add sequence if all targets are valid
            if valid_target and len(target_values) == len(self.forecast_horizons):
                sequences.append(sequence)
                targets.append(target_values)
        
        return sequences, targets
    
    def create_temporal_features(
        self,
        data: pd.DataFrame,
        visit_date_col: str = 'visit_date',
        baseline_date_col: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Create temporal features from visit dates.
        
        Args:
            data: DataFrame with visit data
            visit_date_col: Column name for visit date
            baseline_date_col: Column for baseline date (if None, use first visit)
            
        Returns:
            DataFrame with added temporal features
        """
        data = data.copy()
        
        # Ensure datetime
        if not pd.api.types.is_datetime64_any_dtype(data[visit_date_col]):
            data[visit_date_col] = pd.to_datetime(data[visit_date_col])
        
        # Time since baseline
        if baseline_date_col and baseline_date_col in data.columns:
            data['months_since_baseline'] = (
                (data[visit_date_col] - data[baseline_date_col]).dt.days / 30.44
            )
        else:
            # Use first visit as baseline for each patient
            if 'patient_id' in data.columns:
                data['months_since_baseline'] = data.groupby('patient_id')[visit_date_col].transform(
                    lambda x: (x - x.min()).dt.days / 30.44
                )
            else:
                data['months_since_baseline'] = (
                    (data[visit_date_col] - data[visit_date_col].min()).dt.days / 30.44
                )
        
        # Age at visit (if age and baseline available)
        if 'age' in data.columns and 'months_since_baseline' in data.columns:
            data['age_at_visit'] = data['age'] + (data['months_since_baseline'] / 12)
        
        # Visit number
        if 'patient_id' in data.columns:
            data['visit_number'] = data.groupby('patient_id').cumcount() + 1
        
        logger.info(f"Created temporal features: {['months_since_baseline', 'age_at_visit', 'visit_number']}")
        
        return data
    
    def calculate_rate_of_change(
        self,
        data: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        visit_date_col: str = 'visit_date',
        value_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calculate rate of change for specified columns.
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Column name for patient ID
            visit_date_col: Column name for visit date
            value_cols: Columns to calculate rate of change for
            
        Returns:
            DataFrame with added rate of change features
        """
        data = data.copy()
        
        # Ensure sorted by patient and date
        data = data.sort_values([patient_id_col, visit_date_col])
        
        if value_cols is None:
            # Default to numeric columns
            value_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in [patient_id_col]]
        
        for col in value_cols:
            if col not in data.columns:
                continue
            
            # Calculate difference from previous visit
            data[f'{col}_change'] = data.groupby(patient_id_col)[col].diff()
            
            # Calculate time between visits (in months)
            data['time_diff_months'] = (
                data.groupby(patient_id_col)[visit_date_col]
                .diff()
                .dt.days / 30.44
            )
            
            # Calculate rate of change per month
            data[f'{col}_rate'] = data[f'{col}_change'] / data['time_diff_months']
            
            # Fill first visit with 0
            data[f'{col}_rate'] = data[f'{col}_rate'].fillna(0)
        
        # Drop temporary column
        if 'time_diff_months' in data.columns:
            data = data.drop('time_diff_months', axis=1)
        
        logger.info(f"Calculated rate of change for {len(value_cols)} features")
        
        return data
    
    def normalize_sequences(
        self,
        X: np.ndarray,
        fit: bool = True
    ) -> np.ndarray:
        """
        Normalize sequences using z-score normalization.
        
        Args:
            X: Input sequences (n_samples, sequence_length, n_features)
            fit: If True, fit scaler on data. If False, use existing scaler.
            
        Returns:
            Normalized sequences
        """
        n_samples, seq_len, n_features = X.shape
        
        # Reshape to 2D for normalization
        X_reshaped = X.reshape(-1, n_features)
        
        if fit:
            # Calculate mean and std
            self.scaler_params = {
                'mean': np.nanmean(X_reshaped, axis=0),
                'std': np.nanstd(X_reshaped, axis=0)
            }
            
            # Avoid division by zero
            self.scaler_params['std'] = np.where(
                self.scaler_params['std'] == 0,
                1.0,
                self.scaler_params['std']
            )
        
        if self.scaler_params is None:
            raise ValueError("Scaler not fitted. Call with fit=True first.")
        
        # Normalize
        X_normalized = (X_reshaped - self.scaler_params['mean']) / self.scaler_params['std']
        
        # Reshape back to 3D
        X_normalized = X_normalized.reshape(n_samples, seq_len, n_features)
        
        logger.info(f"Normalized sequences with shape {X_normalized.shape}")
        
        return X_normalized
    
    def split_sequences(
        self,
        X: np.ndarray,
        y: np.ndarray,
        patient_ids: List[str],
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        random_state: int = 42
    ) -> Dict[str, np.ndarray]:
        """
        Split sequences into train/val/test sets by patient.
        
        Ensures all sequences from same patient stay in same split.
        
        Args:
            X: Input sequences
            y: Target values
            patient_ids: List of patient IDs for each sequence
            train_ratio: Proportion for training
            val_ratio: Proportion for validation
            test_ratio: Proportion for testing
            random_state: Random seed
            
        Returns:
            Dictionary with train/val/test splits
        """
        np.random.seed(random_state)
        
        # Get unique patients
        unique_patients = list(set(patient_ids))
        n_patients = len(unique_patients)
        
        # Shuffle patients
        np.random.shuffle(unique_patients)
        
        # Calculate split indices
        train_end = int(n_patients * train_ratio)
        val_end = train_end + int(n_patients * val_ratio)
        
        train_patients = set(unique_patients[:train_end])
        val_patients = set(unique_patients[train_end:val_end])
        test_patients = set(unique_patients[val_end:])
        
        # Create masks
        train_mask = np.array([pid in train_patients for pid in patient_ids])
        val_mask = np.array([pid in val_patients for pid in patient_ids])
        test_mask = np.array([pid in test_patients for pid in patient_ids])
        
        splits = {
            'X_train': X[train_mask],
            'y_train': y[train_mask],
            'X_val': X[val_mask],
            'y_val': y[val_mask],
            'X_test': X[test_mask],
            'y_test': y[test_mask]
        }
        
        logger.info(
            f"Split data: train={len(splits['X_train'])} ({len(train_patients)} patients), "
            f"val={len(splits['X_val'])} ({len(val_patients)} patients), "
            f"test={len(splits['X_test'])} ({len(test_patients)} patients)"
        )
        
        return splits
