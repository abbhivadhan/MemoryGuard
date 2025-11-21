"""
Script to seed the database with cognitive training exercises.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
import uuid


def seed_exercises():
    db = SessionLocal()
    
    exercises = [
        # Memory Games
        {
            "id": str(uuid.uuid4()),
            "name": "Card Memory Match",
            "description": "Match pairs of cards by remembering their positions",
            "type": ExerciseType.MEMORY_GAME,
            "difficulty": DifficultyLevel.EASY,
            "instructions": "Click cards to reveal them. Find matching pairs. Complete all pairs to finish.",
            "config": {
                "pairs": 6,
                "time_limit": 120,
                "show_time": 1000
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Card Memory Match - Medium",
            "description": "Match pairs of cards with more cards and less time",
            "type": ExerciseType.MEMORY_GAME,
            "difficulty": DifficultyLevel.MEDIUM,
            "instructions": "Click cards to reveal them. Find matching pairs. Complete all pairs to finish.",
            "config": {
                "pairs": 10,
                "time_limit": 180,
                "show_time": 800
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Card Memory Match - Hard",
            "description": "Match pairs of cards with many cards and limited time",
            "type": ExerciseType.MEMORY_GAME,
            "difficulty": DifficultyLevel.HARD,
            "instructions": "Click cards to reveal them. Find matching pairs. Complete all pairs to finish.",
            "config": {
                "pairs": 15,
                "time_limit": 240,
                "show_time": 600
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Number Sequence",
            "description": "Remember and repeat a sequence of numbers",
            "type": ExerciseType.MEMORY_GAME,
            "difficulty": DifficultyLevel.EASY,
            "instructions": "Watch the sequence of numbers, then repeat it in order.",
            "config": {
                "sequence_length": 4,
                "display_time": 1000,
                "max_number": 9
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Number Sequence - Medium",
            "description": "Remember longer sequences of numbers",
            "type": ExerciseType.MEMORY_GAME,
            "difficulty": DifficultyLevel.MEDIUM,
            "instructions": "Watch the sequence of numbers, then repeat it in order.",
            "config": {
                "sequence_length": 6,
                "display_time": 800,
                "max_number": 9
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Number Sequence - Hard",
            "description": "Remember complex sequences of numbers",
            "type": ExerciseType.MEMORY_GAME,
            "difficulty": DifficultyLevel.HARD,
            "instructions": "Watch the sequence of numbers, then repeat it in order.",
            "config": {
                "sequence_length": 8,
                "display_time": 600,
                "max_number": 9
            }
        },
        
        # Pattern Recognition
        {
            "id": str(uuid.uuid4()),
            "name": "Shape Patterns",
            "description": "Identify the next shape in a pattern sequence",
            "type": ExerciseType.PATTERN_RECOGNITION,
            "difficulty": DifficultyLevel.EASY,
            "instructions": "Look at the pattern and select the shape that comes next.",
            "config": {
                "pattern_length": 4,
                "options": 4,
                "shapes": ["circle", "square", "triangle"]
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Shape Patterns - Medium",
            "description": "Identify patterns with more complex sequences",
            "type": ExerciseType.PATTERN_RECOGNITION,
            "difficulty": DifficultyLevel.MEDIUM,
            "instructions": "Look at the pattern and select the shape that comes next.",
            "config": {
                "pattern_length": 5,
                "options": 6,
                "shapes": ["circle", "square", "triangle", "pentagon", "hexagon"]
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Color Sequence",
            "description": "Identify the next color in a sequence",
            "type": ExerciseType.PATTERN_RECOGNITION,
            "difficulty": DifficultyLevel.EASY,
            "instructions": "Observe the color pattern and select the next color.",
            "config": {
                "sequence_length": 4,
                "colors": ["red", "blue", "green", "yellow"]
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "3D Object Rotation",
            "description": "Identify which 3D object matches the rotated version",
            "type": ExerciseType.PATTERN_RECOGNITION,
            "difficulty": DifficultyLevel.HARD,
            "instructions": "Select the object that matches the target when rotated.",
            "config": {
                "objects": ["cube", "pyramid", "cylinder", "sphere"],
                "rotation_angles": [45, 90, 135, 180]
            }
        },
        
        # Problem Solving
        {
            "id": str(uuid.uuid4()),
            "name": "Tower of Hanoi",
            "description": "Move disks from one peg to another following the rules",
            "type": ExerciseType.PROBLEM_SOLVING,
            "difficulty": DifficultyLevel.EASY,
            "instructions": "Move all disks to the rightmost peg. Only one disk can be moved at a time, and larger disks cannot be placed on smaller ones.",
            "config": {
                "disks": 3,
                "pegs": 3
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Tower of Hanoi - Medium",
            "description": "Solve the Tower of Hanoi with more disks",
            "type": ExerciseType.PROBLEM_SOLVING,
            "difficulty": DifficultyLevel.MEDIUM,
            "instructions": "Move all disks to the rightmost peg. Only one disk can be moved at a time, and larger disks cannot be placed on smaller ones.",
            "config": {
                "disks": 4,
                "pegs": 3
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Path Finding",
            "description": "Find the shortest path through a maze",
            "type": ExerciseType.PROBLEM_SOLVING,
            "difficulty": DifficultyLevel.EASY,
            "instructions": "Navigate from start to finish using the shortest path possible.",
            "config": {
                "grid_size": 5,
                "obstacles": 3
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Path Finding - Medium",
            "description": "Find the shortest path through a larger maze",
            "type": ExerciseType.PROBLEM_SOLVING,
            "difficulty": DifficultyLevel.MEDIUM,
            "instructions": "Navigate from start to finish using the shortest path possible.",
            "config": {
                "grid_size": 8,
                "obstacles": 8
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Logic Puzzle",
            "description": "Solve a logic puzzle by deduction",
            "type": ExerciseType.PROBLEM_SOLVING,
            "difficulty": DifficultyLevel.HARD,
            "instructions": "Use the clues to determine the correct arrangement.",
            "config": {
                "items": 4,
                "clues": 5
            }
        }
    ]
    
    try:
        for exercise_data in exercises:
            # Check if exercise already exists
            existing = db.query(Exercise).filter(Exercise.name == exercise_data["name"]).first()
            if not existing:
                exercise = Exercise(**exercise_data)
                db.add(exercise)
                print(f"Added exercise: {exercise_data['name']}")
            else:
                print(f"Exercise already exists: {exercise_data['name']}")
        
        db.commit()
        print(f"\nSuccessfully seeded {len(exercises)} exercises!")
    except Exception as e:
        print(f"Error seeding exercises: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_exercises()
