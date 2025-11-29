"""
Interpretability Visualization Module

Creates visualizations for SHAP values and feature importance.

Implements Requirement 7.3:
- Create SHAP summary plots
- Create feature importance charts
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from pathlib import Path

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class InterpretabilityVisualizer:
    """
    Creates visualizations for model interpretability.
    
    Generates SHAP summary plots, feature importance charts,
    waterfall plots, and other interpretability visualizations.
    """
    
    def __init__(
        self,
        output_dir: Path,
        feature_names: List[str]
    ):
        """
        Initialize interpretability visualizer.
        
        Args:
            output_dir: Directory for saving plots
            feature_names: List of feature names
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.feature_names = feature_names
        
        logger.info(f"Initialized InterpretabilityVisualizer")
        logger.info(f"Output directory: {output_dir}")
    
    def create_shap_summary_plot(
        self,
        shap_values: np.ndarray,
        X: np.ndarray,
        model_name: str = "model",
        max_display: int = 20,
        plot_type: str = "dot"
    ) -> Path:
        """
        Create SHAP summary plot.
        
        Implements Requirement 7.3: Create SHAP summary plots
        
        Args:
            shap_values: SHAP values array (n_samples, n_features)
            X: Feature values array (n_samples, n_features)
            model_name: Name of the model
            max_display: Maximum number of features to display
            plot_type: Type of plot ('dot', 'bar', 'violin')
            
        Returns:
            Path to saved plot
        """
        logger.info(f"Creating SHAP summary plot for {model_name}")
        
        plt.figure(figsize=(12, 8))
        
        # Create DataFrame for better labeling
        X_df = pd.DataFrame(X, columns=self.feature_names)
        
        # Create summary plot
        shap.summary_plot(
            shap_values,
            X_df,
            max_display=max_display,
            plot_type=plot_type,
            show=False
        )
        
        plt.title(f'SHAP Summary Plot - {model_name}', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        # Save plot
        plot_path = self.output_dir / f"{model_name}_shap_summary_{plot_type}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"SHAP summary plot saved to {plot_path}")
        
        return plot_path
    
    def create_feature_importance_chart(
        self,
        feature_importance: Dict[str, float],
        model_name: str = "model",
        top_n: int = 20,
        chart_type: str = "bar"
    ) -> Path:
        """
        Create feature importance chart.
        
        Implements Requirement 7.3: Create feature importance charts
        
        Args:
            feature_importance: Dictionary of feature importance scores
            model_name: Name of the model
            top_n: Number of top features to display
            chart_type: Type of chart ('bar', 'horizontal_bar')
            
        Returns:
            Path to saved plot
        """
        logger.info(f"Creating feature importance chart for {model_name}")
        
        # Sort and get top N features
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:top_n]
        
        features = [f for f, _ in sorted_features]
        importances = [imp for _, imp in sorted_features]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, max(8, top_n * 0.4)))
        
        if chart_type == "horizontal_bar":
            # Horizontal bar chart (better for many features)
            colors = ['#d62728' if imp < 0 else '#2ca02c' for imp in importances]
            y_pos = np.arange(len(features))
            
            ax.barh(y_pos, importances, color=colors, alpha=0.7)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(features)
            ax.invert_yaxis()  # Top feature at top
            ax.set_xlabel('Mean Absolute SHAP Value', fontsize=12)
            ax.set_ylabel('Feature', fontsize=12)
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
            
        else:  # vertical bar
            colors = ['#d62728' if imp < 0 else '#2ca02c' for imp in importances]
            x_pos = np.arange(len(features))
            
            ax.bar(x_pos, importances, color=colors, alpha=0.7)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(features, rotation=45, ha='right')
            ax.set_ylabel('Mean Absolute SHAP Value', fontsize=12)
            ax.set_xlabel('Feature', fontsize=12)
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        ax.set_title(
            f'Top {top_n} Feature Importance - {model_name}',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        ax.grid(axis='x' if chart_type == "horizontal_bar" else 'y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = self.output_dir / f"{model_name}_feature_importance.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Feature importance chart saved to {plot_path}")
        
        return plot_path
    
    def create_waterfall_plot(
        self,
        shap_values: np.ndarray,
        base_value: float,
        feature_values: np.ndarray,
        model_name: str = "model",
        max_display: int = 10
    ) -> Path:
        """
        Create waterfall plot for a single prediction.
        
        Shows how each feature contributes to moving the prediction
        from the base value to the final prediction.
        
        Args:
            shap_values: SHAP values for single prediction
            base_value: Base value (expected value)
            feature_values: Feature values for the prediction
            model_name: Name of the model
            max_display: Maximum features to display
            
        Returns:
            Path to saved plot
        """
        logger.info(f"Creating waterfall plot for {model_name}")
        
        plt.figure(figsize=(10, 8))
        
        # Create explanation object for waterfall plot
        explanation = shap.Explanation(
            values=shap_values,
            base_values=base_value,
            data=feature_values,
            feature_names=self.feature_names
        )
        
        # Create waterfall plot
        shap.plots.waterfall(explanation, max_display=max_display, show=False)
        
        plt.title(f'SHAP Waterfall Plot - {model_name}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Save plot
        plot_path = self.output_dir / f"{model_name}_waterfall.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Waterfall plot saved to {plot_path}")
        
        return plot_path
    
    def create_force_plot(
        self,
        shap_values: np.ndarray,
        base_value: float,
        feature_values: np.ndarray,
        model_name: str = "model"
    ) -> Path:
        """
        Create force plot for a single prediction.
        
        Args:
            shap_values: SHAP values for single prediction
            base_value: Base value (expected value)
            feature_values: Feature values for the prediction
            model_name: Name of the model
            
        Returns:
            Path to saved HTML file
        """
        logger.info(f"Creating force plot for {model_name}")
        
        # Create force plot
        force_plot = shap.force_plot(
            base_value,
            shap_values,
            feature_values,
            feature_names=self.feature_names,
            matplotlib=False
        )
        
        # Save as HTML
        plot_path = self.output_dir / f"{model_name}_force_plot.html"
        shap.save_html(str(plot_path), force_plot)
        
        logger.info(f"Force plot saved to {plot_path}")
        
        return plot_path
    
    def create_dependence_plot(
        self,
        shap_values: np.ndarray,
        X: np.ndarray,
        feature_name: str,
        interaction_feature: Optional[str] = None,
        model_name: str = "model"
    ) -> Path:
        """
        Create dependence plot showing relationship between feature and SHAP values.
        
        Args:
            shap_values: SHAP values array
            X: Feature values array
            feature_name: Feature to plot
            interaction_feature: Optional interaction feature for coloring
            model_name: Name of the model
            
        Returns:
            Path to saved plot
        """
        logger.info(f"Creating dependence plot for {feature_name}")
        
        plt.figure(figsize=(10, 6))
        
        # Get feature index
        feature_idx = self.feature_names.index(feature_name)
        
        # Create DataFrame
        X_df = pd.DataFrame(X, columns=self.feature_names)
        
        # Create dependence plot
        if interaction_feature:
            shap.dependence_plot(
                feature_idx,
                shap_values,
                X_df,
                interaction_index=interaction_feature,
                show=False
            )
        else:
            shap.dependence_plot(
                feature_idx,
                shap_values,
                X_df,
                show=False
            )
        
        plt.title(
            f'SHAP Dependence Plot - {feature_name} ({model_name})',
            fontsize=14,
            fontweight='bold'
        )
        plt.tight_layout()
        
        # Save plot
        safe_feature_name = feature_name.replace('/', '_').replace(' ', '_')
        plot_path = self.output_dir / f"{model_name}_dependence_{safe_feature_name}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Dependence plot saved to {plot_path}")
        
        return plot_path
    
    def create_feature_category_importance(
        self,
        feature_importance: Dict[str, float],
        model_name: str = "model"
    ) -> Path:
        """
        Create grouped bar chart showing importance by feature category.
        
        Args:
            feature_importance: Dictionary of feature importance
            model_name: Name of the model
            
        Returns:
            Path to saved plot
        """
        logger.info(f"Creating feature category importance chart for {model_name}")
        
        # Categorize features
        categories = {
            'Cognitive': [],
            'Biomarker': [],
            'Imaging': [],
            'Genetic': [],
            'Demographic': [],
            'Other': []
        }
        
        for feature, importance in feature_importance.items():
            feature_lower = feature.lower()
            
            if any(kw in feature_lower for kw in ['mmse', 'moca', 'cdr', 'adas', 'cognitive']):
                categories['Cognitive'].append((feature, importance))
            elif any(kw in feature_lower for kw in ['csf', 'ab42', 'tau', 'biomarker', 'plasma']):
                categories['Biomarker'].append((feature, importance))
            elif any(kw in feature_lower for kw in ['hippocampus', 'volume', 'thickness', 'mri', 'brain']):
                categories['Imaging'].append((feature, importance))
            elif any(kw in feature_lower for kw in ['apoe', 'genetic', 'gene']):
                categories['Genetic'].append((feature, importance))
            elif any(kw in feature_lower for kw in ['age', 'sex', 'education', 'demographic']):
                categories['Demographic'].append((feature, importance))
            else:
                categories['Other'].append((feature, importance))
        
        # Calculate total importance per category
        category_totals = {
            cat: sum(abs(imp) for _, imp in features)
            for cat, features in categories.items()
            if features
        }
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        cats = list(category_totals.keys())
        totals = list(category_totals.values())
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(cats)))
        bars = ax.bar(cats, totals, color=colors, alpha=0.8, edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{height:.3f}',
                ha='center',
                va='bottom',
                fontsize=10
            )
        
        ax.set_xlabel('Feature Category', fontsize=12)
        ax.set_ylabel('Total Importance (Mean |SHAP|)', fontsize=12)
        ax.set_title(
            f'Feature Importance by Category - {model_name}',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = self.output_dir / f"{model_name}_category_importance.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Category importance chart saved to {plot_path}")
        
        return plot_path
    
    def create_comparison_plot(
        self,
        model_importance: Dict[str, Dict[str, float]],
        top_n: int = 15
    ) -> Path:
        """
        Create comparison plot of feature importance across models.
        
        Args:
            model_importance: Dictionary mapping model names to importance dicts
            top_n: Number of top features to display
            
        Returns:
            Path to saved plot
        """
        logger.info(f"Creating model comparison plot")
        
        # Get union of top features across all models
        all_features = set()
        for importance in model_importance.values():
            sorted_features = sorted(
                importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            all_features.update([f for f, _ in sorted_features[:top_n]])
        
        # Create DataFrame
        data = []
        for feature in all_features:
            row = {'feature': feature}
            for model_name, importance in model_importance.items():
                row[model_name] = importance.get(feature, 0.0)
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Calculate average importance
        model_cols = [col for col in df.columns if col != 'feature']
        df['avg_importance'] = df[model_cols].abs().mean(axis=1)
        df = df.sort_values('avg_importance', ascending=False).head(top_n)
        
        # Create grouped bar plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(df))
        width = 0.8 / len(model_cols)
        
        for i, model_name in enumerate(model_cols):
            offset = (i - len(model_cols) / 2) * width + width / 2
            ax.bar(
                x + offset,
                df[model_name],
                width,
                label=model_name,
                alpha=0.8
            )
        
        ax.set_xlabel('Feature', fontsize=12)
        ax.set_ylabel('Mean Absolute SHAP Value', fontsize=12)
        ax.set_title(
            f'Feature Importance Comparison Across Models',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        ax.set_xticks(x)
        ax.set_xticklabels(df['feature'], rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = self.output_dir / "model_comparison_importance.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Comparison plot saved to {plot_path}")
        
        return plot_path
    
    def create_all_visualizations(
        self,
        shap_values: np.ndarray,
        X: np.ndarray,
        feature_importance: Dict[str, float],
        model_name: str = "model"
    ) -> Dict[str, Path]:
        """
        Create all standard visualizations.
        
        Args:
            shap_values: SHAP values array
            X: Feature values array
            feature_importance: Feature importance dictionary
            model_name: Name of the model
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        logger.info(f"Creating all visualizations for {model_name}")
        
        plots = {}
        
        # SHAP summary plots
        plots['shap_summary_dot'] = self.create_shap_summary_plot(
            shap_values, X, model_name, plot_type='dot'
        )
        plots['shap_summary_bar'] = self.create_shap_summary_plot(
            shap_values, X, model_name, plot_type='bar'
        )
        
        # Feature importance chart
        plots['feature_importance'] = self.create_feature_importance_chart(
            feature_importance, model_name, chart_type='horizontal_bar'
        )
        
        # Category importance
        plots['category_importance'] = self.create_feature_category_importance(
            feature_importance, model_name
        )
        
        logger.info(f"Created {len(plots)} visualizations")
        
        return plots
