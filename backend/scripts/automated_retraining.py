"""
Automated model retraining pipeline.

This script:
1. Checks if retraining is needed based on monitoring data
2. Prepares updated training dataset
3. Trains new model version
4. Evaluates new model
5. Promotes to staging if performance improves

Usage:
    python scripts/automated_retraining.py --check-only
    python scripts/automated_retraining.py --force
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime
import sys
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.model_monitoring import get_model_monitor
from app.ml.model_registry import get_model_registry
from scripts.train_models import ModelTrainer
from scripts.evaluate_models import ModelEvaluator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomatedRetrainingPipeline:
    """
    Automated pipeline for model retraining.
    """
    
    def __init__(
        self,
        data_dir: str = "data/processed",
        models_dir: str = "models",
        monitoring_dir: str = "models/monitoring"
    ):
        """
        Initialize retraining pipeline.
        
        Args:
            data_dir: Directory with training data
            models_dir: Directory for models
            monitoring_dir: Directory for monitoring data
        """
        self.data_dir = Path(data_dir)
        self.models_dir = Path(models_dir)
        self.monitoring_dir = Path(monitoring_dir)
        
        self.monitor = get_model_monitor(str(monitoring_dir))
        self.registry = get_model_registry(str(models_dir))
    
    def check_retraining_needed(
        self,
        min_predictions: int = 100,
        accuracy_threshold: float = 0.05
    ) -> tuple[bool, str]:
        """
        Check if retraining is needed.
        
        Args:
            min_predictions: Minimum predictions for decision
            accuracy_threshold: Accuracy drop threshold
            
        Returns:
            Tuple of (should_retrain, reason)
        """
        logger.info("Checking if retraining is needed...")
        
        # Get current production model
        production_model = self.registry.get_production_model()
        
        if not production_model:
            return False, "No production model to compare against"
        
        # Get baseline accuracy
        baseline_accuracy = production_model['metrics'].get('accuracy', 0.85)
        
        # Check monitoring data
        should_retrain, reason = self.monitor.should_retrain(
            baseline_accuracy=baseline_accuracy,
            min_predictions=min_predictions,
            accuracy_threshold=accuracy_threshold
        )
        
        logger.info(f"Retraining decision: {should_retrain}")
        logger.info(f"Reason: {reason}")
        
        return should_retrain, reason
    
    def prepare_updated_dataset(self) -> bool:
        """
        Prepare updated training dataset with new data.
        
        Returns:
            True if dataset prepared successfully
        """
        logger.info("Preparing updated training dataset...")
        
        # In a real implementation, this would:
        # 1. Fetch new labeled data from database
        # 2. Combine with existing training data
        # 3. Re-split into train/val/test
        # 4. Save to data_dir
        
        # For now, we'll assume the data is already prepared
        if not (self.data_dir / 'X_train.npy').exists():
            logger.error("Training data not found")
            return False
        
        logger.info("Training data ready")
        return True
    
    def train_new_model(self) -> str:
        """
        Train a new model version.
        
        Returns:
            Path to trained model
        """
        logger.info("Training new model version...")
        
        # Generate version name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"v1.0.0_retrain_{timestamp}"
        
        # Train model
        trainer = ModelTrainer(
            data_dir=str(self.data_dir),
            output_dir=str(self.models_dir)
        )
        
        model_path = trainer.train_and_save(version=version)
        
        logger.info(f"New model trained: {version}")
        
        return model_path
    
    def evaluate_new_model(self, model_path: str) -> dict:
        """
        Evaluate newly trained model.
        
        Args:
            model_path: Path to model directory
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating new model...")
        
        evaluator = ModelEvaluator(
            model_dir=model_path,
            data_dir=str(self.data_dir)
        )
        
        results = evaluator.evaluate()
        
        return results['metrics']
    
    def compare_with_production(
        self,
        new_model_path: str,
        new_metrics: dict
    ) -> tuple[bool, str]:
        """
        Compare new model with production model.
        
        Args:
            new_model_path: Path to new model
            new_metrics: New model metrics
            
        Returns:
            Tuple of (is_better, reason)
        """
        logger.info("Comparing with production model...")
        
        production_model = self.registry.get_production_model()
        
        if not production_model:
            return True, "No production model to compare against"
        
        prod_metrics = production_model['metrics']
        
        # Compare key metrics
        new_accuracy = new_metrics.get('accuracy', 0)
        prod_accuracy = prod_metrics.get('accuracy', 0)
        
        new_f1 = new_metrics.get('f1_score', 0)
        prod_f1 = prod_metrics.get('f1_score', 0)
        
        new_auc = new_metrics.get('auc_roc', 0)
        prod_auc = prod_metrics.get('auc_roc', 0)
        
        # Calculate improvement
        accuracy_improvement = new_accuracy - prod_accuracy
        f1_improvement = new_f1 - prod_f1
        auc_improvement = new_auc - prod_auc
        
        # Decision criteria: new model must be better in at least 2 out of 3 metrics
        improvements = [
            accuracy_improvement > 0,
            f1_improvement > 0,
            auc_improvement > 0
        ]
        
        is_better = sum(improvements) >= 2
        
        reason = (
            f"Accuracy: {accuracy_improvement:+.4f}, "
            f"F1: {f1_improvement:+.4f}, "
            f"AUC: {auc_improvement:+.4f}"
        )
        
        logger.info(f"Comparison result: {'Better' if is_better else 'Not better'}")
        logger.info(f"Details: {reason}")
        
        return is_better, reason
    
    def promote_to_staging(self, model_path: str) -> None:
        """
        Promote model to staging.
        
        Args:
            model_path: Path to model directory
        """
        logger.info("Promoting model to staging...")
        
        # Extract version from path
        version = Path(model_path).name
        
        self.registry.promote_to_staging(version)
        
        logger.info(f"Model {version} promoted to staging")
    
    def run_retraining_pipeline(
        self,
        force: bool = False,
        auto_promote: bool = True
    ) -> dict:
        """
        Run complete retraining pipeline.
        
        Args:
            force: Force retraining even if not needed
            auto_promote: Automatically promote to staging if better
            
        Returns:
            Dictionary with pipeline results
        """
        logger.info("=" * 80)
        logger.info("STARTING AUTOMATED RETRAINING PIPELINE")
        logger.info("=" * 80)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'retraining_needed': False,
            'model_trained': False,
            'model_promoted': False,
            'new_model_version': None,
            'metrics': {}
        }
        
        # Check if retraining is needed
        if not force:
            should_retrain, reason = self.check_retraining_needed()
            results['retraining_needed'] = should_retrain
            results['retraining_reason'] = reason
            
            if not should_retrain:
                logger.info("Retraining not needed. Exiting.")
                return results
        else:
            logger.info("Forced retraining mode")
            results['retraining_needed'] = True
            results['retraining_reason'] = "Forced by user"
        
        # Prepare dataset
        if not self.prepare_updated_dataset():
            results['error'] = "Failed to prepare dataset"
            return results
        
        # Train new model
        try:
            model_path = self.train_new_model()
            results['model_trained'] = True
            results['new_model_version'] = Path(model_path).name
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            results['error'] = f"Training failed: {str(e)}"
            return results
        
        # Evaluate new model
        try:
            new_metrics = self.evaluate_new_model(model_path)
            results['metrics'] = new_metrics
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            results['error'] = f"Evaluation failed: {str(e)}"
            return results
        
        # Compare with production
        is_better, comparison_reason = self.compare_with_production(
            model_path, new_metrics
        )
        results['is_better_than_production'] = is_better
        results['comparison_reason'] = comparison_reason
        
        # Promote to staging if better
        if is_better and auto_promote:
            try:
                self.promote_to_staging(model_path)
                results['model_promoted'] = True
            except Exception as e:
                logger.error(f"Promotion failed: {str(e)}")
                results['promotion_error'] = str(e)
        
        logger.info("\n" + "=" * 80)
        logger.info("RETRAINING PIPELINE COMPLETE")
        logger.info("=" * 80)
        
        # Save results
        results_file = self.monitoring_dir / 'retraining_history.jsonl'
        with open(results_file, 'a') as f:
            f.write(json.dumps(results) + '\n')
        
        return results


def main():
    """Main function to run automated retraining."""
    parser = argparse.ArgumentParser(
        description='Automated model retraining pipeline'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/processed',
        help='Directory with training data'
    )
    parser.add_argument(
        '--models-dir',
        type=str,
        default='models',
        help='Directory for models'
    )
    parser.add_argument(
        '--monitoring-dir',
        type=str,
        default='models/monitoring',
        help='Directory for monitoring data'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check if retraining is needed'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retraining even if not needed'
    )
    parser.add_argument(
        '--no-auto-promote',
        action='store_true',
        help='Do not automatically promote to staging'
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = AutomatedRetrainingPipeline(
        data_dir=args.data_dir,
        models_dir=args.models_dir,
        monitoring_dir=args.monitoring_dir
    )
    
    if args.check_only:
        # Just check if retraining is needed
        should_retrain, reason = pipeline.check_retraining_needed()
        print(f"\nRetraining needed: {should_retrain}")
        print(f"Reason: {reason}")
    else:
        # Run full pipeline
        results = pipeline.run_retraining_pipeline(
            force=args.force,
            auto_promote=not args.no_auto_promote
        )
        
        print("\n" + "=" * 80)
        print("PIPELINE RESULTS")
        print("=" * 80)
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
