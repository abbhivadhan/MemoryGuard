"""
ML service for handling predictions, explanations, and forecasts.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from datetime import datetime
import numpy as np
import logging
from pathlib import Path

from app.models.prediction import Prediction
from app.models.health_metric import HealthMetric
# Lazy imports to avoid XGBoost loading issues in dev mode
# from app.ml.preprocessing import FeaturePreprocessor
# from app.ml.models.ensemble import AlzheimerEnsemble
# from app.ml.interpretability import EnsembleSHAPExplainer
# from app.ml.forecasting import ProgressionForecaster

logger = logging.getLogger(__name__)


class MLService:
    """
    Service for ML predictions and analysis.
    """
    
    def __init__(self, db: Session):
        """
        Initialize ML service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.preprocessor = FeaturePreprocessor()
        self.ensemble_model = None
        self.explainer = None
        self.forecaster = ProgressionForecaster()
        self.model_version = "1.0.0"
        
        # Load models if available
        self._load_models()
    
    def _load_models(self) -> None:
        """Load trained models from disk."""
        try:
            model_dir = Path("models/ensemble")
            if model_dir.exists():
                self.ensemble_model = AlzheimerEnsemble()
                self.ensemble_model.load(str(model_dir))
                logger.info("Ensemble model loaded successfully")
            else:
                logger.warning("No trained models found. Models need to be trained.")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
    
    async def create_prediction_async(
        self,
        user_id: int,
        health_metrics: Optional[Dict[str, float]],
        background_tasks: BackgroundTasks
    ) -> Prediction:
        """
        Create prediction asynchronously.
        
        Args:
            user_id: User ID
            health_metrics: Optional health metrics dict
            background_tasks: FastAPI background tasks
            
        Returns:
            Prediction object with pending status
        """
        # Create prediction record
        prediction = Prediction(
            user_id=user_id,
            status='pending',
            model_version=self.model_version,
            created_at=datetime.utcnow()
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        # Queue Celery task for processing
        try:
            from app.tasks.ml_tasks import process_prediction_task
            process_prediction_task.delay(
                prediction.id,
                user_id,
                health_metrics
            )
        except Exception as e:
            logger.warning(f"Celery not available, using background task: {str(e)}")
            # Fallback to FastAPI background tasks
            background_tasks.add_task(
                self._process_prediction,
                prediction.id,
                user_id,
                health_metrics
            )
        
        return prediction
    
    def _process_prediction(
        self,
        prediction_id: int,
        user_id: int,
        health_metrics: Optional[Dict[str, float]]
    ) -> None:
        """
        Process prediction in background.
        
        Args:
            prediction_id: Prediction ID
            user_id: User ID
            health_metrics: Optional health metrics
        """
        try:
            # Get prediction record
            prediction = self.db.query(Prediction).filter(
                Prediction.id == prediction_id
            ).first()
            
            if not prediction:
                logger.error(f"Prediction {prediction_id} not found")
                return
            
            # Update status
            prediction.status = 'processing'
            self.db.commit()
            
            # Get health metrics if not provided
            if not health_metrics:
                health_metrics = self._get_latest_health_metrics(user_id)
            
            # Get imaging features
            imaging_features = self._get_latest_imaging_features(user_id)
            
            # Merge features
            all_features = self._merge_features(health_metrics, imaging_features)
            
            # Extract and preprocess features
            features = self.preprocessor.extract_features_from_metrics(
                [{'name': k, 'value': v} for k, v in all_features.items()]
            )
            
            # Validate features
            is_valid, missing = self.preprocessor.validate_features(features)
            if not is_valid:
                prediction.status = 'failed'
                prediction.metadata = {'error': f'Missing features: {missing}'}
                self.db.commit()
                return
            
            # Make prediction
            if self.ensemble_model and self.ensemble_model.is_trained:
                # Preprocess features
                X = self.preprocessor.transform(features)
                
                # Get prediction with confidence
                pred, confidence, ci = self.ensemble_model.predict_with_confidence(X)
                prob_neg, prob_pos = self.ensemble_model.predict_proba(X)
                
                # Determine risk level
                risk_level = self._determine_risk_level(prob_pos)
                
                # Update prediction
                prediction.prediction = pred
                prediction.probability = prob_pos
                prediction.confidence_score = confidence
                prediction.confidence_interval_lower = ci[0]
                prediction.confidence_interval_upper = ci[1]
                prediction.risk_level = risk_level
                prediction.status = 'completed'
                prediction.completed_at = datetime.utcnow()
                
                # Store model predictions
                model_preds = self.ensemble_model.get_model_predictions(X)
                prediction.metadata = {
                    'model_predictions': model_preds,
                    'features_used': list(features.keys())
                }
            else:
                prediction.status = 'failed'
                prediction.metadata = {'error': 'Models not trained'}
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error processing prediction {prediction_id}: {str(e)}")
            prediction.status = 'failed'
            prediction.metadata = {'error': str(e)}
            self.db.commit()
    
    def _get_latest_health_metrics(self, user_id: int) -> Dict[str, float]:
        """
        Get latest health metrics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary of health metrics
        """
        metrics = self.db.query(HealthMetric).filter(
            HealthMetric.user_id == user_id
        ).order_by(HealthMetric.recorded_at.desc()).limit(50).all()
        
        # Convert to dictionary
        metrics_dict = {}
        for metric in metrics:
            name = metric.name.lower().replace(' ', '_')
            metrics_dict[name] = float(metric.value)
        
        return metrics_dict
    
    def _get_latest_imaging_features(self, user_id: int) -> Dict[str, float]:
        """
        Get latest imaging features for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary of imaging features
        """
        from app.models.imaging import MedicalImaging, ImagingStatus
        
        # Get most recent completed imaging study
        imaging = self.db.query(MedicalImaging).filter(
            MedicalImaging.user_id == user_id,
            MedicalImaging.status == ImagingStatus.COMPLETED
        ).order_by(MedicalImaging.created_at.desc()).first()
        
        if not imaging or not imaging.ml_features:
            return {}
        
        return imaging.ml_features
    
    def _merge_features(
        self,
        health_metrics: Dict[str, float],
        imaging_features: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Merge health metrics and imaging features.
        
        Args:
            health_metrics: Health metrics dictionary
            imaging_features: Imaging features dictionary
            
        Returns:
            Merged features dictionary
        """
        merged = health_metrics.copy()
        
        # Add imaging features with prefix to avoid conflicts
        for key, value in imaging_features.items():
            merged[f"imaging_{key}"] = value
        
        return merged
    
    def _determine_risk_level(self, probability: float) -> str:
        """
        Determine risk level from probability.
        
        Args:
            probability: Prediction probability
            
        Returns:
            Risk level string
        """
        if probability < 0.3:
            return 'low'
        elif probability < 0.6:
            return 'moderate'
        elif probability < 0.8:
            return 'high'
        else:
            return 'very_high'
    
    def get_user_predictions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Prediction]:
        """
        Get predictions for a user.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of predictions
        """
        return self.db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).order_by(
            Prediction.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def count_user_predictions(self, user_id: int) -> int:
        """Count total predictions for a user."""
        return self.db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).count()
    
    def get_prediction_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Get prediction by ID."""
        return self.db.query(Prediction).filter(
            Prediction.id == prediction_id
        ).first()
    
    def generate_explanation(self, prediction_id: int) -> Dict:
        """
        Generate SHAP explanation for a prediction.
        
        Args:
            prediction_id: Prediction ID
            
        Returns:
            Dictionary with explanation data
        """
        prediction = self.get_prediction_by_id(prediction_id)
        
        if not prediction:
            raise ValueError("Prediction not found")
        
        if prediction.status != 'completed':
            raise ValueError("Prediction not completed")
        
        # Get health metrics
        health_metrics = self._get_latest_health_metrics(prediction.user_id)
        
        # Get imaging features
        imaging_features = self._get_latest_imaging_features(prediction.user_id)
        
        # Merge features
        all_features = self._merge_features(health_metrics, imaging_features)
        
        # Extract features
        features = self.preprocessor.extract_features_from_metrics(
            [{'name': k, 'value': v} for k, v in all_features.items()]
        )
        
        # Preprocess
        X = self.preprocessor.transform(features)
        
        # Initialize explainer if needed
        if not self.explainer and self.ensemble_model:
            self.explainer = EnsembleSHAPExplainer(self.ensemble_model)
            # Use dummy background data for now
            background_data = np.random.randn(10, len(features))
            self.explainer.initialize_explainers(background_data)
        
        if self.explainer:
            # Generate explanation
            explanation = self.explainer.explain_prediction(
                X,
                self.preprocessor.get_feature_names()
            )
            
            # Format for response
            top_features = [
                {'feature': k, 'shap_value': v}
                for k, v in list(explanation['aggregated_shap_values'].items())[:10]
            ]
            
            # Get positive and negative contributors
            positive_contributors = [
                {'feature': k, 'contribution': v}
                for k, v in explanation['aggregated_shap_values'].items()
                if v > 0
            ][:5]
            
            negative_contributors = [
                {'feature': k, 'contribution': abs(v)}
                for k, v in explanation['aggregated_shap_values'].items()
                if v < 0
            ][:5]
            
            # Generate text explanation
            explanation_text = self._generate_explanation_text(
                prediction.prediction,
                prediction.probability,
                top_features
            )
            
            return {
                'top_features': top_features,
                'positive_contributors': positive_contributors,
                'negative_contributors': negative_contributors,
                'explanation_text': explanation_text,
                'shap_values': explanation['aggregated_shap_values']
            }
        else:
            # Return basic explanation without SHAP
            return {
                'top_features': [],
                'positive_contributors': [],
                'negative_contributors': [],
                'explanation_text': f"Prediction: {prediction.prediction}, Probability: {prediction.probability:.2%}",
                'shap_values': {}
            }
    
    def _generate_explanation_text(
        self,
        prediction: int,
        probability: float,
        top_features: List[Dict]
    ) -> str:
        """Generate human-readable explanation."""
        risk = "high" if prediction == 1 else "low"
        
        text = f"The model predicts a {risk} risk of Alzheimer's disease "
        text += f"with {probability:.1%} probability.\n\n"
        
        if top_features:
            text += "Most influential factors:\n"
            for feat in top_features[:3]:
                feature_name = feat['feature'].replace('_', ' ').title()
                text += f"  • {feature_name}\n"
        
        return text
    
    def generate_forecast(
        self,
        user_id: int,
        current_metrics: Dict[str, float],
        forecast_months: List[int]
    ) -> Dict:
        """
        Generate progression forecast.
        
        Args:
            user_id: User ID
            current_metrics: Current health metrics
            forecast_months: List of months to forecast
            
        Returns:
            Forecast data
        """
        # Get historical data
        historical_metrics = self.db.query(HealthMetric).filter(
            HealthMetric.user_id == user_id
        ).order_by(HealthMetric.recorded_at.asc()).all()
        
        # Convert to list of dicts
        historical_data = []
        for metric in historical_metrics:
            historical_data.append({
                metric.name.lower().replace(' ', '_'): float(metric.value),
                'recorded_at': metric.recorded_at
            })
        
        # Generate forecast
        forecast = self.forecaster.forecast_progression(
            current_metrics,
            historical_data if historical_data else None,
            forecast_months
        )
        
        return forecast
    
    def get_model_info(self) -> Dict:
        """Get model information."""
        info = {
            'version': self.model_version,
            'last_trained': None,
            'ensemble_info': {},
            'performance_metrics': {}
        }
        
        if self.ensemble_model and self.ensemble_model.is_trained:
            info['ensemble_info'] = self.ensemble_model.get_ensemble_info()
        
        return info
    
    def check_health(self) -> bool:
        """Check if ML service is healthy."""
        return self.ensemble_model is not None and self.ensemble_model.is_trained
