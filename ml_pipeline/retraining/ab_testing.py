"""
A/B Testing Manager

This module provides A/B testing capabilities for gradual model rollout including:
- Traffic splitting between model versions
- Performance tracking for each version
- Automatic winner selection
- Gradual rollout strategies
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import hashlib

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import get_logger
from ml_pipeline.models.model_registry import ModelRegistry
from ml_pipeline.data_storage.database import get_db_session
from ml_pipeline.data_storage.models import AuditLog

logger = get_logger(__name__)


class RolloutStrategy(Enum):
    """Rollout strategy types"""
    IMMEDIATE = "immediate"  # 100% traffic to new model
    CANARY = "canary"  # Small percentage, then full
    GRADUAL = "gradual"  # Gradually increase percentage
    AB_TEST = "ab_test"  # 50/50 split for testing


class ABTestingManager:
    """
    Manage A/B testing and gradual rollout of model versions
    
    Implements:
    - A/B testing capability for gradual rollout (Requirement 11.7)
    - Traffic splitting
    - Performance monitoring
    - Automatic winner selection
    """
    
    def __init__(self):
        """Initialize A/B testing manager"""
        self.model_registry = ModelRegistry(storage_path=settings.MODELS_PATH)
        self.active_tests = {}  # In-memory storage of active tests
        
        logger.info("Initialized ABTestingManager")
    
    def create_ab_test(
        self,
        model_name: str,
        version_a: str,
        version_b: str,
        traffic_split: float = 0.5,
        duration_days: int = 7,
        success_metric: str = 'roc_auc',
        min_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Create an A/B test between two model versions
        
        Implements Requirement 11.7: Support gradual rollout
        
        Args:
            model_name: Name of the model
            version_a: Version ID for variant A (typically production)
            version_b: Version ID for variant B (typically new model)
            traffic_split: Percentage of traffic to variant B (0.0 to 1.0)
            duration_days: Duration of the test in days
            success_metric: Metric to use for determining winner
            min_samples: Minimum samples required before declaring winner
            
        Returns:
            Dictionary with A/B test configuration
        """
        logger.info(
            f"Creating A/B test for {model_name}: "
            f"{version_a} vs {version_b} ({traffic_split*100}% to B)"
        )
        
        test_id = self._generate_test_id(model_name, version_a, version_b)
        
        test_config = {
            'test_id': test_id,
            'model_name': model_name,
            'version_a': version_a,
            'version_b': version_b,
            'traffic_split': traffic_split,
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(days=duration_days),
            'duration_days': duration_days,
            'success_metric': success_metric,
            'min_samples': min_samples,
            'status': 'active',
            'results': {
                'version_a': {'samples': 0, 'metrics': {}},
                'version_b': {'samples': 0, 'metrics': {}}
            }
        }
        
        # Store test configuration
        self.active_tests[test_id] = test_config
        
        # Log test creation
        self._log_test_event(
            test_id=test_id,
            event='test_created',
            details=test_config
        )
        
        logger.info(f"A/B test created: {test_id}")
        
        return test_config
    
    def route_prediction(
        self,
        model_name: str,
        request_id: str
    ) -> Tuple[str, str]:
        """
        Route a prediction request to the appropriate model version
        
        Args:
            model_name: Name of the model
            request_id: Unique identifier for the request (for consistent routing)
            
        Returns:
            Tuple of (version_id, variant) where variant is 'A' or 'B'
        """
        # Check if there's an active A/B test for this model
        active_test = self._get_active_test(model_name)
        
        if not active_test:
            # No active test, use production model
            prod_model = self.model_registry.get_production_model(model_name)
            if prod_model:
                return prod_model['version_id'], 'production'
            else:
                logger.warning(f"No production model found for {model_name}")
                return None, None
        
        # Determine which variant to use based on traffic split
        variant = self._assign_variant(
            request_id,
            active_test['traffic_split']
        )
        
        if variant == 'A':
            return active_test['version_a'], 'A'
        else:
            return active_test['version_b'], 'B'
    
    def record_prediction_result(
        self,
        model_name: str,
        version_id: str,
        variant: str,
        prediction: Any,
        actual: Optional[Any] = None,
        metrics: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        Record the result of a prediction for A/B test tracking
        
        Args:
            model_name: Name of the model
            version_id: Version ID that made the prediction
            variant: Variant identifier ('A' or 'B')
            prediction: Model prediction
            actual: Actual outcome (if available)
            metrics: Computed metrics for this prediction
            
        Returns:
            True if recorded successfully
        """
        active_test = self._get_active_test(model_name)
        
        if not active_test:
            # No active test, nothing to record
            return False
        
        try:
            # Update sample count
            variant_key = f'version_{variant.lower()}'
            active_test['results'][variant_key]['samples'] += 1
            
            # Update metrics if provided
            if metrics:
                for metric, value in metrics.items():
                    if metric not in active_test['results'][variant_key]['metrics']:
                        active_test['results'][variant_key]['metrics'][metric] = []
                    
                    active_test['results'][variant_key]['metrics'][metric].append(value)
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording prediction result: {e}", exc_info=True)
            return False
    
    def check_test_status(
        self,
        test_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of an A/B test
        
        Args:
            test_id: Test identifier
            
        Returns:
            Dictionary with test status and results
        """
        if test_id not in self.active_tests:
            return {
                'found': False,
                'error': 'Test not found'
            }
        
        test = self.active_tests[test_id]
        
        # Calculate current metrics
        results_a = test['results']['version_a']
        results_b = test['results']['version_b']
        
        # Compute average metrics
        avg_metrics_a = self._compute_average_metrics(results_a['metrics'])
        avg_metrics_b = self._compute_average_metrics(results_b['metrics'])
        
        # Check if test should end
        should_end, reason = self._should_end_test(test)
        
        # Determine winner if test is complete
        winner = None
        if should_end:
            winner = self._determine_winner(
                avg_metrics_a,
                avg_metrics_b,
                test['success_metric']
            )
        
        status = {
            'found': True,
            'test_id': test_id,
            'model_name': test['model_name'],
            'status': test['status'],
            'start_time': test['start_time'].isoformat(),
            'end_time': test['end_time'].isoformat(),
            'elapsed_days': (datetime.now() - test['start_time']).days,
            'remaining_days': (test['end_time'] - datetime.now()).days,
            'should_end': should_end,
            'end_reason': reason,
            'winner': winner,
            'results': {
                'version_a': {
                    'version_id': test['version_a'],
                    'samples': results_a['samples'],
                    'metrics': avg_metrics_a
                },
                'version_b': {
                    'version_id': test['version_b'],
                    'samples': results_b['samples'],
                    'metrics': avg_metrics_b
                }
            }
        }
        
        return status
    
    def end_test(
        self,
        test_id: str,
        promote_winner: bool = True
    ) -> Dict[str, Any]:
        """
        End an A/B test and optionally promote the winner
        
        Args:
            test_id: Test identifier
            promote_winner: Whether to promote the winning version to production
            
        Returns:
            Dictionary with test results and promotion status
        """
        logger.info(f"Ending A/B test: {test_id}")
        
        if test_id not in self.active_tests:
            return {
                'success': False,
                'error': 'Test not found'
            }
        
        test = self.active_tests[test_id]
        
        # Get final status
        status = self.check_test_status(test_id)
        
        # Mark test as complete
        test['status'] = 'completed'
        test['completed_at'] = datetime.now()
        
        result = {
            'success': True,
            'test_id': test_id,
            'model_name': test['model_name'],
            'winner': status['winner'],
            'results': status['results']
        }
        
        # Promote winner if requested
        if promote_winner and status['winner']:
            winner_version = (
                test['version_b'] if status['winner'] == 'B'
                else test['version_a']
            )
            
            promotion_success = self.model_registry.promote_to_production(
                model_name=test['model_name'],
                version_id=winner_version,
                user_id='ab_testing'
            )
            
            result['promoted'] = promotion_success
            result['promoted_version'] = winner_version if promotion_success else None
            
            if promotion_success:
                logger.info(
                    f"Promoted winner {winner_version} to production for {test['model_name']}"
                )
        else:
            result['promoted'] = False
        
        # Log test completion
        self._log_test_event(
            test_id=test_id,
            event='test_completed',
            details=result
        )
        
        # Remove from active tests
        del self.active_tests[test_id]
        
        logger.info(f"A/B test {test_id} completed")
        
        return result
    
    def create_gradual_rollout(
        self,
        model_name: str,
        new_version: str,
        strategy: RolloutStrategy = RolloutStrategy.CANARY,
        initial_traffic: float = 0.1,
        increment: float = 0.2,
        increment_interval_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Create a gradual rollout plan for a new model version
        
        Implements Requirement 11.7: Support gradual rollout
        
        Args:
            model_name: Name of the model
            new_version: New version ID to roll out
            strategy: Rollout strategy
            initial_traffic: Initial traffic percentage to new version
            increment: Traffic increment per step
            increment_interval_hours: Hours between increments
            
        Returns:
            Dictionary with rollout plan
        """
        logger.info(
            f"Creating gradual rollout for {model_name} v{new_version} "
            f"using {strategy.value} strategy"
        )
        
        # Get current production version
        prod_model = self.model_registry.get_production_model(model_name)
        
        if not prod_model:
            logger.warning(f"No production model found for {model_name}")
            current_version = None
        else:
            current_version = prod_model['version_id']
        
        # Generate rollout schedule
        schedule = self._generate_rollout_schedule(
            strategy=strategy,
            initial_traffic=initial_traffic,
            increment=increment,
            increment_interval_hours=increment_interval_hours
        )
        
        rollout_plan = {
            'model_name': model_name,
            'current_version': current_version,
            'new_version': new_version,
            'strategy': strategy.value,
            'schedule': schedule,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        logger.info(f"Gradual rollout plan created with {len(schedule)} steps")
        
        return rollout_plan
    
    def _generate_test_id(
        self,
        model_name: str,
        version_a: str,
        version_b: str
    ) -> str:
        """Generate unique test ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"abtest_{model_name}_{timestamp}"
    
    def _get_active_test(
        self,
        model_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get active A/B test for a model"""
        for test_id, test in self.active_tests.items():
            if test['model_name'] == model_name and test['status'] == 'active':
                return test
        return None
    
    def _assign_variant(
        self,
        request_id: str,
        traffic_split: float
    ) -> str:
        """
        Assign a variant based on request ID and traffic split
        
        Uses consistent hashing to ensure same request always gets same variant
        
        Args:
            request_id: Unique request identifier
            traffic_split: Percentage of traffic to variant B
            
        Returns:
            'A' or 'B'
        """
        # Use hash of request_id for consistent assignment
        hash_value = int(hashlib.md5(request_id.encode()).hexdigest(), 16)
        normalized = (hash_value % 10000) / 10000.0
        
        return 'B' if normalized < traffic_split else 'A'
    
    def _compute_average_metrics(
        self,
        metrics: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """Compute average of metrics"""
        avg_metrics = {}
        
        for metric, values in metrics.items():
            if values:
                avg_metrics[metric] = sum(values) / len(values)
            else:
                avg_metrics[metric] = 0.0
        
        return avg_metrics
    
    def _should_end_test(
        self,
        test: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if a test should end
        
        Returns:
            Tuple of (should_end, reason)
        """
        # Check if duration has elapsed
        if datetime.now() >= test['end_time']:
            return True, 'duration_elapsed'
        
        # Check if minimum samples reached
        samples_a = test['results']['version_a']['samples']
        samples_b = test['results']['version_b']['samples']
        
        if samples_a < test['min_samples'] or samples_b < test['min_samples']:
            return False, None
        
        # Check for statistical significance (simplified)
        # In production, would use proper statistical tests
        metrics_a = self._compute_average_metrics(
            test['results']['version_a']['metrics']
        )
        metrics_b = self._compute_average_metrics(
            test['results']['version_b']['metrics']
        )
        
        success_metric = test['success_metric']
        
        if success_metric in metrics_a and success_metric in metrics_b:
            diff = abs(metrics_a[success_metric] - metrics_b[success_metric])
            
            # If difference is > 10%, we have a clear winner
            if diff > 0.1:
                return True, 'clear_winner'
        
        return False, None
    
    def _determine_winner(
        self,
        metrics_a: Dict[str, float],
        metrics_b: Dict[str, float],
        success_metric: str
    ) -> Optional[str]:
        """
        Determine the winner of an A/B test
        
        Args:
            metrics_a: Metrics for variant A
            metrics_b: Metrics for variant B
            success_metric: Metric to use for comparison
            
        Returns:
            'A', 'B', or None if tie
        """
        if success_metric not in metrics_a or success_metric not in metrics_b:
            logger.warning(f"Success metric {success_metric} not found in results")
            return None
        
        value_a = metrics_a[success_metric]
        value_b = metrics_b[success_metric]
        
        if value_b > value_a:
            return 'B'
        elif value_a > value_b:
            return 'A'
        else:
            return None  # Tie
    
    def _generate_rollout_schedule(
        self,
        strategy: RolloutStrategy,
        initial_traffic: float,
        increment: float,
        increment_interval_hours: int
    ) -> List[Dict[str, Any]]:
        """Generate rollout schedule based on strategy"""
        schedule = []
        
        if strategy == RolloutStrategy.IMMEDIATE:
            schedule.append({
                'step': 1,
                'traffic_percentage': 100.0,
                'delay_hours': 0
            })
        
        elif strategy == RolloutStrategy.CANARY:
            # Start with small percentage, then jump to 100%
            schedule.append({
                'step': 1,
                'traffic_percentage': initial_traffic * 100,
                'delay_hours': 0
            })
            schedule.append({
                'step': 2,
                'traffic_percentage': 100.0,
                'delay_hours': increment_interval_hours
            })
        
        elif strategy == RolloutStrategy.GRADUAL:
            # Gradually increase traffic
            current_traffic = initial_traffic
            step = 1
            
            while current_traffic < 1.0:
                schedule.append({
                    'step': step,
                    'traffic_percentage': current_traffic * 100,
                    'delay_hours': (step - 1) * increment_interval_hours
                })
                current_traffic = min(current_traffic + increment, 1.0)
                step += 1
            
            # Final step at 100%
            schedule.append({
                'step': step,
                'traffic_percentage': 100.0,
                'delay_hours': (step - 1) * increment_interval_hours
            })
        
        elif strategy == RolloutStrategy.AB_TEST:
            # 50/50 split
            schedule.append({
                'step': 1,
                'traffic_percentage': 50.0,
                'delay_hours': 0
            })
        
        return schedule
    
    def _log_test_event(
        self,
        test_id: str,
        event: str,
        details: Dict[str, Any]
    ):
        """Log A/B test event to audit log"""
        try:
            with get_db_session() as db:
                audit_log = AuditLog(
                    timestamp=datetime.now(),
                    operation='ab_testing',
                    user_id='system',
                    resource_type='ab_test',
                    resource_id=test_id,
                    action=event,
                    details=details,
                    success=True
                )
                db.add(audit_log)
                db.commit()
        except Exception as e:
            logger.error(f"Error logging test event: {e}", exc_info=True)
