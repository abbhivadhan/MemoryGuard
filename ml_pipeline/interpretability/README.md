# Model Interpretability System

Comprehensive SHAP-based interpretability system for Alzheimer's Disease ML models.

## Overview

This module provides tools for explaining ML model predictions using SHAP (SHapley Additive exPlanations) values. It implements all requirements from the design specification for model interpretability.

## Features

### 1. SHAP Explainers (Requirement 7.1)
- **TreeSHAPExplainer**: Fast, exact SHAP values for tree-based models (Random Forest, XGBoost)
- **DeepSHAPExplainer**: SHAP values for neural networks
- **EnsembleSHAPExplainer**: Aggregated explanations from multiple models

### 2. Feature Importance Analysis (Requirements 7.2, 7.6)
- Global feature importance across all predictions
- Identification of top contributing features
- Biomarker, cognitive, and imaging feature analysis
- Feature importance by category

### 3. Individual Prediction Explanations (Requirement 7.4)
- SHAP values for single predictions
- Top 5 contributing features
- Human-readable explanations
- Clinical summaries for healthcare providers

### 4. Visualizations (Requirement 7.3)
- SHAP summary plots (dot, bar, violin)
- Feature importance charts
- Waterfall plots for individual predictions
- Force plots
- Dependence plots
- Category-based importance charts
- Model comparison plots

### 5. Confidence Intervals (Requirement 7.5)
- Prediction confidence intervals
- Ensemble prediction uncertainty
- SHAP value confidence intervals
- Calibrated confidence scores

### 6. Performance Optimization (Requirement 7.7)
- SHAP generation within 2 seconds
- Explanation caching
- Background data sampling
- Batch processing optimization

## Installation

Required packages:
```bash
pip install shap numpy pandas matplotlib seaborn scipy scikit-learn
```

## Quick Start

```python
from ml_pipeline.interpretability import InterpretabilitySystem

# Initialize system
interp_system = InterpretabilitySystem(
    model=trained_model,
    model_type='tree',  # or 'deep', 'ensemble'
    feature_names=feature_names,
    output_dir=Path("outputs/interpretability")
)

# Initialize with background data
interp_system.initialize(background_data)

# Explain a single prediction
explanation = interp_system.explain_prediction(
    X=feature_vector,
    prediction=model_prediction,
    probability=prediction_probability
)

# Analyze global feature importance
importance_report = interp_system.analyze_feature_importance(
    X_sample=test_data,
    model_name="MyModel"
)

# Create visualizations
plots = interp_system.create_visualizations(
    X_sample=test_data,
    model_name="MyModel"
)

# Generate complete report
report = interp_system.generate_complete_report(
    X_sample=test_data,
    model_name="MyModel"
)
```

## Components

### InterpretabilitySystem
Main interface for all interpretability functionality.

**Key Methods:**
- `initialize(background_data)`: Initialize SHAP explainer
- `explain_prediction(X, prediction, probability)`: Explain single prediction
- `analyze_feature_importance(X_sample)`: Global feature importance
- `create_visualizations(X_sample)`: Generate all plots
- `calculate_confidence_intervals(predictions)`: Compute confidence intervals
- `benchmark_performance(X_sample)`: Test performance requirements

### SHAPExplainer Classes
Generate SHAP values for different model types.

**TreeSHAPExplainer:**
```python
explainer = TreeSHAPExplainer(model, feature_names)
explainer.initialize()
explanation = explainer.explain_prediction(X)
top_features = explainer.get_top_features(X, top_n=5)
```

**DeepSHAPExplainer:**
```python
explainer = DeepSHAPExplainer(model, feature_names)
explainer.initialize(background_data)
explanation = explainer.explain_prediction(X)
```

**EnsembleSHAPExplainer:**
```python
explainer = EnsembleSHAPExplainer(
    models={'rf': rf_model, 'xgb': xgb_model},
    model_types={'rf': 'tree', 'xgb': 'tree'},
    feature_names=feature_names,
    weights={'rf': 0.5, 'xgb': 0.5}
)
explainer.initialize(background_data)
explanation = explainer.explain_prediction(X, aggregate=True)
```

### FeatureImportanceAnalyzer
Analyze global feature importance.

```python
analyzer = FeatureImportanceAnalyzer(feature_names, output_dir)

# Calculate global importance
importance = analyzer.calculate_global_importance(shap_values)

# Get ranked features
ranked = analyzer.get_ranked_features(shap_values, top_n=20)

# Identify biomarker contributions
biomarkers = analyzer.identify_biomarker_contributions(shap_values)

# Generate comprehensive report
report = analyzer.generate_importance_report(
    shap_values,
    model_name="MyModel"
)
```

### PredictionExplainer
Generate detailed explanations for individual predictions.

```python
explainer = PredictionExplainer(shap_explainer, feature_names)

# Explain single prediction
explanation = explainer.explain_single_prediction(
    X, prediction, probability, top_n=5
)

# Generate clinical summary
summary = explainer.generate_clinical_summary(
    X, prediction, probability, patient_data
)

# Compare two predictions
comparison = explainer.generate_comparison_explanation(
    X1, X2, pred1, pred2, prob1, prob2
)
```

### InterpretabilityVisualizer
Create interpretability visualizations.

```python
visualizer = InterpretabilityVisualizer(output_dir, feature_names)

# SHAP summary plot
plot_path = visualizer.create_shap_summary_plot(
    shap_values, X, model_name="MyModel"
)

# Feature importance chart
plot_path = visualizer.create_feature_importance_chart(
    feature_importance, model_name="MyModel"
)

# Waterfall plot for single prediction
plot_path = visualizer.create_waterfall_plot(
    shap_values[0], base_value, X[0], model_name="MyModel"
)

# Create all visualizations
plots = visualizer.create_all_visualizations(
    shap_values, X, feature_importance, model_name="MyModel"
)
```

### ConfidenceIntervalCalculator
Calculate confidence intervals for predictions.

```python
ci_calculator = ConfidenceIntervalCalculator(confidence_level=0.95)

# Ensemble prediction CI
ci_info = ci_calculator.calculate_ensemble_prediction_ci(
    model_predictions={'rf': rf_preds, 'xgb': xgb_preds}
)

# Assess uncertainty
assessment = ci_calculator.assess_prediction_uncertainty(
    prediction, lower_bound, upper_bound
)

# Generate confidence report
report = ci_calculator.generate_confidence_report(
    prediction, lower_bound, upper_bound, model_predictions
)
```

## Performance

The system is optimized to meet the requirement of generating SHAP explanations within 2 seconds:

- **TreeSHAPExplainer**: Typically < 0.1 seconds (exact, no approximation)
- **DeepSHAPExplainer**: Typically < 1 second with 100 background samples
- **Caching**: Repeated explanations are instant

Benchmark performance:
```python
metrics = interp_system.benchmark_performance(X_sample, n_iterations=20)
# Returns: mean_time, median_time, meets_requirement, etc.
```

## Output Structure

```
output_dir/
├── feature_importance/
│   ├── model_feature_importance.json
│   ├── model_feature_statistics.csv
│   └── ...
├── visualizations/
│   ├── model_shap_summary_dot.png
│   ├── model_shap_summary_bar.png
│   ├── model_feature_importance.png
│   ├── model_category_importance.png
│   └── ...
└── cache/
    └── explanation_cache.pkl
```

## Examples

See `ml_pipeline/examples/interpretability_example.py` for a complete working example.

## Requirements Mapping

| Requirement | Component | Status |
|------------|-----------|--------|
| 7.1 - Generate SHAP values | SHAPExplainer classes | ✓ |
| 7.2 - Global feature importance | FeatureImportanceAnalyzer | ✓ |
| 7.3 - Visualizations | InterpretabilityVisualizer | ✓ |
| 7.4 - Individual explanations | PredictionExplainer | ✓ |
| 7.5 - Confidence intervals | ConfidenceIntervalCalculator | ✓ |
| 7.6 - Biomarker contributions | FeatureImportanceAnalyzer | ✓ |
| 7.7 - Performance (< 2s) | InterpretabilitySystem | ✓ |

## Best Practices

1. **Initialize once**: Initialize the interpretability system once and reuse it
2. **Use caching**: Enable caching for repeated explanations
3. **Sample background data**: Use 100-200 samples for background data
4. **Batch processing**: Process multiple predictions together when possible
5. **Tree models preferred**: TreeSHAP is faster and exact compared to DeepSHAP

## Troubleshooting

**Slow SHAP generation:**
- Reduce background data samples (max_background_samples=50)
- Use TreeSHAP instead of DeepSHAP when possible
- Enable caching

**Memory issues:**
- Process data in smaller batches
- Reduce background data size
- Clear cache periodically

**Visualization errors:**
- Ensure matplotlib backend is configured
- Check that output directory is writable
- Verify SHAP values shape matches feature count

## References

- SHAP: https://github.com/slundberg/shap
- Lundberg & Lee (2017): "A Unified Approach to Interpreting Model Predictions"
- Lundberg et al. (2020): "From local explanations to global understanding"
