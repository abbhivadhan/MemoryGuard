"""
Example: ML Training Pipeline

Demonstrates how to use the ML training pipeline to train models
for Alzheimer's Disease detection.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.training_pipeline import MLTrainingPipeline
from config.logging_config import setup_logging


def main():
    """Run ML training pipeline example."""
    
    # Setup logging
    setup_logging()
    
    # Define paths
    feature_store_path = Path("data_storage/features")
    output_dir = Path("data_storage/models/training_run_001")
    
    # Create pipeline
    pipeline = MLTrainingPipeline(
        feature_store_path=feature_store_path,
        output_dir=output_dir,
        random_state=42
    )
    
    # Option 1: Run full training pipeline
    print("\n" + "=" * 80)
    print("Running Full Training Pipeline")
    print("=" * 80)
    
    results = pipeline.run_full_pipeline(
        dataset_name="train_features",
        target_column="diagnosis",
        enable_gpu=True,
        save_models=True
    )
    
    print("\n" + "=" * 80)
    print("Training Complete!")
    print("=" * 80)
    print(f"\nTraining time: {results['training_time_minutes']:.2f} minutes")
    print("\nTest Set Performance:")
    
    for model_name, metrics in results['models'].items():
        print(f"\n{model_name.upper()}:")
        print(f"  ROC-AUC: {metrics.get('roc_auc', 0):.4f}")
        print(f"  Accuracy: {metrics.get('accuracy', 0):.4f}")
        print(f"  F1-Score: {metrics.get('f1_score', 0):.4f}")
    
    # Option 2: Run cross-validation
    print("\n" + "=" * 80)
    print("Running Cross-Validation")
    print("=" * 80)
    
    cv_results = pipeline.run_cross_validation(
        dataset_name="train_features",
        target_column="diagnosis"
    )
    
    print(f"\nBest model: {cv_results['best_model']}")
    print("\nCross-validation results:")
    print(cv_results['comparison'])
    
    print("\n" + "=" * 80)
    print("Example Complete!")
    print("=" * 80)
    print(f"\nModels saved to: {output_dir / 'models'}")
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
