"""
Apache Airflow DAG for Automated Model Retraining

This DAG orchestrates the complete retraining workflow:
1. Check for data drift
2. Check data volume
3. Load new data
4. Retrain models
5. Evaluate new models
6. Deploy if better
7. Send notifications
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator, BranchPythonOperator
    from airflow.operators.dummy import DummyOperator
    from airflow.utils.trigger_rule import TriggerRule
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    logging.warning("Apache Airflow not installed. DAG will not be available.")

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import get_logger

logger = get_logger(__name__)


# Default arguments for the DAG
DEFAULT_ARGS = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email': [settings.PERFORMANCE_ALERT_EMAIL] if settings.PERFORMANCE_ALERT_EMAIL else [],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def check_drift_task(**context):
    """
    Task to check for data drift
    
    Returns:
        'retrain' if drift detected, 'skip_retrain' otherwise
    """
    from ml_pipeline.retraining.retraining_triggers import RetrainingTriggers
    
    logger.info("Checking for data drift...")
    
    triggers = RetrainingTriggers()
    drift_detected, drift_results = triggers.check_drift()
    
    # Store results in XCom
    context['task_instance'].xcom_push(key='drift_detected', value=drift_detected)
    context['task_instance'].xcom_push(key='drift_results', value=drift_results)
    
    if drift_detected:
        logger.info("Drift detected - proceeding with retraining")
        return 'check_data_volume'
    else:
        logger.info("No drift detected")
        return 'check_data_volume'  # Still check data volume


def check_data_volume_task(**context):
    """
    Task to check if sufficient new data is available
    
    Returns:
        'retrain' if volume threshold met, 'skip_retrain' otherwise
    """
    from ml_pipeline.retraining.retraining_triggers import RetrainingTriggers
    
    logger.info("Checking data volume...")
    
    triggers = RetrainingTriggers()
    volume_threshold_met, new_records = triggers.check_data_volume()
    
    # Store results in XCom
    context['task_instance'].xcom_push(key='volume_threshold_met', value=volume_threshold_met)
    context['task_instance'].xcom_push(key='new_records', value=new_records)
    
    # Get drift status from previous task
    drift_detected = context['task_instance'].xcom_pull(
        task_ids='check_drift',
        key='drift_detected'
    )
    
    # Retrain if either drift detected OR volume threshold met
    should_retrain = drift_detected or volume_threshold_met
    
    context['task_instance'].xcom_push(key='should_retrain', value=should_retrain)
    
    if should_retrain:
        logger.info(f"Retraining triggered: drift={drift_detected}, volume={volume_threshold_met}")
        return 'load_new_data'
    else:
        logger.info("No retraining needed")
        return 'skip_retrain'


def load_data_task(**context):
    """Task to load new training data"""
    from ml_pipeline.training.data_loader import DataLoader
    
    logger.info("Loading new training data...")
    
    data_loader = DataLoader(settings.FEATURES_PATH)
    splits = data_loader.load_and_split(
        dataset_name="train_features",
        target_column="diagnosis"
    )
    
    # Store data info in XCom
    context['task_instance'].xcom_push(key='n_train_samples', value=len(splits['X_train']))
    context['task_instance'].xcom_push(key='n_val_samples', value=len(splits['X_val']))
    context['task_instance'].xcom_push(key='n_test_samples', value=len(splits['X_test']))
    
    logger.info(f"Loaded {len(splits['X_train'])} training samples")
    
    return "Data loaded successfully"


def retrain_models_task(**context):
    """Task to retrain all models"""
    from ml_pipeline.retraining.retraining_pipeline import AutomatedRetrainingPipeline
    
    logger.info("Starting model retraining...")
    
    pipeline = AutomatedRetrainingPipeline()
    results = pipeline.retrain_all_models()
    
    # Store results in XCom
    context['task_instance'].xcom_push(key='retraining_results', value=results)
    
    logger.info("Model retraining completed")
    
    return results


def evaluate_models_task(**context):
    """Task to evaluate new models against production"""
    from ml_pipeline.retraining.retraining_pipeline import AutomatedRetrainingPipeline
    
    logger.info("Evaluating new models...")
    
    # Get retraining results
    retraining_results = context['task_instance'].xcom_pull(
        task_ids='retrain_models',
        key='retraining_results'
    )
    
    pipeline = AutomatedRetrainingPipeline()
    evaluation_results = pipeline.evaluate_new_models(retraining_results)
    
    # Store evaluation results
    context['task_instance'].xcom_push(key='evaluation_results', value=evaluation_results)
    
    logger.info("Model evaluation completed")
    
    return evaluation_results


def deploy_models_task(**context):
    """Task to deploy models if they perform better"""
    from ml_pipeline.retraining.model_promoter import ModelPromoter
    
    logger.info("Checking if new models should be deployed...")
    
    # Get evaluation results
    evaluation_results = context['task_instance'].xcom_pull(
        task_ids='evaluate_models',
        key='evaluation_results'
    )
    
    promoter = ModelPromoter()
    deployment_results = promoter.promote_if_better(evaluation_results)
    
    # Store deployment results
    context['task_instance'].xcom_push(key='deployment_results', value=deployment_results)
    
    logger.info("Deployment check completed")
    
    return deployment_results


def send_notification_task(**context):
    """Task to send notifications about retraining results"""
    from ml_pipeline.retraining.notification_service import NotificationService
    
    logger.info("Sending notifications...")
    
    # Gather all results
    drift_detected = context['task_instance'].xcom_pull(
        task_ids='check_drift',
        key='drift_detected'
    )
    
    volume_threshold_met = context['task_instance'].xcom_pull(
        task_ids='check_data_volume',
        key='volume_threshold_met'
    )
    
    deployment_results = context['task_instance'].xcom_pull(
        task_ids='deploy_models',
        key='deployment_results'
    )
    
    notification_service = NotificationService()
    notification_service.send_retraining_summary(
        drift_detected=drift_detected,
        volume_threshold_met=volume_threshold_met,
        deployment_results=deployment_results
    )
    
    logger.info("Notifications sent")
    
    return "Notifications sent successfully"


def create_retraining_dag():
    """
    Create the Airflow DAG for automated model retraining
    
    Returns:
        DAG object configured for automated retraining
    """
    if not AIRFLOW_AVAILABLE:
        logger.error("Cannot create DAG: Apache Airflow not installed")
        return None
    
    dag = DAG(
        'model_retraining',
        default_args=DEFAULT_ARGS,
        description='Automated ML model retraining pipeline for Alzheimer\'s Disease detection',
        schedule_interval='@monthly',  # Run monthly as per requirements
        catchup=False,
        tags=['ml', 'retraining', 'alzheimers']
    )
    
    with dag:
        # Start task
        start = DummyOperator(
            task_id='start'
        )
        
        # Check for data drift
        check_drift = PythonOperator(
            task_id='check_drift',
            python_callable=check_drift_task,
            provide_context=True
        )
        
        # Check data volume
        check_data_volume = BranchPythonOperator(
            task_id='check_data_volume',
            python_callable=check_data_volume_task,
            provide_context=True
        )
        
        # Skip retraining branch
        skip_retrain = DummyOperator(
            task_id='skip_retrain'
        )
        
        # Load new data
        load_data = PythonOperator(
            task_id='load_new_data',
            python_callable=load_data_task,
            provide_context=True
        )
        
        # Retrain models
        retrain = PythonOperator(
            task_id='retrain_models',
            python_callable=retrain_models_task,
            provide_context=True
        )
        
        # Evaluate new models
        evaluate = PythonOperator(
            task_id='evaluate_models',
            python_callable=evaluate_models_task,
            provide_context=True
        )
        
        # Deploy if better
        deploy = PythonOperator(
            task_id='deploy_models',
            python_callable=deploy_models_task,
            provide_context=True
        )
        
        # Send notifications
        notify = PythonOperator(
            task_id='send_notifications',
            python_callable=send_notification_task,
            provide_context=True,
            trigger_rule=TriggerRule.ALL_DONE  # Run even if upstream fails
        )
        
        # End task
        end = DummyOperator(
            task_id='end',
            trigger_rule=TriggerRule.ALL_DONE
        )
        
        # Define task dependencies
        start >> check_drift >> check_data_volume
        check_data_volume >> [skip_retrain, load_data]
        load_data >> retrain >> evaluate >> deploy >> notify >> end
        skip_retrain >> end
    
    logger.info("Retraining DAG created successfully")
    
    return dag


# Create the DAG instance
if AIRFLOW_AVAILABLE:
    dag = create_retraining_dag()
