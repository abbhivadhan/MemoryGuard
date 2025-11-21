"""
Celery tasks for ML predictions and processing.
"""

from celery import Task
from typing import Dict, Optional
import logging

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.ml_service import MLService

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""
    
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='ml.process_prediction',
    max_retries=3,
    default_retry_delay=60
)
def process_prediction_task(
    self,
    prediction_id: int,
    user_id: int,
    health_metrics: Optional[Dict[str, float]] = None
):
    """
    Process ML prediction asynchronously.
    
    Args:
        prediction_id: Prediction ID
        user_id: User ID
        health_metrics: Optional health metrics dictionary
    """
    try:
        logger.info(f"Processing prediction {prediction_id} for user {user_id}")
        
        # Create ML service
        ml_service = MLService(self.db)
        
        # Process prediction
        ml_service._process_prediction(prediction_id, user_id, health_metrics)
        
        logger.info(f"Prediction {prediction_id} processed successfully")
        
        return {
            'status': 'success',
            'prediction_id': prediction_id
        }
        
    except Exception as e:
        logger.error(f"Error processing prediction {prediction_id}: {str(e)}")
        
        # Retry task
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for prediction {prediction_id}")
            
            # Update prediction status to failed
            from app.models.prediction import Prediction
            prediction = self.db.query(Prediction).filter(
                Prediction.id == prediction_id
            ).first()
            
            if prediction:
                prediction.status = 'failed'
                prediction.metadata = {'error': str(e), 'max_retries_exceeded': True}
                self.db.commit()
            
            return {
                'status': 'failed',
                'prediction_id': prediction_id,
                'error': str(e)
            }


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='ml.batch_predictions',
    max_retries=2
)
def batch_predictions_task(
    self,
    user_ids: list,
    health_metrics_list: Optional[list] = None
):
    """
    Process batch predictions for multiple users.
    
    Args:
        user_ids: List of user IDs
        health_metrics_list: Optional list of health metrics dicts
    """
    try:
        logger.info(f"Processing batch predictions for {len(user_ids)} users")
        
        ml_service = MLService(self.db)
        results = []
        
        for i, user_id in enumerate(user_ids):
            health_metrics = health_metrics_list[i] if health_metrics_list else None
            
            try:
                # Create prediction record
                from app.models.prediction import Prediction
                from datetime import datetime
                
                prediction = Prediction(
                    user_id=user_id,
                    status='pending',
                    model_version=ml_service.model_version,
                    created_at=datetime.utcnow()
                )
                
                self.db.add(prediction)
                self.db.commit()
                self.db.refresh(prediction)
                
                # Process prediction
                ml_service._process_prediction(
                    prediction.id,
                    user_id,
                    health_metrics
                )
                
                results.append({
                    'user_id': user_id,
                    'prediction_id': prediction.id,
                    'status': 'success'
                })
                
            except Exception as e:
                logger.error(f"Error processing prediction for user {user_id}: {str(e)}")
                results.append({
                    'user_id': user_id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Batch predictions completed: {len(results)} processed")
        
        return {
            'status': 'completed',
            'total': len(user_ids),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error in batch predictions: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='ml.generate_explanation',
    max_retries=2
)
def generate_explanation_task(
    self,
    prediction_id: int
):
    """
    Generate SHAP explanation for a prediction.
    
    Args:
        prediction_id: Prediction ID
    """
    try:
        logger.info(f"Generating explanation for prediction {prediction_id}")
        
        ml_service = MLService(self.db)
        explanation = ml_service.generate_explanation(prediction_id)
        
        # Store explanation in prediction metadata
        from app.models.prediction import Prediction
        prediction = self.db.query(Prediction).filter(
            Prediction.id == prediction_id
        ).first()
        
        if prediction:
            if not prediction.metadata:
                prediction.metadata = {}
            
            prediction.metadata['explanation'] = explanation
            self.db.commit()
        
        logger.info(f"Explanation generated for prediction {prediction_id}")
        
        return {
            'status': 'success',
            'prediction_id': prediction_id
        }
        
    except Exception as e:
        logger.error(f"Error generating explanation for {prediction_id}: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='ml.update_forecasts',
    max_retries=2
)
def update_forecasts_task(
    self,
    user_id: int
):
    """
    Update progression forecasts for a user.
    
    Args:
        user_id: User ID
    """
    try:
        logger.info(f"Updating forecasts for user {user_id}")
        
        ml_service = MLService(self.db)
        
        # Get latest health metrics
        health_metrics = ml_service._get_latest_health_metrics(user_id)
        
        # Generate forecast
        forecast = ml_service.generate_forecast(
            user_id=user_id,
            current_metrics=health_metrics,
            forecast_months=[6, 12, 24]
        )
        
        # Store forecast (could be in a separate table)
        # For now, just log it
        logger.info(f"Forecast generated for user {user_id}")
        
        return {
            'status': 'success',
            'user_id': user_id,
            'forecast': forecast
        }
        
    except Exception as e:
        logger.error(f"Error updating forecasts for user {user_id}: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(name='ml.health_check')
def ml_health_check_task():
    """
    Health check task for ML workers.
    """
    try:
        logger.info("ML worker health check")
        
        # Basic health check
        return {
            'status': 'healthy',
            'worker': 'ml',
            'timestamp': str(celery_app.now())
        }
        
    except Exception as e:
        logger.error(f"ML worker health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
