"""
Progression Forecasting Example

Demonstrates how to use the progression forecasting module to:
1. Prepare longitudinal data sequences
2. Train LSTM forecasting model
3. Generate multi-horizon forecasts (6, 12, 24 months)
4. Quantify uncertainty
5. Validate forecast accuracy
"""

import numpy as np
import pandas as pd
from pathlib import Path
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from forecasting import (
    ProgressionForecastingTrainer,
    ForecastEvaluator,
    UncertaintyQuantifier
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_synthetic_longitudinal_data(n_patients: int = 200, n_visits_per_patient: int = 8):
    """
    Generate synthetic longitudinal data for demonstration.
    
    In production, this would load real data from the feature store.
    """
    logger.info(f"Generating synthetic data for {n_patients} patients")
    
    data = []
    
    for patient_id in range(n_patients):
        # Baseline characteristics
        age = np.random.randint(60, 85)
        sex = np.random.choice([0, 1])
        education = np.random.randint(12, 20)
        apoe_e4_count = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
        
        # Initial MMSE score (higher for healthier patients)
        baseline_mmse = np.random.normal(26, 3)
        baseline_mmse = np.clip(baseline_mmse, 10, 30)
        
        # Decline rate (faster for APOE e4 carriers)
        decline_rate = 0.5 + apoe_e4_count * 0.3 + np.random.normal(0, 0.2)
        
        # Generate visits
        for visit_num in range(n_visits_per_patient):
            months_since_baseline = visit_num * 6  # Visits every 6 months
            
            # MMSE score with decline
            mmse = baseline_mmse - (decline_rate * months_since_baseline / 12)
            mmse = np.clip(mmse + np.random.normal(0, 1), 0, 30)
            
            # Biomarkers
            csf_ab42 = np.random.normal(800, 200)
            csf_tau = np.random.normal(400, 100)
            csf_ptau = np.random.normal(60, 20)
            
            # Imaging features
            hippocampus_volume = np.random.normal(3500, 500) - (months_since_baseline * 10)
            
            visit_date = pd.Timestamp('2020-01-01') + pd.DateOffset(months=months_since_baseline)
            
            data.append({
                'patient_id': f'P{patient_id:04d}',
                'visit_date': visit_date,
                'visit_number': visit_num + 1,
                'mmse_score': mmse,
                'age': age + (months_since_baseline / 12),
                'sex': sex,
                'education': education,
                'apoe_e4_count': apoe_e4_count,
                'csf_ab42': csf_ab42,
                'csf_tau': csf_tau,
                'csf_ptau': csf_ptau,
                'hippocampus_volume': hippocampus_volume,
                'months_since_baseline': months_since_baseline
            })
    
    df = pd.DataFrame(data)
    logger.info(f"Generated {len(df)} records for {n_patients} patients")
    
    return df


def main():
    """Main example workflow."""
    
    logger.info("=" * 80)
    logger.info("Progression Forecasting Example")
    logger.info("=" * 80)
    
    # Step 1: Generate synthetic data
    logger.info("\n1. Generating synthetic longitudinal data...")
    data = generate_synthetic_longitudinal_data(n_patients=200, n_visits_per_patient=8)
    
    logger.info(f"Data shape: {data.shape}")
    logger.info(f"Patients: {data['patient_id'].nunique()}")
    logger.info(f"Date range: {data['visit_date'].min()} to {data['visit_date'].max()}")
    
    # Step 2: Initialize trainer
    logger.info("\n2. Initializing progression forecasting trainer...")
    trainer = ProgressionForecastingTrainer(
        sequence_length=4,
        forecast_horizons=[6, 12, 24],
        lstm_units=[128, 64],
        dropout_rate=0.3,
        learning_rate=0.001,
        output_dir=Path('ml_pipeline/models/forecasting')
    )
    
    # Step 3: Prepare data
    logger.info("\n3. Preparing sequences from longitudinal data...")
    
    feature_cols = [
        'age', 'sex', 'education', 'apoe_e4_count',
        'csf_ab42', 'csf_tau', 'csf_ptau',
        'hippocampus_volume', 'months_since_baseline'
    ]
    
    data_splits = trainer.prepare_data(
        data,
        patient_id_col='patient_id',
        visit_date_col='visit_date',
        target_col='mmse_score',
        feature_cols=feature_cols,
        add_temporal_features=True,
        add_rate_features=True
    )
    
    logger.info(f"Training sequences: {len(data_splits['X_train'])}")
    logger.info(f"Validation sequences: {len(data_splits['X_val'])}")
    logger.info(f"Test sequences: {len(data_splits['X_test'])}")
    
    # Step 4: Train model
    logger.info("\n4. Training LSTM forecasting model...")
    training_result = trainer.train(
        data_splits,
        epochs=50,  # Reduced for demo
        batch_size=32,
        early_stopping_patience=10,
        save_best_model=True
    )
    
    logger.info(f"Training complete in {training_result['metrics']['epochs_trained']} epochs")
    logger.info(f"Validation MAE: {training_result['metrics']['val_mae']:.3f}")
    
    # Step 5: Evaluate on test set
    logger.info("\n5. Evaluating forecast accuracy...")
    evaluator = ForecastEvaluator(
        mae_threshold=3.0,
        forecast_horizons=[6, 12, 24]
    )
    
    # Generate predictions
    predictions = trainer.forecaster.predict(
        data_splits['X_test'],
        return_dict=False
    )
    
    # Evaluate accuracy
    metrics = evaluator.evaluate_accuracy(
        data_splits['y_test'],
        predictions,
        detailed=True
    )
    
    # Validate requirements
    passes, issues = evaluator.validate_requirements(metrics)
    
    if passes:
        logger.info("\n✓ Forecast meets accuracy requirements (MAE < 3.0)")
    else:
        logger.warning("\n✗ Forecast does not meet requirements:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    
    # Step 6: Uncertainty quantification
    logger.info("\n6. Quantifying prediction uncertainty...")
    uncertainty_quantifier = UncertaintyQuantifier(
        n_mc_samples=50,  # Reduced for demo
        confidence_level=0.95
    )
    
    # Calibrate with test data
    uncertainty_quantifier.calibrate_intervals(
        data_splits['y_test'],
        predictions,
        [6, 12, 24]
    )
    
    # Generate predictions with uncertainty
    uncertainty_results = uncertainty_quantifier.predict_with_uncertainty(
        trainer.forecaster.model,
        data_splits['X_test'][:10],  # First 10 samples
        [6, 12, 24],
        return_intervals=True
    )
    
    logger.info("Sample prediction with uncertainty:")
    for horizon in [6, 12, 24]:
        horizon_key = f'{horizon}_month'
        pred = uncertainty_results['by_horizon'][horizon_key]['prediction'][0]
        std = uncertainty_results['by_horizon'][horizon_key]['std'][0]
        lower = uncertainty_results['by_horizon'][horizon_key]['lower_bound'][0]
        upper = uncertainty_results['by_horizon'][horizon_key]['upper_bound'][0]
        
        logger.info(
            f"  {horizon}-month: {pred:.2f} ± {std:.2f} "
            f"(95% CI: [{lower:.2f}, {upper:.2f}])"
        )
    
    # Step 7: Single patient forecast
    logger.info("\n7. Generating forecast for single patient...")
    
    # Get a patient with sufficient history
    sample_patient_id = data['patient_id'].iloc[0]
    patient_history = data[data['patient_id'] == sample_patient_id].copy()
    
    if len(patient_history) >= 4:
        forecast = trainer.forecast_patient(patient_history)
        
        logger.info(f"Patient {sample_patient_id} forecast:")
        for horizon, score in forecast.items():
            logger.info(f"  {horizon}: {score:.2f}")
    
    # Step 8: Update forecast with new assessment
    logger.info("\n8. Demonstrating forecast update...")
    
    if len(patient_history) >= 5:
        # Use first 4 visits for initial forecast
        initial_history = patient_history.iloc[:4]
        initial_forecast = trainer.forecast_patient(initial_history)
        
        logger.info("Initial forecast (based on 4 visits):")
        for horizon, score in initial_forecast.items():
            logger.info(f"  {horizon}: {score:.2f}")
        
        # Add 5th visit and update forecast
        new_assessment = patient_history.iloc[4:5]
        updated_forecast = trainer.update_forecast(
            initial_history,
            new_assessment
        )
        
        logger.info("Updated forecast (after new assessment):")
        for horizon, score in updated_forecast.items():
            logger.info(f"  {horizon}: {score:.2f}")
    
    # Step 9: Save model
    logger.info("\n9. Saving trained model...")
    trainer.save_model()
    logger.info(f"Model saved to {trainer.output_dir}")
    
    # Step 10: Generate evaluation report
    logger.info("\n10. Generating evaluation report...")
    report_path = trainer.output_dir / 'evaluation_report.md'
    evaluator.generate_evaluation_report(metrics, report_path)
    
    # Generate plots
    plot_dir = trainer.output_dir / 'plots'
    plot_dir.mkdir(exist_ok=True)
    
    evaluator.plot_predictions_vs_actual(
        data_splits['y_test'],
        predictions,
        output_path=plot_dir / 'predictions_vs_actual.png'
    )
    
    evaluator.plot_error_distribution(
        data_splits['y_test'],
        predictions,
        output_path=plot_dir / 'error_distribution.png'
    )
    
    logger.info(f"Plots saved to {plot_dir}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Example complete!")
    logger.info("=" * 80)
    
    # Summary
    logger.info("\nSummary:")
    logger.info(f"  - Trained on {len(data_splits['X_train'])} sequences")
    logger.info(f"  - Overall MAE: {metrics['overall_mae']:.3f}")
    logger.info(f"  - Overall RMSE: {metrics['overall_rmse']:.3f}")
    logger.info(f"  - Overall R²: {metrics['overall_r2']:.3f}")
    logger.info(f"  - Meets requirements: {'Yes' if passes else 'No'}")


if __name__ == '__main__':
    main()
