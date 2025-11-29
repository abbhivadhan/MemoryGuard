"""
Distribution monitoring for data drift detection
Tracks feature distributions over time and stores reference distributions
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from ml_pipeline.config.settings import settings
from ml_pipeline.data_storage.database import get_db
from ml_pipeline.data_storage.models import DataDriftReport

logger = logging.getLogger(__name__)


class DistributionMonitor:
    """
    Monitor and track feature distributions over time
    Stores reference distributions for drift detection
    """
    
    def __init__(self, reference_data: Optional[pd.DataFrame] = None):
        """
        Initialize distribution monitor
        
        Args:
            reference_data: Reference dataset for comparison (optional)
        """
        self.reference_data = reference_data
        self.reference_distributions = None
        self.distribution_history = []
        
        # Storage path for distribution history
        self.storage_path = settings.METADATA_PATH / "distributions"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        if reference_data is not None:
            self.reference_distributions = self._compute_distributions(reference_data)
            logger.info(f"Initialized with reference data: {len(reference_data)} samples")
    
    def set_reference_data(self, data: pd.DataFrame) -> None:
        """
        Set reference data and compute distributions
        
        Args:
            data: Reference dataset
        """
        self.reference_data = data
        self.reference_distributions = self._compute_distributions(data)
        
        # Save reference distributions
        self._save_reference_distributions()
        
        logger.info(f"Reference data set: {len(data)} samples, {len(data.columns)} features")
    
    def load_reference_distributions(self, reference_name: str = "latest") -> None:
        """
        Load reference distributions from storage
        
        Args:
            reference_name: Name of the reference distribution to load
        """
        filepath = self.storage_path / f"reference_{reference_name}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Reference distribution not found: {filepath}")
        
        with open(filepath, 'r') as f:
            self.reference_distributions = json.load(f)
        
        logger.info(f"Loaded reference distributions from {filepath}")
    
    def _save_reference_distributions(self) -> None:
        """Save reference distributions to storage"""
        if self.reference_distributions is None:
            logger.warning("No reference distributions to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save with timestamp
        filepath_timestamped = self.storage_path / f"reference_{timestamp}.json"
        with open(filepath_timestamped, 'w') as f:
            json.dump(self.reference_distributions, f, indent=2)
        
        # Save as latest
        filepath_latest = self.storage_path / "reference_latest.json"
        with open(filepath_latest, 'w') as f:
            json.dump(self.reference_distributions, f, indent=2)
        
        logger.info(f"Saved reference distributions to {filepath_timestamped}")
    
    def _compute_distributions(self, data: pd.DataFrame) -> Dict:
        """
        Compute distribution statistics for each feature
        
        Args:
            data: Dataset to compute distributions for
            
        Returns:
            Dictionary of distribution statistics per feature
        """
        distributions = {}
        
        for col in data.columns:
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(data[col]):
                continue
            
            # Remove NaN values for statistics
            col_data = data[col].dropna()
            
            if len(col_data) == 0:
                logger.warning(f"Column {col} has no valid data")
                continue
            
            distributions[col] = {
                'count': int(len(col_data)),
                'mean': float(col_data.mean()),
                'std': float(col_data.std()),
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'median': float(col_data.median()),
                'q25': float(col_data.quantile(0.25)),
                'q75': float(col_data.quantile(0.75)),
                'skewness': float(col_data.skew()),
                'kurtosis': float(col_data.kurtosis()),
            }
        
        return distributions
    
    def compute_current_distributions(self, data: pd.DataFrame) -> Dict:
        """
        Compute distributions for current data
        
        Args:
            data: Current dataset
            
        Returns:
            Dictionary of distribution statistics
        """
        return self._compute_distributions(data)
    
    def track_distributions(
        self,
        data: pd.DataFrame,
        dataset_name: str,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Track distributions for a dataset and store in history
        
        Args:
            data: Dataset to track
            dataset_name: Name/identifier for the dataset
            timestamp: Timestamp for the tracking (defaults to now)
            
        Returns:
            Computed distributions
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        distributions = self._compute_distributions(data)
        
        # Add to history
        history_entry = {
            'timestamp': timestamp.isoformat(),
            'dataset_name': dataset_name,
            'n_samples': len(data),
            'n_features': len(distributions),
            'distributions': distributions
        }
        
        self.distribution_history.append(history_entry)
        
        # Save to disk
        self._save_distribution_history(history_entry)
        
        logger.info(f"Tracked distributions for {dataset_name}: {len(data)} samples")
        
        return distributions
    
    def _save_distribution_history(self, entry: Dict) -> None:
        """
        Save distribution history entry to storage
        
        Args:
            entry: History entry to save
        """
        timestamp = entry['timestamp'].replace(':', '-').replace('.', '-')
        filepath = self.storage_path / f"history_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump(entry, f, indent=2)
    
    def load_distribution_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Load distribution history from storage
        
        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            List of distribution history entries
        """
        history = []
        
        for filepath in sorted(self.storage_path.glob("history_*.json")):
            with open(filepath, 'r') as f:
                entry = json.load(f)
            
            entry_time = datetime.fromisoformat(entry['timestamp'])
            
            # Filter by date range if specified
            if start_date and entry_time < start_date:
                continue
            if end_date and entry_time > end_date:
                continue
            
            history.append(entry)
        
        self.distribution_history = history
        logger.info(f"Loaded {len(history)} distribution history entries")
        
        return history
    
    def get_distribution_summary(self, feature_name: str) -> pd.DataFrame:
        """
        Get summary of distribution changes over time for a feature
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            DataFrame with distribution statistics over time
        """
        if not self.distribution_history:
            logger.warning("No distribution history available")
            return pd.DataFrame()
        
        summary_data = []
        
        for entry in self.distribution_history:
            if feature_name in entry['distributions']:
                dist = entry['distributions'][feature_name]
                summary_data.append({
                    'timestamp': entry['timestamp'],
                    'dataset_name': entry['dataset_name'],
                    'mean': dist['mean'],
                    'std': dist['std'],
                    'median': dist['median'],
                    'min': dist['min'],
                    'max': dist['max']
                })
        
        df = pd.DataFrame(summary_data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        return df
    
    def compare_distributions(
        self,
        current_data: pd.DataFrame,
        reference_distributions: Optional[Dict] = None
    ) -> Dict:
        """
        Compare current data distributions with reference
        
        Args:
            current_data: Current dataset
            reference_distributions: Reference distributions (uses stored if None)
            
        Returns:
            Dictionary with comparison results
        """
        if reference_distributions is None:
            reference_distributions = self.reference_distributions
        
        if reference_distributions is None:
            raise ValueError("No reference distributions available")
        
        current_distributions = self._compute_distributions(current_data)
        
        comparison = {}
        
        for feature in reference_distributions.keys():
            if feature not in current_distributions:
                logger.warning(f"Feature {feature} not in current data")
                continue
            
            ref = reference_distributions[feature]
            curr = current_distributions[feature]
            
            # Calculate relative changes
            mean_change = (curr['mean'] - ref['mean']) / (ref['std'] + 1e-10)
            std_change = (curr['std'] - ref['std']) / (ref['std'] + 1e-10)
            
            comparison[feature] = {
                'reference_mean': ref['mean'],
                'current_mean': curr['mean'],
                'mean_change': mean_change,
                'reference_std': ref['std'],
                'current_std': curr['std'],
                'std_change': std_change,
                'reference_median': ref['median'],
                'current_median': curr['median'],
            }
        
        return comparison
    
    def get_reference_distributions(self) -> Optional[Dict]:
        """
        Get stored reference distributions
        
        Returns:
            Reference distributions dictionary
        """
        return self.reference_distributions
    
    def clear_history(self) -> None:
        """Clear distribution history from memory"""
        self.distribution_history = []
        logger.info("Cleared distribution history from memory")
