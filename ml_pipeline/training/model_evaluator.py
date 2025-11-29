"""
Model Evaluation Module

Comprehensive evaluation system for ML models including:
- Classification metrics (accuracy, precision, recall, F1, balanced accuracy)
- Confusion matrices with visualization
- ROC and PR curves
- Sensitivity analysis across demographic groups
- Calibration metrics (Brier score, calibration curves)
- Performance comparison reports
- Integration with Model Registry
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    balanced_accuracy_score, roc_auc_score, average_precision_score,
    confusion_matrix, roc_curve, precision_recall_curve,
    brier_score_loss, classification_report
)
from sklearn.calibration import calibration_curve
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Comprehensive model evaluation system.
    
    Provides methods for calculating metrics, generating visualizations,
    performing sensitivity analysis, and saving results to Model Registry.
    """
    
    def __init__(self, output_dir: Path, min_auc_roc: float = 0.80):
        """
        Initialize model evaluator.
        
        Args:
            output_dir: Directory for saving evaluation results
            min_auc_roc: Minimum required AUC-ROC score (default 0.80)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_auc_roc = min_auc_roc
        
        # Create subdirectories
        self.plots_dir = self.output_dir / "plots"
        self.plots_dir.mkdir(exist_ok=True)
        
        self.reports_dir = self.output_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized ModelEvaluator with output_dir: {output_dir}")
        logger.info(f"Minimum AUC-ROC requirement: {min_auc_roc}")
    
    def calculate_classification_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray,
        model_name: str = "model"
    ) -> Dict[str, float]:
        """
        Calculate comprehensive classification metrics.
        
        Implements Requirements 6.1 and 15.5:
        - Accuracy, precision, recall, F1-score
        - Balanced accuracy for imbalanced datasets
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities
            model_name: Name of the model
            
        Returns:
            Dictionary of classification metrics
        """
        logger.info(f"Calculating classification metrics for {model_name}")
        
        # Basic classification metrics
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='binary', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='binary', zero_division=0),
            'f1_score': f1_score(y_true, y_pred, average='binary', zero_division=0),
            'roc_auc': roc_auc_score(y_true, y_proba),
            'pr_auc': average_precision_score(y_true, y_proba)
        }
        
        # Log metrics
        logger.info(f"\n{model_name} Classification Metrics:")
        logger.info("-" * 50)
        for metric, value in metrics.items():
            logger.info(f"  {metric:20s}: {value:.4f}")
        
        # Check AUC-ROC requirement
        if metrics['roc_auc'] < self.min_auc_roc:
            logger.warning(
                f"⚠️  AUC-ROC {metrics['roc_auc']:.4f} is below "
                f"minimum requirement of {self.min_auc_roc}"
            )
        else:
            logger.info(
                f"✓ AUC-ROC {metrics['roc_auc']:.4f} meets "
                f"minimum requirement of {self.min_auc_roc}"
            )
        
        return metrics
    
    def generate_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        model_name: str = "model",
        class_names: Optional[List[str]] = None
    ) -> Tuple[np.ndarray, Path]:
        """
        Generate and visualize confusion matrix.
        
        Implements Requirement 6.2:
        - Create confusion matrix for each model
        - Visualize confusion matrices
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            model_name: Name of the model
            class_names: Names of classes for labels
            
        Returns:
            Tuple of (confusion matrix array, path to saved plot)
        """
        logger.info(f"Generating confusion matrix for {model_name}")
        
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Create visualization
        plt.figure(figsize=(8, 6))
        
        if class_names is None:
            class_names = ['Negative', 'Positive']
        
        # Plot heatmap
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=class_names,
            yticklabels=class_names,
            cbar_kws={'label': 'Count'}
        )
        
        plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        # Save plot
        plot_path = self.plots_dir / f"{model_name}_confusion_matrix.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Confusion matrix saved to {plot_path}")
        logger.info(f"Confusion Matrix:\n{cm}")
        
        return cm, plot_path
    
    def calculate_roc_pr_curves(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        model_name: str = "model"
    ) -> Tuple[Dict[str, Any], Path, Path]:
        """
        Calculate ROC and PR curves with AUC scores.
        
        Implements Requirements 6.3 and 5.6:
        - Calculate AUC-ROC and AUC-PR
        - Ensure minimum AUC-ROC of 0.80
        - Generate curve visualizations
        
        Args:
            y_true: True labels
            y_proba: Predicted probabilities
            model_name: Name of the model
            
        Returns:
            Tuple of (metrics dict, ROC plot path, PR plot path)
        """
        logger.info(f"Calculating ROC and PR curves for {model_name}")
        
        # Calculate ROC curve
        fpr, tpr, roc_thresholds = roc_curve(y_true, y_proba)
        roc_auc = roc_auc_score(y_true, y_proba)
        
        # Calculate PR curve
        precision, recall, pr_thresholds = precision_recall_curve(y_true, y_proba)
        pr_auc = average_precision_score(y_true, y_proba)
        
        # Create ROC curve plot
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
                label='Random classifier')
        
        # Add minimum requirement line
        if roc_auc >= self.min_auc_roc:
            plt.axhline(y=self.min_auc_roc, color='green', linestyle=':', 
                       label=f'Min requirement ({self.min_auc_roc})')
        else:
            plt.axhline(y=self.min_auc_roc, color='red', linestyle=':', 
                       label=f'Min requirement ({self.min_auc_roc})')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(f'ROC Curve - {model_name}', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        roc_plot_path = self.plots_dir / f"{model_name}_roc_curve.png"
        plt.savefig(roc_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create PR curve plot
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color='darkorange', lw=2,
                label=f'PR curve (AUC = {pr_auc:.4f})')
        
        # Baseline (random classifier)
        baseline = np.sum(y_true) / len(y_true)
        plt.axhline(y=baseline, color='navy', lw=2, linestyle='--',
                   label=f'Random classifier ({baseline:.4f})')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall', fontsize=12)
        plt.ylabel('Precision', fontsize=12)
        plt.title(f'Precision-Recall Curve - {model_name}', 
                 fontsize=14, fontweight='bold')
        plt.legend(loc="lower left")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        pr_plot_path = self.plots_dir / f"{model_name}_pr_curve.png"
        plt.savefig(pr_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"ROC curve saved to {roc_plot_path}")
        logger.info(f"PR curve saved to {pr_plot_path}")
        logger.info(f"AUC-ROC: {roc_auc:.4f}, AUC-PR: {pr_auc:.4f}")
        
        metrics = {
            'roc_auc': roc_auc,
            'pr_auc': pr_auc,
            'fpr': fpr.tolist(),
            'tpr': tpr.tolist(),
            'precision': precision.tolist(),
            'recall': recall.tolist()
        }
        
        return metrics, roc_plot_path, pr_plot_path
    
    def perform_sensitivity_analysis(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray,
        demographic_data: pd.DataFrame,
        model_name: str = "model"
    ) -> Dict[str, Dict[str, float]]:
        """
        Perform sensitivity analysis across demographic groups.
        
        Implements Requirement 6.4:
        - Evaluate performance across demographic groups
        - Check for bias in predictions
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities
            demographic_data: DataFrame with demographic columns (age, sex, etc.)
            model_name: Name of the model
            
        Returns:
            Dictionary of metrics by demographic group
        """
        logger.info(f"Performing sensitivity analysis for {model_name}")
        
        sensitivity_results = {}
        
        # Analyze by sex
        if 'sex' in demographic_data.columns:
            logger.info("\nAnalyzing by sex:")
            for sex in demographic_data['sex'].unique():
                mask = demographic_data['sex'] == sex
                if mask.sum() > 0:
                    group_metrics = self._calculate_group_metrics(
                        y_true[mask], y_pred[mask], y_proba[mask]
                    )
                    sensitivity_results[f'sex_{sex}'] = group_metrics
                    logger.info(f"  Sex={sex}: AUC-ROC={group_metrics['roc_auc']:.4f}")
        
        # Analyze by age groups
        if 'age' in demographic_data.columns:
            logger.info("\nAnalyzing by age groups:")
            age_bins = [0, 65, 75, 85, 120]
            age_labels = ['<65', '65-74', '75-84', '85+']
            demographic_data['age_group'] = pd.cut(
                demographic_data['age'], 
                bins=age_bins, 
                labels=age_labels
            )
            
            for age_group in age_labels:
                mask = demographic_data['age_group'] == age_group
                if mask.sum() > 0:
                    group_metrics = self._calculate_group_metrics(
                        y_true[mask], y_pred[mask], y_proba[mask]
                    )
                    sensitivity_results[f'age_{age_group}'] = group_metrics
                    logger.info(
                        f"  Age {age_group}: AUC-ROC={group_metrics['roc_auc']:.4f}"
                    )
        
        # Analyze by APOE e4 status if available
        if 'apoe_e4_count' in demographic_data.columns:
            logger.info("\nAnalyzing by APOE e4 status:")
            for e4_count in [0, 1, 2]:
                mask = demographic_data['apoe_e4_count'] == e4_count
                if mask.sum() > 0:
                    group_metrics = self._calculate_group_metrics(
                        y_true[mask], y_pred[mask], y_proba[mask]
                    )
                    sensitivity_results[f'apoe_e4_{e4_count}'] = group_metrics
                    logger.info(
                        f"  APOE e4 count={e4_count}: "
                        f"AUC-ROC={group_metrics['roc_auc']:.4f}"
                    )
        
        # Check for significant performance disparities
        self._check_bias(sensitivity_results, model_name)
        
        # Save sensitivity analysis report
        report_path = self.reports_dir / f"{model_name}_sensitivity_analysis.json"
        with open(report_path, 'w') as f:
            json.dump(sensitivity_results, f, indent=2)
        
        logger.info(f"Sensitivity analysis saved to {report_path}")
        
        return sensitivity_results
    
    def _calculate_group_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray
    ) -> Dict[str, float]:
        """Calculate metrics for a demographic group."""
        if len(y_true) == 0:
            return {}
        
        return {
            'n_samples': len(y_true),
            'accuracy': accuracy_score(y_true, y_pred),
            'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_true, y_proba) if len(np.unique(y_true)) > 1 else 0.0
        }
    
    def _check_bias(
        self,
        sensitivity_results: Dict[str, Dict[str, float]],
        model_name: str
    ):
        """Check for significant performance disparities indicating bias."""
        logger.info(f"\nChecking for bias in {model_name}:")
        
        # Extract AUC-ROC scores
        auc_scores = {
            group: metrics.get('roc_auc', 0.0)
            for group, metrics in sensitivity_results.items()
            if metrics.get('n_samples', 0) > 30  # Only groups with sufficient samples
        }
        
        if len(auc_scores) < 2:
            logger.info("  Insufficient groups for bias analysis")
            return
        
        # Calculate disparity
        max_auc = max(auc_scores.values())
        min_auc = min(auc_scores.values())
        disparity = max_auc - min_auc
        
        logger.info(f"  AUC-ROC range: {min_auc:.4f} to {max_auc:.4f}")
        logger.info(f"  Disparity: {disparity:.4f}")
        
        # Flag if disparity > 0.10 (10% difference)
        if disparity > 0.10:
            logger.warning(
                f"  ⚠️  Significant performance disparity detected ({disparity:.4f})"
            )
            logger.warning("  Consider investigating potential bias")
        else:
            logger.info("  ✓ No significant bias detected")

    def calculate_calibration_metrics(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        model_name: str = "model",
        n_bins: int = 10
    ) -> Tuple[Dict[str, float], Path]:
        """
        Calculate calibration metrics and generate calibration curve.
        
        Implements Requirement 6.5:
        - Calculate Brier score
        - Generate calibration curves
        
        Args:
            y_true: True labels
            y_proba: Predicted probabilities
            model_name: Name of the model
            n_bins: Number of bins for calibration curve
            
        Returns:
            Tuple of (calibration metrics dict, plot path)
        """
        logger.info(f"Calculating calibration metrics for {model_name}")
        
        # Calculate Brier score
        brier_score = brier_score_loss(y_true, y_proba)
        
        # Calculate calibration curve
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true, y_proba, n_bins=n_bins, strategy='uniform'
        )
        
        # Calculate Expected Calibration Error (ECE)
        ece = self._calculate_ece(y_true, y_proba, n_bins)
        
        # Create calibration plot
        plt.figure(figsize=(8, 6))
        
        # Plot calibration curve
        plt.plot(mean_predicted_value, fraction_of_positives, 
                marker='o', linewidth=2, label=model_name)
        
        # Plot perfect calibration
        plt.plot([0, 1], [0, 1], linestyle='--', color='gray', 
                label='Perfect calibration')
        
        plt.xlabel('Mean Predicted Probability', fontsize=12)
        plt.ylabel('Fraction of Positives', fontsize=12)
        plt.title(
            f'Calibration Curve - {model_name}\n'
            f'Brier Score: {brier_score:.4f}, ECE: {ece:.4f}',
            fontsize=14, fontweight='bold'
        )
        plt.legend(loc='upper left')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        # Save plot
        plot_path = self.plots_dir / f"{model_name}_calibration_curve.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Calibration curve saved to {plot_path}")
        logger.info(f"Brier Score: {brier_score:.4f}")
        logger.info(f"Expected Calibration Error: {ece:.4f}")
        
        metrics = {
            'brier_score': brier_score,
            'expected_calibration_error': ece,
            'fraction_of_positives': fraction_of_positives.tolist(),
            'mean_predicted_value': mean_predicted_value.tolist()
        }
        
        return metrics, plot_path
    
    def _calculate_ece(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """
        Calculate Expected Calibration Error.
        
        Args:
            y_true: True labels
            y_proba: Predicted probabilities
            n_bins: Number of bins
            
        Returns:
            Expected Calibration Error
        """
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0.0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find predictions in this bin
            in_bin = (y_proba > bin_lower) & (y_proba <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = y_true[in_bin].mean()
                avg_confidence_in_bin = y_proba[in_bin].mean()
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece
    
    def generate_performance_comparison(
        self,
        models_results: Dict[str, Dict[str, Any]],
        save_report: bool = True
    ) -> Tuple[pd.DataFrame, Path]:
        """
        Generate performance comparison report across all models.
        
        Implements Requirement 6.6:
        - Compare all models
        - Identify best performing model
        
        Args:
            models_results: Dictionary mapping model names to their results
            save_report: Whether to save the comparison report
            
        Returns:
            Tuple of (comparison DataFrame, report path)
        """
        logger.info("Generating performance comparison report")
        
        # Extract metrics for comparison
        comparison_data = []
        
        for model_name, results in models_results.items():
            metrics = results.get('metrics', {})
            
            row = {
                'model': model_name,
                'accuracy': metrics.get('accuracy', 0.0),
                'balanced_accuracy': metrics.get('balanced_accuracy', 0.0),
                'precision': metrics.get('precision', 0.0),
                'recall': metrics.get('recall', 0.0),
                'f1_score': metrics.get('f1_score', 0.0),
                'roc_auc': metrics.get('roc_auc', 0.0),
                'pr_auc': metrics.get('pr_auc', 0.0),
                'brier_score': metrics.get('brier_score', 0.0)
            }
            comparison_data.append(row)
        
        # Create DataFrame
        comparison_df = pd.DataFrame(comparison_data)
        
        # Sort by ROC-AUC (primary metric)
        comparison_df = comparison_df.sort_values('roc_auc', ascending=False)
        
        # Identify best model
        best_model = comparison_df.iloc[0]['model']
        best_auc = comparison_df.iloc[0]['roc_auc']
        
        logger.info("\n" + "=" * 80)
        logger.info("MODEL PERFORMANCE COMPARISON")
        logger.info("=" * 80)
        logger.info(f"\n{comparison_df.to_string(index=False)}")
        logger.info("\n" + "=" * 80)
        logger.info(f"🏆 Best Model: {best_model} (AUC-ROC: {best_auc:.4f})")
        logger.info("=" * 80)
        
        # Create visualization
        self._plot_model_comparison(comparison_df)
        
        # Save report
        report_path = None
        if save_report:
            report_path = self.reports_dir / "model_comparison.csv"
            comparison_df.to_csv(report_path, index=False)
            logger.info(f"\nComparison report saved to {report_path}")
            
            # Also save as JSON with more details
            json_path = self.reports_dir / "model_comparison.json"
            comparison_dict = {
                'comparison': comparison_df.to_dict('records'),
                'best_model': best_model,
                'best_auc_roc': float(best_auc),
                'timestamp': datetime.now().isoformat()
            }
            with open(json_path, 'w') as f:
                json.dump(comparison_dict, f, indent=2)
            logger.info(f"Detailed comparison saved to {json_path}")
        
        return comparison_df, report_path
    
    def _plot_model_comparison(self, comparison_df: pd.DataFrame):
        """Create visualization comparing model performance."""
        # Select key metrics for visualization
        metrics_to_plot = [
            'accuracy', 'balanced_accuracy', 'precision', 
            'recall', 'f1_score', 'roc_auc', 'pr_auc'
        ]
        
        # Create bar plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(comparison_df))
        width = 0.12
        
        for i, metric in enumerate(metrics_to_plot):
            offset = (i - len(metrics_to_plot) / 2) * width
            ax.bar(
                x + offset, 
                comparison_df[metric], 
                width, 
                label=metric.replace('_', ' ').title()
            )
        
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(comparison_df['model'], rotation=45, ha='right')
        ax.legend(loc='lower right', ncol=2)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim([0, 1.05])
        
        plt.tight_layout()
        
        plot_path = self.plots_dir / "model_comparison.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Comparison plot saved to {plot_path}")
    
    def save_to_model_registry(
        self,
        model_name: str,
        version_id: str,
        metrics: Dict[str, float],
        registry_db_path: Optional[Path] = None
    ) -> bool:
        """
        Save evaluation metrics to Model Registry.
        
        Implements Requirements 6.7 and 15.6:
        - Store metrics in Model Registry
        
        Args:
            model_name: Name of the model
            version_id: Version identifier
            metrics: Dictionary of evaluation metrics
            registry_db_path: Path to registry database (optional)
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Saving metrics to Model Registry for {model_name} v{version_id}")
        
        try:
            # If registry DB path provided, update database
            if registry_db_path:
                from ml_pipeline.data_storage.database import get_session
                from ml_pipeline.data_storage.models import ModelVersion
                
                session = get_session()
                
                # Find model version
                model_version = session.query(ModelVersion).filter_by(
                    version_id=version_id
                ).first()
                
                if model_version:
                    # Update metrics
                    model_version.accuracy = metrics.get('accuracy')
                    model_version.balanced_accuracy = metrics.get('balanced_accuracy')
                    model_version.precision = metrics.get('precision')
                    model_version.recall = metrics.get('recall')
                    model_version.f1_score = metrics.get('f1_score')
                    model_version.roc_auc = metrics.get('roc_auc')
                    model_version.pr_auc = metrics.get('pr_auc')
                    
                    session.commit()
                    logger.info("✓ Metrics saved to database")
                else:
                    logger.warning(f"Model version {version_id} not found in registry")
                    session.close()
                    return False
                
                session.close()
            
            # Always save to JSON file as backup
            metrics_file = self.reports_dir / f"{model_name}_{version_id}_metrics.json"
            metrics_data = {
                'model_name': model_name,
                'version_id': version_id,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            logger.info(f"✓ Metrics saved to {metrics_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving metrics to registry: {e}")
            return False
    
    def evaluate_model_complete(
        self,
        model,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        demographic_data: Optional[pd.DataFrame] = None,
        model_name: str = "model",
        version_id: Optional[str] = None,
        save_to_registry: bool = True
    ) -> Dict[str, Any]:
        """
        Perform complete model evaluation with all metrics and visualizations.
        
        This is a convenience method that runs all evaluation steps.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            demographic_data: Demographic data for sensitivity analysis
            model_name: Name of the model
            version_id: Version identifier for registry
            save_to_registry: Whether to save to model registry
            
        Returns:
            Dictionary with all evaluation results
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"COMPLETE EVALUATION: {model_name}")
        logger.info("=" * 80)
        
        # Get predictions
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        results = {}
        
        # 1. Classification metrics
        logger.info("\n[1/5] Calculating classification metrics...")
        classification_metrics = self.calculate_classification_metrics(
            y_test.values, y_pred, y_proba, model_name
        )
        results['classification_metrics'] = classification_metrics
        
        # 2. Confusion matrix
        logger.info("\n[2/5] Generating confusion matrix...")
        cm, cm_path = self.generate_confusion_matrix(
            y_test.values, y_pred, model_name
        )
        results['confusion_matrix'] = cm.tolist()
        results['confusion_matrix_plot'] = str(cm_path)
        
        # 3. ROC and PR curves
        logger.info("\n[3/5] Calculating ROC and PR curves...")
        curve_metrics, roc_path, pr_path = self.calculate_roc_pr_curves(
            y_test.values, y_proba, model_name
        )
        results['curve_metrics'] = curve_metrics
        results['roc_plot'] = str(roc_path)
        results['pr_plot'] = str(pr_path)
        
        # 4. Calibration metrics
        logger.info("\n[4/5] Calculating calibration metrics...")
        calibration_metrics, cal_path = self.calculate_calibration_metrics(
            y_test.values, y_proba, model_name
        )
        results['calibration_metrics'] = calibration_metrics
        results['calibration_plot'] = str(cal_path)
        
        # 5. Sensitivity analysis (if demographic data provided)
        if demographic_data is not None:
            logger.info("\n[5/5] Performing sensitivity analysis...")
            sensitivity_results = self.perform_sensitivity_analysis(
                y_test.values, y_pred, y_proba, 
                demographic_data, model_name
            )
            results['sensitivity_analysis'] = sensitivity_results
        else:
            logger.info("\n[5/5] Skipping sensitivity analysis (no demographic data)")
        
        # Combine all metrics
        all_metrics = {
            **classification_metrics,
            'brier_score': calibration_metrics['brier_score'],
            'expected_calibration_error': calibration_metrics['expected_calibration_error']
        }
        results['metrics'] = all_metrics
        
        # Save to model registry
        if save_to_registry and version_id:
            logger.info("\nSaving to Model Registry...")
            self.save_to_model_registry(model_name, version_id, all_metrics)
        
        # Save complete results
        results_file = self.reports_dir / f"{model_name}_complete_evaluation.json"
        with open(results_file, 'w') as f:
            # Convert numpy types to native Python types for JSON serialization
            json_results = self._convert_to_json_serializable(results)
            json.dump(json_results, f, indent=2)
        
        logger.info(f"\nComplete evaluation results saved to {results_file}")
        logger.info("\n" + "=" * 80)
        logger.info(f"EVALUATION COMPLETE: {model_name}")
        logger.info("=" * 80)
        
        return results
    
    def _convert_to_json_serializable(self, obj):
        """Convert numpy types to JSON-serializable types."""
        if isinstance(obj, dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, Path):
            return str(obj)
        else:
            return obj
