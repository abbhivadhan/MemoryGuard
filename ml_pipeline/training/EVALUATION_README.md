# Model Evaluation System

## Overview

The Model Evaluation system provides comprehensive evaluation capabilities for ML models trained in the biomedical data pipeline. It implements all requirements from Task 7 of the implementation plan.

## Features

### 1. Classification Metrics (Task 7.1)
- **Accuracy**: Overall correctness of predictions
- **Balanced Accuracy**: Accuracy adjusted for class imbalance
- **Precision**: Proportion of positive predictions that are correct
- **Recall**: Proportion of actual positives correctly identified
- **F1-Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Area under the ROC curve
- **PR-AUC**: Area under the Precision-Recall curve

**Requirements Implemented**: 6.1, 15.5

### 2. Confusion Matrices (Task 7.2)
- Generate confusion matrices for each model
- Visualize with heatmaps
- Save as high-resolution PNG files

**Requirements Implemented**: 6.2

### 3. ROC and PR Curves (Task 7.3)
- Calculate and plot ROC curves with AUC scores
- Calculate and plot Precision-Recall curves
- Verify minimum AUC-ROC of 0.80 requirement
- Visual indicators for requirement compliance

**Requirements Implemented**: 6.3, 5.6

### 4. Sensitivity Analysis (Task 7.4)
- Evaluate performance across demographic groups:
  - Sex (M/F)
  - Age groups (<65, 65-74, 75-84, 85+)
  - APOE e4 status (0, 1, 2 alleles)
- Detect performance disparities indicating bias
- Generate detailed reports by subgroup

**Requirements Implemented**: 6.4

### 5. Calibration Metrics (Task 7.5)
- Calculate Brier score
- Calculate Expected Calibration Error (ECE)
- Generate calibration curves
- Visualize calibration quality

**Requirements Implemented**: 6.5

### 6. Performance Comparison (Task 7.6)
- Compare all models side-by-side
- Identify best performing model
- Generate comparison visualizations
- Export to CSV and JSON formats

**Requirements Implemented**: 6.6

### 7. Model Registry Integration (Task 7.7)
- Save metrics to Model Registry database
- Store metrics as JSON files
- Track evaluation timestamps
- Support version control

**Requirements Implemented**: 6.7, 15.6

## Usage

### Basic Usage

```python
from pathlib import Path
from ml_pipeline.training.model_evaluator import ModelEvaluator

# Initialize evaluator
evaluator = ModelEvaluator(
    output_dir=Path("evaluation_results"),
    min_auc_roc=0.80  # Minimum requirement
)

# Evaluate a single model
results = evaluator.evaluate_model_complete(
    model=trained_model,
    X_test=X_test,
    y_test=y_test,
    demographic_data=demographics,
    model_name="RandomForest",
    version_id="v1.0.0",
    save_to_registry=True
)
```

### Individual Metric Calculations

```python
# 1. Classification metrics
metrics = evaluator.calculate_classification_metrics(
    y_true, y_pred, y_proba, model_name="MyModel"
)

# 2. Confusion matrix
cm, plot_path = evaluator.generate_confusion_matrix(
    y_true, y_pred, model_name="MyModel"
)

# 3. ROC and PR curves
curve_metrics, roc_path, pr_path = evaluator.calculate_roc_pr_curves(
    y_true, y_proba, model_name="MyModel"
)

# 4. Sensitivity analysis
sensitivity_results = evaluator.perform_sensitivity_analysis(
    y_true, y_pred, y_proba, demographic_data, model_name="MyModel"
)

# 5. Calibration metrics
cal_metrics, cal_path = evaluator.calculate_calibration_metrics(
    y_true, y_proba, model_name="MyModel"
)
```

### Model Comparison

```python
# Evaluate multiple models
models_results = {
    'RandomForest': {'metrics': rf_metrics},
    'XGBoost': {'metrics': xgb_metrics},
    'NeuralNetwork': {'metrics': nn_metrics}
}

# Generate comparison report
comparison_df, report_path = evaluator.generate_performance_comparison(
    models_results, save_report=True
)
```

### Integration with Training Pipeline

The evaluator is automatically integrated into the training pipeline:

```python
from ml_pipeline.training.training_pipeline import MLTrainingPipeline

pipeline = MLTrainingPipeline(
    feature_store_path=Path("data_storage/features"),
    output_dir=Path("training_output")
)

# Run full pipeline (includes evaluation)
summary = pipeline.run_full_pipeline(
    dataset_name="train_features",
    target_column="diagnosis",
    save_models=True
)

# Evaluation results are in summary['evaluation']
```

## Output Structure

```
evaluation_results/
├── plots/
│   ├── RandomForest_confusion_matrix.png
│   ├── RandomForest_roc_curve.png
│   ├── RandomForest_pr_curve.png
│   ├── RandomForest_calibration_curve.png
│   ├── XGBoost_confusion_matrix.png
│   ├── XGBoost_roc_curve.png
│   ├── ...
│   └── model_comparison.png
├── reports/
│   ├── RandomForest_sensitivity_analysis.json
│   ├── RandomForest_complete_evaluation.json
│   ├── RandomForest_v1.0.0_metrics.json
│   ├── XGBoost_sensitivity_analysis.json
│   ├── ...
│   ├── model_comparison.csv
│   └── model_comparison.json
```

## Metrics Definitions

### Classification Metrics

- **Accuracy**: (TP + TN) / (TP + TN + FP + FN)
- **Balanced Accuracy**: (Sensitivity + Specificity) / 2
- **Precision**: TP / (TP + FP)
- **Recall (Sensitivity)**: TP / (TP + FN)
- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)
- **ROC-AUC**: Area under the Receiver Operating Characteristic curve
- **PR-AUC**: Area under the Precision-Recall curve

### Calibration Metrics

- **Brier Score**: Mean squared difference between predicted probabilities and actual outcomes (lower is better)
- **Expected Calibration Error (ECE)**: Average difference between predicted confidence and actual accuracy across bins

## Requirements Compliance

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| 6.1 - Classification metrics | ✅ | `calculate_classification_metrics()` |
| 6.2 - Confusion matrices | ✅ | `generate_confusion_matrix()` |
| 6.3 - ROC/PR curves | ✅ | `calculate_roc_pr_curves()` |
| 6.4 - Sensitivity analysis | ✅ | `perform_sensitivity_analysis()` |
| 6.5 - Calibration metrics | ✅ | `calculate_calibration_metrics()` |
| 6.6 - Performance comparison | ✅ | `generate_performance_comparison()` |
| 6.7 - Save to registry | ✅ | `save_to_model_registry()` |
| 5.6 - Min AUC-ROC 0.80 | ✅ | Verified in `calculate_roc_pr_curves()` |
| 15.5 - Balanced accuracy | ✅ | Included in classification metrics |
| 15.6 - Registry storage | ✅ | Database and JSON storage |

## Example Output

### Classification Metrics
```
RandomForest Classification Metrics:
--------------------------------------------------
  accuracy            : 0.8542
  balanced_accuracy   : 0.8456
  precision           : 0.8234
  recall              : 0.8678
  f1_score            : 0.8450
  roc_auc             : 0.9123
  pr_auc              : 0.8876
✓ AUC-ROC 0.9123 meets minimum requirement of 0.80
```

### Sensitivity Analysis
```
Analyzing by sex:
  Sex=M: AUC-ROC=0.9145
  Sex=F: AUC-ROC=0.9098

Analyzing by age groups:
  Age <65: AUC-ROC=0.9234
  Age 65-74: AUC-ROC=0.9156
  Age 75-84: AUC-ROC=0.9089
  Age 85+: AUC-ROC=0.8967

Checking for bias:
  AUC-ROC range: 0.8967 to 0.9234
  Disparity: 0.0267
  ✓ No significant bias detected
```

### Model Comparison
```
MODEL PERFORMANCE COMPARISON
================================================================================
         model  accuracy  balanced_accuracy  precision  recall  f1_score  roc_auc  pr_auc
  RandomForest    0.8542             0.8456     0.8234  0.8678    0.8450   0.9123  0.8876
       XGBoost    0.8623             0.8534     0.8345  0.8756    0.8545   0.9234  0.8967
 NeuralNetwork    0.8489             0.8401     0.8189  0.8623    0.8401   0.9089  0.8823
      Ensemble    0.8678             0.8589     0.8423  0.8812    0.8612   0.9289  0.9012
================================================================================
🏆 Best Model: Ensemble (AUC-ROC: 0.9289)
================================================================================
```

## Running the Example

```bash
# Run the evaluation example
cd ml_pipeline
python examples/model_evaluation_example.py
```

This will:
1. Train Random Forest, XGBoost, and Neural Network models
2. Evaluate each model with all metrics
3. Generate visualizations
4. Perform sensitivity analysis
5. Create performance comparison
6. Save results to Model Registry

## Dependencies

- scikit-learn >= 1.0.0
- matplotlib >= 3.5.0
- seaborn >= 0.11.0
- pandas >= 1.3.0
- numpy >= 1.21.0

## Notes

- All plots are saved as 300 DPI PNG files for publication quality
- Metrics are saved in both JSON (detailed) and CSV (tabular) formats
- The minimum AUC-ROC requirement of 0.80 is automatically checked
- Bias detection flags disparities > 0.10 (10% difference)
- Calibration curves use 10 bins by default (configurable)

## Future Enhancements

- Support for multi-class classification
- Additional fairness metrics (demographic parity, equalized odds)
- Interactive visualizations with Plotly
- Automated report generation in PDF format
- Integration with MLflow for experiment tracking
