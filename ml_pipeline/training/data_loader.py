"""
Data Loading and Splitting Module

Handles loading processed features from the feature store and creating
stratified train-validation-test splits for ML model training.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Load processed features from feature store and create train-test splits.
    
    Implements stratified splitting to maintain class distribution across splits.
    """
    
    def __init__(self, feature_store_path: Path):
        """
        Initialize DataLoader.
        
        Args:
            feature_store_path: Path to the feature store directory
        """
        self.feature_store_path = Path(feature_store_path)
        logger.info(f"Initialized DataLoader with feature store: {feature_store_path}")
    
    def load_features(
        self,
        dataset_name: str = "train_features",
        target_column: str = "diagnosis"
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Load processed features from feature store.
        
        Args:
            dataset_name: Name of the dataset file (without extension)
            target_column: Name of the target column
            
        Returns:
            Tuple of (features DataFrame, target Series)
            
        Raises:
            FileNotFoundError: If feature file doesn't exist
            ValueError: If target column not found
        """
        feature_file = self.feature_store_path / f"{dataset_name}.parquet"
        
        if not feature_file.exists():
            raise FileNotFoundError(
                f"Feature file not found: {feature_file}. "
                "Please run feature engineering pipeline first."
            )
        
        logger.info(f"Loading features from {feature_file}")
        
        # Load features
        data = pd.read_parquet(feature_file)
        logger.info(f"Loaded {len(data)} samples with {len(data.columns)} columns")
        
        # Separate features and target
        if target_column not in data.columns:
            raise ValueError(
                f"Target column '{target_column}' not found in dataset. "
                f"Available columns: {list(data.columns)}"
            )
        
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")
        logger.info(f"Class distribution: {y.value_counts().to_dict()}")
        
        return X, y
    
    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.15,
        val_size: float = 0.18,
        random_state: int = 42,
        stratify: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Create stratified train-validation-test split.
        
        The data is split into:
        - Training set: ~70% of data
        - Validation set: ~15% of data
        - Test set: ~15% of data
        
        Args:
            X: Feature DataFrame
            y: Target Series
            test_size: Proportion of data for test set
            val_size: Proportion of remaining data for validation set
            random_state: Random seed for reproducibility
            stratify: Whether to use stratified splitting
            
        Returns:
            Dictionary containing train, validation, and test splits:
            {
                'X_train': Training features,
                'y_train': Training labels,
                'X_val': Validation features,
                'y_val': Validation labels,
                'X_test': Test features,
                'y_test': Test labels
            }
        """
        logger.info("Creating stratified train-validation-test split")
        logger.info(f"Test size: {test_size}, Validation size: {val_size}")
        
        # First split: separate test set
        stratify_test = y if stratify else None
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=test_size,
            stratify=stratify_test,
            random_state=random_state
        )
        
        # Second split: separate validation from training
        stratify_val = y_temp if stratify else None
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size,
            stratify=stratify_val,
            random_state=random_state
        )
        
        # Log split statistics
        logger.info(f"Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
        logger.info(f"Validation set: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%)")
        logger.info(f"Test set: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
        
        # Log class distributions
        logger.info(f"Training class distribution: {y_train.value_counts().to_dict()}")
        logger.info(f"Validation class distribution: {y_val.value_counts().to_dict()}")
        logger.info(f"Test class distribution: {y_test.value_counts().to_dict()}")
        
        return {
            'X_train': X_train,
            'y_train': y_train,
            'X_val': X_val,
            'y_val': y_val,
            'X_test': X_test,
            'y_test': y_test
        }
    
    def load_and_split(
        self,
        dataset_name: str = "train_features",
        target_column: str = "diagnosis",
        test_size: float = 0.15,
        val_size: float = 0.18,
        random_state: int = 42
    ) -> Dict[str, pd.DataFrame]:
        """
        Convenience method to load features and create splits in one call.
        
        Args:
            dataset_name: Name of the dataset file
            target_column: Name of the target column
            test_size: Proportion for test set
            val_size: Proportion for validation set
            random_state: Random seed
            
        Returns:
            Dictionary with train, validation, and test splits
        """
        X, y = self.load_features(dataset_name, target_column)
        return self.split_data(X, y, test_size, val_size, random_state)
    
    def get_feature_names(self, X: pd.DataFrame) -> list:
        """
        Get list of feature names.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            List of feature column names
        """
        return list(X.columns)
    
    def get_dataset_info(self, splits: Dict) -> Dict:
        """
        Get summary information about the dataset splits.
        
        Args:
            splits: Dictionary containing data splits
            
        Returns:
            Dictionary with dataset statistics
        """
        info = {
            'n_features': splits['X_train'].shape[1],
            'n_train_samples': len(splits['X_train']),
            'n_val_samples': len(splits['X_val']),
            'n_test_samples': len(splits['X_test']),
            'train_class_dist': splits['y_train'].value_counts().to_dict(),
            'val_class_dist': splits['y_val'].value_counts().to_dict(),
            'test_class_dist': splits['y_test'].value_counts().to_dict(),
            'feature_names': self.get_feature_names(splits['X_train'])
        }
        
        return info
