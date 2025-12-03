"""
Startup migrations that run automatically when the app starts.
This is useful for Render free tier where shell access is not available.
"""

import logging
import uuid
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.models.exercise import Exercise

logger = logging.getLogger(__name__)


def run_startup_migrations():
    """
    Run critical migrations on startup.
    This ensures the database schema is up to date even without shell access.
    """
    try:
        logger.info("Running startup migrations...")
        
        # Migration 1: Fix photo_url column for face recognition
        fix_photo_url_column()
        
        # Migration 2: Seed cognitive training exercises
        seed_exercises()
        
        # Migration 3: Fix NULL last_active timestamps
        fix_null_last_active()
        
        logger.info("✅ Startup migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Startup migrations failed: {e}")
        # Don't crash the app, just log the error
        return False


def fix_photo_url_column():
    """
    Change photo_url from VARCHAR(500) to TEXT to support base64 images.
    This is idempotent - safe to run multiple times.
    """
    try:
        with engine.connect() as conn:
            # Check if the column exists and its current type
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'face_profiles' 
                AND column_name = 'photo_url'
            """))
            
            column_info = result.fetchone()
            
            if not column_info:
                logger.info("face_profiles.photo_url column doesn't exist yet - skipping migration")
                return
            
            current_type = column_info[1]
            max_length = column_info[2]
            
            # Only run migration if it's still VARCHAR
            if current_type == 'character varying' and max_length == 500:
                logger.info(f"Migrating photo_url from VARCHAR(500) to TEXT...")
                
                conn.execute(text("""
                    ALTER TABLE face_profiles 
                    ALTER COLUMN photo_url TYPE TEXT
                """))
                conn.commit()
                
                logger.info("✅ Successfully migrated photo_url to TEXT")
            elif current_type == 'text':
                logger.info("photo_url is already TEXT - migration not needed")
            else:
                logger.info(f"photo_url has unexpected type: {current_type} - skipping migration")
                
    except Exception as e:
        logger.error(f"Error in fix_photo_url_column migration: {e}")
        raise



def seed_exercises():
    """
    Seed cognitive training exercises if they don't exist.
    This is idempotent - safe to run multiple times.
    """
    try:
        db = SessionLocal()
        
        # Check if exercises already exist
        existing_count = db.query(Exercise).count()
        if existing_count > 0:
            logger.info(f"Exercises already seeded ({existing_count} exercises found) - skipping")
            db.close()
            return
        
        logger.info("Seeding cognitive training exercises...")
        
        exercises = [
            # Memory Games
            {
                "id": str(uuid.uuid4()),
                "name": "Card Memory Match",
                "description": "Match pairs of cards by remembering their positions",
                "type": "memory_game",
                "difficulty": "easy",
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
                "type": "memory_game",
                "difficulty": "medium",
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
                "type": "memory_game",
                "difficulty": "hard",
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
                "type": "memory_game",
                "difficulty": "easy",
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
                "type": "memory_game",
                "difficulty": "medium",
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
                "type": "memory_game",
                "difficulty": "hard",
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
                "type": "pattern_recognition",
                "difficulty": "easy",
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
                "type": "pattern_recognition",
                "difficulty": "medium",
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
                "type": "pattern_recognition",
                "difficulty": "easy",
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
                "type": "pattern_recognition",
                "difficulty": "hard",
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
                "type": "problem_solving",
                "difficulty": "easy",
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
                "type": "problem_solving",
                "difficulty": "medium",
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
                "type": "problem_solving",
                "difficulty": "easy",
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
                "type": "problem_solving",
                "difficulty": "medium",
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
                "type": "problem_solving",
                "difficulty": "hard",
                "instructions": "Use the clues to determine the correct arrangement.",
                "config": {
                    "items": 4,
                    "clues": 5
                }
            }
        ]
        
        added_count = 0
        for exercise_data in exercises:
            exercise = Exercise(**exercise_data)
            db.add(exercise)
            added_count += 1
        
        db.commit()
        logger.info(f"✅ Successfully seeded {added_count} cognitive training exercises")
        db.close()
        
    except Exception as e:
        logger.error(f"Error seeding exercises: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        # Don't raise - let the app continue


def fix_null_last_active():
    """
    Fix NULL last_active timestamps for users.
    Sets them to created_at or current time.
    """
    try:
        with engine.connect() as conn:
            logger.info("Fixing NULL last_active timestamps...")
            
            result = conn.execute(text("""
                UPDATE users 
                SET last_active = COALESCE(created_at, NOW())
                WHERE last_active IS NULL
            """))
            conn.commit()
            
            rows_updated = result.rowcount
            if rows_updated > 0:
                logger.info(f"✅ Fixed {rows_updated} users with NULL last_active")
            else:
                logger.info("No users with NULL last_active found")
                
    except Exception as e:
        logger.error(f"Error fixing NULL last_active: {e}")
        # Don't raise - this is not critical
