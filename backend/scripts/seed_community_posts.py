"""Seed sample community posts for testing."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.community_post import CommunityPost
from app.models.user import User
import uuid
from datetime import datetime, timedelta


def seed_posts(db: Session):
    """Seed sample community posts."""
    
    # Get first user to assign posts to
    user = db.query(User).first()
    if not user:
        print("No users found. Please create a user first.")
        return
    
    # Check if posts already exist
    existing_count = db.query(CommunityPost).count()
    if existing_count > 0:
        print(f"Posts already exist ({existing_count} found). Skipping seed.")
        return
    
    posts = [
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Newly diagnosed - looking for support and advice",
            "content": "Hi everyone, I was just diagnosed with early-stage Alzheimer's last month. I'm feeling overwhelmed and scared. How did you cope with your diagnosis? What helped you in the early days? Any advice would be greatly appreciated.",
            "category": "support",
            "visibility": "public",
            "is_anonymous": False,
            "view_count": 45,
            "created_at": datetime.now() - timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Best exercises for brain health?",
            "content": "I've been reading about how exercise can help slow cognitive decline. What types of exercises have you found most helpful? I'm currently doing walking and some light yoga, but wondering if there are other activities I should try.",
            "category": "questions",
            "visibility": "public",
            "is_anonymous": False,
            "view_count": 67,
            "created_at": datetime.now() - timedelta(days=5)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Memory aids that actually work",
            "content": "I wanted to share some memory aids that have been really helpful for me:\n\n1. Color-coded calendar on the fridge\n2. Medication organizer with alarms\n3. Voice memos on my phone\n4. Sticky notes in key locations\n5. Daily routine checklist\n\nWhat memory aids work for you?",
            "category": "tips",
            "visibility": "public",
            "is_anonymous": False,
            "view_count": 123,
            "created_at": datetime.now() - timedelta(days=7)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Caregiver burnout - how to cope?",
            "content": "I'm caring for my mother who has moderate Alzheimer's. I love her dearly but I'm exhausted. I feel guilty taking breaks. How do other caregivers manage? When did you know it was time to ask for help?",
            "category": "support",
            "visibility": "public",
            "is_anonymous": True,
            "view_count": 89,
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "MIND diet recipes - share your favorites!",
            "content": "I've been following the MIND diet for 3 months now. Would love to exchange recipes! Here's my favorite breakfast: Oatmeal with blueberries, walnuts, and a drizzle of honey. What are your go-to MIND diet meals?",
            "category": "tips",
            "visibility": "public",
            "is_anonymous": False,
            "view_count": 156,
            "created_at": datetime.now() - timedelta(days=4)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Question about clinical trials",
            "content": "Has anyone here participated in an Alzheimer's clinical trial? I'm considering it but nervous about potential side effects. What was your experience like? Would you recommend it?",
            "category": "questions",
            "visibility": "public",
            "is_anonymous": False,
            "view_count": 78,
            "created_at": datetime.now() - timedelta(days=1)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Celebrating small victories",
            "content": "Today I remembered my grandson's birthday without any reminders! It might seem small, but these moments mean everything. Let's share our wins, no matter how small. What victories have you celebrated recently?",
            "category": "general",
            "visibility": "public",
            "is_anonymous": False,
            "view_count": 201,
            "created_at": datetime.now() - timedelta(hours=12)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Helpful apps and technology",
            "content": "I've found some great apps that help with daily tasks:\n- Medication reminder apps\n- GPS tracking for safety\n- Brain training games\n- Voice assistants for reminders\n\nWhat technology has been helpful for you or your loved ones?",
            "category": "resources",
            "visibility": "public",
            "is_anonymous": False,
            "view_count": 134,
            "created_at": datetime.now() - timedelta(days=6)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Dealing with frustration and anger",
            "content": "Sometimes I get so frustrated when I can't remember things or do tasks that used to be easy. How do you manage these feelings? I don't want to take it out on my family but it's hard.",
            "category": "support",
            "visibility": "public",
            "is_anonymous": True,
            "view_count": 92,
            "created_at": datetime.now() - timedelta(days=8)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "title": "Music therapy experiences",
            "content": "My doctor recommended music therapy. I've been listening to songs from my youth and it's amazing how it brings back memories and improves my mood. Has anyone else tried music therapy? What kind of music works best for you?",
            "category": "general",
            "visibility": "public",
            "is_anonymous": False,
            "view_count": 167,
            "created_at": datetime.now() - timedelta(days=9)
        }
    ]
    
    # Add all posts
    for post_data in posts:
        post = CommunityPost(**post_data)
        db.add(post)
    
    db.commit()
    print(f"Successfully seeded {len(posts)} community posts!")


def main():
    """Main function to seed posts."""
    db = SessionLocal()
    try:
        seed_posts(db)
    except Exception as e:
        print(f"Error seeding posts: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
