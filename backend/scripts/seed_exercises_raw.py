"""
Script to seed the database with cognitive training exercises using raw SQL.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from sqlalchemy import text
import uuid
import json


def seed_exercises():
    db = SessionLocal()
    
    exercises = [
        # Memory Games
        ("Card Memory Match", "Match pairs of cards by remembering their positions", "memory_game", "easy", "Click cards to reveal them. Find matching pairs. Complete all pairs to finish.", {"pairs": 6, "time_limit": 120, "show_time": 1000}),
        ("Card Memory Match - Medium", "Match pairs of cards with more cards and less time", "memory_game", "medium", "Click cards to reveal them. Find matching pairs. Complete all pairs to finish.", {"pairs": 10, "time_limit": 180, "show_time": 800}),
        ("Card Memory Match - Hard", "Match pairs of cards with many cards and limited time", "memory_game", "hard", "Click cards to reveal them. Find matching pairs. Complete all pairs to finish.", {"pairs": 15, "time_limit": 240, "show_time": 600}),
        ("Number Sequence", "Remember and repeat a sequence of numbers", "memory_game", "easy", "Watch the sequence of numbers, then repeat it in order.", {"sequence_length": 4, "display_time": 1000, "max_number": 9}),
        ("Number Sequence - Medium", "Remember longer sequences of numbers", "memory_game", "medium", "Watch the sequence of numbers, then repeat it in order.", {"sequence_length": 6, "display_time": 800, "max_number": 9}),
        ("Number Sequence - Hard", "Remember complex sequences of numbers", "memory_game", "hard", "Watch the sequence of numbers, then repeat it in order.", {"sequence_length": 8, "display_time": 600, "max_number": 9}),
        
        # Pattern Recognition
        ("Shape Patterns", "Identify the next shape in a pattern sequence", "pattern_recognition", "easy", "Look at the pattern and select the shape that comes next.", {"pattern_length": 4, "options": 4, "shapes": ["circle", "square", "triangle"]}),
        ("Shape Patterns - Medium", "Identify patterns with more complex sequences", "pattern_recognition", "medium", "Look at the pattern and select the shape that comes next.", {"pattern_length": 5, "options": 6, "shapes": ["circle", "square", "triangle", "pentagon", "hexagon"]}),
        ("Color Sequence", "Identify the next color in a sequence", "pattern_recognition", "easy", "Observe the color pattern and select the next color.", {"sequence_length": 4, "colors": ["red", "blue", "green", "yellow"]}),
        ("3D Object Rotation", "Identify which 3D object matches the rotated version", "pattern_recognition", "hard", "Select the object that matches the target when rotated.", {"objects": ["cube", "pyramid", "cylinder", "sphere"], "rotation_angles": [45, 90, 135, 180]}),
        
        # Problem Solving
        ("Tower of Hanoi", "Move disks from one peg to another following the rules", "problem_solving", "easy", "Move all disks to the rightmost peg. Only one disk can be moved at a time, and larger disks cannot be placed on smaller ones.", {"disks": 3, "pegs": 3}),
        ("Tower of Hanoi - Medium", "Solve the Tower of Hanoi with more disks", "problem_solving", "medium", "Move all disks to the rightmost peg. Only one disk can be moved at a time, and larger disks cannot be placed on smaller ones.", {"disks": 4, "pegs": 3}),
        ("Path Finding", "Find the shortest path through a maze", "problem_solving", "easy", "Navigate from start to finish using the shortest path possible.", {"grid_size": 5, "obstacles": 3}),
        ("Path Finding - Medium", "Find the shortest path through a larger maze", "problem_solving", "medium", "Navigate from start to finish using the shortest path possible.", {"grid_size": 8, "obstacles": 8}),
        ("Logic Puzzle", "Solve a logic puzzle by deduction", "problem_solving", "hard", "Use the clues to determine the correct arrangement.", {"items": 4, "clues": 5}),
    ]
    
    try:
        added_count = 0
        for name, description, ex_type, difficulty, instructions, config in exercises:
            # Check if exercise already exists
            result = db.execute(text("SELECT id FROM exercises WHERE name = :name"), {"name": name})
            existing = result.fetchone()
            
            if not existing:
                exercise_id = str(uuid.uuid4())
                config_json = json.dumps(config)
                
                db.execute(
                    text("""
                    INSERT INTO exercises (id, name, description, type, difficulty, instructions, config, created_at)
                    VALUES (:id, :name, :description, CAST(:type AS exercisetype), CAST(:difficulty AS difficultylevel), :instructions, CAST(:config AS jsonb), NOW())
                    """),
                    {
                        "id": exercise_id,
                        "name": name,
                        "description": description,
                        "type": ex_type,
                        "difficulty": difficulty,
                        "instructions": instructions,
                        "config": config_json
                    }
                )
                db.commit()
                print(f"Added exercise: {name}")
                added_count += 1
            else:
                print(f"Exercise already exists: {name}")
        
        print(f"\nSuccessfully seeded {added_count} new exercises!")
    except Exception as e:
        print(f"Error seeding exercises: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_exercises()
