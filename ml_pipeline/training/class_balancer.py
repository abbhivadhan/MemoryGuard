"""
Class Imbalance Handling Module

Handles class imbalance in training data using SMOTE and class weights.
"""

import logging
from typing import Tuple, Dict, Optional
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.utils.class_weight import compute_class_weight

logger = logging.getLogger(__name__)


class ClassBalancer:
    """
    Handle class imbalance in training data.
    
    Provides methods to:
    - Calculate class distribution and imbalance ratio
    - Apply SMOTE when imbalance exceeds threshold
    - Compute class weights for model training
    """
    
    def __init__(self, imbalance_threshold: float = 3.0, random_state: int = 42):
        """
        Initialize ClassBalancer.
        
        Args:
            imbalance_threshold: Ratio threshold above which to apply SMOTE
            random_state: Random seed for reproducibility
        """
        self.imbalance_threshold = imbalance_threshold
        self.random_state = random_state
        logger.info(f"Initialized ClassBalancer with threshold: {imbalance_threshold}")
    
    def calculate_class_distribution(self, y: pd.Series) -> Dict:
        """
        Calculate class distribution statistics.
        
        Args:
            y: Target labels
            
        Returns:
            Dictionary with class counts, proportions, and imbalance ratio
        """
        class_counts = y.value_counts().to_dict()
        total = len(y)
        class_proportions = {k: v/total for k, v in class_counts.items()}
        
        # Calculate imbalance ratio (majority / minority)
        counts = list(class_counts.values())
        imbalance_ratio = max(counts) / min(counts) if min(counts) > 0 else float('inf')
        
        distribution = {
            'class_counts': class_counts,
            'class_proportions': class_proportions,
            'imbalance_ratio': imbalance_ratio,
            'total_samples': total
        }
        
        logger.info(f"Class distribution: {class_counts}")
        logger.info(f"Imbalance ratio: {imbalance_ratio:.2f}")
        
        return distribution
    
    def should_apply_smote(self, y: pd.Series) -> bool:
        """
        Determine if SMOTE should be applied based on imbalance ratio.
        
        Args:
            y: Target labels
            
        Returns:
            True if SMOTE should be applied, False otherwise
        """
        distribution = self.calculate_class_distribution(y)
        imbalance_ratio = distribution['imbalance_ratio']
        
        should_apply = imbalance_ratio > self.imbalance_threshold
        
        if should_apply:
            logger.info(
                f"Imbalance ratio {imbalance_ratio:.2f} exceeds threshold "
                f"{self.imbalance_threshold}. SMOTE will be applied."
            )
        else:
            logger.info(
                f"Imbalance ratio {imbalance_ratio:.2f} is below threshold "
                f"{self.imbalance_threshold}. SMOTE not needed."
            )
        
        return should_apply
    
    def apply_smote(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        sampling_strategy: str = 'auto',
        k_neighbors: int = 5
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Apply SMOTE to balance classes.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            sampling_strategy: SMOTE sampling strategy ('auto', 'minority', or dict)
            k_neighbors: Number of nearest neighbors for SMOTE
            
        Returns:
            Tuple of (resampled features, resampled labels)
        """
        logger.info("Applying SMOTE for class balancing")
        
        # Log original distribution
        original_dist = self.calculate_class_distribution(y)
        logger.info(f"Original samples: {original_dist['total_samples']}")
        
        # Apply SMOTE
        smote = SMOTE(
            sampling_strategy=sampling_strategy,
            k_neighbors=k_neighbors,
            random_state=self.random_state
        )
        
        X_resampled, y_resampled = smote.fit_resample(X, y)
        
        # Convert back to DataFrame/Series with original column names
        X_resampled = pd.DataFrame(X_resampled, columns=X.columns)
        y_resampled = pd.Series(y_resampled, name=y.name)
        
        # Log new distribution
        new_dist = self.calculate_class_distribution(y_resampled)
        logger.info(f"Resampled samples: {new_dist['total_samples']}")
        logger.info(f"New class distribution: {new_dist['class_counts']}")
        logger.info(f"New imbalance ratio: {new_dist['imbalance_ratio']:.2f}")
        
        return X_resampled, y_resampled
    
    def compute_class_weights(
        self,
        y: pd.Series,
        weight_type: str = 'balanced'
    ) -> Dict[int, float]:
        """
        Compute class weights for handling imbalance during training.
        
        Args:
            y: Target labels
            weight_type: Type of weighting ('balanced' or 'balanced_subsample')
            
        Returns:
            Dictionary mapping class labels to weights
        """
        logger.info(f"Computing class weights with type: {weight_type}")
        
        classes = np.unique(y)
        weights = compute_class_weight(
            class_weight=weight_type,
            classes=classes,
            y=y
        )
        
        class_weights = dict(zip(classes, weights))
        
        logger.info(f"Class weights: {class_weights}")
        
        return class_weights
    
    def balance_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        method: str = 'auto'
    ) -> Tuple[pd.DataFrame, pd.Series, Optional[Dict]]:
        """
        Balance data using appropriate method based on imbalance.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            method: Balancing method ('auto', 'smote', 'weights', 'none')
                   'auto' applies SMOTE if imbalance exceeds threshold
            
        Returns:
            Tuple of (features, labels, class_weights)
            If SMOTE is applied, returns resampled data with None for weights
            Otherwise returns original data with computed weights
        """
        distribution = self.calculate_class_distribution(y)
        
        if method == 'none':
            logger.info("No balancing applied")
            return X, y, None
        
        elif method == 'smote':
            X_balanced, y_balanced = self.apply_smote(X, y)
            return X_balanced, y_balanced, None
        
        elif method == 'weights':
            class_weights = self.compute_class_weights(y)
            return X, y, class_weights
        
        elif method == 'auto':
            if self.should_apply_smote(y):
                X_balanced, y_balanced = self.apply_smote(X, y)
                return X_balanced, y_balanced, None
            else:
                # Still compute weights for mild imbalance
                class_weights = self.compute_class_weights(y)
                return X, y, class_weights
        
        else:
            raise ValueError(
                f"Unknown balancing method: {method}. "
                "Choose from 'auto', 'smote', 'weights', 'none'"
            )
    
    def get_balanced_splits(
        self,
        splits: Dict,
        balance_train: bool = True,
        balance_val: bool = False
    ) -> Tuple[Dict, Optional[Dict]]:
        """
        Apply balancing to train and optionally validation splits.
        
        Args:
            splits: Dictionary with train/val/test splits
            balance_train: Whether to balance training data
            balance_val: Whether to balance validation data
            
        Returns:
            Tuple of (balanced_splits, class_weights)
        """
        balanced_splits = splits.copy()
        class_weights = None
        
        if balance_train:
            logger.info("Balancing training data")
            X_train, y_train, weights = self.balance_data(
                splits['X_train'],
                splits['y_train'],
                method='auto'
            )
            balanced_splits['X_train'] = X_train
            balanced_splits['y_train'] = y_train
            class_weights = weights
        
        if balance_val:
            logger.info("Balancing validation data")
            X_val, y_val, _ = self.balance_data(
                splits['X_val'],
                splits['y_val'],
                method='auto'
            )
            balanced_splits['X_val'] = X_val
            balanced_splits['y_val'] = y_val
        
        return balanced_splits, class_weights
