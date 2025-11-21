from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.exercise import Exercise, ExercisePerformance, ExerciseType, DifficultyLevel
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseResponse,
    ExercisePerformanceCreate,
    ExercisePerformanceResponse,
    ExerciseStats,
    UserExerciseProgress
)
from app.services.exercise_ml_service import ExerciseMLService

router = APIRouter()


@router.get("/library", response_model=List[ExerciseResponse])
async def get_exercise_library(
    type: Optional[ExerciseType] = None,
    difficulty: Optional[DifficultyLevel] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available exercises, optionally filtered by type and difficulty"""
    query = db.query(Exercise)
    
    if type:
        query = query.filter(Exercise.type == type)
    if difficulty:
        query = query.filter(Exercise.difficulty == difficulty)
    
    exercises = query.all()
    return exercises


@router.post("/library", response_model=ExerciseResponse)
async def create_exercise(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new exercise (admin only - for seeding)"""
    db_exercise = Exercise(
        id=str(uuid.uuid4()),
        **exercise.dict()
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@router.get("/library/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific exercise by ID"""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.post("/performances", response_model=ExercisePerformanceResponse)
async def record_performance(
    performance: ExercisePerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a user's exercise performance"""
    # Verify exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == performance.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db_performance = ExercisePerformance(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        **performance.dict()
    )
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return db_performance


@router.get("/performances", response_model=List[ExercisePerformanceResponse])
async def get_user_performances(
    exercise_id: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's exercise performance history"""
    query = db.query(ExercisePerformance).filter(
        ExercisePerformance.user_id == str(current_user.id)
    )
    
    if exercise_id:
        query = query.filter(ExercisePerformance.exercise_id == exercise_id)
    
    performances = query.order_by(desc(ExercisePerformance.created_at)).limit(limit).all()
    return performances


@router.get("/stats/{exercise_id}", response_model=ExerciseStats)
async def get_exercise_stats(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific exercise"""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    performances = db.query(ExercisePerformance).filter(
        ExercisePerformance.user_id == str(current_user.id),
        ExercisePerformance.exercise_id == exercise_id
    ).all()
    
    if not performances:
        return ExerciseStats(
            exercise_id=exercise_id,
            exercise_name=exercise.name,
            exercise_type=exercise.type,
            total_attempts=0,
            average_score=0.0,
            best_score=0.0,
            average_time=None,
            current_difficulty=exercise.difficulty,
            improvement_rate=0.0
        )
    
    scores = [p.score for p in performances]
    times = [p.time_taken for p in performances if p.time_taken]
    
    # Calculate improvement rate (compare first half to second half)
    improvement_rate = 0.0
    if len(scores) >= 4:
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / mid
        second_half_avg = sum(scores[mid:]) / (len(scores) - mid)
        if first_half_avg > 0:
            improvement_rate = ((second_half_avg - first_half_avg) / first_half_avg) * 100
    
    # Get current difficulty (from most recent performance)
    current_difficulty = performances[-1].difficulty
    
    return ExerciseStats(
        exercise_id=exercise_id,
        exercise_name=exercise.name,
        exercise_type=exercise.type,
        total_attempts=len(performances),
        average_score=sum(scores) / len(scores),
        best_score=max(scores),
        average_time=sum(times) / len(times) if times else None,
        current_difficulty=current_difficulty,
        improvement_rate=improvement_rate
    )


@router.get("/progress", response_model=UserExerciseProgress)
async def get_user_progress(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive user exercise progress"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    performances = db.query(ExercisePerformance).filter(
        ExercisePerformance.user_id == str(current_user.id),
        ExercisePerformance.created_at >= since_date
    ).all()
    
    if not performances:
        return UserExerciseProgress(
            total_exercises_completed=0,
            total_time_spent=0,
            exercises_by_type={},
            average_scores_by_type={},
            recent_performances=[],
            exercise_stats=[]
        )
    
    # Calculate statistics
    total_time = sum(p.time_taken for p in performances if p.time_taken) or 0
    
    # Group by exercise type
    exercises_by_type = {}
    scores_by_type = {}
    
    for perf in performances:
        exercise = db.query(Exercise).filter(Exercise.id == perf.exercise_id).first()
        if exercise:
            type_str = exercise.type.value
            exercises_by_type[type_str] = exercises_by_type.get(type_str, 0) + 1
            if type_str not in scores_by_type:
                scores_by_type[type_str] = []
            scores_by_type[type_str].append(perf.score)
    
    average_scores_by_type = {
        type_str: sum(scores) / len(scores)
        for type_str, scores in scores_by_type.items()
    }
    
    # Get recent performances
    recent = db.query(ExercisePerformance).filter(
        ExercisePerformance.user_id == str(current_user.id)
    ).order_by(desc(ExercisePerformance.created_at)).limit(10).all()
    
    # Get stats for each unique exercise
    unique_exercise_ids = list(set(p.exercise_id for p in performances))
    exercise_stats = []
    for ex_id in unique_exercise_ids:
        try:
            stats = await get_exercise_stats(ex_id, db, current_user)
            exercise_stats.append(stats)
        except:
            continue
    
    return UserExerciseProgress(
        total_exercises_completed=len(performances),
        total_time_spent=total_time,
        exercises_by_type=exercises_by_type,
        average_scores_by_type=average_scores_by_type,
        recent_performances=recent,
        exercise_stats=exercise_stats
    )


@router.get("/recommended-difficulty/{exercise_id}")
async def get_recommended_difficulty(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recommended difficulty level based on user's performance history"""
    performances = db.query(ExercisePerformance).filter(
        ExercisePerformance.user_id == str(current_user.id),
        ExercisePerformance.exercise_id == exercise_id
    ).order_by(desc(ExercisePerformance.created_at)).limit(5).all()
    
    if not performances:
        return {"recommended_difficulty": DifficultyLevel.EASY.value}
    
    # Calculate average score from recent performances
    recent_avg = sum(p.score / p.max_score for p in performances) / len(performances)
    current_difficulty = performances[0].difficulty
    
    # Adaptive difficulty logic
    if recent_avg >= 0.9 and current_difficulty != DifficultyLevel.EXPERT:
        # Increase difficulty
        difficulty_order = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.EXPERT]
        current_index = difficulty_order.index(current_difficulty)
        recommended = difficulty_order[min(current_index + 1, len(difficulty_order) - 1)]
    elif recent_avg < 0.5 and current_difficulty != DifficultyLevel.EASY:
        # Decrease difficulty
        difficulty_order = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.EXPERT]
        current_index = difficulty_order.index(current_difficulty)
        recommended = difficulty_order[max(current_index - 1, 0)]
    else:
        # Keep current difficulty
        recommended = current_difficulty
    
    return {
        "recommended_difficulty": recommended.value,
        "current_difficulty": current_difficulty.value,
        "recent_average_score": recent_avg
    }


@router.get("/ml-insights")
async def get_ml_insights(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ML-powered insights from exercise performance data"""
    ml_service = ExerciseMLService(db)
    
    # Calculate cognitive score
    cognitive_score = ml_service.calculate_cognitive_score_from_exercises(
        str(current_user.id),
        days
    )
    
    # Analyze trends
    trends = ml_service.analyze_performance_trends(
        str(current_user.id),
        days=days
    )
    
    # Get decline indicators
    decline_indicators = ml_service.get_cognitive_decline_indicators(
        str(current_user.id),
        days=days
    )
    
    # Get recommendations
    recommendations = ml_service.get_exercise_recommendations(
        str(current_user.id)
    )
    
    return {
        "cognitive_score": cognitive_score,
        "trends": trends,
        "decline_indicators": decline_indicators,
        "recommendations": recommendations
    }


@router.post("/sync-to-health-metrics")
async def sync_to_health_metrics(
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync exercise performance data to health metrics for ML predictions.
    This allows exercise data to be included in progression forecasting.
    """
    ml_service = ExerciseMLService(db)
    
    metric = ml_service.create_health_metric_from_exercises(
        str(current_user.id),
        days
    )
    
    if metric:
        return {
            "success": True,
            "message": "Exercise data synced to health metrics",
            "metric_id": metric.id,
            "cognitive_score": metric.value
        }
    else:
        return {
            "success": False,
            "message": "Insufficient exercise data to create health metric"
        }
