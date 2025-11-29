"""
Individual Prediction Explainer Module

Generates detailed explanations for individual predictions.

Implements Requirement 7.4:
- Generate SHAP values for single predictions
- Identify top 5 contributing features
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class PredictionExplainer:
    """
    Generates detailed explanations for individual predictions.
    
    Provides human-readable explanations with top contributing features
    and their impacts on the prediction.
    """
    
    def __init__(
        self,
        shap_explainer,
        feature_names: List[str],
        class_names: Optional[List[str]] = None
    ):
        """
        Initialize prediction explainer.
        
        Args:
            shap_explainer: Initialized SHAP explainer
            feature_names: List of feature names
            class_names: Optional class names (default: ['Low Risk', 'High Risk'])
        """
        self.shap_explainer = shap_explainer
        self.feature_names = feature_names
        self.class_names = class_names or ['Low Risk', 'High Risk']
        
        logger.info("Initialized PredictionExplainer")
    
    def explain_single_prediction(
        self,
        X: np.ndarray,
        prediction: int,
        probability: float,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a single prediction.
        
        Implements Requirement 7.4:
        - Generate SHAP values for single predictions
        - Identify top 5 contributing features
        
        Args:
            X: Feature vector (1D or 2D array)
            prediction: Model prediction (0 or 1)
            probability: Prediction probability
            top_n: Number of top features to include (default 5)
            
        Returns:
            Dictionary with comprehensive explanation
        """
        logger.info(f"Generating explanation for prediction: {prediction} (prob: {probability:.3f})")
        
        # Get SHAP explanation
        shap_explanation = self.shap_explainer.explain_prediction(X)
        
        # Get top contributing features
        top_features = self.shap_explainer.get_top_features(X, top_n=top_n)
        
        # Get feature contributions (positive and negative)
        contributions = self.shap_explainer.get_feature_contributions(X)
        
        # Generate human-readable explanation
        explanation_text = self._generate_explanation_text(
            prediction,
            probability,
            top_features,
            contributions
        )
        
        # Create detailed explanation
        explanation = {
            'prediction': {
                'class': prediction,
                'class_name': self.class_names[prediction],
                'probability': float(probability),
                'confidence': self._calculate_confidence(probability)
            },
            'base_value': shap_explanation['base_value'],
            'top_features': [
                {
                    'rank': i + 1,
                    'feature': feature,
                    'shap_value': float(shap_value),
                    'impact': 'increases' if shap_value > 0 else 'decreases',
                    'magnitude': abs(float(shap_value))
                }
                for i, (feature, shap_value) in enumerate(top_features)
            ],
            'positive_contributors': [
                {
                    'feature': feature,
                    'contribution': float(value)
                }
                for feature, value in contributions['positive'][:5]
            ],
            'negative_contributors': [
                {
                    'feature': feature,
                    'contribution': float(value)
                }
                for feature, value in contributions['negative'][:5]
            ],
            'explanation_text': explanation_text,
            'computation_time': shap_explanation.get('computation_time', 0.0)
        }
        
        logger.info(f"Explanation generated successfully")
        logger.info(f"Top 5 features: {[f['feature'] for f in explanation['top_features']]}")
        
        return explanation
    
    def _calculate_confidence(self, probability: float) -> str:
        """
        Calculate confidence level from probability.
        
        Args:
            probability: Prediction probability
            
        Returns:
            Confidence level string
        """
        if probability > 0.9 or probability < 0.1:
            return 'very_high'
        elif probability > 0.75 or probability < 0.25:
            return 'high'
        elif probability > 0.6 or probability < 0.4:
            return 'moderate'
        else:
            return 'low'
    
    def _generate_explanation_text(
        self,
        prediction: int,
        probability: float,
        top_features: List[Tuple[str, float]],
        contributions: Dict[str, List[Tuple[str, float]]]
    ) -> str:
        """
        Generate human-readable explanation text.
        
        Args:
            prediction: Model prediction
            probability: Prediction probability
            top_features: Top contributing features
            contributions: Positive and negative contributions
            
        Returns:
            Human-readable explanation string
        """
        class_name = self.class_names[prediction]
        confidence = self._calculate_confidence(probability)
        
        # Start with prediction summary
        text = f"The model predicts {class_name} with {confidence.replace('_', ' ')} confidence "
        text += f"({probability:.1%} probability).\n\n"
        
        # Add top contributing features
        text += f"Top {len(top_features)} Contributing Factors:\n"
        for i, (feature, shap_value) in enumerate(top_features, 1):
            impact = "increases" if shap_value > 0 else "decreases"
            feature_readable = self._make_feature_readable(feature)
            text += f"{i}. {feature_readable} {impact} risk\n"
        
        # Add positive contributors if any
        if contributions['positive']:
            text += "\nFactors Increasing Risk:\n"
            for feature, _ in contributions['positive'][:3]:
                feature_readable = self._make_feature_readable(feature)
                text += f"  • {feature_readable}\n"
        
        # Add negative contributors if any
        if contributions['negative']:
            text += "\nFactors Decreasing Risk:\n"
            for feature, _ in contributions['negative'][:3]:
                feature_readable = self._make_feature_readable(feature)
                text += f"  • {feature_readable}\n"
        
        return text
    
    def _make_feature_readable(self, feature: str) -> str:
        """
        Convert feature name to human-readable format.
        
        Args:
            feature: Feature name
            
        Returns:
            Human-readable feature name
        """
        # Replace underscores with spaces
        readable = feature.replace('_', ' ')
        
        # Capitalize words
        readable = readable.title()
        
        # Handle common abbreviations
        replacements = {
            'Mmse': 'MMSE',
            'Moca': 'MoCA',
            'Cdr': 'CDR',
            'Csf': 'CSF',
            'Ab42': 'Aβ42',
            'Tau': 'Tau',
            'Ptau': 'p-Tau',
            'Apoe': 'APOE',
            'E4': 'e4',
            'Mri': 'MRI'
        }
        
        for old, new in replacements.items():
            readable = readable.replace(old, new)
        
        return readable
    
    def explain_batch_predictions(
        self,
        X_batch: np.ndarray,
        predictions: np.ndarray,
        probabilities: np.ndarray,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate explanations for a batch of predictions.
        
        Args:
            X_batch: Batch of feature vectors
            predictions: Array of predictions
            probabilities: Array of probabilities
            top_n: Number of top features per prediction
            
        Returns:
            List of explanation dictionaries
        """
        logger.info(f"Generating explanations for {len(X_batch)} predictions")
        
        explanations = []
        
        for i in range(len(X_batch)):
            X = X_batch[i:i+1]
            pred = int(predictions[i])
            prob = float(probabilities[i])
            
            explanation = self.explain_single_prediction(X, pred, prob, top_n)
            explanations.append(explanation)
        
        logger.info(f"Generated {len(explanations)} explanations")
        
        return explanations
    
    def generate_comparison_explanation(
        self,
        X1: np.ndarray,
        X2: np.ndarray,
        pred1: int,
        pred2: int,
        prob1: float,
        prob2: float
    ) -> Dict[str, Any]:
        """
        Generate comparative explanation for two predictions.
        
        Useful for understanding why two similar patients have different predictions.
        
        Args:
            X1: First feature vector
            X2: Second feature vector
            pred1: First prediction
            pred2: Second prediction
            prob1: First probability
            prob2: Second probability
            
        Returns:
            Dictionary with comparative explanation
        """
        logger.info("Generating comparative explanation")
        
        # Get individual explanations
        exp1 = self.explain_single_prediction(X1, pred1, prob1)
        exp2 = self.explain_single_prediction(X2, pred2, prob2)
        
        # Calculate feature differences
        shap1 = self.shap_explainer.explain_prediction(X1)
        shap2 = self.shap_explainer.explain_prediction(X2)
        
        feature_diffs = {}
        for feature in self.feature_names:
            diff = shap2['shap_values'][feature] - shap1['shap_values'][feature]
            feature_diffs[feature] = float(diff)
        
        # Sort by absolute difference
        sorted_diffs = sorted(
            feature_diffs.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        comparison = {
            'prediction_1': exp1['prediction'],
            'prediction_2': exp2['prediction'],
            'probability_difference': float(prob2 - prob1),
            'top_differentiating_features': [
                {
                    'feature': feature,
                    'shap_difference': diff,
                    'impact': 'increases' if diff > 0 else 'decreases'
                }
                for feature, diff in sorted_diffs[:5]
            ],
            'explanation_1': exp1,
            'explanation_2': exp2
        }
        
        return comparison
    
    def save_explanation(
        self,
        explanation: Dict[str, Any],
        output_path: Path,
        patient_id: Optional[str] = None
    ):
        """
        Save explanation to file.
        
        Args:
            explanation: Explanation dictionary
            output_path: Path to save the explanation
            patient_id: Optional patient identifier
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata
        explanation_with_meta = {
            'patient_id': patient_id,
            'explanation': explanation
        }
        
        # Save as JSON
        with open(output_path, 'w') as f:
            json.dump(explanation_with_meta, f, indent=2)
        
        logger.info(f"Explanation saved to {output_path}")
    
    def generate_clinical_summary(
        self,
        X: np.ndarray,
        prediction: int,
        probability: float,
        patient_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate clinical summary for healthcare providers.
        
        Args:
            X: Feature vector
            prediction: Model prediction
            probability: Prediction probability
            patient_data: Optional patient demographic data
            
        Returns:
            Clinical summary text
        """
        explanation = self.explain_single_prediction(X, prediction, probability)
        
        summary = "CLINICAL RISK ASSESSMENT SUMMARY\n"
        summary += "=" * 60 + "\n\n"
        
        # Patient info if available
        if patient_data:
            summary += "Patient Information:\n"
            if 'age' in patient_data:
                summary += f"  Age: {patient_data['age']} years\n"
            if 'sex' in patient_data:
                summary += f"  Sex: {patient_data['sex']}\n"
            summary += "\n"
        
        # Risk assessment
        summary += "Risk Assessment:\n"
        summary += f"  Predicted Risk: {explanation['prediction']['class_name']}\n"
        summary += f"  Probability: {explanation['prediction']['probability']:.1%}\n"
        summary += f"  Confidence: {explanation['prediction']['confidence'].replace('_', ' ').title()}\n\n"
        
        # Key factors
        summary += "Key Contributing Factors:\n"
        for item in explanation['top_features']:
            summary += f"  {item['rank']}. {self._make_feature_readable(item['feature'])}\n"
            summary += f"     Impact: {item['impact']} risk (SHAP: {item['shap_value']:.3f})\n"
        
        summary += "\n" + "=" * 60 + "\n"
        summary += "Note: This is a computational risk assessment and should be\n"
        summary += "interpreted by qualified healthcare professionals in conjunction\n"
        summary += "with clinical judgment and other diagnostic information.\n"
        
        return summary
