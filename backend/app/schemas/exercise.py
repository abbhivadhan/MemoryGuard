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


class ExerciseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: str
    difficulty: str
    instructions: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExercisePerformanceBase(BaseModel):
    exercise_id: str
    difficulty: str  # Accept string, will be converted to enum
    score: float
    max_score: float
    time_taken: Optional[int] = None
    completed: Optional[bool] = True
    performance_data: Optional[Dict[str, Any]] = None


class ExercisePerformanceCreate(ExercisePerformanceBase):
    pass


class ExercisePerformanceResponse(BaseModel):
    id: str
    user_id: str
    exercise_id: str
    difficulty: str
    score: float
    max_score: float
    time_taken: Optional[int] = None
    completed: int  # Database stores as integer
    performance_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
        # Allow UUID to be converted to string
        json_encoders = {
            'UUID': str
        }
    
    @classmethod
    def model_validate(cls, obj):
        # Convert UUID to string if needed
        if hasattr(obj, 'user_id') and hasattr(obj.user_id, '__str__'):
            obj_dict = {
                'id': str(obj.id),
                'user_id': str(obj.user_id),
                'exercise_id': str(obj.exercise_id),
                'difficulty': str(obj.difficulty),
                'score': float(obj.score),
                'max_score': float(obj.max_score),
                'time_taken': obj.time_taken,
                'completed': int(obj.completed),
                'performance_data': obj.performance_data,
                'created_at': obj.created_at
            }
            return cls(**obj_dict)
        return super().model_validate(obj)


class ExerciseStats(BaseModel):
    exercise_id: str
    exercise_name: str
    exercise_type: str
    total_attempts: int
    average_score: float
    best_score: float
    average_time: Optional[float] = None
    current_difficulty: str
    improvement_rate: float  # Percentage improvement over time


class UserExerciseProgress(BaseModel):
    total_exercises_completed: int
    total_time_spent: int  # seconds
    exercises_by_type: Dict[str, int]
    average_scores_by_type: Dict[str, float]
    recent_performances: List[ExercisePerformanceResponse]
    exercise_stats: List[ExerciseStats]
