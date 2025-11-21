"""
Recommendation service for generating personalized health recommendations.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.models.recommendation import (
    Recommendation,
    RecommendationAdherence,
    RecommendationCategory,
    RecommendationPriority
)
from app.models.prediction import Prediction
from app.models.health_metric import HealthMetric
from app.models.assessment import Assessment

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for generating and managing personalized recommendations.
    
    Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
    """
    
    def __init__(self, db: Session):
        """
        Initialize recommendation service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def generate_recommendations(
        self,
        user_id: str,
        risk_factors: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> List[Recommendation]:
        """
        Generate personalized recommendations based on risk factors.
        
        Args:
            user_id: User ID
            risk_factors: Dictionary of risk factors and their importance
            current_metrics: Current health metrics
            
        Returns:
            List of generated recommendations
        """
        recommendations = []
        
        # Deactivate old recommendations
        self._deactivate_old_recommendations(user_id)
        
        # Generate recommendations for each category
        recommendations.extend(self._generate_diet_recommendations(user_id, risk_factors, current_metrics))
        recommendations.extend(self._generate_exercise_recommendations(user_id, risk_factors, current_metrics))
        recommendations.extend(self._generate_sleep_recommendations(user_id, risk_factors, current_metrics))
        recommendations.extend(self._generate_cognitive_recommendations(user_id, risk_factors, current_metrics))
        recommendations.extend(self._generate_social_recommendations(user_id, risk_factors, current_metrics))
        
        # Save to database
        for rec in recommendations:
            self.db.add(rec)
        
        self.db.commit()
        
        # Refresh all recommendations
        for rec in recommendations:
            self.db.refresh(rec)
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
        
        return recommendations
    
    def _deactivate_old_recommendations(self, user_id: str) -> None:
        """Deactivate old recommendations for a user."""
        self.db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.is_active == True
        ).update({"is_active": False, "last_updated": datetime.utcnow()})
        self.db.commit()
    
    def _generate_diet_recommendations(
        self,
        user_id: str,
        risk_factors: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> List[Recommendation]:
        """Generate diet-related recommendations."""
        recommendations = []
        
        # Mediterranean diet recommendation
        if risk_factors.get('cardiovascular_risk', 0) > 0.3 or risk_factors.get('inflammation', 0) > 0.3:
            rec = Recommendation(
                user_id=user_id,
                category=RecommendationCategory.DIET,
                priority=RecommendationPriority.HIGH,
                title="Adopt Mediterranean Diet",
                description="Follow a Mediterranean diet rich in fruits, vegetables, whole grains, fish, and olive oil. "
                           "This dietary pattern has been shown to reduce Alzheimer's risk by up to 53% and improve "
                           "cardiovascular health, which is closely linked to brain health.",
                research_citations=[
                    {
                        "title": "Mediterranean diet and risk of Alzheimer's disease",
                        "authors": "Scarmeas N, et al.",
                        "journal": "Annals of Neurology",
                        "year": 2006,
                        "doi": "10.1002/ana.20854",
                        "summary": "Higher adherence to Mediterranean diet associated with reduced AD risk"
                    }
                ],
                evidence_strength="strong",
                generated_from_risk_factors={"cardiovascular_risk": risk_factors.get('cardiovascular_risk', 0)},
                target_metrics=["cholesterol", "blood_pressure", "inflammation_markers"]
            )
            recommendations.append(rec)
        
        # Omega-3 fatty acids
        if risk_factors.get('cognitive_decline', 0) > 0.2:
            rec = Recommendation(
                user_id=user_id,
                category=RecommendationCategory.DIET,
                priority=RecommendationPriority.MEDIUM,
                title="Increase Omega-3 Fatty Acids",
                description="Consume fatty fish (salmon, mackerel, sardines) 2-3 times per week or consider "
                           "omega-3 supplements. DHA and EPA support brain health and may slow cognitive decline.",
                research_citations=[
                    {
                        "title": "Omega-3 fatty acids and cognitive health",
                        "authors": "Yurko-Mauro K, et al.",
                        "journal": "Alzheimer's & Dementia",
                        "year": 2010,
                        "doi": "10.1016/j.jalz.2010.02.006",
                        "summary": "DHA supplementation improved memory function in older adults"
                    }
                ],
                evidence_strength="moderate",
                generated_from_risk_factors={"cognitive_decline": risk_factors.get('cognitive_decline', 0)},
                target_metrics=["cognitive_score", "memory_function"]
            )
            recommendations.append(rec)
        
        # Reduce sugar intake
        if current_metrics.get('glucose', 0) > 100 or risk_factors.get('diabetes_risk', 0) > 0.3:
            rec = Recommendation(
                user_id=user_id,
                category=RecommendationCategory.DIET,
                priority=RecommendationPriority.HIGH,
                title="Reduce Added Sugar Intake",
                description="Limit added sugars to less than 25g per day. High blood sugar and insulin resistance "
                           "are linked to increased Alzheimer's risk. Focus on whole foods and avoid processed foods.",
                research_citations=[
                    {
                        "title": "Diabetes and Alzheimer's disease risk",
                        "authors": "Biessels GJ, et al.",
                        "journal": "Nature Reviews Neuroscience",
                        "year": 2014,
                        "doi": "10.1038/nrn3801",
                        "summary": "Type 2 diabetes doubles the risk of Alzheimer's disease"
                    }
                ],
                evidence_strength="strong",
                generated_from_risk_factors={"diabetes_risk": risk_factors.get('diabetes_risk', 0)},
                target_metrics=["glucose", "insulin_sensitivity", "hba1c"]
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_exercise_recommendations(
        self,
        user_id: str,
        risk_factors: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> List[Recommendation]:
        """Generate exercise-related recommendations."""
        recommendations = []
        
        # Aerobic exercise
        if current_metrics.get('physical_activity_minutes', 0) < 150:
            rec = Recommendation(
                user_id=user_id,
                category=RecommendationCategory.EXERCISE,
                priority=RecommendationPriority.HIGH,
                title="Regular Aerobic Exercise",
                description="Engage in at least 150 minutes of moderate-intensity aerobic exercise per week. "
                           "Activities like brisk walking, swimming, or cycling improve blood flow to the brain "
                           "and may reduce Alzheimer's risk by 45%.",
                research_citations=[
                    {
                        "title": "Physical activity and Alzheimer's disease",
                        "authors": "Hamer M, Chida Y",
                        "journal": "Psychological Medicine",
                        "year": 2009,
                        "doi": "10.1017/S0033291708003681",
                        "summary": "Physical activity associated with 45% reduced risk of Alzheimer's"
                    }
                ],
                evidence_strength="strong",
                generated_from_risk_factors={"sedentary_lifestyle": risk_factors.get('sedentary_lifestyle', 0)},
                target_metrics=["physical_activity_minutes", "cardiovascular_fitness", "hippocampal_volume"]
            )
            recommendations.append(rec)
        
        # Strength training
        rec = Recommendation(
            user_id=user_id,
            category=RecommendationCategory.EXERCISE,
            priority=RecommendationPriority.MEDIUM,
            title="Incorporate Strength Training",
            description="Add resistance training 2-3 times per week. Strength training improves insulin sensitivity, "
                       "reduces inflammation, and supports overall brain health.",
            research_citations=[
                {
                    "title": "Resistance training and cognitive function",
                    "authors": "Liu-Ambrose T, et al.",
                    "journal": "Archives of Internal Medicine",
                    "year": 2010,
                    "doi": "10.1001/archinternmed.2010.379",
                    "summary": "Resistance training improved executive functions in older women"
                }
            ],
            evidence_strength="moderate",
            generated_from_risk_factors={"muscle_weakness": risk_factors.get('muscle_weakness', 0)},
            target_metrics=["muscle_strength", "insulin_sensitivity", "cognitive_score"]
        )
        recommendations.append(rec)
        
        return recommendations
    
    def _generate_sleep_recommendations(
        self,
        user_id: str,
        risk_factors: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> List[Recommendation]:
        """Generate sleep-related recommendations."""
        recommendations = []
        
        # Sleep duration
        if current_metrics.get('sleep_hours', 0) < 7 or current_metrics.get('sleep_hours', 0) > 9:
            rec = Recommendation(
                user_id=user_id,
                category=RecommendationCategory.SLEEP,
                priority=RecommendationPriority.HIGH,
                title="Optimize Sleep Duration",
                description="Aim for 7-8 hours of quality sleep per night. Both insufficient and excessive sleep "
                           "are associated with increased Alzheimer's risk. Sleep is crucial for clearing amyloid-beta "
                           "from the brain.",
                research_citations=[
                    {
                        "title": "Sleep and Alzheimer's disease pathology",
                        "authors": "Ju YE, et al.",
                        "journal": "JAMA Neurology",
                        "year": 2013,
                        "doi": "10.1001/jamaneurol.2013.2334",
                        "summary": "Poor sleep quality associated with increased amyloid deposition"
                    }
                ],
                evidence_strength="strong",
                generated_from_risk_factors={"poor_sleep": risk_factors.get('poor_sleep', 0)},
                target_metrics=["sleep_hours", "sleep_quality", "amyloid_beta_levels"]
            )
            recommendations.append(rec)
        
        # Sleep quality
        if current_metrics.get('sleep_quality', 0) < 7:
            rec = Recommendation(
                user_id=user_id,
                category=RecommendationCategory.SLEEP,
                priority=RecommendationPriority.MEDIUM,
                title="Improve Sleep Quality",
                description="Establish a consistent sleep schedule, create a dark and cool sleeping environment, "
                           "and avoid screens 1 hour before bed. Consider evaluation for sleep apnea if you snore.",
                research_citations=[
                    {
                        "title": "Sleep apnea and Alzheimer's disease",
                        "authors": "Osorio RS, et al.",
                        "journal": "Neurology",
                        "year": 2015,
                        "doi": "10.1212/WNL.0000000000001566",
                        "summary": "Sleep apnea associated with earlier age of cognitive impairment"
                    }
                ],
                evidence_strength="moderate",
                generated_from_risk_factors={"sleep_apnea_risk": risk_factors.get('sleep_apnea_risk', 0)},
                target_metrics=["sleep_quality", "sleep_efficiency", "cognitive_score"]
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_cognitive_recommendations(
        self,
        user_id: str,
        risk_factors: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> List[Recommendation]:
        """Generate cognitive activity recommendations."""
        recommendations = []
        
        # Cognitive training
        if risk_factors.get('cognitive_decline', 0) > 0.2:
            rec = Recommendation(
                user_id=user_id,
                category=RecommendationCategory.COGNITIVE,
                priority=RecommendationPriority.HIGH,
                title="Engage in Cognitive Training",
                description="Complete cognitive training exercises 3-4 times per week. Focus on memory, attention, "
                           "and problem-solving tasks. Use the app's built-in cognitive training games.",
                research_citations=[
                    {
                        "title": "Cognitive training and cognitive function",
                        "authors": "Rebok GW, et al.",
                        "journal": "Journal of the American Geriatrics Society",
                        "year": 2014,
                        "doi": "10.1111/jgs.12607",
                        "summary": "Cognitive training showed long-term benefits for cognitive function"
                    }
                ],
                evidence_strength="moderate",
                generated_from_risk_factors={"cognitive_decline": risk_factors.get('cognitive_decline', 0)},
                target_metrics=["mmse_score", "moca_score", "memory_score"]
            )
            recommendations.append(rec)
        
        # Lifelong learning
        rec = Recommendation(
            user_id=user_id,
            category=RecommendationCategory.COGNITIVE,
            priority=RecommendationPriority.MEDIUM,
            title="Pursue Lifelong Learning",
            description="Engage in mentally stimulating activities like reading, learning a new language, "
                       "playing musical instruments, or taking classes. Cognitive reserve helps protect against dementia.",
                research_citations=[
                    {
                        "title": "Education and cognitive reserve",
                        "authors": "Stern Y",
                        "journal": "Lancet Neurology",
                        "year": 2012,
                        "doi": "10.1016/S1474-4422(12)70191-6",
                        "summary": "Higher education and cognitive activity build cognitive reserve"
                    }
                ],
                evidence_strength="strong",
                generated_from_risk_factors={"low_cognitive_reserve": risk_factors.get('low_cognitive_reserve', 0)},
                target_metrics=["cognitive_reserve", "cognitive_score"]
        )
        recommendations.append(rec)
        
        return recommendations
    
    def _generate_social_recommendations(
        self,
        user_id: str,
        risk_factors: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> List[Recommendation]:
        """Generate social engagement recommendations."""
        recommendations = []
        
        # Social interaction
        if current_metrics.get('social_interactions_per_week', 0) < 3:
            rec = Recommendation(
                user_id=user_id,
                category=RecommendationCategory.SOCIAL,
                priority=RecommendationPriority.HIGH,
                title="Increase Social Engagement",
                description="Maintain regular social interactions with family and friends. Aim for meaningful "
                           "social contact at least 3-4 times per week. Join clubs, volunteer, or participate "
                           "in group activities.",
                research_citations=[
                    {
                        "title": "Social engagement and dementia risk",
                        "authors": "Fratiglioni L, et al.",
                        "journal": "Lancet Neurology",
                        "year": 2004,
                        "doi": "10.1016/S1474-4422(04)00850-2",
                        "summary": "Social networks and activities reduce dementia risk"
                    }
                ],
                evidence_strength="strong",
                generated_from_risk_factors={"social_isolation": risk_factors.get('social_isolation', 0)},
                target_metrics=["social_interactions_per_week", "loneliness_score", "cognitive_score"]
            )
            recommendations.append(rec)
        
        # Community involvement
        rec = Recommendation(
            user_id=user_id,
            category=RecommendationCategory.SOCIAL,
            priority=RecommendationPriority.MEDIUM,
            title="Join Community Activities",
            description="Participate in community groups, volunteer work, or support groups. Social purpose "
                       "and engagement provide cognitive stimulation and emotional support.",
                research_citations=[
                    {
                        "title": "Social activities and cognitive function",
                        "authors": "Wang HX, et al.",
                        "journal": "American Journal of Epidemiology",
                        "year": 2002,
                        "doi": "10.1093/aje/kwf017",
                        "summary": "Leisure activities reduce dementia risk"
                    }
                ],
                evidence_strength="moderate",
                generated_from_risk_factors={"lack_of_purpose": risk_factors.get('lack_of_purpose', 0)},
                target_metrics=["social_engagement_score", "quality_of_life"]
        )
        recommendations.append(rec)
        
        return recommendations
    
    def get_user_recommendations(
        self,
        user_id: str,
        category: Optional[RecommendationCategory] = None,
        active_only: bool = True
    ) -> List[Recommendation]:
        """
        Get recommendations for a user.
        
        Args:
            user_id: User ID
            category: Optional category filter
            active_only: Only return active recommendations
            
        Returns:
            List of recommendations
        """
        query = self.db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        )
        
        if category:
            query = query.filter(Recommendation.category == category)
        
        if active_only:
            query = query.filter(Recommendation.is_active == True)
        
        return query.order_by(
            Recommendation.priority.desc(),
            Recommendation.generated_at.desc()
        ).all()
    
    def track_adherence(
        self,
        recommendation_id: str,
        user_id: str,
        completed: bool,
        notes: Optional[str] = None,
        outcome_metrics: Optional[Dict] = None
    ) -> RecommendationAdherence:
        """
        Track user adherence to a recommendation.
        
        Args:
            recommendation_id: Recommendation ID
            user_id: User ID
            completed: Whether the recommendation was followed
            notes: Optional notes
            outcome_metrics: Optional outcome metrics
            
        Returns:
            Adherence record
        """
        adherence = RecommendationAdherence(
            recommendation_id=recommendation_id,
            user_id=user_id,
            date=datetime.utcnow(),
            completed=completed,
            notes=notes,
            outcome_metrics=outcome_metrics
        )
        
        self.db.add(adherence)
        self.db.commit()
        self.db.refresh(adherence)
        
        # Update adherence score
        self._update_adherence_score(recommendation_id)
        
        return adherence
    
    def _update_adherence_score(self, recommendation_id: str) -> None:
        """Update adherence score for a recommendation."""
        # Get last 30 days of adherence records
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        adherence_records = self.db.query(RecommendationAdherence).filter(
            RecommendationAdherence.recommendation_id == recommendation_id,
            RecommendationAdherence.date >= thirty_days_ago
        ).all()
        
        if adherence_records:
            completed_count = sum(1 for r in adherence_records if r.completed)
            adherence_score = completed_count / len(adherence_records)
            
            # Update recommendation
            recommendation = self.db.query(Recommendation).filter(
                Recommendation.id == recommendation_id
            ).first()
            
            if recommendation:
                recommendation.adherence_score = adherence_score
                recommendation.last_updated = datetime.utcnow()
                self.db.commit()
    
    def get_adherence_stats(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Get adherence statistics for a user.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Dictionary with adherence statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        adherence_records = self.db.query(RecommendationAdherence).filter(
            RecommendationAdherence.user_id == user_id,
            RecommendationAdherence.date >= start_date
        ).all()
        
        if not adherence_records:
            return {
                "total_records": 0,
                "completed": 0,
                "adherence_rate": 0.0,
                "by_category": {}
            }
        
        completed = sum(1 for r in adherence_records if r.completed)
        adherence_rate = completed / len(adherence_records)
        
        # Calculate by category
        by_category = {}
        for record in adherence_records:
            rec = self.db.query(Recommendation).filter(
                Recommendation.id == record.recommendation_id
            ).first()
            
            if rec:
                category = rec.category.value
                if category not in by_category:
                    by_category[category] = {"total": 0, "completed": 0}
                
                by_category[category]["total"] += 1
                if record.completed:
                    by_category[category]["completed"] += 1
        
        # Calculate rates
        for category in by_category:
            total = by_category[category]["total"]
            completed = by_category[category]["completed"]
            by_category[category]["adherence_rate"] = completed / total if total > 0 else 0.0
        
        return {
            "total_records": len(adherence_records),
            "completed": completed,
            "adherence_rate": adherence_rate,
            "by_category": by_category
        }
    
    def update_recommendations_based_on_progress(
        self,
        user_id: str,
        new_metrics: Dict[str, float]
    ) -> List[Recommendation]:
        """
        Update recommendations based on user progress.
        
        Args:
            user_id: User ID
            new_metrics: New health metrics
            
        Returns:
            List of updated/new recommendations
        """
        # Get latest prediction for risk factors
        latest_prediction = self.db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).order_by(Prediction.prediction_date.desc()).first()
        
        if not latest_prediction:
            logger.warning(f"No prediction found for user {user_id}")
            return []
        
        # Extract risk factors from feature importance
        risk_factors = latest_prediction.feature_importance
        
        # Generate new recommendations
        return self.generate_recommendations(user_id, risk_factors, new_metrics)
