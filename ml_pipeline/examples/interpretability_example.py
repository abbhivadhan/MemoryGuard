"""
Model Interpretability Example

Demonstrates the use of the interpretability system for explaining
ML model predictions.
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from interpretability.interpretability_system import InterpretabilitySystem
from training.trainers import RandomForestTrainer, XGBoostTrainer
from training.data_loader import DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run interpretability example."""
    
    logger.info("=" * 80)
    logger.info("MODEL INTERPRETABILITY EXAMPLE")
    logger.info("=" * 80)
    
    # Set paths
    output_dir = Path("ml_pipeline/outputs/interpretability_example")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    logger.info("\n1. Loading data...")
    data_loader = DataLoader()
    
    # For this example, we'll create synthetic data
    # In practice, you would load from feature store
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    # Create synthetic features
    X = np.random.randn(n_samples, n_features)
    
    # Create synthetic labels (with some pattern)
    y = (X[:, 0] + X[:, 1] * 2 - X[:, 2] + np.random.randn(n_samples) * 0.5 > 0).astype(int)
    
    # Feature names
    feature_names = [f'feature_{i}' for i in range(n_features)]
    
    # Split data
    train_size = int(0.7 * n_samples)
    val_size = int(0.15 * n_samples)
    
    X_train = X[:train_size]
    y_train = y[:train_size]
    X_val = X[train_size:train_size+val_size]
    y_val = y[train_size:train_size+val_size]
    X_test = X[train_size+val_size:]
    y_test = y[train_size+val_size:]
    
    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Validation samples: {len(X_val)}")
    logger.info(f"Test samples: {len(X_test)}")
    
    # Train a Random Forest model
    logger.info("\n2. Training Random Forest model...")
    rf_trainer = RandomForestTrainer(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )
    
    rf_result = rf_trainer.train(
        pd.DataFrame(X_train, columns=feature_names),
        pd.Series(y_train),
        pd.DataFrame(X_val, columns=feature_names),
        pd.Series(y_val)
    )
    
    model = rf_result['model']
    logger.info(f"Model trained. Validation AUC: {rf_result['metrics']['val_roc_auc']:.4f}")
    
    # Initialize interpretability system
    logger.info("\n3. Initializing interpretability system...")
    interp_system = InterpretabilitySystem(
        model=model,
        model_type='tree',
        feature_names=feature_names,
        output_dir=output_dir,
        cache_explanations=True
    )
    
    # Initialize with background data (sample from training set)
    background_data = X_train[:100]
    interp_system.initialize(background_data)
    
    # Explain a single prediction
    logger.info("\n4. Explaining a single prediction...")
    test_sample = X_test[0:1]
    prediction = model.predict(test_sample)[0]
    probability = model.predict_proba(test_sample)[0, 1]
    
    explanation = interp_system.explain_prediction(
        test_sample,
        prediction,
        probability
    )
    
    logger.info(f"\nPrediction: {explanation['prediction']['class_name']}")
    logger.info(f"Probability: {explanation['prediction']['probability']:.3f}")
    logger.info(f"Confidence: {explanation['prediction']['confidence']}")
    logger.info(f"\nTop 5 Contributing Features:")
    for item in explanation['top_features']:
        logger.info(
            f"  {item['rank']}. {item['feature']}: "
            f"{item['impact']} risk (SHAP: {item['shap_value']:.4f})"
        )
    
    logger.info(f"\nExplanation Text:")
    logger.info(explanation['explanation_text'])
    
    # Analyze global feature importance
    logger.info("\n5. Analyzing global feature importance...")
    importance_report = interp_system.analyze_feature_importance(
        X_test[:200],  # Use subset for faster computation
        model_name="RandomForest",
        save_report=True
    )
    
    logger.info(f"\nTop 10 Most Important Features:")
    for item in importance_report['top_20_features'][:10]:
        logger.info(f"  {item['feature']}: {item['importance']:.4f}")
    
    # Create visualizations
    logger.info("\n6. Creating visualizations...")
    plots = interp_system.create_visualizations(
        X_test[:200],
        model_name="RandomForest"
    )
    
    logger.info(f"Created {len(plots)} visualizations:")
    for plot_name, plot_path in plots.items():
        logger.info(f"  {plot_name}: {plot_path}")
    
    # Benchmark performance
    logger.info("\n7. Benchmarking performance...")
    performance_metrics = interp_system.benchmark_performance(
        X_test[:50],
        n_iterations=20
    )
    
    # Generate complete report
    logger.info("\n8. Generating complete interpretability report...")
    complete_report = interp_system.generate_complete_report(
        X_test[:200],
        model_name="RandomForest",
        create_plots=True
    )
    
    logger.info(f"\nComplete report generated:")
    logger.info(f"  Samples analyzed: {complete_report['n_samples_analyzed']}")
    logger.info(f"  Generation time: {complete_report['generation_time']:.2f}s")
    logger.info(f"  Visualizations: {len(complete_report['visualizations'])}")
    
    # Save cache
    logger.info("\n9. Saving explanation cache...")
    interp_system.save_cache()
    
    logger.info("\n" + "=" * 80)
    logger.info("INTERPRETABILITY EXAMPLE COMPLETED")
    logger.info("=" * 80)
    logger.info(f"\nOutputs saved to: {output_dir}")
    logger.info("\nKey files:")
    logger.info(f"  - Feature importance report: {output_dir}/feature_importance/")
    logger.info(f"  - Visualizations: {output_dir}/visualizations/")
    logger.info(f"  - Explanation cache: {output_dir}/cache/")


if __name__ == "__main__":
    main()
