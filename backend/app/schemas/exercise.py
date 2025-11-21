from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.exercise import ExerciseType, DifficultyLevel


class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: ExerciseType
    difficulty: DifficultyLevel
    instructions: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(ExerciseBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExercisePerformanceBase(BaseModel):
    exercise_id: str
    difficulty: DifficultyLevel
    score: float
    max_score: float
    time_taken: Optional[int] = None
    completed: bool = True
    performance_data: Optional[Dict[str, Any]] = None


class ExercisePerformanceCreate(ExercisePerformanceBase):
    pass


class ExercisePerformanceResponse(ExercisePerformanceBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseStats(BaseModel):
    exercise_id: str
    exercise_name: str
    exercise_type: ExerciseType
    total_attempts: int
    average_score: float
    best_score: float
    average_time: Optional[float] = None
    current_difficulty: DifficultyLevel
    improvement_rate: float  # Percentage improvement over time


class UserExerciseProgress(BaseModel):
    total_exercises_completed: int
    total_time_spent: int  # seconds
    exercises_by_type: Dict[str, int]
    average_scores_by_type: Dict[str, float]
    recent_performances: List[ExercisePerformanceResponse]
    exercise_stats: List[ExerciseStats]
