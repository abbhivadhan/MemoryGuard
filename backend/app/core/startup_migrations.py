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
        
        # Migration 4: Seed community posts and resources
        seed_community_data()
        
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


def seed_community_data():
    """
    Seed community posts and educational resources if they don't exist.
    This is idempotent - safe to run multiple times.
    """
    try:
        from app.models.community_post import CommunityPost, EducationalResource
        from app.models.user import User
        from datetime import timedelta
        
        db = SessionLocal()
        
        # Check if posts already exist
        existing_posts = db.query(CommunityPost).count()
        if existing_posts == 0:
            logger.info("Seeding community posts...")
            
            # Get first user to assign posts to
            user = db.query(User).first()
            if not user:
                logger.warning("No users found. Skipping community posts seed.")
                db.close()
                return
            
            posts_data = [
                {
                    "user_id": user.id,
                    "title": "Newly diagnosed - looking for support and advice",
                    "content": "Hi everyone, I was just diagnosed with early-stage Alzheimer's last month. I'm feeling overwhelmed and scared. How did you cope with your diagnosis? What helped you in the early days?",
                    "category": "support",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 45,
                    "created_at": datetime.utcnow() - timedelta(days=2)
                },
                {
                    "user_id": user.id,
                    "title": "Best exercises for brain health?",
                    "content": "I've been reading about how exercise can help slow cognitive decline. What types of exercises have you found most helpful?",
                    "category": "questions",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 67,
                    "created_at": datetime.utcnow() - timedelta(days=5)
                },
                {
                    "user_id": user.id,
                    "title": "Memory aids that actually work",
                    "content": "I wanted to share some memory aids that have been really helpful for me: color-coded calendar, medication organizer with alarms, voice memos on my phone.",
                    "category": "tips",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 123,
                    "created_at": datetime.utcnow() - timedelta(days=7)
                },
                {
                    "user_id": user.id,
                    "title": "Caregiver burnout - how to cope?",
                    "content": "I'm caring for my mother who has moderate Alzheimer's. I love her dearly but I'm exhausted. How do other caregivers manage?",
                    "category": "support",
                    "visibility": "public",
                    "is_anonymous": True,
                    "view_count": 89,
                    "created_at": datetime.utcnow() - timedelta(days=3)
                },
                {
                    "user_id": user.id,
                    "title": "MIND diet recipes - share your favorites!",
                    "content": "I've been following the MIND diet for 3 months now. Would love to exchange recipes!",
                    "category": "tips",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 156,
                    "created_at": datetime.utcnow() - timedelta(days=4)
                },
                {
                    "user_id": user.id,
                    "title": "Question about clinical trials",
                    "content": "Has anyone here participated in an Alzheimer's clinical trial? I'm considering it but nervous about potential side effects.",
                    "category": "questions",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 78,
                    "created_at": datetime.utcnow() - timedelta(days=1)
                },
                {
                    "user_id": user.id,
                    "title": "Celebrating small victories",
                    "content": "Today I remembered my grandson's birthday without any reminders! Let's share our wins, no matter how small.",
                    "category": "general",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 201,
                    "created_at": datetime.utcnow() - timedelta(hours=12)
                },
                {
                    "user_id": user.id,
                    "title": "Helpful apps and technology",
                    "content": "I've found some great apps that help with daily tasks: medication reminders, GPS tracking, brain training games.",
                    "category": "resources",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 134,
                    "created_at": datetime.utcnow() - timedelta(days=6)
                },
                {
                    "user_id": user.id,
                    "title": "Dealing with frustration and anger",
                    "content": "Sometimes I get so frustrated when I can't remember things. How do you manage these feelings?",
                    "category": "support",
                    "visibility": "public",
                    "is_anonymous": True,
                    "view_count": 92,
                    "created_at": datetime.utcnow() - timedelta(days=8)
                },
                {
                    "user_id": user.id,
                    "title": "Music therapy experiences",
                    "content": "My doctor recommended music therapy. I've been listening to songs from my youth and it's amazing how it brings back memories.",
                    "category": "general",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 167,
                    "created_at": datetime.utcnow() - timedelta(days=9)
                },
                {
                    "user_id": user.id,
                    "title": "Support group recommendations",
                    "content": "Looking for recommendations for online or in-person support groups. What has worked well for you?",
                    "category": "questions",
                    "visibility": "public",
                    "is_anonymous": False,
                    "view_count": 54,
                    "created_at": datetime.utcnow() - timedelta(days=10)
                }
            ]
            
            for post_data in posts_data:
                post = CommunityPost(**post_data)
                db.add(post)
            
            db.commit()
            logger.info(f"✅ Seeded {len(posts_data)} community posts")
        else:
            logger.info(f"Community posts already exist ({existing_posts} found) - skipping")
        
        # Check if resources already exist
        existing_resources = db.query(EducationalResource).count()
        if existing_resources == 0:
            logger.info("Seeding educational resources...")
            
            resources_data = [
                {
                    "title": "Understanding Alzheimer's Disease",
                    "description": "Learn about the causes, symptoms, and progression of Alzheimer's disease.",
                    "content": "Alzheimer's disease is a progressive neurological disorder that affects memory, thinking, and behavior...",
                    "resource_type": "article",
                    "author": "Dr. Sarah Johnson",
                    "source_url": "https://www.alz.org/alzheimers-dementia/what-is-alzheimers",
                    "tags": "alzheimers,basics,symptoms",
                    "is_featured": True,
                    "view_count": 1247
                },
                {
                    "title": "The MIND Diet for Brain Health",
                    "description": "Discover how the MIND diet supports cognitive function.",
                    "content": "The MIND diet combines Mediterranean and DASH diets to promote brain health...",
                    "resource_type": "article",
                    "author": "Dr. Martha Clare Morris",
                    "source_url": "https://www.rush.edu/news/diet-may-help-prevent-alzheimers",
                    "tags": "diet,nutrition,prevention",
                    "is_featured": True,
                    "view_count": 892
                },
                {
                    "title": "Exercise and Brain Health",
                    "description": "Learn how physical activity protects your brain.",
                    "content": "Regular physical exercise is one of the most powerful tools for maintaining brain health...",
                    "resource_type": "article",
                    "author": "Dr. John Ratey",
                    "source_url": "https://www.health.harvard.edu/mind-and-mood/exercise-can-boost-your-memory",
                    "tags": "exercise,prevention,physical-activity",
                    "is_featured": False,
                    "view_count": 654
                },
                {
                    "title": "What Happens to the Brain in Alzheimer's?",
                    "description": "An animated explanation of biological changes in the brain.",
                    "content": "This educational video provides a clear, visual explanation of what happens in the brain during Alzheimer's disease...",
                    "resource_type": "video",
                    "author": "Alzheimer's Association",
                    "source_url": "https://www.youtube.com/watch?v=yJXTXN4xrI8",
                    "tags": "video,education,brain",
                    "is_featured": True,
                    "view_count": 2103
                },
                {
                    "title": "Caregiver Self-Care: Preventing Burnout",
                    "description": "Essential strategies for caregivers to maintain their health.",
                    "content": "This video addresses the critical importance of caregiver self-care...",
                    "resource_type": "video",
                    "author": "Family Caregiver Alliance",
                    "source_url": "https://www.caregiver.org/resource/caregiver-self-care/",
                    "tags": "video,caregiving,self-care",
                    "is_featured": False,
                    "view_count": 876
                },
                {
                    "title": "Common Questions About Alzheimer's Diagnosis",
                    "description": "Answers to frequently asked questions about diagnosis.",
                    "content": "Q: What tests are used to diagnose Alzheimer's? A: Diagnosis typically involves medical history review, cognitive tests...",
                    "resource_type": "qa",
                    "author": "Dr. Michael Chen",
                    "source_url": "https://www.nia.nih.gov/health/alzheimers-disease-fact-sheet",
                    "tags": "qa,diagnosis,faq",
                    "is_featured": True,
                    "view_count": 1456
                },
                {
                    "title": "Questions About Caregiving",
                    "description": "Practical answers to common caregiving questions.",
                    "content": "Q: How do I talk to someone with Alzheimer's? A: Speak slowly and clearly, use simple words...",
                    "resource_type": "qa",
                    "author": "Nancy Pearce, MSW",
                    "source_url": "https://www.alz.org/help-support/caregiving",
                    "tags": "qa,caregiving,communication",
                    "is_featured": False,
                    "view_count": 723
                },
                {
                    "title": "Creating a Dementia-Friendly Home",
                    "description": "Step-by-step instructions for home modifications.",
                    "content": "Creating a safe, comfortable environment is crucial for people with Alzheimer's disease...",
                    "resource_type": "guide",
                    "author": "Home Safety Council",
                    "source_url": "https://www.alz.org/help-support/caregiving/safety/home-safety",
                    "tags": "guide,home-safety,modifications",
                    "is_featured": True,
                    "view_count": 1089
                },
                {
                    "title": "Guide to Clinical Trials",
                    "description": "Everything you need to know about Alzheimer's clinical trials.",
                    "content": "Clinical trials are research studies that test new treatments, interventions, or diagnostic tools...",
                    "resource_type": "guide",
                    "author": "Dr. Rebecca Edelmayer",
                    "source_url": "https://www.alz.org/alzheimers-dementia/research_progress/clinical-trials",
                    "tags": "guide,clinical-trials,research",
                    "is_featured": False,
                    "view_count": 567
                }
            ]
            
            for resource_data in resources_data:
                resource = EducationalResource(**resource_data)
                db.add(resource)
            
            db.commit()
            logger.info(f"✅ Seeded {len(resources_data)} educational resources")
        else:
            logger.info(f"Educational resources already exist ({existing_resources} found) - skipping")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error seeding community data: {e}")
        # Don't raise - this is not critical
