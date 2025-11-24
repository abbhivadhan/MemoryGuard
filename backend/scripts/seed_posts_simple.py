"""Simple seed script for community posts using raw SQL."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from sqlalchemy import text
import uuid
from datetime import datetime, timedelta


def seed_posts():
    """Seed sample community posts using raw SQL."""
    db = SessionLocal()
    
    try:
        # Check if posts exist
        result = db.execute(text("SELECT COUNT(*) FROM community_posts"))
        count = result.scalar()
        
        if count > 0:
            print(f"Posts already exist ({count} found). Skipping seed.")
            return
        
        # Get first user
        result = db.execute(text("SELECT id FROM users LIMIT 1"))
        user_row = result.fetchone()
        if not user_row:
            print("No users found. Please create a user first.")
            return
        
        user_id = str(user_row[0])
        
        posts = [
            (str(uuid.uuid4()), user_id, "Newly diagnosed - looking for support and advice", 
             "Hi everyone, I was just diagnosed with early-stage Alzheimer's last month. I'm feeling overwhelmed and scared. How did you cope with your diagnosis? What helped you in the early days? Any advice would be greatly appreciated.",
             "support", "public", False, 45, datetime.now() - timedelta(days=2)),
            
            (str(uuid.uuid4()), user_id, "Best exercises for brain health?",
             "I've been reading about how exercise can help slow cognitive decline. What types of exercises have you found most helpful? I'm currently doing walking and some light yoga, but wondering if there are other activities I should try.",
             "questions", "public", False, 67, datetime.now() - timedelta(days=5)),
            
            (str(uuid.uuid4()), user_id, "Memory aids that actually work",
             "I wanted to share some memory aids that have been really helpful for me:\n\n1. Color-coded calendar on the fridge\n2. Medication organizer with alarms\n3. Voice memos on my phone\n4. Sticky notes in key locations\n5. Daily routine checklist\n\nWhat memory aids work for you?",
             "tips", "public", False, 123, datetime.now() - timedelta(days=7)),
            
            (str(uuid.uuid4()), user_id, "Caregiver burnout - how to cope?",
             "I'm caring for my mother who has moderate Alzheimer's. I love her dearly but I'm exhausted. I feel guilty taking breaks. How do other caregivers manage? When did you know it was time to ask for help?",
             "support", "public", True, 89, datetime.now() - timedelta(days=3)),
            
            (str(uuid.uuid4()), user_id, "MIND diet recipes - share your favorites!",
             "I've been following the MIND diet for 3 months now. Would love to exchange recipes! Here's my favorite breakfast: Oatmeal with blueberries, walnuts, and a drizzle of honey. What are your go-to MIND diet meals?",
             "tips", "public", False, 156, datetime.now() - timedelta(days=4)),
            
            (str(uuid.uuid4()), user_id, "Question about clinical trials",
             "Has anyone here participated in an Alzheimer's clinical trial? I'm considering it but nervous about potential side effects. What was your experience like? Would you recommend it?",
             "questions", "public", False, 78, datetime.now() - timedelta(days=1)),
            
            (str(uuid.uuid4()), user_id, "Celebrating small victories",
             "Today I remembered my grandson's birthday without any reminders! It might seem small, but these moments mean everything. Let's share our wins, no matter how small. What victories have you celebrated recently?",
             "general", "public", False, 201, datetime.now() - timedelta(hours=12)),
            
            (str(uuid.uuid4()), user_id, "Helpful apps and technology",
             "I've found some great apps that help with daily tasks:\n- Medication reminder apps\n- GPS tracking for safety\n- Brain training games\n- Voice assistants for reminders\n\nWhat technology has been helpful for you or your loved ones?",
             "resources", "public", False, 134, datetime.now() - timedelta(days=6)),
            
            (str(uuid.uuid4()), user_id, "Dealing with frustration and anger",
             "Sometimes I get so frustrated when I can't remember things or do tasks that used to be easy. How do you manage these feelings? I don't want to take it out on my family but it's hard.",
             "support", "public", True, 92, datetime.now() - timedelta(days=8)),
            
            (str(uuid.uuid4()), user_id, "Music therapy experiences",
             "My doctor recommended music therapy. I've been listening to songs from my youth and it's amazing how it brings back memories and improves my mood. Has anyone else tried music therapy? What kind of music works best for you?",
             "general", "public", False, 167, datetime.now() - timedelta(days=9)),
        ]
        
        for post in posts:
            db.execute(
                text("""
                INSERT INTO community_posts 
                (id, user_id, title, content, category, visibility, is_anonymous, view_count, created_at, updated_at)
                VALUES (:id, CAST(:user_id AS UUID), :title, :content, CAST(:category AS postcategory), CAST(:visibility AS postvisibility), :is_anonymous, :view_count, :created_at, :updated_at)
                """),
                {
                    "id": post[0],
                    "user_id": post[1],
                    "title": post[2],
                    "content": post[3],
                    "category": post[4],
                    "visibility": post[5],
                    "is_anonymous": post[6],
                    "view_count": post[7],
                    "created_at": post[8],
                    "updated_at": datetime.now()
                }
            )
        
        db.commit()
        print(f"Successfully seeded {len(posts)} community posts!")
        
    except Exception as e:
        print(f"Error seeding posts: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_posts()
