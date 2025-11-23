"""
Script to train ensemble ML models for Alzheimer's disease prediction.

This script:
1. Loads preprocessed training data
2. Trains Random Forest, XGBoost, and Neural Network models
3. Implements ensemble voting mechanism
4. Saves trained models with versioning

Usage:
    python scripts/train_models.py --data-dir data/processed --output-dir models
"""

import argparse
import logging
from pathlib import Path
from typing import Dict
import numpy as np
import json
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.models.ensemble import AlzheimerEnsemble
from app.ml.preprocessing import FeaturePreprocessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trains ensemble ML models for Alzheimer's prediction.
    """
    
    def __init__(self, data_dir: str, output_dir: str):
        """
        Initialize model trainer.
        
        Args:
            data_dir: Directory containing processed data
            output_dir: Directory to save trained models
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.X_test = None
        self.y_test = None
        self.feature_names = []
        self.metadata = {}
    
    def load_data(self) -> None:
        """Load preprocessed training data."""
        logger.info(f"Loading data from {self.data_dir}")
        
        try:
            # Load numpy arrays
            self.X_train = np.load(self.data_dir / 'X_train.npy')
            self.y_train = np.load(self.data_dir / 'y_train.npy')
            self.X_val = np.load(self.data_dir / 'X_val.npy')
            self.y_val = np.load(self.data_dir / 'y_val.npy')
            self.X_test = np.load(self.data_dir / 'X_test.npy')
            self.y_test = np.load(self.data_dir / 'y_test.npy')
            
            # Load metadata
            with open(self.data_dir / 'metadata.json', 'r') as f:
                self.metadata = json.load(f)
            
            self.feature_names = self.metadata['feature_names']
            
            logger.info(f"Loaded training data:")
            logger.info(f"  Train: {self.X_train.shape}")
            logger.info(f"  Validation: {self.X_val.shape}")
            logger.info(f"  Test: {self.X_test.shape}")
            logger.info(f"  Features: {len(self.feature_names)}")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def train_ensemble(
        self,
        weights: Dict[str, float] = None,
        random_state: int = 42
    ) -> AlzheimerEnsemble:
        """
        Train ensemble model.
        
        Args:
            weights: Optional model weights
            random_state: Random seed
            
        Returns:
            Trained ensemble model
        """
        logger.info("=" * 80)
        logger.info("TRAINING ENSEMBLE MODEL")
        logger.info("=" * 80)
        
        # Initialize ensemble
        ensemble = AlzheimerEnsemble(
            weights=weights,
            random_state=random_state
        )
        
        # Train ensemble
        training_metrics = ensemble.train(
            X_train=self.X_train,
            y_train=self.y_train,
            feature_names=self.feature_names,
            X_val=self.X_val,
            y_val=self.y_val
        )
        
        logger.info("\nTraining Metrics:")
        logger.info("-" * 80)
        for model_name, metrics in training_metrics.items():
            logger.info(f"\n{model_name.upper()}:")
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    logger.info(f"  {metric_name}: {value:.4f}")
                else:
                    logger.info(f"  {metric_name}: {value}")
        
        return ensemble
    
    def evaluate_on_test_set(self, ensemble: AlzheimerEnsemble) -> Dict:
        """
        Evaluate ensemble on test set.
        
        Args:
            ensemble: Trained ensemble model
            
        Returns:
            Dictionary with test metrics
        """
        logger.info("\n" + "=" * 80)
        logger.info("EVALUATING ON TEST SET")
        logger.info("=" * 80)
        
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, 
            f1_score, roc_auc_score, confusion_matrix
        )
        
        # Make predictions
        predictions = []
        probabilities = []
        
        for i in range(len(self.X_test)):
            pred = ensemble.predict(self.X_test[i])
            _, prob = ensemble.predict_proba(self.X_test[i])
            predictions.append(pred)
            probabilities.append(prob)
        
        predictions = np.array(predictions)
        probabilities = np.array(probabilities)
        
        # Calculate metrics
        accuracy = accuracy_score(self.y_test, predictions)
        precision = precision_score(self.y_test, predictions, zero_division=0)
        recall = recall_score(self.y_test, predictions, zero_division=0)
        f1 = f1_score(self.y_test, predictions, zero_division=0)
        
        try:
            auc = roc_auc_score(self.y_test, probabilities)
        except:
            auc = 0.0
        
        cm = confusion_matrix(self.y_test, predictions)
        
        # Calculate specificity and sensitivity
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'auc_roc': float(auc),
            'sensitivity': float(sensitivity),
            'specificity': float(specificity),
            'confusion_matrix': cm.tolist(),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp)
        }
        
        logger.info("\nTest Set Performance:")
        logger.info("-" * 80)
        logger.info(f"Accuracy:    {accuracy:.4f}")
        logger.info(f"Precision:   {precision:.4f}")
        logger.info(f"Recall:      {recall:.4f}")
        logger.info(f"F1 Score:    {f1:.4f}")
        logger.info(f"AUC-ROC:     {auc:.4f}")
        logger.info(f"Sensitivity: {sensitivity:.4f}")
        logger.info(f"Specificity: {specificity:.4f}")
        logger.info(f"\nConfusion Matrix:")
        logger.info(f"  TN: {tn:4d}  FP: {fp:4d}")
        logger.info(f"  FN: {fn:4d}  TP: {tp:4d}")
        
        return metrics
    
    def save_model(
        self,
        ensemble: AlzheimerEnsemble,
        test_metrics: Dict,
        version: str = None
    ) -> str:
        """
        Save trained model with versioning.
        
        Args:
            ensemble: Trained ensemble model
            test_metrics: Test set metrics
            version: Model version (auto-generated if None)
            
        Returns:
            Path to saved model
        """
        # Generate version if not provided
        if version is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version = f"v1.0.0_{timestamp}"
        
        # Create version directory
        model_dir = self.output_dir / version
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save ensemble
        ensemble.save(str(model_dir / 'ensemble'))
        
        # Save model metadata
        model_metadata = {
            'version': version,
            'created_at': datetime.now().isoformat(),
            'model_type': 'ensemble',
            'ensemble_weights': ensemble.weights,
            'feature_names': self.feature_names,
            'n_features': len(self.feature_names),
            'training_samples': len(self.y_train),
            'validation_samples': len(self.y_val),
            'test_samples': len(self.y_test),
            'test_metrics': test_metrics,
            'data_metadata': self.metadata
        }
        
        with open(model_dir / 'model_metadata.json', 'w') as f:
            json.dump(model_metadata, f, indent=2)
        
        # Create symlink to latest
        latest_link = self.output_dir / 'latest'
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(version, target_is_directory=True)
        
        logger.info(f"\nModel saved to: {model_dir}")
        logger.info(f"Version: {version}")
        
        return str(model_dir)
    
    def train_and_save(
        self,
        weights: Dict[str, float] = None,
        version: str = None,
        random_state: int = 42
    ) -> str:
        """
        Complete training pipeline.
        
        Args:
            weights: Optional model weights
            version: Model version
            random_state: Random seed
            
        Returns:
            Path to saved model
        """
        # Load data
        self.load_data()
        
        # Train ensemble
        ensemble = self.train_ensemble(
            weights=weights,
            random_state=random_state
        )
        
        # Evaluate on test set
        test_metrics = self.evaluate_on_test_set(ensemble)
        
        # Save model
        model_path = self.save_model(ensemble, test_metrics, version)
        
        logger.info("\n" + "=" * 80)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 80)
        
        return model_path


def main():
    """Main function to run model training."""
    parser = argparse.ArgumentParser(
        description='Train ensemble ML models for Alzheimer\'s prediction'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/processed',
        help='Directory containing processed data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='models',
        help='Output directory for trained models'
    )
    parser.add_argument(
        '--version',
        type=str,
        default=None,
        help='Model version (auto-generated if not provided)'
    )
    parser.add_argument(
        '--random-state',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    parser.add_argument(
        '--rf-weight',
        type=float,
        default=0.33,
        help='Weight for Random Forest model'
    )
    parser.add_argument(
        '--xgb-weight',
        type=float,
        default=0.33,
        help='Weight for XGBoost model'
    )
    parser.add_argument(
        '--nn-weight',
        type=float,
        default=0.34,
        help='Weight for Neural Network model'
    )
    
    args = parser.parse_args()
    
    # Create model weights
    weights = {
        'rf': args.rf_weight,
        'xgb': args.xgb_weight,
        'nn': args.nn_weight
    }
    
    # Train models
    trainer = ModelTrainer(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    
    model_path = trainer.train_and_save(
        weights=weights,
        version=args.version,
        random_state=args.random_state
    )
    
    logger.info(f"\nTrained model available at: {model_path}")
    logger.info("To use this model, update the ML service to load from this path.")


if __name__ == '__main__':
    main()
