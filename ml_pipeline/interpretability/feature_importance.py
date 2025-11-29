"""
Feature Importance Analyzer Module

Calculates global feature importance using SHAP values and model-specific methods.

Implements Requirements 7.2 and 7.6:
- Generate global feature importance
- Identify top contributing features
- Identify which biomarkers contribute most to risk assessment
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class FeatureImportanceAnalyzer:
    """
    Analyzer for calculating and ranking feature importance.
    
    Uses SHAP values to compute global feature importance across
    all predictions in a dataset.
    """
    
    def __init__(
        self,
        feature_names: List[str],
        output_dir: Optional[Path] = None
    ):
        """
        Initialize feature importance analyzer.
        
        Args:
            feature_names: List of feature names
            output_dir: Optional directory for saving results
        """
        self.feature_names = feature_names
        self.output_dir = Path(output_dir) if output_dir else None
        
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized FeatureImportanceAnalyzer with {len(feature_names)} features")
    
    def calculate_global_importance(
        self,
        shap_values: np.ndarray,
        method: str = 'mean_abs'
    ) -> Dict[str, float]:
        """
        Calculate global feature importance from SHAP values.
        
        Implements Requirement 7.2: Generate global feature importance
        
        Args:
            shap_values: SHAP values array (n_samples, n_features)
            method: Method for aggregation ('mean_abs', 'mean', 'std')
            
        Returns:
            Dictionary mapping feature names to importance scores
        """
        logger.info(f"Calculating global feature importance using {method} method")
        
        if shap_values.shape[1] != len(self.feature_names):
            raise ValueError(
                f"SHAP values shape {shap_values.shape} doesn't match "
                f"number of features {len(self.feature_names)}"
            )
        
        importance = {}
        
        if method == 'mean_abs':
            # Mean absolute SHAP value (most common)
            importance_values = np.mean(np.abs(shap_values), axis=0)
        elif method == 'mean':
            # Mean SHAP value (shows direction)
            importance_values = np.mean(shap_values, axis=0)
        elif method == 'std':
            # Standard deviation (shows variability)
            importance_values = np.std(shap_values, axis=0)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        for i, feature in enumerate(self.feature_names):
            importance[feature] = float(importance_values[i])
        
        logger.info(f"Calculated importance for {len(importance)} features")
        
        return importance
    
    def get_ranked_features(
        self,
        shap_values: np.ndarray,
        top_n: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """
        Get features ranked by importance.
        
        Implements Requirement 7.2: Identify top contributing features
        
        Args:
            shap_values: SHAP values array
            top_n: Optional number of top features to return
            
        Returns:
            List of (feature_name, importance_score) tuples
        """
        importance = self.calculate_global_importance(shap_values)
        
        # Sort by importance (descending)
        ranked = sorted(
            importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        if top_n is not None:
            ranked = ranked[:top_n]
        
        logger.info(f"Top {len(ranked)} features ranked by importance")
        
        return ranked
    
    def calculate_feature_statistics(
        self,
        shap_values: np.ndarray
    ) -> pd.DataFrame:
        """
        Calculate comprehensive statistics for each feature.
        
        Args:
            shap_values: SHAP values array (n_samples, n_features)
            
        Returns:
            DataFrame with feature statistics
        """
        logger.info("Calculating feature statistics")
        
        stats = []
        
        for i, feature in enumerate(self.feature_names):
            feature_shap = shap_values[:, i]
            
            stats.append({
                'feature': feature,
                'mean_abs_shap': float(np.mean(np.abs(feature_shap))),
                'mean_shap': float(np.mean(feature_shap)),
                'std_shap': float(np.std(feature_shap)),
                'min_shap': float(np.min(feature_shap)),
                'max_shap': float(np.max(feature_shap)),
                'median_shap': float(np.median(feature_shap)),
                'q25_shap': float(np.percentile(feature_shap, 25)),
                'q75_shap': float(np.percentile(feature_shap, 75))
            })
        
        df = pd.DataFrame(stats)
        df = df.sort_values('mean_abs_shap', ascending=False)
        
        logger.info(f"Calculated statistics for {len(df)} features")
        
        return df
    
    def identify_biomarker_contributions(
        self,
        shap_values: np.ndarray,
        biomarker_features: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Identify which biomarkers contribute most to risk assessment.
        
        Implements Requirement 7.6: Identify which biomarkers contribute most
        
        Args:
            shap_values: SHAP values array
            biomarker_features: Optional list of biomarker feature names
                              If None, identifies them automatically
            
        Returns:
            Dictionary of biomarker contributions
        """
        logger.info("Identifying biomarker contributions to risk assessment")
        
        # Auto-identify biomarker features if not provided
        if biomarker_features is None:
            biomarker_keywords = [
                'csf', 'ab42', 'tau', 'ptau', 'amyloid', 'beta',
                'biomarker', 'plasma', 'serum'
            ]
            biomarker_features = [
                f for f in self.feature_names
                if any(keyword in f.lower() for keyword in biomarker_keywords)
            ]
            logger.info(f"Auto-identified {len(biomarker_features)} biomarker features")
        
        # Calculate importance for biomarkers
        all_importance = self.calculate_global_importance(shap_values)
        
        biomarker_importance = {
            feature: all_importance[feature]
            for feature in biomarker_features
            if feature in all_importance
        }
        
        # Sort by importance
        biomarker_importance = dict(
            sorted(
                biomarker_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
        )
        
        logger.info(f"Top biomarker contributors:")
        for i, (feature, importance) in enumerate(list(biomarker_importance.items())[:5], 1):
            logger.info(f"  {i}. {feature}: {importance:.4f}")
        
        return biomarker_importance
    
    def identify_cognitive_contributions(
        self,
        shap_values: np.ndarray,
        cognitive_features: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Identify which cognitive features contribute most.
        
        Args:
            shap_values: SHAP values array
            cognitive_features: Optional list of cognitive feature names
            
        Returns:
            Dictionary of cognitive feature contributions
        """
        logger.info("Identifying cognitive feature contributions")
        
        # Auto-identify cognitive features if not provided
        if cognitive_features is None:
            cognitive_keywords = [
                'mmse', 'moca', 'cdr', 'adas', 'cognitive',
                'memory', 'attention', 'executive'
            ]
            cognitive_features = [
                f for f in self.feature_names
                if any(keyword in f.lower() for keyword in cognitive_keywords)
            ]
            logger.info(f"Auto-identified {len(cognitive_features)} cognitive features")
        
        # Calculate importance
        all_importance = self.calculate_global_importance(shap_values)
        
        cognitive_importance = {
            feature: all_importance[feature]
            for feature in cognitive_features
            if feature in all_importance
        }
        
        # Sort by importance
        cognitive_importance = dict(
            sorted(
                cognitive_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
        )
        
        return cognitive_importance
    
    def identify_imaging_contributions(
        self,
        shap_values: np.ndarray,
        imaging_features: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Identify which imaging features contribute most.
        
        Args:
            shap_values: SHAP values array
            imaging_features: Optional list of imaging feature names
            
        Returns:
            Dictionary of imaging feature contributions
        """
        logger.info("Identifying imaging feature contributions")
        
        # Auto-identify imaging features if not provided
        if imaging_features is None:
            imaging_keywords = [
                'hippocampus', 'volume', 'thickness', 'cortical',
                'ventricle', 'entorhinal', 'mri', 'brain'
            ]
            imaging_features = [
                f for f in self.feature_names
                if any(keyword in f.lower() for keyword in imaging_keywords)
            ]
            logger.info(f"Auto-identified {len(imaging_features)} imaging features")
        
        # Calculate importance
        all_importance = self.calculate_global_importance(shap_values)
        
        imaging_importance = {
            feature: all_importance[feature]
            for feature in imaging_features
            if feature in all_importance
        }
        
        # Sort by importance
        imaging_importance = dict(
            sorted(
                imaging_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
        )
        
        return imaging_importance
    
    def generate_importance_report(
        self,
        shap_values: np.ndarray,
        model_name: str = "model",
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive feature importance report.
        
        Args:
            shap_values: SHAP values array
            model_name: Name of the model
            save: Whether to save the report
            
        Returns:
            Dictionary with complete importance analysis
        """
        logger.info(f"Generating feature importance report for {model_name}")
        
        # Calculate global importance
        global_importance = self.calculate_global_importance(shap_values)
        ranked_features = self.get_ranked_features(shap_values, top_n=20)
        
        # Calculate statistics
        feature_stats = self.calculate_feature_statistics(shap_values)
        
        # Identify category-specific contributions
        biomarker_contributions = self.identify_biomarker_contributions(shap_values)
        cognitive_contributions = self.identify_cognitive_contributions(shap_values)
        imaging_contributions = self.identify_imaging_contributions(shap_values)
        
        report = {
            'model_name': model_name,
            'n_samples': shap_values.shape[0],
            'n_features': shap_values.shape[1],
            'global_importance': global_importance,
            'top_20_features': [
                {'feature': f, 'importance': float(imp)}
                for f, imp in ranked_features
            ],
            'feature_statistics': feature_stats.to_dict('records'),
            'biomarker_contributions': biomarker_contributions,
            'cognitive_contributions': cognitive_contributions,
            'imaging_contributions': imaging_contributions
        }
        
        # Log summary
        logger.info("\n" + "=" * 80)
        logger.info(f"FEATURE IMPORTANCE REPORT: {model_name}")
        logger.info("=" * 80)
        logger.info(f"\nTop 10 Most Important Features:")
        for i, (feature, importance) in enumerate(ranked_features[:10], 1):
            logger.info(f"  {i:2d}. {feature:40s}: {importance:.4f}")
        
        logger.info(f"\nTop 5 Biomarker Contributors:")
        for i, (feature, importance) in enumerate(list(biomarker_contributions.items())[:5], 1):
            logger.info(f"  {i}. {feature:40s}: {importance:.4f}")
        
        logger.info(f"\nTop 5 Cognitive Contributors:")
        for i, (feature, importance) in enumerate(list(cognitive_contributions.items())[:5], 1):
            logger.info(f"  {i}. {feature:40s}: {importance:.4f}")
        
        logger.info(f"\nTop 5 Imaging Contributors:")
        for i, (feature, importance) in enumerate(list(imaging_contributions.items())[:5], 1):
            logger.info(f"  {i}. {feature:40s}: {importance:.4f}")
        
        logger.info("=" * 80)
        
        # Save report
        if save and self.output_dir:
            # Save as JSON
            json_path = self.output_dir / f"{model_name}_feature_importance.json"
            with open(json_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {json_path}")
            
            # Save statistics as CSV
            csv_path = self.output_dir / f"{model_name}_feature_statistics.csv"
            feature_stats.to_csv(csv_path, index=False)
            logger.info(f"Statistics saved to {csv_path}")
        
        return report
    
    def compare_feature_importance_across_models(
        self,
        model_shap_values: Dict[str, np.ndarray],
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Compare feature importance across multiple models.
        
        Args:
            model_shap_values: Dictionary mapping model names to SHAP values
            top_n: Number of top features to include
            
        Returns:
            DataFrame comparing feature importance across models
        """
        logger.info(f"Comparing feature importance across {len(model_shap_values)} models")
        
        # Calculate importance for each model
        model_importance = {}
        for model_name, shap_values in model_shap_values.items():
            importance = self.calculate_global_importance(shap_values)
            model_importance[model_name] = importance
        
        # Get union of top features across all models
        all_top_features = set()
        for model_name, importance in model_importance.items():
            ranked = sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)
            top_features = [f for f, _ in ranked[:top_n]]
            all_top_features.update(top_features)
        
        # Create comparison DataFrame
        comparison_data = []
        for feature in all_top_features:
            row = {'feature': feature}
            for model_name in model_importance.keys():
                row[model_name] = model_importance[model_name].get(feature, 0.0)
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        
        # Calculate average importance across models
        model_cols = [col for col in df.columns if col != 'feature']
        df['avg_importance'] = df[model_cols].abs().mean(axis=1)
        
        # Sort by average importance
        df = df.sort_values('avg_importance', ascending=False)
        
        logger.info(f"Comparison includes {len(df)} features")
        
        return df
