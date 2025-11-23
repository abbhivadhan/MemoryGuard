"""
Script to prepare real Alzheimer's dataset for ML model training.

This script:
1. Sources de-identified Alzheimer's datasets (ADNI, OASIS, etc.)
2. Cleans and preprocesses the data
3. Splits into train/validation/test sets
4. Saves processed data for model training

Usage:
    python scripts/prepare_training_data.py --data-source <path> --output-dir <path>
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlzheimerDatasetPreparator:
    """
    Prepares Alzheimer's disease datasets for ML training.
    """
    
    def __init__(self):
        self.label_encoders = {}
        self.feature_columns = []
        self.target_column = 'diagnosis'
        
    def load_adni_format(self, filepath: str) -> pd.DataFrame:
        """
        Load dataset in ADNI format.
        
        ADNI (Alzheimer's Disease Neuroimaging Initiative) format includes:
        - Subject ID
        - Demographics (age, gender, education)
        - Cognitive scores (MMSE, ADAS, CDR)
        - Biomarkers (CSF, plasma)
        - Imaging metrics (MRI volumes)
        - Diagnosis label
        
        Args:
            filepath: Path to ADNI CSV file
            
        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading ADNI format data from {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} samples with {len(df.columns)} features")
            return df
        except Exception as e:
            logger.error(f"Error loading ADNI data: {str(e)}")
            raise
    
    def load_oasis_format(self, filepath: str) -> pd.DataFrame:
        """
        Load dataset in OASIS format.
        
        OASIS (Open Access Series of Imaging Studies) format includes:
        - Subject ID
        - Demographics
        - Clinical assessments
        - MRI measurements
        - Diagnosis
        
        Args:
            filepath: Path to OASIS CSV file
            
        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading OASIS format data from {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} samples with {len(df.columns)} features")
            return df
        except Exception as e:
            logger.error(f"Error loading OASIS data: {str(e)}")
            raise
    
    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names across different dataset formats.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized column names
        """
        # Common column name mappings
        column_mappings = {
            # Demographics
            'AGE': 'age',
            'Age': 'age',
            'PTAGE': 'age',
            'GENDER': 'gender',
            'Gender': 'gender',
            'PTGENDER': 'gender',
            'SEX': 'gender',
            'EDUC': 'education_years',
            'Education': 'education_years',
            'PTEDUCAT': 'education_years',
            
            # Cognitive scores
            'MMSE': 'mmse_score',
            'MMSCORE': 'mmse_score',
            'MoCA': 'moca_score',
            'MOCASCORE': 'moca_score',
            'CDR': 'cdr_score',
            'CDRSCORE': 'cdr_score',
            'CDGLOBAL': 'cdr_score',
            
            # Biomarkers
            'ABETA': 'csf_abeta42',
            'ABETA42': 'csf_abeta42',
            'TAU': 'csf_tau',
            'TOTALTAU': 'csf_tau',
            'PTAU': 'csf_ptau',
            'PTAU181': 'csf_ptau',
            
            # Imaging
            'Hippocampus': 'hippocampal_volume',
            'HIPPO': 'hippocampal_volume',
            'Entorhinal': 'entorhinal_thickness',
            'ENTORHINAL': 'entorhinal_thickness',
            'WholeBrain': 'whole_brain_volume',
            'Ventricles': 'ventricular_volume',
            
            # Genetics
            'APOE4': 'apoe4_alleles',
            'APOE': 'apoe4_alleles',
            
            # Diagnosis
            'DX': 'diagnosis',
            'Diagnosis': 'diagnosis',
            'GROUP': 'diagnosis',
            'Group': 'diagnosis',
        }
        
        # Rename columns
        df = df.rename(columns=column_mappings)
        
        # Convert column names to lowercase and replace spaces
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        logger.info(f"Standardized column names: {list(df.columns)}")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning data...")
        
        initial_rows = len(df)
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle missing diagnosis labels
        if 'diagnosis' in df.columns:
            df = df.dropna(subset=['diagnosis'])
            logger.info(f"Removed rows with missing diagnosis: {len(df)} rows remaining")
        
        # Standardize diagnosis labels
        df = self._standardize_diagnosis_labels(df)
        
        # Handle gender encoding
        if 'gender' in df.columns:
            df['gender'] = df['gender'].map({
                'M': 0, 'Male': 0, 'male': 0, 1: 0,
                'F': 1, 'Female': 1, 'female': 1, 2: 1
            })
        
        # Handle APOE4 encoding
        if 'apoe4_alleles' in df.columns:
            # Convert to number of APOE4 alleles (0, 1, or 2)
            df['apoe4_alleles'] = pd.to_numeric(df['apoe4_alleles'], errors='coerce')
            df['apoe4_alleles'] = df['apoe4_alleles'].clip(0, 2)
        
        # Remove outliers for numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col != 'diagnosis':
                df = self._remove_outliers(df, col)
        
        logger.info(f"Data cleaning complete: {len(df)} samples remaining")
        
        return df
    
    def _standardize_diagnosis_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize diagnosis labels to binary classification.
        
        0 = Cognitively Normal (CN)
        1 = Alzheimer's Disease (AD, including MCI that converts to AD)
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized diagnosis labels
        """
        if 'diagnosis' not in df.columns:
            return df
        
        # Map various diagnosis labels to binary
        diagnosis_mapping = {
            # Normal
            'CN': 0,
            'Normal': 0,
            'Nondemented': 0,
            'Control': 0,
            'NL': 0,
            0: 0,
            
            # Alzheimer's Disease
            'AD': 1,
            'Alzheimer': 1,
            'Demented': 1,
            'Dementia': 1,
            1: 1,
            
            # MCI - treat as intermediate (we'll handle separately)
            'MCI': 0.5,
            'LMCI': 0.5,
            'EMCI': 0.5,
            'SMC': 0.5,
        }
        
        # Apply mapping
        df['diagnosis'] = df['diagnosis'].map(diagnosis_mapping)
        
        # For MCI cases, we can either:
        # 1. Remove them (conservative)
        # 2. Include them as negative class (less conservative)
        # 3. Use longitudinal data to determine conversion
        
        # For now, treat MCI as negative class (0)
        df['diagnosis'] = df['diagnosis'].replace(0.5, 0)
        
        # Remove any unmapped values
        df = df.dropna(subset=['diagnosis'])
        
        # Convert to integer
        df['diagnosis'] = df['diagnosis'].astype(int)
        
        logger.info(f"Diagnosis distribution: {df['diagnosis'].value_counts().to_dict()}")
        
        return df
    
    def _remove_outliers(
        self, 
        df: pd.DataFrame, 
        column: str, 
        n_std: float = 3.0
    ) -> pd.DataFrame:
        """
        Remove outliers using standard deviation method.
        
        Args:
            df: Input DataFrame
            column: Column name
            n_std: Number of standard deviations for outlier threshold
            
        Returns:
            DataFrame with outliers removed
        """
        if column not in df.columns:
            return df
        
        mean = df[column].mean()
        std = df[column].std()
        
        if pd.isna(mean) or pd.isna(std) or std == 0:
            return df
        
        lower_bound = mean - n_std * std
        upper_bound = mean + n_std * std
        
        initial_count = len(df)
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        removed = initial_count - len(df)
        
        if removed > 0:
            logger.debug(f"Removed {removed} outliers from {column}")
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer additional features from existing data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features...")
        
        # Calculate tau/abeta ratio if both available
        if 'csf_tau' in df.columns and 'csf_abeta42' in df.columns:
            df['tau_abeta_ratio'] = df['csf_tau'] / df['csf_abeta42']
            df['tau_abeta_ratio'] = df['tau_abeta_ratio'].replace([np.inf, -np.inf], np.nan)
        
        # Calculate brain atrophy indicators
        if 'hippocampal_volume' in df.columns and 'whole_brain_volume' in df.columns:
            df['hippocampal_ratio'] = df['hippocampal_volume'] / df['whole_brain_volume']
        
        # Age-related features
        if 'age' in df.columns:
            df['age_squared'] = df['age'] ** 2
            df['age_group'] = pd.cut(
                df['age'], 
                bins=[0, 60, 70, 80, 100], 
                labels=[0, 1, 2, 3]
            ).astype(float)
        
        # Cognitive decline indicator
        if 'mmse_score' in df.columns:
            df['cognitive_impairment'] = (df['mmse_score'] < 24).astype(int)
        
        logger.info(f"Feature engineering complete: {len(df.columns)} features")
        
        return df
    
    def select_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Select relevant features for model training.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (DataFrame with selected features, list of feature names)
        """
        # Define feature categories
        demographic_features = ['age', 'gender', 'education_years', 'apoe4_alleles']
        cognitive_features = ['mmse_score', 'moca_score', 'cdr_score']
        biomarker_features = ['csf_abeta42', 'csf_tau', 'csf_ptau', 'tau_abeta_ratio']
        imaging_features = [
            'hippocampal_volume', 'entorhinal_thickness', 
            'whole_brain_volume', 'ventricular_volume',
            'hippocampal_ratio'
        ]
        engineered_features = ['age_squared', 'age_group', 'cognitive_impairment']
        
        # Combine all feature categories
        all_features = (
            demographic_features + 
            cognitive_features + 
            biomarker_features + 
            imaging_features + 
            engineered_features
        )
        
        # Select only features that exist in the dataframe
        available_features = [f for f in all_features if f in df.columns]
        
        logger.info(f"Selected {len(available_features)} features: {available_features}")
        
        # Create feature DataFrame
        X = df[available_features].copy()
        
        return X, available_features
    
    def split_dataset(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42
    ) -> Dict[str, np.ndarray]:
        """
        Split dataset into train/validation/test sets.
        
        Args:
            X: Features DataFrame
            y: Target Series
            test_size: Proportion for test set
            val_size: Proportion for validation set (from training set)
            random_state: Random seed
            
        Returns:
            Dictionary with train/val/test splits
        """
        logger.info("Splitting dataset...")
        
        # First split: train+val vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )
        
        # Second split: train vs val
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            random_state=random_state,
            stratify=y_temp
        )
        
        logger.info(f"Train set: {len(X_train)} samples")
        logger.info(f"Validation set: {len(X_val)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Check class distribution
        logger.info(f"Train distribution: {pd.Series(y_train).value_counts().to_dict()}")
        logger.info(f"Val distribution: {pd.Series(y_val).value_counts().to_dict()}")
        logger.info(f"Test distribution: {pd.Series(y_test).value_counts().to_dict()}")
        
        return {
            'X_train': X_train.values,
            'y_train': y_train.values,
            'X_val': X_val.values,
            'y_val': y_val.values,
            'X_test': X_test.values,
            'y_test': y_test.values,
            'feature_names': list(X.columns)
        }
    
    def save_processed_data(
        self,
        data_splits: Dict[str, np.ndarray],
        output_dir: str
    ) -> None:
        """
        Save processed data splits to disk.
        
        Args:
            data_splits: Dictionary with train/val/test splits
            output_dir: Output directory path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save numpy arrays
        np.save(output_path / 'X_train.npy', data_splits['X_train'])
        np.save(output_path / 'y_train.npy', data_splits['y_train'])
        np.save(output_path / 'X_val.npy', data_splits['X_val'])
        np.save(output_path / 'y_val.npy', data_splits['y_val'])
        np.save(output_path / 'X_test.npy', data_splits['X_test'])
        np.save(output_path / 'y_test.npy', data_splits['y_test'])
        
        # Save metadata
        metadata = {
            'feature_names': data_splits['feature_names'],
            'n_features': len(data_splits['feature_names']),
            'n_train': len(data_splits['y_train']),
            'n_val': len(data_splits['y_val']),
            'n_test': len(data_splits['y_test']),
            'train_distribution': {
                int(k): int(v) 
                for k, v in pd.Series(data_splits['y_train']).value_counts().items()
            },
            'val_distribution': {
                int(k): int(v) 
                for k, v in pd.Series(data_splits['y_val']).value_counts().items()
            },
            'test_distribution': {
                int(k): int(v) 
                for k, v in pd.Series(data_splits['y_test']).value_counts().items()
            }
        }
        
        with open(output_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Processed data saved to {output_dir}")
    
    def prepare_dataset(
        self,
        data_source: str,
        data_format: str,
        output_dir: str
    ) -> Dict[str, np.ndarray]:
        """
        Complete pipeline to prepare dataset.
        
        Args:
            data_source: Path to source data file
            data_format: Format of data ('adni' or 'oasis')
            output_dir: Output directory for processed data
            
        Returns:
            Dictionary with train/val/test splits
        """
        # Load data
        if data_format.lower() == 'adni':
            df = self.load_adni_format(data_source)
        elif data_format.lower() == 'oasis':
            df = self.load_oasis_format(data_source)
        else:
            raise ValueError(f"Unknown data format: {data_format}")
        
        # Standardize column names
        df = self.standardize_column_names(df)
        
        # Clean data
        df = self.clean_data(df)
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Select features
        X, feature_names = self.select_features(df)
        y = df['diagnosis']
        
        # Split dataset
        data_splits = self.split_dataset(X, y)
        
        # Save processed data
        self.save_processed_data(data_splits, output_dir)
        
        return data_splits


def main():
    """Main function to run data preparation."""
    parser = argparse.ArgumentParser(
        description='Prepare Alzheimer\'s dataset for ML training'
    )
    parser.add_argument(
        '--data-source',
        type=str,
        required=True,
        help='Path to source data file (CSV format)'
    )
    parser.add_argument(
        '--data-format',
        type=str,
        choices=['adni', 'oasis'],
        default='adni',
        help='Format of the source data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/processed',
        help='Output directory for processed data'
    )
    
    args = parser.parse_args()
    
    # Prepare dataset
    preparator = AlzheimerDatasetPreparator()
    data_splits = preparator.prepare_dataset(
        data_source=args.data_source,
        data_format=args.data_format,
        output_dir=args.output_dir
    )
    
    logger.info("Dataset preparation complete!")
    logger.info(f"Train samples: {len(data_splits['y_train'])}")
    logger.info(f"Validation samples: {len(data_splits['y_val'])}")
    logger.info(f"Test samples: {len(data_splits['y_test'])}")
    logger.info(f"Features: {len(data_splits['feature_names'])}")


if __name__ == '__main__':
    main()
