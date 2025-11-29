"""
Integrated Model Interpretability System

Provides a unified interface for model interpretability with performance optimization.

Implements Requirement 7.7:
- Ensure SHAP generation within 2 seconds
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import hashlib

from ml_pipeline.interpretability.shap_explainer import (
    TreeSHAPExplainer,
    DeepSHAPExplainer,
    EnsembleSHAPExplainer
)
from ml_pipeline.interpretability.feature_importance import FeatureImportanceAnalyzer
from ml_pipeline.interpretability.prediction_explainer import PredictionExplainer
from ml_pipeline.interpretability.visualization import InterpretabilityVisualizer
from ml_pipeline.interpretability.confidence_intervals import ConfidenceIntervalCalculator

logger = logging.getLogger(__name__)


class InterpretabilitySystem:
    """
    Integrated system for model interpretability.
    
    Provides a unified interface for:
    - SHAP explanations
    - Feature importance analysis
    - Individual prediction explanations
    - Visualizations
    - Confidence intervals
    
    Optimized for performance (Requirement 7.7: SHAP within 2 seconds).
    """
    
    def __init__(
        self,
        model,
        model_type: str,
        feature_names: List[str],
        output_dir: Path,
        cache_explanations: bool = True,
        max_background_samples: int = 100
    ):
        """
        Initialize interpretability system.
        
        Args:
            model: Trained model
            model_type: Type of model ('tree', 'deep', 'ensemble')
            feature_names: List of feature names
            output_dir: Directory for outputs
            cache_explanations: Whether to cache SHAP explanations
            max_background_samples: Maximum background samples for SHAP
        """
        self.model = model
        self.model_type = model_type
        self.feature_names = feature_names
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_explanations = cache_explanations
        self.max_background_samples = max_background_samples
        
        # Initialize components
        self.shap_explainer = None
        self.feature_analyzer = FeatureImportanceAnalyzer(
            feature_names,
            output_dir / "feature_importance"
        )
        self.visualizer = InterpretabilityVisualizer(
            output_dir / "visualizations",
            feature_names
        )
        self.ci_calculator = ConfidenceIntervalCalculator(confidence_level=0.95)
        self.prediction_explainer = None
        
        # Cache for explanations
        self.explanation_cache = {}
        self.cache_dir = self.output_dir / "cache"
        if cache_explanations:
            self.cache_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized InterpretabilitySystem for {model_type} model")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Caching enabled: {cache_explanations}")
    
    def initialize(self, background_data: Optional[np.ndarray] = None):
        """
        Initialize SHAP explainer with background data.
        
        Args:
            background_data: Background dataset for SHAP calculations
        """
        logger.info("Initializing SHAP explainer")
        
        start_time = time.time()
        
        # Create appropriate SHAP explainer
        if self.model_type == 'tree':
            self.shap_explainer = TreeSHAPExplainer(
                self.model,
                self.feature_names,
                self.max_background_samples
            )
            self.shap_explainer.initialize()
            
        elif self.model_type == 'deep':
            if background_data is None:
                raise ValueError("DeepSHAPExplainer requires background data")
            
            self.shap_explainer = DeepSHAPExplainer(
                self.model,
                self.feature_names,
                self.max_background_samples
            )
            self.shap_explainer.initialize(background_data)
            
        elif self.model_type == 'ensemble':
            # For ensemble, model should be a dict of models
            if not isinstance(self.model, dict):
                raise ValueError("Ensemble model should be a dictionary of models")
            
            # Determine model types
            model_types = {}
            for name, m in self.model.items():
                # Simple heuristic to determine type
                if hasattr(m, 'estimators_'):  # RandomForest
                    model_types[name] = 'tree'
                elif hasattr(m, 'get_booster'):  # XGBoost
                    model_types[name] = 'tree'
                else:
                    model_types[name] = 'deep'
            
            self.shap_explainer = EnsembleSHAPExplainer(
                self.model,
                model_types,
                self.feature_names
            )
            self.shap_explainer.initialize(background_data)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Initialize prediction explainer
        self.prediction_explainer = PredictionExplainer(
            self.shap_explainer,
            self.feature_names
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"SHAP explainer initialized in {elapsed_time:.2f} seconds")
    
    def explain_prediction(
        self,
        X: np.ndarray,
        prediction: int,
        probability: float,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a single prediction.
        
        Optimized for performance (Requirement 7.7: within 2 seconds).
        
        Args:
            X: Feature vector
            prediction: Model prediction
            probability: Prediction probability
            use_cache: Whether to use cached explanations
            
        Returns:
            Dictionary with comprehensive explanation
        """
        if self.shap_explainer is None:
            raise ValueError("System must be initialized first")
        
        # Check cache
        if use_cache and self.cache_explanations:
            cache_key = self._get_cache_key(X)
            if cache_key in self.explanation_cache:
                logger.debug("Using cached explanation")
                return self.explanation_cache[cache_key]
        
        # Time the explanation generation
        start_time = time.time()
        
        # Generate explanation
        explanation = self.prediction_explainer.explain_single_prediction(
            X, prediction, probability, top_n=5
        )
        
        elapsed_time = time.time() - start_time
        
        # Check performance requirement
        if elapsed_time > 2.0:
            logger.warning(
                f"⚠️  Explanation generation took {elapsed_time:.3f}s, "
                f"exceeding 2s requirement"
            )
        else:
            logger.info(
                f"✓ Explanation generated in {elapsed_time:.3f}s "
                f"(within 2s requirement)"
            )
        
        explanation['generation_time'] = elapsed_time
        
        # Cache the explanation
        if use_cache and self.cache_explanations:
            self.explanation_cache[cache_key] = explanation
        
        return explanation
    
    def _get_cache_key(self, X: np.ndarray) -> str:
        """
        Generate cache key for feature vector.
        
        Args:
            X: Feature vector
            
        Returns:
            Cache key string
        """
        # Use hash of feature values
        return hashlib.md5(X.tobytes()).hexdigest()
    
    def analyze_feature_importance(
        self,
        X_sample: np.ndarray,
        model_name: str = "model",
        save_report: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze global feature importance.
        
        Args:
            X_sample: Sample of data for SHAP calculation
            model_name: Name of the model
            save_report: Whether to save the report
            
        Returns:
            Dictionary with feature importance analysis
        """
        logger.info(f"Analyzing feature importance for {model_name}")
        
        if self.shap_explainer is None:
            raise ValueError("System must be initialized first")
        
        # Calculate SHAP values for sample
        start_time = time.time()
        shap_values = self.shap_explainer.explain_batch(X_sample)
        elapsed_time = time.time() - start_time
        
        logger.info(
            f"SHAP values calculated for {len(X_sample)} samples "
            f"in {elapsed_time:.2f} seconds"
        )
        
        # Generate importance report
        report = self.feature_analyzer.generate_importance_report(
            shap_values,
            model_name,
            save=save_report
        )
        
        return report
    
    def create_visualizations(
        self,
        X_sample: np.ndarray,
        shap_values: Optional[np.ndarray] = None,
        model_name: str = "model"
    ) -> Dict[str, Path]:
        """
        Create all interpretability visualizations.
        
        Args:
            X_sample: Sample of data
            shap_values: Optional pre-computed SHAP values
            model_name: Name of the model
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        logger.info(f"Creating visualizations for {model_name}")
        
        if self.shap_explainer is None:
            raise ValueError("System must be initialized first")
        
        # Calculate SHAP values if not provided
        if shap_values is None:
            shap_values = self.shap_explainer.explain_batch(X_sample)
        
        # Calculate feature importance
        feature_importance = self.feature_analyzer.calculate_global_importance(
            shap_values
        )
        
        # Create all visualizations
        plots = self.visualizer.create_all_visualizations(
            shap_values,
            X_sample,
            feature_importance,
            model_name
        )
        
        logger.info(f"Created {len(plots)} visualizations")
        
        return plots
    
    def calculate_confidence_intervals(
        self,
        model_predictions: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Calculate confidence intervals for ensemble predictions.
        
        Args:
            model_predictions: Dictionary of predictions from each model
            
        Returns:
            Dictionary with confidence interval information
        """
        logger.info("Calculating confidence intervals")
        
        ci_info = self.ci_calculator.calculate_ensemble_prediction_ci(
            model_predictions
        )
        
        return ci_info
    
    def generate_complete_report(
        self,
        X_sample: np.ndarray,
        model_name: str = "model",
        create_plots: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete interpretability report.
        
        Args:
            X_sample: Sample of data for analysis
            model_name: Name of the model
            create_plots: Whether to create visualizations
            
        Returns:
            Dictionary with complete interpretability analysis
        """
        logger.info(f"Generating complete interpretability report for {model_name}")
        
        if self.shap_explainer is None:
            raise ValueError("System must be initialized first")
        
        start_time = time.time()
        
        # Calculate SHAP values
        logger.info("Calculating SHAP values...")
        shap_values = self.shap_explainer.explain_batch(X_sample)
        
        # Feature importance analysis
        logger.info("Analyzing feature importance...")
        importance_report = self.feature_analyzer.generate_importance_report(
            shap_values,
            model_name,
            save=True
        )
        
        # Create visualizations
        plots = {}
        if create_plots:
            logger.info("Creating visualizations...")
            plots = self.create_visualizations(
                X_sample,
                shap_values,
                model_name
            )
        
        elapsed_time = time.time() - start_time
        
        report = {
            'model_name': model_name,
            'n_samples_analyzed': len(X_sample),
            'feature_importance': importance_report,
            'visualizations': {k: str(v) for k, v in plots.items()},
            'generation_time': elapsed_time
        }
        
        logger.info(f"Complete report generated in {elapsed_time:.2f} seconds")
        
        return report
    
    def save_cache(self):
        """Save explanation cache to disk."""
        if not self.cache_explanations or not self.explanation_cache:
            return
        
        cache_file = self.cache_dir / "explanation_cache.pkl"
        
        with open(cache_file, 'wb') as f:
            pickle.dump(self.explanation_cache, f)
        
        logger.info(f"Saved {len(self.explanation_cache)} cached explanations to {cache_file}")
    
    def load_cache(self):
        """Load explanation cache from disk."""
        if not self.cache_explanations:
            return
        
        cache_file = self.cache_dir / "explanation_cache.pkl"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                self.explanation_cache = pickle.load(f)
            
            logger.info(f"Loaded {len(self.explanation_cache)} cached explanations")
        else:
            logger.info("No cache file found")
    
    def clear_cache(self):
        """Clear explanation cache."""
        self.explanation_cache = {}
        logger.info("Explanation cache cleared")
    
    def benchmark_performance(
        self,
        X_sample: np.ndarray,
        n_iterations: int = 10
    ) -> Dict[str, float]:
        """
        Benchmark explanation generation performance.
        
        Tests if system meets Requirement 7.7 (within 2 seconds).
        
        Args:
            X_sample: Sample data for testing
            n_iterations: Number of iterations for benchmarking
            
        Returns:
            Dictionary with performance metrics
        """
        logger.info(f"Benchmarking performance with {n_iterations} iterations")
        
        if self.shap_explainer is None:
            raise ValueError("System must be initialized first")
        
        times = []
        
        for i in range(n_iterations):
            # Use different samples
            idx = i % len(X_sample)
            X = X_sample[idx:idx+1]
            
            start_time = time.time()
            _ = self.shap_explainer.explain_prediction(X, return_dict=False)
            elapsed_time = time.time() - start_time
            
            times.append(elapsed_time)
        
        times = np.array(times)
        
        metrics = {
            'mean_time': float(np.mean(times)),
            'median_time': float(np.median(times)),
            'min_time': float(np.min(times)),
            'max_time': float(np.max(times)),
            'std_time': float(np.std(times)),
            'meets_requirement': float(np.mean(times)) < 2.0,
            'requirement_threshold': 2.0
        }
        
        logger.info("\n" + "=" * 60)
        logger.info("PERFORMANCE BENCHMARK RESULTS")
        logger.info("=" * 60)
        logger.info(f"Mean time: {metrics['mean_time']:.3f}s")
        logger.info(f"Median time: {metrics['median_time']:.3f}s")
        logger.info(f"Min time: {metrics['min_time']:.3f}s")
        logger.info(f"Max time: {metrics['max_time']:.3f}s")
        logger.info(f"Std dev: {metrics['std_time']:.3f}s")
        
        if metrics['meets_requirement']:
            logger.info(f"✓ Meets 2-second requirement")
        else:
            logger.warning(f"⚠️  Does not meet 2-second requirement")
        
        logger.info("=" * 60)
        
        return metrics
