"""Test community API endpoints."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.community_post import CommunityPost, EducationalResource
from app.models.user import User

def test_community_data():
    """Test that community data exists and is accessible."""
    db = SessionLocal()
    try:
        # Check posts
        posts = db.query(CommunityPost).all()
        print(f"✓ Found {len(posts)} community posts")
        
        if posts:
            post = posts[0]
            print(f"\nSample Post:")
            print(f"  ID: {post.id}")
            print(f"  Title: {post.title}")
            print(f"  Category: {post.category}")
            print(f"  Visibility: {post.visibility}")
            print(f"  Is Moderated: {post.is_moderated}")
            
            # Check if user exists
            user = db.query(User).filter(User.id == post.user_id).first()
            if user:
                print(f"  User: {user.name} ({user.email})")
            else:
                print(f"  ⚠ User not found for post!")
        
        # Check resources
        resources = db.query(EducationalResource).all()
        print(f"\n✓ Found {len(resources)} educational resources")
        
        if resources:
            resource = resources[0]
            print(f"\nSample Resource:")
            print(f"  ID: {resource.id}")
            print(f"  Title: {resource.title}")
            print(f"  Type: {resource.resource_type}")
            print(f"  Featured: {resource.is_featured}")
        
        # Check users
        users = db.query(User).all()
        print(f"\n✓ Found {len(users)} users in database")
        
        if users:
            print("\nUsers:")
            for user in users[:5]:  # Show first 5
                print(f"  - {user.name} ({user.email})")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_community_data()
