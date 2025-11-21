"""
Face recognition model for storing face embeddings and person information.
"""
from sqlalchemy import Column, String, Text, ARRAY, Float
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class FaceProfile(BaseModel):
    """
    Face profile model for storing person information and face embeddings.
    """
    __tablename__ = "face_profiles"
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Person details
    name = Column(String(255), nullable=False)
    relationship = Column(String(100), nullable=True)  # e.g., "daughter", "son", "friend"
    notes = Column(Text, nullable=True)  # Memory prompts, context
    
    # Face embedding (128 or 512 dimensional vector from face recognition model)
    face_embedding = Column(ARRAY(Float), nullable=False)
    
    # Photo storage
    photo_url = Column(String(500), nullable=True)  # URL to stored photo
    
    def __repr__(self):
        return f"<FaceProfile(id={self.id}, name={self.name}, relationship={self.relationship})>"
    
    def to_dict(self):
        """Convert face profile to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "relationship": self.relationship,
            "notes": self.notes,
            "photo_url": self.photo_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def to_dict_with_embedding(self):
        """Convert face profile to dictionary including embedding"""
        data = self.to_dict()
        data["face_embedding"] = self.face_embedding
        return data
