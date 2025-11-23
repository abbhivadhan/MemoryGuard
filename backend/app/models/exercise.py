from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base


class ExerciseType(str, enum.Enum):
    MEMORY_GAME = "memory_game"
    PATTERN_RECOGNITION = "pattern_recognition"
    PROBLEM_SOLVING = "problem_solving"


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(SQLEnum(ExerciseType), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    instructions = Column(String)
    config = Column(JSON)  # Exercise-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    performances = relationship("ExercisePerformance", back_populates="exercise")


class ExercisePerformance(Base):
    __tablename__ = "exercise_performances"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exercise_id = Column(String, ForeignKey("exercises.id"), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    time_taken = Column(Integer)  # seconds
    completed = Column(Integer, default=1)  # boolean as int
    performance_data = Column(JSON)  # Detailed performance metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exercise = relationship("Exercise", back_populates="performances")
    user = relationship("User", back_populates="exercise_performances")
