"""
Example: Automated Retraining Pipeline

This example demonstrates the complete automated retraining workflow including:
- Checking retraining triggers
- Running automated retraining
- Evaluating new models
- Promoting models
- A/B testing
"""

import logging
from pathlib import Path

from ml_pipeline.retraining import (
    AutomatedRetrainingPipeline,
    RetrainingTriggers,
    ModelPromoter,
    NotificationService,
    ABTestingManager,
    RolloutStrategy
)
from ml_pipeline.config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def example_check_triggers():
    """Example: Check if retraining should be triggered"""
    print("\n" + "=" * 80)
    print("Example 1: Checking Retraining Triggers")
    print("=" * 80)
    
    triggers = RetrainingTriggers()
    
    # Check all triggers
    should_retrain, trigger_info = triggers.should_retrain(
        check_drift=True,
        check_volume=True,
        check_performance=False
    )
    
    print(f"\nShould retrain: {should_retrain}")
    if should_retrain:
        print(f"Trigger reason: {trigger_info.get('trigger_reason')}")
    
    # Check individual triggers
    print("\n--- Individual Trigger Checks ---")
    
    # Drift check
    drift_detected, drift_results = triggers.check_drift()
    print(f"\nDrift detected: {drift_detected}")
    if drift_detected:
        print(f"Features with KS drift: {len(drift_results.get('features_with_ks_drift', []))}")
        print(f"Features with high PSI: {len(drift_results.get('features_with_high_psi', []))}")
    
    # Volume check
    volume_met, new_records = triggers.check_data_volume()
    print(f"\nVolume threshold met: {volume_met}")
    print(f"New records: {new_records}")


def example_automated_retraining():
    """Example: Run automated retraining"""
    print("\n" + "=" * 80)
    print("Example 2: Automated Retraining")
    print("=" * 80)
    
    # Initialize pipeline
    pipeline = AutomatedRetrainingPipeline()
    
    # Run retraining
    print("\nStarting automated retraining...")
    results = pipeline.retrain_all_models()
    
    if results['success']:
        print(f"\n✓ Retraining completed successfully")
        print(f"  Training time: {results['elapsed_time_seconds']:.2f}s")
        print(f"  Output directory: {results['output_dir']}")
        
        # Show registered models
        registration = results.get('registration_results', {})
        print(f"\n  Registered models:")
        for model_name, version_id in registration.items():
            print(f"    - {model_name}: {version_id}")
    else:
        print(f"\n✗ Retraining failed: {results.get('error')}")
    
    return results


def example_model_evaluation(retraining_results):
    """Example: Evaluate new models against production"""
    print("\n" + "=" * 80)
    print("Example 3: Model Evaluation")
    print("=" * 80)
    
    pipeline = AutomatedRetrainingPipeline()
    
    # Evaluate new models
    print("\nEvaluating new models vs production...")
    evaluation = pipeline.evaluate_new_models(retraining_results)
    
    if evaluation['success']:
        print(f"\n✓ Evaluation completed")
        
        summary = evaluation['summary']
        print(f"\n  Models evaluated: {summary['models_evaluated']}")
        print(f"  Recommended for deployment: {summary['models_recommended_for_deployment']}")
        print(f"  Requiring manual review: {summary['models_requiring_manual_review']}")
        
        # Show individual model results
        print(f"\n  Model Results:")
        for model_name, result in evaluation['model_evaluations'].items():
            recommendation = result['recommendation']
            comparison = result.get('comparison', {})
            
            if isinstance(comparison, dict):
                improvement = comparison.get('primary_metric_improvement_percent', 0)
                print(f"    - {model_name}: {recommendation} ({improvement:+.2f}%)")
            else:
                print(f"    - {model_name}: {recommendation}")
    else:
        print(f"\n✗ Evaluation failed: {evaluation.get('error')}")
    
    return evaluation


def example_model_promotion(evaluation_results):
    """Example: Promote models if they meet criteria"""
    print("\n" + "=" * 80)
    print("Example 4: Model Promotion")
    print("=" * 80)
    
    promoter = ModelPromoter(improvement_threshold=0.05)  # 5% improvement
    
    # Promote models
    print("\nChecking models for promotion...")
    promotion_results = promoter.promote_if_better(evaluation_results)
    
    if promotion_results['success']:
        print(f"\n✓ Promotion check completed")
        
        summary = promotion_results['summary']
        print(f"\n  Models promoted: {summary['models_promoted']}")
        print(f"  Requiring manual review: {summary['models_requiring_review']}")
        print(f"  Not promoted: {summary['models_not_promoted']}")
        
        # Show promoted models
        if summary['models_promoted'] > 0:
            print(f"\n  Promoted Models:")
            for model in summary.get('promoted_models', []):
                print(f"    - {model['model_name']} v{model['version_id']} "
                      f"(+{model['improvement_percent']:.2f}%)")
        
        # Show models requiring review
        if summary['models_requiring_review'] > 0:
            print(f"\n  Models Requiring Manual Review:")
            for model in summary.get('review_required_models', []):
                print(f"    - {model['model_name']} "
                      f"(+{model['improvement_percent']:.2f}%)")
    else:
        print(f"\n✗ Promotion failed: {promotion_results.get('error')}")
    
    return promotion_results


def example_notifications(promotion_results):
    """Example: Send notifications"""
    print("\n" + "=" * 80)
    print("Example 5: Notifications")
    print("=" * 80)
    
    # Initialize notification service
    # Note: Email will fail without proper SMTP config, but will log instead
    notifier = NotificationService()
    
    # Send retraining summary
    print("\nSending retraining summary notification...")
    success = notifier.send_retraining_summary(
        drift_detected=True,
        volume_threshold_met=False,
        deployment_results=promotion_results
    )
    
    if success:
        print("✓ Notification sent (or logged)")
    else:
        print("✗ Notification failed")


def example_ab_testing():
    """Example: A/B testing and gradual rollout"""
    print("\n" + "=" * 80)
    print("Example 6: A/B Testing")
    print("=" * 80)
    
    ab_manager = ABTestingManager()
    
    # Create A/B test
    print("\nCreating A/B test...")
    test = ab_manager.create_ab_test(
        model_name='random_forest',
        version_a='v_production',
        version_b='v_new',
        traffic_split=0.5,
        duration_days=7
    )
    
    print(f"✓ A/B test created: {test['test_id']}")
    print(f"  Model: {test['model_name']}")
    print(f"  Version A: {test['version_a']}")
    print(f"  Version B: {test['version_b']}")
    print(f"  Traffic split: {test['traffic_split']*100}% to B")
    print(f"  Duration: {test['duration_days']} days")
    
    # Simulate routing
    print("\n--- Simulating Prediction Routing ---")
    for i in range(5):
        request_id = f"request_{i}"
        version_id, variant = ab_manager.route_prediction(
            model_name='random_forest',
            request_id=request_id
        )
        print(f"  Request {i}: routed to variant {variant} ({version_id})")
    
    # Check test status
    print("\n--- Test Status ---")
    status = ab_manager.check_test_status(test['test_id'])
    print(f"  Status: {status['status']}")
    print(f"  Elapsed days: {status['elapsed_days']}")
    print(f"  Remaining days: {status['remaining_days']}")
    
    # Create gradual rollout plan
    print("\n--- Gradual Rollout Plan ---")
    rollout = ab_manager.create_gradual_rollout(
        model_name='xgboost',
        new_version='v_new',
        strategy=RolloutStrategy.CANARY,
        initial_traffic=0.1,
        increment=0.2,
        increment_interval_hours=24
    )
    
    print(f"✓ Rollout plan created: {rollout['strategy']}")
    print(f"  Schedule ({len(rollout['schedule'])} steps):")
    for step in rollout['schedule']:
        print(f"    Step {step['step']}: {step['traffic_percentage']}% "
              f"after {step['delay_hours']}h")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("Automated Retraining Pipeline Examples")
    print("=" * 80)
    
    try:
        # Example 1: Check triggers
        example_check_triggers()
        
        # Example 2: Run retraining (commented out to avoid long execution)
        # Uncomment to actually run retraining
        # retraining_results = example_automated_retraining()
        
        # For demonstration, use mock results
        print("\n[Note: Using mock results for demonstration]")
        retraining_results = {
            'success': True,
            'elapsed_time_seconds': 3600,
            'training_results': {
                'models': {
                    'random_forest': {'roc_auc': 0.87, 'accuracy': 0.82},
                    'xgboost': {'roc_auc': 0.88, 'accuracy': 0.83},
                    'neural_network': {'roc_auc': 0.86, 'accuracy': 0.81}
                }
            },
            'registration_results': {
                'random_forest': 'v20250126_001',
                'xgboost': 'v20250126_002',
                'neural_network': 'v20250126_003'
            }
        }
        
        # Example 3: Evaluate models (commented out - requires actual models)
        # evaluation_results = example_model_evaluation(retraining_results)
        
        # For demonstration, use mock evaluation
        evaluation_results = {
            'success': True,
            'model_evaluations': {
                'random_forest': {
                    'new_metrics': {'roc_auc': 0.87},
                    'production_metrics': {'roc_auc': 0.82},
                    'comparison': {
                        'primary_metric_improvement_percent': 6.1
                    },
                    'recommendation': 'deploy'
                }
            },
            'summary': {
                'models_evaluated': 3,
                'models_recommended_for_deployment': 1,
                'models_requiring_manual_review': 1
            }
        }
        
        # Example 4: Promote models (commented out - requires actual models)
        # promotion_results = example_model_promotion(evaluation_results)
        
        # For demonstration, use mock promotion
        promotion_results = {
            'success': True,
            'promotion_results': {
                'random_forest': {
                    'promoted': True,
                    'version_id': 'v20250126_001',
                    'improvement_percent': 6.1
                }
            },
            'summary': {
                'models_promoted': 1,
                'models_requiring_review': 1,
                'models_not_promoted': 1,
                'promoted_models': [
                    {
                        'model_name': 'random_forest',
                        'version_id': 'v20250126_001',
                        'improvement_percent': 6.1
                    }
                ]
            }
        }
        
        # Example 5: Send notifications
        example_notifications(promotion_results)
        
        # Example 6: A/B testing
        example_ab_testing()
        
        print("\n" + "=" * 80)
        print("All examples completed!")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
