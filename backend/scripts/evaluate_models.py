"""
Script to evaluate trained ML models with comprehensive metrics.

This script:
1. Loads trained models
2. Calculates accuracy, precision, recall, F1 scores
3. Generates confusion matrices
4. Performs cross-validation
5. Creates evaluation reports and visualizations

Usage:
    python scripts/evaluate_models.py --model-dir models/latest --data-dir data/processed
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, List
import numpy as np
import json
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.models.ensemble import AlzheimerEnsemble
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve,
    confusion_matrix, classification_report
)
from sklearn.model_selection import cross_val_score, StratifiedKFold
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Comprehensive model evaluation and validation.
    """
    
    def __init__(self, model_dir: str, data_dir: str, output_dir: str = None):
        """
        Initialize model evaluator.
        
        Args:
            model_dir: Directory containing trained model
            data_dir: Directory containing test data
            output_dir: Directory to save evaluation results
        """
        self.model_dir = Path(model_dir)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir) if output_dir else self.model_dir / 'evaluation'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.ensemble = None
        self.X_test = None
        self.y_test = None
        self.X_train = None
        self.y_train = None
        self.feature_names = []
    
    def load_model(self) -> None:
        """Load trained ensemble model."""
        logger.info(f"Loading model from {self.model_dir}")
        
        try:
            self.ensemble = AlzheimerEnsemble()
            self.ensemble.load(str(self.model_dir / 'ensemble'))
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def load_data(self) -> None:
        """Load test data."""
        logger.info(f"Loading data from {self.data_dir}")
        
        try:
            self.X_test = np.load(self.data_dir / 'X_test.npy')
            self.y_test = np.load(self.data_dir / 'y_test.npy')
            self.X_train = np.load(self.data_dir / 'X_train.npy')
            self.y_train = np.load(self.data_dir / 'y_train.npy')
            
            with open(self.data_dir / 'metadata.json', 'r') as f:
                metadata = json.load(f)
            
            self.feature_names = metadata['feature_names']
            
            logger.info(f"Loaded test data: {self.X_test.shape}")
            logger.info(f"Loaded train data: {self.X_train.shape}")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def calculate_metrics(self) -> Dict:
        """
        Calculate comprehensive evaluation metrics.
        
        Returns:
            Dictionary with all metrics
        """
        logger.info("Calculating evaluation metrics...")
        
        # Make predictions
        predictions = []
        probabilities = []
        confidence_scores = []
        confidence_intervals = []
        
        for i in range(len(self.X_test)):
            pred, conf, ci = self.ensemble.predict_with_confidence(self.X_test[i])
            _, prob = self.ensemble.predict_proba(self.X_test[i])
            
            predictions.append(pred)
            probabilities.append(prob)
            confidence_scores.append(conf)
            confidence_intervals.append(ci)
        
        predictions = np.array(predictions)
        probabilities = np.array(probabilities)
        confidence_scores = np.array(confidence_scores)
        
        # Basic metrics
        accuracy = accuracy_score(self.y_test, predictions)
        precision = precision_score(self.y_test, predictions, zero_division=0)
        recall = recall_score(self.y_test, predictions, zero_division=0)
        f1 = f1_score(self.y_test, predictions, zero_division=0)
        
        # ROC AUC
        try:
            auc = roc_auc_score(self.y_test, probabilities)
        except:
            auc = 0.0
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, predictions)
        tn, fp, fn, tp = cm.ravel()
        
        # Additional metrics
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0  # Negative Predictive Value
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0  # Positive Predictive Value
        
        # Balanced accuracy
        balanced_acc = (sensitivity + specificity) / 2
        
        # Matthews Correlation Coefficient
        mcc_num = (tp * tn) - (fp * fn)
        mcc_den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = mcc_num / mcc_den if mcc_den > 0 else 0
        
        metrics = {
            'accuracy': float(accuracy),
            'balanced_accuracy': float(balanced_acc),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'auc_roc': float(auc),
            'sensitivity': float(sensitivity),
            'specificity': float(specificity),
            'ppv': float(ppv),
            'npv': float(npv),
            'mcc': float(mcc),
            'confusion_matrix': cm.tolist(),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
            'mean_confidence': float(np.mean(confidence_scores)),
            'std_confidence': float(np.std(confidence_scores))
        }
        
        return metrics
    
    def perform_cross_validation(self, n_folds: int = 5) -> Dict:
        """
        Perform k-fold cross-validation.
        
        Args:
            n_folds: Number of folds
            
        Returns:
            Dictionary with CV metrics
        """
        logger.info(f"Performing {n_folds}-fold cross-validation...")
        
        # Use stratified k-fold
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        
        cv_scores = {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1': []
        }
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(self.X_train, self.y_train)):
            X_fold_train = self.X_train[train_idx]
            y_fold_train = self.y_train[train_idx]
            X_fold_val = self.X_train[val_idx]
            y_fold_val = self.y_train[val_idx]
            
            # Make predictions on validation fold
            fold_predictions = []
            for i in range(len(X_fold_val)):
                pred = self.ensemble.predict(X_fold_val[i])
                fold_predictions.append(pred)
            
            fold_predictions = np.array(fold_predictions)
            
            # Calculate metrics
            cv_scores['accuracy'].append(accuracy_score(y_fold_val, fold_predictions))
            cv_scores['precision'].append(precision_score(y_fold_val, fold_predictions, zero_division=0))
            cv_scores['recall'].append(recall_score(y_fold_val, fold_predictions, zero_division=0))
            cv_scores['f1'].append(f1_score(y_fold_val, fold_predictions, zero_division=0))
        
        # Calculate mean and std
        cv_results = {}
        for metric, scores in cv_scores.items():
            cv_results[f'{metric}_mean'] = float(np.mean(scores))
            cv_results[f'{metric}_std'] = float(np.std(scores))
            cv_results[f'{metric}_scores'] = [float(s) for s in scores]
        
        return cv_results
    
    def generate_confusion_matrix_plot(self, cm: np.ndarray) -> str:
        """
        Generate confusion matrix visualization.
        
        Args:
            cm: Confusion matrix
            
        Returns:
            Path to saved plot
        """
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Normal', 'AD'],
            yticklabels=['Normal', 'AD']
        )
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        plot_path = self.output_dir / 'confusion_matrix.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(plot_path)
    
    def generate_roc_curve_plot(self, y_true: np.ndarray, y_prob: np.ndarray) -> str:
        """
        Generate ROC curve visualization.
        
        Args:
            y_true: True labels
            y_prob: Predicted probabilities
            
        Returns:
            Path to saved plot
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_prob)
        auc = roc_auc_score(y_true, y_prob)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend()
        plt.grid(alpha=0.3)
        
        plot_path = self.output_dir / 'roc_curve.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(plot_path)
    
    def generate_precision_recall_plot(self, y_true: np.ndarray, y_prob: np.ndarray) -> str:
        """
        Generate precision-recall curve visualization.
        
        Args:
            y_true: True labels
            y_prob: Predicted probabilities
            
        Returns:
            Path to saved plot
        """
        precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, linewidth=2)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.grid(alpha=0.3)
        
        plot_path = self.output_dir / 'precision_recall_curve.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(plot_path)
    
    def generate_feature_importance_plot(self) -> str:
        """
        Generate feature importance visualization.
        
        Returns:
            Path to saved plot
        """
        importance = self.ensemble.get_feature_importance()
        
        # Get top 15 features
        top_features = list(importance.items())[:15]
        features, scores = zip(*top_features)
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(features)), scores)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Importance Score')
        plt.title('Top 15 Feature Importance')
        plt.tight_layout()
        
        plot_path = self.output_dir / 'feature_importance.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(plot_path)
    
    def save_evaluation_report(
        self,
        metrics: Dict,
        cv_results: Dict
    ) -> str:
        """
        Save comprehensive evaluation report.
        
        Args:
            metrics: Test metrics
            cv_results: Cross-validation results
            
        Returns:
            Path to saved report
        """
        report = {
            'evaluation_date': datetime.now().isoformat(),
            'model_dir': str(self.model_dir),
            'test_set_metrics': metrics,
            'cross_validation_results': cv_results,
            'feature_importance': self.ensemble.get_feature_importance(),
            'ensemble_info': self.ensemble.get_ensemble_info()
        }
        
        report_path = self.output_dir / 'evaluation_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Evaluation report saved to {report_path}")
        
        # Also create a human-readable text report
        text_report_path = self.output_dir / 'evaluation_report.txt'
        with open(text_report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MODEL EVALUATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Evaluation Date: {report['evaluation_date']}\n")
            f.write(f"Model Directory: {report['model_dir']}\n\n")
            
            f.write("TEST SET METRICS\n")
            f.write("-" * 80 + "\n")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    f.write(f"{key:25s}: {value:.4f}\n")
            
            f.write("\n\nCROSS-VALIDATION RESULTS\n")
            f.write("-" * 80 + "\n")
            for key, value in cv_results.items():
                if '_mean' in key or '_std' in key:
                    f.write(f"{key:25s}: {value:.4f}\n")
            
            f.write("\n\nTOP 10 IMPORTANT FEATURES\n")
            f.write("-" * 80 + "\n")
            for i, (feature, score) in enumerate(list(report['feature_importance'].items())[:10], 1):
                f.write(f"{i:2d}. {feature:30s}: {score:.4f}\n")
        
        logger.info(f"Text report saved to {text_report_path}")
        
        return str(report_path)
    
    def evaluate(self) -> Dict:
        """
        Complete evaluation pipeline.
        
        Returns:
            Dictionary with all evaluation results
        """
        logger.info("=" * 80)
        logger.info("STARTING MODEL EVALUATION")
        logger.info("=" * 80)
        
        # Load model and data
        self.load_model()
        self.load_data()
        
        # Calculate metrics
        logger.info("\n" + "=" * 80)
        logger.info("TEST SET EVALUATION")
        logger.info("=" * 80)
        metrics = self.calculate_metrics()
        
        logger.info("\nTest Set Metrics:")
        logger.info("-" * 80)
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                logger.info(f"{key:25s}: {value:.4f}")
        
        # Perform cross-validation
        logger.info("\n" + "=" * 80)
        logger.info("CROSS-VALIDATION")
        logger.info("=" * 80)
        cv_results = self.perform_cross_validation()
        
        logger.info("\nCross-Validation Results:")
        logger.info("-" * 80)
        for key, value in cv_results.items():
            if '_mean' in key or '_std' in key:
                logger.info(f"{key:25s}: {value:.4f}")
        
        # Generate visualizations
        logger.info("\n" + "=" * 80)
        logger.info("GENERATING VISUALIZATIONS")
        logger.info("=" * 80)
        
        # Get predictions for plots
        predictions = []
        probabilities = []
        for i in range(len(self.X_test)):
            pred = self.ensemble.predict(self.X_test[i])
            _, prob = self.ensemble.predict_proba(self.X_test[i])
            predictions.append(pred)
            probabilities.append(prob)
        
        predictions = np.array(predictions)
        probabilities = np.array(probabilities)
        
        cm = confusion_matrix(self.y_test, predictions)
        
        cm_plot = self.generate_confusion_matrix_plot(cm)
        logger.info(f"Confusion matrix saved to: {cm_plot}")
        
        roc_plot = self.generate_roc_curve_plot(self.y_test, probabilities)
        logger.info(f"ROC curve saved to: {roc_plot}")
        
        pr_plot = self.generate_precision_recall_plot(self.y_test, probabilities)
        logger.info(f"Precision-Recall curve saved to: {pr_plot}")
        
        fi_plot = self.generate_feature_importance_plot()
        logger.info(f"Feature importance plot saved to: {fi_plot}")
        
        # Save report
        logger.info("\n" + "=" * 80)
        logger.info("SAVING EVALUATION REPORT")
        logger.info("=" * 80)
        report_path = self.save_evaluation_report(metrics, cv_results)
        
        logger.info("\n" + "=" * 80)
        logger.info("EVALUATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"\nAll results saved to: {self.output_dir}")
        
        return {
            'metrics': metrics,
            'cv_results': cv_results,
            'report_path': report_path
        }


def main():
    """Main function to run model evaluation."""
    parser = argparse.ArgumentParser(
        description='Evaluate trained ML models'
    )
    parser.add_argument(
        '--model-dir',
        type=str,
        default='models/latest',
        help='Directory containing trained model'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/processed',
        help='Directory containing test data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for evaluation results (default: model_dir/evaluation)'
    )
    
    args = parser.parse_args()
    
    # Evaluate model
    evaluator = ModelEvaluator(
        model_dir=args.model_dir,
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    
    results = evaluator.evaluate()
    
    logger.info("\nEvaluation complete!")
    logger.info(f"Report available at: {results['report_path']}")


if __name__ == '__main__':
    main()
