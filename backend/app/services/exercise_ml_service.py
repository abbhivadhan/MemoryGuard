"""
Service for integrating exercise performance data with ML predictions.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import numpy as np
import logging

from app.models.exercise import ExercisePerformance, ExerciseType
from app.models.health_metric import HealthMetric, MetricType, MetricSource
from app.models.user import User

logger = logging.getLogger(__name__)


class ExerciseMLService:
    """
    Service for analyzing exercise performance and integrating with ML predictions.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_cognitive_score_from_exercises(
        self,
        user_id: str,
        days: int = 30
    ) -> Optional[float]:
        """
        Calculate an aggregate cognitive score based on exercise performance.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Cognitive score (0-100) or None if insufficient data
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        performances = self.db.query(ExercisePerformance).filter(
            ExercisePerformance.user_id == user_id,
            ExercisePerformance.created_at >= since_date
        ).all()
        
        if not performances:
            return None
        
        # Calculate weighted average by exercise type
        type_scores = {}
        type_weights = {
            ExerciseType.MEMORY_GAME: 0.4,
            ExerciseType.PATTERN_RECOGNITION: 0.3,
            ExerciseType.PROBLEM_SOLVING: 0.3
        }
        
        for perf in performances:
            exercise = perf.exercise
            if exercise and exercise.type:
                if exercise.type not in type_scores:
                    type_scores[exercise.type] = []
                
                # Normalize score to 0-100
                normalized_score = (perf.score / perf.max_score) * 100
                type_scores[exercise.type].append(normalized_score)
        
        # Calculate weighted average
        total_score = 0
        total_weight = 0
        
        for ex_type, scores in type_scores.items():
            if ex_type in type_weights:
                avg_score = sum(scores) / len(scores)
                weight = type_weights[ex_type]
                total_score += avg_score * weight
                total_weight += weight
        
        if total_weight == 0:
            return None
        
        return total_score / total_weight
    
    def create_health_metric_from_exercises(
        self,
        user_id: str,
        days: int = 30
    ) -> Optional[HealthMetric]:
        """
        Create a health metric entry based on exercise performance.
        This allows exercise data to be used in ML predictions.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Created HealthMetric or None
        """
        cognitive_score = self.calculate_cognitive_score_from_exercises(user_id, days)
        
        if cognitive_score is None:
            return None
        
        # Create a health metric for cognitive function
        metric = HealthMetric(
            user_id=user_id,
            type=MetricType.COGNITIVE,
            name="Exercise-Based Cognitive Score",
            value=cognitive_score,
            unit="score",
            source=MetricSource.ASSESSMENT,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        
        logger.info(f"Created cognitive health metric from exercises for user {user_id}: {cognitive_score}")
        
        return metric
    
    def analyze_performance_trends(
        self,
        user_id: str,
        exercise_id: Optional[str] = None,
        days: int = 90
    ) -> Dict:
        """
        Analyze performance trends over time.
        
        Args:
            user_id: User ID
            exercise_id: Optional specific exercise ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(ExercisePerformance).filter(
            ExercisePerformance.user_id == user_id,
            ExercisePerformance.created_at >= since_date
        )
        
        if exercise_id:
            query = query.filter(ExercisePerformance.exercise_id == exercise_id)
        
        performances = query.order_by(ExercisePerformance.created_at).all()
        
        if len(performances) < 2:
            return {
                "trend": "insufficient_data",
                "slope": 0,
                "improvement_rate": 0,
                "consistency": 0
            }
        
        # Calculate trend using linear regression
        scores = [(perf.score / perf.max_score) * 100 for perf in performances]
        x = np.arange(len(scores))
        
        # Simple linear regression
        x_mean = np.mean(x)
        y_mean = np.mean(scores)
        
        numerator = np.sum((x - x_mean) * (scores - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine trend
        if slope > 1:
            trend = "improving"
        elif slope < -1:
            trend = "declining"
        else:
            trend = "stable"
        
        # Calculate consistency (inverse of standard deviation)
        std_dev = np.std(scores)
        consistency = max(0, 100 - std_dev)
        
        # Calculate improvement rate
        if len(scores) >= 4:
            mid = len(scores) // 2
            first_half_avg = np.mean(scores[:mid])
            second_half_avg = np.mean(scores[mid:])
            
            if first_half_avg > 0:
                improvement_rate = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            else:
                improvement_rate = 0
        else:
            improvement_rate = 0
        
        return {
            "trend": trend,
            "slope": float(slope),
            "improvement_rate": float(improvement_rate),
            "consistency": float(consistency),
            "average_score": float(np.mean(scores)),
            "recent_average": float(np.mean(scores[-5:])) if len(scores) >= 5 else float(np.mean(scores)),
            "total_sessions": len(performances)
        }
    
    def get_cognitive_decline_indicators(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Identify potential cognitive decline indicators from exercise performance.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with decline indicators
        """
        trends = self.analyze_performance_trends(user_id, days=days)
        
        indicators = {
            "has_concerns": False,
            "concerns": [],
            "recommendations": []
        }
        
        # Check for declining trend
        if trends["trend"] == "declining" and trends["slope"] < -2:
            indicators["has_concerns"] = True
            indicators["concerns"].append("Declining performance trend detected")
            indicators["recommendations"].append("Consider scheduling a cognitive assessment")
        
        # Check for low recent performance
        if trends.get("recent_average", 100) < 50:
            indicators["has_concerns"] = True
            indicators["concerns"].append("Recent performance below expected levels")
            indicators["recommendations"].append("Try easier difficulty levels to build confidence")
        
        # Check for inconsistency
        if trends.get("consistency", 100) < 50:
            indicators["has_concerns"] = True
            indicators["concerns"].append("Inconsistent performance patterns")
            indicators["recommendations"].append("Establish a regular exercise routine")
        
        # Check for low engagement
        if trends.get("total_sessions", 0) < 5:
            indicators["concerns"].append("Low engagement with cognitive exercises")
            indicators["recommendations"].append("Try to complete at least 3-4 exercises per week")
        
        return indicators
    
    def get_exercise_recommendations(
        self,
        user_id: str
    ) -> List[Dict]:
        """
        Get personalized exercise recommendations based on performance.
        
        Args:
            user_id: User ID
            
        Returns:
            List of exercise recommendations
        """
        recommendations = []
        
        # Analyze performance by type
        for ex_type in ExerciseType:
            performances = self.db.query(ExercisePerformance).join(
                ExercisePerformance.exercise
            ).filter(
                ExercisePerformance.user_id == user_id,
                ExercisePerformance.exercise.has(type=ex_type)
            ).order_by(desc(ExercisePerformance.created_at)).limit(10).all()
            
            if not performances:
                recommendations.append({
                    "type": ex_type.value,
                    "reason": "No recent activity",
                    "suggestion": f"Try some {ex_type.value.replace('_', ' ')} exercises to diversify your training"
                })
            else:
                avg_score = sum(p.score / p.max_score for p in performances) / len(performances)
                
                if avg_score < 0.5:
                    recommendations.append({
                        "type": ex_type.value,
                        "reason": "Low performance",
                        "suggestion": f"Practice more {ex_type.value.replace('_', ' ')} exercises at easier difficulty"
                    })
                elif avg_score > 0.9:
                    recommendations.append({
                        "type": ex_type.value,
                        "reason": "High performance",
                        "suggestion": f"Challenge yourself with harder {ex_type.value.replace('_', ' ')} exercises"
                    })
        
        return recommendations
