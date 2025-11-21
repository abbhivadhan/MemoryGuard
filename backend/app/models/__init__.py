"""
Models package initialization.
Import all models here to ensure they are registered with SQLAlchemy.
"""
from app.models.base import BaseModel
from app.models.user import User, APOEGenotype
from app.models.health_metric import HealthMetric, MetricType, MetricSource
from app.models.assessment import Assessment, AssessmentType, AssessmentStatus
from app.models.medication import Medication
from app.models.prediction import Prediction, RiskCategory
from app.models.emergency_contact import (
    EmergencyContact,
    CaregiverRelationship,
    ProviderRelationship,
    RelationshipType
)
from app.models.emergency_alert import EmergencyAlert
from app.models.reminder import Reminder, ReminderType, ReminderFrequency
from app.models.routine import DailyRoutine, RoutineCompletion
from app.models.face_recognition import FaceProfile
from app.models.exercise import Exercise, ExercisePerformance, ExerciseType, DifficultyLevel
from app.models.recommendation import (
    Recommendation,
    RecommendationAdherence,
    RecommendationCategory,
    RecommendationPriority
)
from app.models.imaging import MedicalImaging, ImagingModality, ImagingStatus
from app.models.provider import (
    Provider,
    ProviderAccess,
    ProviderAccessLog,
    ClinicalNote,
    ProviderType,
    AccessStatus
)
from app.models.community_post import CommunityPost, CommunityReply, ContentFlag

__all__ = [
    "BaseModel",
    "User",
    "APOEGenotype",
    "HealthMetric",
    "MetricType",
    "MetricSource",
    "Assessment",
    "AssessmentType",
    "AssessmentStatus",
    "Medication",
    "Prediction",
    "RiskCategory",
    "EmergencyContact",
    "CaregiverRelationship",
    "ProviderRelationship",
    "RelationshipType",
    "EmergencyAlert",
    "Reminder",
    "ReminderType",
    "ReminderFrequency",
    "DailyRoutine",
    "RoutineCompletion",
    "FaceProfile",
    "Exercise",
    "ExercisePerformance",
    "ExerciseType",
    "DifficultyLevel",
    "Recommendation",
    "RecommendationAdherence",
    "RecommendationCategory",
    "RecommendationPriority",
    "MedicalImaging",
    "ImagingModality",
    "ImagingStatus",
    "Provider",
    "ProviderAccess",
    "ProviderAccessLog",
    "ClinicalNote",
    "ProviderType",
    "AccessStatus",
    "CommunityPost",
    "CommunityReply",
    "ContentFlag"
]
