"""
Model Evaluation Example

Demonstrates how to use the ModelEvaluator class to:
1. Calculate classification metrics
2. Generate confusion matrices
3. Calculate ROC and PR curves
4. Perform sensitivity analysis
5. Calculate calibration metrics
6. Generate performance comparison reports
7. Save metrics to Model Registry
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.model_evaluator import ModelEvaluator
from training.data_loader import DataLoader
from training.trainers import RandomForestTrainer, XGBoostTrainer, NeuralNetworkTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run model evaluation example."""
    logger.info("=" * 80)
    logger.info("MODEL EVALUATION EXAMPLE")
    logger.info("=" * 80)
    
    # Setup paths
    feature_store_path = Path("ml_pipeline/data_storage/features")
    output_dir = Path("ml_pipeline/evaluation_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize evaluator
    evaluator = ModelEvaluator(
        output_dir=output_dir,
        min_auc_roc=0.80  # Requirement: minimum AUC-ROC of 0.80
    )
    
    # Load data
    logger.info("\nLoading test data...")
    data_loader = DataLoader(feature_store_path)
    
    try:
        splits = data_loader.load_and_split(
            dataset_name="train_features",
            target_column="diagnosis"
        )
        
        X_test = splits['X_test']
        y_test = splits['y_test']
        X_train = splits['X_train']
        y_train = splits['y_train']
        X_val = splits['X_val']
        y_val = splits['y_val']
        
        logger.info(f"Test set size: {len(X_test)} samples")
        
    except Exception as e:
        logger.warning(f"Could not load real data: {e}")
        logger.info("Generating synthetic data for demonstration...")
        
        # Generate synthetic data
        np.random.seed(42)
        n_samples = 1000
        n_features = 20
        
        X_train = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        y_train = pd.Series(np.random.randint(0, 2, n_samples))
        
        X_val = pd.DataFrame(
            np.random.randn(200, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        y_val = pd.Series(np.random.randint(0, 2, 200))
        
        X_test = pd.DataFrame(
            np.random.randn(300, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        y_test = pd.Series(np.random.randint(0, 2, 300))
    
    # Train models for evaluation
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING MODELS FOR EVALUATION")
    logger.info("=" * 80)
    
    models_results = {}
    
    # 1. Train Random Forest
    logger.info("\n[1/3] Training Random Forest...")
    rf_trainer = RandomForestTrainer(
        n_estimators=200,
        max_depth=15,
        random_state=42
    )
    rf_result = rf_trainer.train(X_train, y_train, X_val, y_val)
    models_results['RandomForest'] = {
        'model': rf_result['model'],
        'trainer': rf_trainer
    }
    
    # 2. Train XGBoost
    logger.info("\n[2/3] Training XGBoost...")
    xgb_trainer = XGBoostTrainer(
        n_estimators=200,
        max_depth=6,
        random_state=42
    )
    xgb_result = xgb_trainer.train(X_train, y_train, X_val, y_val)
    models_results['XGBoost'] = {
        'model': xgb_result['model'],
        'trainer': xgb_trainer
    }
    
    # 3. Train Neural Network
    logger.info("\n[3/3] Training Neural Network...")
    nn_trainer = NeuralNetworkTrainer(
        hidden_layers=[128, 64, 32],
        dropout_rates=[0.3, 0.3, 0.2],
        batch_size=32,
        epochs=50,
        random_state=42
    )
    nn_result = nn_trainer.train(X_train, y_train, X_val, y_val)
    models_results['NeuralNetwork'] = {
        'model': nn_result['model'],
        'trainer': nn_trainer
    }
    
    # Evaluate each model
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATING MODELS")
    logger.info("=" * 80)
    
    evaluation_results = {}
    
    for model_name, model_data in models_results.items():
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Evaluating {model_name}")
        logger.info(f"{'=' * 80}")
        
        model = model_data['model']
        
        # Get predictions
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        # 1. Calculate classification metrics
        logger.info("\n[Step 1/5] Classification Metrics")
        metrics = evaluator.calculate_classification_metrics(
            y_test.values, y_pred, y_proba, model_name
        )
        
        # 2. Generate confusion matrix
        logger.info("\n[Step 2/5] Confusion Matrix")
        cm, cm_path = evaluator.generate_confusion_matrix(
            y_test.values, y_pred, model_name
        )
        
        # 3. Calculate ROC and PR curves
        logger.info("\n[Step 3/5] ROC and PR Curves")
        curve_metrics, roc_path, pr_path = evaluator.calculate_roc_pr_curves(
            y_test.values, y_proba, model_name
        )
        
        # 4. Calculate calibration metrics
        logger.info("\n[Step 4/5] Calibration Metrics")
        cal_metrics, cal_path = evaluator.calculate_calibration_metrics(
            y_test.values, y_proba, model_name
        )
        
        # 5. Sensitivity analysis (with synthetic demographic data)
        logger.info("\n[Step 5/5] Sensitivity Analysis")
        demographic_data = pd.DataFrame({
            'age': np.random.randint(50, 90, len(X_test)),
            'sex': np.random.choice(['M', 'F'], len(X_test)),
            'apoe_e4_count': np.random.choice([0, 1, 2], len(X_test))
        })
        
        sensitivity_results = evaluator.perform_sensitivity_analysis(
            y_test.values, y_pred, y_proba,
            demographic_data, model_name
        )
        
        # Store results
        evaluation_results[model_name] = {
            'metrics': {
                **metrics,
                'brier_score': cal_metrics['brier_score'],
                'expected_calibration_error': cal_metrics['expected_calibration_error']
            },
            'confusion_matrix': cm.tolist(),
            'sensitivity_analysis': sensitivity_results
        }
    
    # Generate performance comparison
    logger.info("\n" + "=" * 80)
    logger.info("PERFORMANCE COMPARISON")
    logger.info("=" * 80)
    
    comparison_df, report_path = evaluator.generate_performance_comparison(
        evaluation_results,
        save_report=True
    )
    
    # Save metrics to Model Registry (demonstration)
    logger.info("\n" + "=" * 80)
    logger.info("SAVING TO MODEL REGISTRY")
    logger.info("=" * 80)
    
    for model_name, results in evaluation_results.items():
        version_id = f"v1.0.0_{model_name.lower()}"
        success = evaluator.save_to_model_registry(
            model_name=model_name,
            version_id=version_id,
            metrics=results['metrics']
        )
        
        if success:
            logger.info(f"✓ {model_name} metrics saved to registry")
        else:
            logger.warning(f"✗ Failed to save {model_name} metrics")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"\nEvaluation results saved to: {output_dir}")
    logger.info(f"  - Plots: {output_dir / 'plots'}")
    logger.info(f"  - Reports: {output_dir / 'reports'}")
    logger.info("\nGenerated files:")
    logger.info("  - Confusion matrices (PNG)")
    logger.info("  - ROC curves (PNG)")
    logger.info("  - PR curves (PNG)")
    logger.info("  - Calibration curves (PNG)")
    logger.info("  - Model comparison plot (PNG)")
    logger.info("  - Sensitivity analysis reports (JSON)")
    logger.info("  - Performance comparison (CSV, JSON)")
    logger.info("  - Model metrics (JSON)")
    
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
