"""
SHAP-based interpretability for Alzheimer's ML models.
Generates SHAP values and feature importance rankings.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import shap
import logging

logger = logging.getLogger(__name__)


class SHAPExplainer:
    """
    SHAP explainer for model interpretability.
    Generates SHAP values and feature importance for predictions.
    """
    
    def __init__(self, model, model_type: str = 'tree'):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model (RandomForest, XGBoost, or Neural Network)
            model_type: Type of model ('tree', 'deep', 'kernel')
        """
        self.model = model
        self.model_type = model_type
        self.explainer = None
        self.background_data = None
    
    def initialize_explainer(
        self, 
        background_data: np.ndarray,
        max_background_samples: int = 100
    ) -> None:
        """
        Initialize the SHAP explainer with background data.
        
        Args:
            background_data: Background dataset for SHAP calculations
            max_background_samples: Maximum samples to use for background
        """
        # Limit background data size for performance
        if len(background_data) > max_background_samples:
            indices = np.random.choice(
                len(background_data), 
                max_background_samples, 
                replace=False
            )
            background_data = background_data[indices]
        
        self.background_data = background_data
        
        if self.model_type == 'tree':
            # For tree-based models (RandomForest, XGBoost)
            self.explainer = shap.TreeExplainer(self.model)
            logger.info("TreeExplainer initialized")
        elif self.model_type == 'deep':
            # For neural networks
            self.explainer = shap.DeepExplainer(self.model, background_data)
            logger.info("DeepExplainer initialized")
        elif self.model_type == 'kernel':
            # For any model (slower but universal)
            self.explainer = shap.KernelExplainer(
                self.model.predict_proba, 
                background_data
            )
            logger.info("KernelExplainer initialized")
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def explain_prediction(
        self, 
        X: np.ndarray,
        feature_names: List[str]
    ) -> Dict:
        """
        Generate SHAP explanation for a single prediction.
        
        Args:
            X: Feature vector to explain
            feature_names: List of feature names
            
        Returns:
            Dictionary with SHAP values and explanation
        """
        if self.explainer is None:
            raise ValueError("Explainer must be initialized first")
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # Handle different SHAP value formats
        if isinstance(shap_values, list):
            # For binary classification, use positive class
            shap_values = shap_values[1]
        
        # Get SHAP values for the single prediction
        if shap_values.ndim > 1:
            shap_values = shap_values[0]
        
        # Create feature importance dictionary
        feature_importance = {}
        for i, feature_name in enumerate(feature_names):
            feature_importance[feature_name] = float(shap_values[i])
        
        # Sort by absolute importance
        sorted_importance = dict(
            sorted(
                feature_importance.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )
        )
        
        # Get base value (expected value)
        base_value = float(self.explainer.expected_value)
        if isinstance(self.explainer.expected_value, (list, np.ndarray)):
            base_value = float(self.explainer.expected_value[1])
        
        explanation = {
            'shap_values': feature_importance,
            'sorted_importance': sorted_importance,
            'base_value': base_value,
            'feature_contributions': self._get_feature_contributions(
                shap_values, feature_names
            )
        }
        
        return explanation
    
    def _get_feature_contributions(
        self, 
        shap_values: np.ndarray,
        feature_names: List[str]
    ) -> Dict:
        """
        Get positive and negative feature contributions.
        
        Args:
            shap_values: SHAP values array
            feature_names: List of feature names
            
        Returns:
            Dictionary with positive and negative contributions
        """
        positive_contributions = {}
        negative_contributions = {}
        
        for i, feature_name in enumerate(feature_names):
            value = float(shap_values[i])
            if value > 0:
                positive_contributions[feature_name] = value
            elif value < 0:
                negative_contributions[feature_name] = abs(value)
        
        # Sort by magnitude
        positive_contributions = dict(
            sorted(positive_contributions.items(), key=lambda x: x[1], reverse=True)
        )
        negative_contributions = dict(
            sorted(negative_contributions.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            'positive': positive_contributions,
            'negative': negative_contributions
        }
    
    def get_top_features(
        self, 
        X: np.ndarray,
        feature_names: List[str],
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Get top N most important features for a prediction.
        
        Args:
            X: Feature vector
            feature_names: List of feature names
            top_n: Number of top features to return
            
        Returns:
            List of (feature_name, shap_value) tuples
        """
        explanation = self.explain_prediction(X, feature_names)
        sorted_features = list(explanation['sorted_importance'].items())
        
        return sorted_features[:top_n]
    
    def explain_batch(
        self,
        X_batch: np.ndarray,
        feature_names: List[str]
    ) -> Dict:
        """
        Generate SHAP explanations for a batch of predictions.
        
        Args:
            X_batch: Batch of feature vectors
            feature_names: List of feature names
            
        Returns:
            Dictionary with batch SHAP values and statistics
        """
        if self.explainer is None:
            raise ValueError("Explainer must be initialized first")
        
        # Calculate SHAP values for batch
        shap_values = self.explainer.shap_values(X_batch)
        
        # Handle different SHAP value formats
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Calculate mean absolute SHAP values (global importance)
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        
        global_importance = {}
        for i, feature_name in enumerate(feature_names):
            global_importance[feature_name] = float(mean_abs_shap[i])
        
        # Sort by importance
        sorted_global_importance = dict(
            sorted(global_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            'global_importance': sorted_global_importance,
            'n_samples': len(X_batch),
            'shap_values_shape': shap_values.shape
        }
    
    def get_feature_importance_ranking(
        self,
        X_batch: np.ndarray,
        feature_names: List[str]
    ) -> List[Dict]:
        """
        Get ranked list of feature importance with statistics.
        
        Args:
            X_batch: Batch of feature vectors
            feature_names: List of feature names
            
        Returns:
            List of dictionaries with feature importance details
        """
        batch_explanation = self.explain_batch(X_batch, feature_names)
        global_importance = batch_explanation['global_importance']
        
        # Calculate SHAP values for detailed statistics
        shap_values = self.explainer.shap_values(X_batch)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        ranking = []
        for i, feature_name in enumerate(feature_names):
            feature_shap = shap_values[:, i]
            
            ranking.append({
                'feature': feature_name,
                'importance': global_importance[feature_name],
                'mean_shap': float(np.mean(feature_shap)),
                'std_shap': float(np.std(feature_shap)),
                'min_shap': float(np.min(feature_shap)),
                'max_shap': float(np.max(feature_shap))
            })
        
        # Sort by importance
        ranking.sort(key=lambda x: x['importance'], reverse=True)
        
        return ranking
    
    def generate_explanation_summary(
        self,
        X: np.ndarray,
        feature_names: List[str],
        prediction: int,
        probability: float
    ) -> Dict:
        """
        Generate a comprehensive explanation summary.
        
        Args:
            X: Feature vector
            feature_names: List of feature names
            prediction: Model prediction (0 or 1)
            probability: Prediction probability
            
        Returns:
            Dictionary with comprehensive explanation
        """
        explanation = self.explain_prediction(X, feature_names)
        top_features = self.get_top_features(X, feature_names, top_n=5)
        
        # Get top positive and negative contributors
        contributions = explanation['feature_contributions']
        top_positive = list(contributions['positive'].items())[:3]
        top_negative = list(contributions['negative'].items())[:3]
        
        summary = {
            'prediction': prediction,
            'probability': probability,
            'base_value': explanation['base_value'],
            'top_features': [
                {'feature': name, 'shap_value': value}
                for name, value in top_features
            ],
            'top_positive_contributors': [
                {'feature': name, 'contribution': value}
                for name, value in top_positive
            ],
            'top_negative_contributors': [
                {'feature': name, 'contribution': value}
                for name, value in top_negative
            ],
            'explanation_text': self._generate_text_explanation(
                prediction, probability, top_positive, top_negative
            )
        }
        
        return summary
    
    def _generate_text_explanation(
        self,
        prediction: int,
        probability: float,
        top_positive: List[Tuple[str, float]],
        top_negative: List[Tuple[str, float]]
    ) -> str:
        """
        Generate human-readable explanation text.
        
        Args:
            prediction: Model prediction
            probability: Prediction probability
            top_positive: Top positive contributors
            top_negative: Top negative contributors
            
        Returns:
            Human-readable explanation string
        """
        risk_level = "high" if prediction == 1 else "low"
        confidence = "high" if probability > 0.8 or probability < 0.2 else "moderate"
        
        text = f"The model predicts a {risk_level} risk of Alzheimer's disease "
        text += f"with {confidence} confidence ({probability:.1%} probability).\n\n"
        
        if top_positive:
            text += "Key factors increasing risk:\n"
            for feature, value in top_positive[:3]:
                text += f"  • {feature.replace('_', ' ').title()}\n"
        
        if top_negative:
            text += "\nKey factors decreasing risk:\n"
            for feature, value in top_negative[:3]:
                text += f"  • {feature.replace('_', ' ').title()}\n"
        
        return text


class EnsembleSHAPExplainer:
    """
    SHAP explainer for ensemble models.
    Aggregates explanations from multiple models.
    """
    
    def __init__(self, ensemble_model):
        """
        Initialize ensemble SHAP explainer.
        
        Args:
            ensemble_model: Trained ensemble model
        """
        self.ensemble_model = ensemble_model
        self.explainers = {}
    
    def initialize_explainers(self, background_data: np.ndarray) -> None:
        """
        Initialize SHAP explainers for all models in ensemble.
        
        Args:
            background_data: Background dataset for SHAP calculations
        """
        # Random Forest explainer
        self.explainers['rf'] = SHAPExplainer(
            self.ensemble_model.models['rf'].model,
            model_type='tree'
        )
        self.explainers['rf'].initialize_explainer(background_data)
        
        # XGBoost explainer
        self.explainers['xgb'] = SHAPExplainer(
            self.ensemble_model.models['xgb'].model,
            model_type='tree'
        )
        self.explainers['xgb'].initialize_explainer(background_data)
        
        logger.info("Ensemble SHAP explainers initialized")
    
    def explain_prediction(
        self,
        X: np.ndarray,
        feature_names: List[str]
    ) -> Dict:
        """
        Generate aggregated SHAP explanation from all models.
        
        Args:
            X: Feature vector
            feature_names: List of feature names
            
        Returns:
            Dictionary with aggregated SHAP explanations
        """
        explanations = {}
        
        # Get explanations from each model
        for model_name, explainer in self.explainers.items():
            explanations[model_name] = explainer.explain_prediction(X, feature_names)
        
        # Aggregate SHAP values using ensemble weights
        weights = self.ensemble_model.weights
        aggregated_shap = {}
        
        for feature in feature_names:
            aggregated_value = 0
            for model_name in ['rf', 'xgb']:
                if model_name in explanations:
                    shap_val = explanations[model_name]['shap_values'].get(feature, 0)
                    aggregated_value += weights[model_name] * shap_val
            
            aggregated_shap[feature] = aggregated_value
        
        # Sort by absolute importance
        sorted_shap = dict(
            sorted(aggregated_shap.items(), key=lambda x: abs(x[1]), reverse=True)
        )
        
        return {
            'aggregated_shap_values': sorted_shap,
            'individual_explanations': explanations
        }
