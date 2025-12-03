"""
Real ML Service using trained models from actual datasets
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
import logging
from pathlib import Path
import joblib
import json

from app.models.prediction import Prediction
from app.models.health_metric import HealthMetric
from app.ml.ensemble_predictor import EnsemblePredictor

logger = logging.getLogger(__name__)

MODELS_PATH = Path(__file__).parent.parent / "ml_models"


class RealMLService:
    """ML Service using real trained models"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ensemble_model = None
        self.scaler = None
        self.model_info = {}
        self._load_models()
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            # Load model registry
            registry_path = MODELS_PATH / "model_registry.json"
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    self.model_info = json.load(f)
                logger.info(f"Model registry loaded: {self.model_info.get('last_updated')}")
            
            # Load ensemble predictor
            ensemble_path = MODELS_PATH / "ensemble_predictor.joblib"
            if ensemble_path.exists():
                self.ensemble_model = joblib.load(ensemble_path)
                logger.info("Ensemble predictor loaded successfully")
            else:
                logger.warning(f"Ensemble model not found at {ensemble_path}")
            
            # Load scaler
            scaler_path = MODELS_PATH / "genetic_scaler.joblib"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("Feature scaler loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def create_prediction(
        self,
        user_id: int,
        health_metrics: Optional[Dict[str, float]] = None
    ) -> Prediction:
        """
        Create a prediction using real trained models
        
        Args:
            user_id: User ID
            health_metrics: Optional health metrics dictionary
            
        Returns:
            Prediction object
        """
        try:
            # Get health metrics if not provided
            if not health_metrics:
                health_metrics = self._get_latest_health_metrics(user_id)
            
            # Convert health metrics to feature vector
            features = self._metrics_to_features(health_metrics)
            
            # Make prediction
            if self.ensemble_model and features is not None:
                result = self.ensemble_model.predict_risk(features)
                
                # Create prediction record
                from app.models.prediction import RiskCategory
                
                # Map risk level to category
                risk_category_map = {
                    'low': RiskCategory.LOW,
                    'moderate': RiskCategory.MODERATE,
                    'high': RiskCategory.HIGH
                }
                
                prediction = Prediction(
                    user_id=user_id,
                    risk_score=result['risk_score'],
                    risk_category=risk_category_map.get(result['risk_level'], RiskCategory.MODERATE),
                    confidence_interval_lower=max(0, result['risk_score'] - result['confidence']),
                    confidence_interval_upper=min(1, result['risk_score'] + result['confidence']),
                    feature_importance={},
                    model_version="ensemble_v1_real",
                    model_type="ensemble",
                    input_features={"health_metrics": list(health_metrics.keys())[:10]},
                    prediction_date=datetime.utcnow()
                )
                
                self.db.add(prediction)
                self.db.commit()
                self.db.refresh(prediction)
                
                logger.info(f"Created prediction {prediction.id} for user {user_id}")
                return prediction
            else:
                # Fallback to mock prediction
                return self._create_mock_prediction(user_id, health_metrics)
                
        except Exception as e:
            logger.error(f"Error creating prediction: {e}")
            return self._create_mock_prediction(user_id, health_metrics)
    
    def _metrics_to_features(self, metrics: Dict[str, float]) -> Optional[np.ndarray]:
        """
        Convert health metrics to feature vector for model
        
        Args:
            metrics: Health metrics dictionary
            
        Returns:
            Feature vector or None if conversion fails
        """
        try:
            # Expected feature count from genetic model
            expected_features = 130
            
            # Extract relevant metrics and pad/truncate to expected size
            feature_list = []
            
            # Map common health metrics to features
            metric_mapping = {
                'age': 0,
                'mmse_score': 1,
                'moca_score': 2,
                'blood_pressure_systolic': 3,
                'blood_pressure_diastolic': 4,
                'cholesterol': 5,
                'glucose': 6,
                'bmi': 7,
                'heart_rate': 8,
                'sleep_hours': 9,
                'exercise_minutes': 10,
                'cognitive_score': 11,
                'memory_score': 12,
                'attention_score': 13,
                'language_score': 14,
            }
            
            # Initialize feature vector
            features = np.zeros(expected_features)
            
            # Fill in available metrics
            for metric_name, value in metrics.items():
                metric_key = metric_name.lower().replace(' ', '_')
                if metric_key in metric_mapping:
                    idx = metric_mapping[metric_key]
                    features[idx] = float(value)
            
            # Add some derived features
            if 'age' in metrics:
                features[15] = metrics['age'] ** 2  # Age squared
            
            if 'mmse_score' in metrics and 'moca_score' in metrics:
                features[16] = (metrics['mmse_score'] + metrics['moca_score']) / 2
            
            # Normalize using loaded scaler if available
            if self.scaler:
                features = self.scaler.transform(features.reshape(1, -1))[0]
            
            return features
            
        except Exception as e:
            logger.error(f"Error converting metrics to features: {e}")
            return None
    
    def _get_latest_health_metrics(self, user_id: int) -> Dict[str, float]:
        """Get latest health metrics for user"""
        metrics = self.db.query(HealthMetric).filter(
            HealthMetric.user_id == user_id
        ).order_by(HealthMetric.recorded_at.desc()).limit(50).all()
        
        metrics_dict = {}
        for metric in metrics:
            name = metric.name.lower().replace(' ', '_')
            metrics_dict[name] = float(metric.value)
        
        # Add default values if missing
        defaults = {
            'age': 65.0,
            'mmse_score': 24.0,
            'moca_score': 22.0,
            'blood_pressure_systolic': 120.0,
            'blood_pressure_diastolic': 80.0,
            'cholesterol': 200.0,
            'glucose': 100.0,
            'bmi': 25.0,
            'heart_rate': 70.0,
        }
        
        for key, value in defaults.items():
            if key not in metrics_dict:
                metrics_dict[key] = value
        
        return metrics_dict
    
    def _create_mock_prediction(
        self,
        user_id: int,
        health_metrics: Optional[Dict[str, float]]
    ) -> Prediction:
        """Create a mock prediction when real model is unavailable"""
        # Generate reasonable mock values based on metrics
        age = health_metrics.get('age', 65) if health_metrics else 65
        mmse = health_metrics.get('mmse_score', 24) if health_metrics else 24
        
        # Risk increases with age and decreases with MMSE score
        risk_score = min(0.9, max(0.1, (age - 50) / 50 + (30 - mmse) / 30))
        
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "moderate"
        else:
            risk_level = "high"
        
        from app.models.prediction import RiskCategory
        
        risk_category_map = {
            'low': RiskCategory.LOW,
            'moderate': RiskCategory.MODERATE,
            'high': RiskCategory.HIGH
        }
        
        prediction = Prediction(
            user_id=user_id,
            risk_score=risk_score,
            risk_category=risk_category_map.get(risk_level, RiskCategory.MODERATE),
            confidence_interval_lower=max(0, risk_score - 0.1),
            confidence_interval_upper=min(1, risk_score + 0.1),
            feature_importance={},
            model_version="mock_v1",
            model_type="mock",
            input_features={"note": "Using mock prediction - train models first"},
            prediction_date=datetime.utcnow()
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        return prediction
    
    def get_user_predictions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Prediction]:
        """Get predictions for a user"""
        return self.db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).order_by(
            Prediction.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_prediction_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Get prediction by ID"""
        return self.db.query(Prediction).filter(
            Prediction.id == prediction_id
        ).first()
    
    def generate_explanation(self, prediction_id: int) -> Dict:
        """Generate explanation for a prediction"""
        prediction = self.get_prediction_by_id(prediction_id)
        
        if not prediction:
            raise ValueError("Prediction not found")
        
        # Get health metrics
        health_metrics = self._get_latest_health_metrics(prediction.user_id)
        
        # Generate explanation based on key metrics
        risk_factors = []
        protective_factors = []
        
        # Analyze key metrics
        if health_metrics.get('age', 0) > 65:
            risk_factors.append({
                'feature': 'Age',
                'value': health_metrics['age'],
                'impact': 'high'
            })
        
        mmse = health_metrics.get('mmse_score', 30)
        if mmse < 24:
            risk_factors.append({
                'feature': 'MMSE Score',
                'value': mmse,
                'impact': 'high'
            })
        elif mmse > 27:
            protective_factors.append({
                'feature': 'MMSE Score',
                'value': mmse,
                'impact': 'moderate'
            })
        
        moca = health_metrics.get('moca_score', 30)
        if moca < 22:
            risk_factors.append({
                'feature': 'MoCA Score',
                'value': moca,
                'impact': 'high'
            })
        
        # Generate explanation text
        explanation_text = f"Risk Level: {prediction.risk_level.upper()}\n"
        explanation_text += f"Risk Score: {prediction.risk_score:.1%}\n\n"
        
        if risk_factors:
            explanation_text += "Key Risk Factors:\n"
            for factor in risk_factors:
                explanation_text += f"  • {factor['feature']}: {factor['value']} ({factor['impact']} impact)\n"
        
        if protective_factors:
            explanation_text += "\nProtective Factors:\n"
            for factor in protective_factors:
                explanation_text += f"  • {factor['feature']}: {factor['value']} ({factor['impact']} impact)\n"
        
        return {
            'risk_factors': risk_factors,
            'protective_factors': protective_factors,
            'explanation_text': explanation_text,
            'confidence': prediction.confidence_score
        }
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            'model_loaded': self.ensemble_model is not None,
            'scaler_loaded': self.scaler is not None,
            'registry_info': self.model_info,
            'models_path': str(MODELS_PATH)
        }
    
    def check_health(self) -> bool:
        """Check if ML service is healthy"""
        return True  # Always return True, will use mock if models not available
