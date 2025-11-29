# Progression Forecasting Module

This module implements LSTM-based time-series forecasting for Alzheimer's Disease progression prediction.

## Overview

The progression forecasting system predicts future cognitive decline (MMSE scores) at multiple time horizons (6, 12, and 24 months) using longitudinal patient data including cognitive assessments, biomarkers, imaging features, and genetic information.

## Features

- **LSTM Architecture**: Multi-layer LSTM with dropout for regularization
- **Multi-Horizon Forecasting**: Simultaneous predictions at 6, 12, and 24 months
- **Uncertainty Quantification**: Monte Carlo Dropout for prediction intervals
- **Temporal Features**: Automatic creation of time-based features
- **Rate of Change**: Calculates biomarker and cognitive decline rates
- **Forecast Updates**: Updates predictions with new assessment data
- **Accuracy Validation**: Ensures MAE < 3 points on MMSE scale

## Components

### 1. ProgressionForecaster
Core LSTM model for time-series forecasting.

```python
from ml_pipeline.forecasting import ProgressionForecaster

forecaster = ProgressionForecaster(
    sequence_length=4,
    n_features=20,
    lstm_units=[128, 64],
    dropout_rate=0.3,
    forecast_horizons=[6, 12, 24]
)

forecaster.build_model()
forecaster.train(X_train, y_train, X_val, y_val)
predictions = forecaster.predict(X_test)
```

### 2. SequenceBuilder
Prepares longitudinal data into time-series sequences.

```python
from ml_pipeline.forecasting import SequenceBuilder

builder = SequenceBuilder(
    sequence_length=4,
    forecast_horizons=[6, 12, 24]
)

# Prepare sequences
X, y, patient_ids = builder.prepare_sequences(
    data,
    patient_id_col='patient_id',
    visit_date_col='visit_date',
    target_col='mmse_score'
)

# Add temporal features
data = builder.create_temporal_features(data)

# Calculate rate of change
data = builder.calculate_rate_of_change(data, value_cols=['mmse_score'])
```

### 3. UncertaintyQuantifier
Quantifies prediction uncertainty using Monte Carlo Dropout.

```python
from ml_pipeline.forecasting import UncertaintyQuantifier

quantifier = UncertaintyQuantifier(
    n_mc_samples=100,
    confidence_level=0.95
)

# Generate predictions with uncertainty
results = quantifier.predict_with_uncertainty(
    model,
    X_test,
    forecast_horizons=[6, 12, 24]
)

# Access predictions and intervals
for horizon in [6, 12, 24]:
    pred = results['by_horizon'][f'{horizon}_month']['prediction']
    lower = results['by_horizon'][f'{horizon}_month']['lower_bound']
    upper = results['by_horizon'][f'{horizon}_month']['upper_bound']
```

### 4. ProgressionForecastingTrainer
Orchestrates the complete training pipeline.

```python
from ml_pipeline.forecasting import ProgressionForecastingTrainer

trainer = ProgressionForecastingTrainer(
    sequence_length=4,
    forecast_horizons=[6, 12, 24],
    lstm_units=[128, 64]
)

# Prepare data
data_splits = trainer.prepare_data(data)

# Train model
results = trainer.train(data_splits, epochs=100)

# Generate forecast for patient
forecast = trainer.forecast_patient(patient_history)

# Update forecast with new data
updated_forecast = trainer.update_forecast(
    patient_history,
    new_assessment
)
```

### 5. ForecastEvaluator
Validates forecast accuracy and generates evaluation reports.

```python
from ml_pipeline.forecasting import ForecastEvaluator

evaluator = ForecastEvaluator(
    mae_threshold=3.0,
    forecast_horizons=[6, 12, 24]
)

# Evaluate accuracy
metrics = evaluator.evaluate_accuracy(y_true, y_pred)

# Validate requirements
passes, issues = evaluator.validate_requirements(metrics)

# Generate report
evaluator.generate_evaluation_report(metrics, 'report.md')
```

## Requirements

The forecasting module requires:
- TensorFlow >= 2.10
- NumPy >= 1.21
- Pandas >= 1.3
- SciPy >= 1.7
- Matplotlib >= 3.4

Install with:
```bash
pip install tensorflow numpy pandas scipy matplotlib
```

## Data Format

### Input Data
Longitudinal patient data with the following structure:

```python
data = pd.DataFrame({
    'patient_id': ['P001', 'P001', 'P001', ...],
    'visit_date': ['2020-01-01', '2020-07-01', '2021-01-01', ...],
    'mmse_score': [28, 27, 25, ...],
    'age': [65, 65.5, 66, ...],
    'sex': [1, 1, 1, ...],
    'education': [16, 16, 16, ...],
    'apoe_e4_count': [1, 1, 1, ...],
    'csf_ab42': [800, 790, 780, ...],
    'csf_tau': [400, 410, 420, ...],
    'hippocampus_volume': [3500, 3450, 3400, ...],
    # ... additional features
})
```

### Output Format
Forecasts are returned as dictionaries:

```python
{
    '6_month_mmse': 26.5,
    '12_month_mmse': 25.2,
    '24_month_mmse': 23.8
}
```

With uncertainty:
```python
{
    '6_month': {
        'prediction': 26.5,
        'std': 1.2,
        'lower_bound': 24.1,
        'upper_bound': 28.9,
        'confidence_level': 0.95
    },
    # ... other horizons
}
```

## Model Architecture

The LSTM model uses the following architecture:

```
Input: (sequence_length, n_features)
  ↓
LSTM Layer 1 (128 units)
  ↓
Dropout (0.3)
  ↓
LSTM Layer 2 (64 units)
  ↓
Dropout (0.3)
  ↓
Dense Layer (64 units, ReLU)
  ↓
Dropout (0.15)
  ↓
Dense Layer (32 units, ReLU)
  ↓
Output Layer (3 units, Linear)
  ↓
Output: [6-month, 12-month, 24-month MMSE predictions]
```

## Training

### Hyperparameters
- **Sequence Length**: 4 visits (typically 2 years of history)
- **LSTM Units**: [128, 64]
- **Dropout Rate**: 0.3
- **Learning Rate**: 0.001
- **Batch Size**: 32
- **Early Stopping Patience**: 15 epochs

### Data Splits
- Training: 70%
- Validation: 15%
- Test: 15%

Splits are performed by patient to prevent data leakage.

## Evaluation Metrics

The model is evaluated using:

1. **Mean Absolute Error (MAE)**: Primary metric, must be < 3.0 points
2. **Root Mean Squared Error (RMSE)**: Penalizes large errors
3. **R-squared (R²)**: Proportion of variance explained
4. **Median Absolute Error**: Robust to outliers
5. **90th Percentile Error**: Captures worst-case performance

### Accuracy Requirements

Per Requirement 9.6:
- Overall MAE must be below 3 points on MMSE scale (0-30)
- Each forecast horizon (6, 12, 24 months) should meet this threshold

## Usage Example

See `ml_pipeline/examples/progression_forecasting_example.py` for a complete example.

```python
from ml_pipeline.forecasting import ProgressionForecastingTrainer

# Initialize trainer
trainer = ProgressionForecastingTrainer(
    sequence_length=4,
    forecast_horizons=[6, 12, 24]
)

# Prepare data
data_splits = trainer.prepare_data(
    longitudinal_data,
    patient_id_col='patient_id',
    visit_date_col='visit_date',
    target_col='mmse_score'
)

# Train model
results = trainer.train(data_splits, epochs=100)

# Generate forecast
forecast = trainer.forecast_patient(patient_history)
print(f"6-month forecast: {forecast['6_month_mmse']:.1f}")
print(f"12-month forecast: {forecast['12_month_mmse']:.1f}")
print(f"24-month forecast: {forecast['24_month_mmse']:.1f}")
```

## Integration with ML Pipeline

The forecasting module integrates with other pipeline components:

1. **Feature Store**: Loads processed longitudinal features
2. **Model Registry**: Stores trained forecasting models
3. **Inference API**: Serves forecasts via REST endpoints
4. **Monitoring**: Tracks forecast accuracy over time

## Performance

- **Training Time**: ~30-60 minutes on CPU for 10,000 sequences
- **Inference Time**: <100ms per patient forecast
- **Memory Usage**: ~2GB during training

## Limitations

1. Requires minimum 4 visits per patient (typically 2 years)
2. Assumes regular visit intervals (±2 months tolerance)
3. Performance degrades for patients with irregular visit patterns
4. Uncertainty estimates require calibration on validation data

## Future Enhancements

- [ ] Attention mechanisms for variable-length sequences
- [ ] Multi-task learning (predict multiple outcomes)
- [ ] Transfer learning from pre-trained models
- [ ] Personalized forecasts using patient-specific features
- [ ] Explainability via attention weights

## References

- Requirement 9: Progression Forecasting (requirements.md)
- Design Document: Progression Forecasting section (design.md)
- LSTM Architecture: Hochreiter & Schmidhuber (1997)
- Monte Carlo Dropout: Gal & Ghahramani (2016)
