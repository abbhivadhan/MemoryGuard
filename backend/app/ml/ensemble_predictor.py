"""
Ensemble Predictor for Alzheimer's risk assessment
"""

import numpy as np


class EnsemblePredictor:
    """Ensemble predictor combining multiple trained models"""
    
    def __init__(self, models, scaler):
        """
        Initialize ensemble predictor
        
        Args:
            models: Dictionary of trained models with their info
            scaler: Feature scaler
        """
        self.models = models
        self.scaler = scaler
    
    def predict_risk(self, features):
        """
        Predict Alzheimer's risk from features
        
        Args:
            features: Feature vector (numpy array)
            
        Returns:
            Dictionary with risk_score, risk_level, and confidence
        """
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        predictions = []
        for model_info in self.models.values():
            model = model_info['model']
            if hasattr(model, 'predict_proba'):
                pred = model.predict_proba(features_scaled)[0, 1]
            else:
                pred = model.predict(features_scaled)[0]
            predictions.append(pred)
        
        # Average prediction
        risk_score = np.mean(predictions)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "moderate"
        else:
            risk_level = "high"
        
        return {
            'risk_score': float(risk_score),
            'risk_level': risk_level,
            'confidence': float(np.std(predictions))  # Lower std = higher confidence
        }
    
    def get_model_info(self):
        """Get information about the ensemble models"""
        return {
            'num_models': len(self.models),
            'model_types': list(self.models.keys()),
            'accuracies': {name: info.get('accuracy', 0) for name, info in self.models.items()}
        }
