"""Community post models for forum functionality."""
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class PostCategory(str, enum.Enum):
    """Post category types."""
    GENERAL = "general"
    SUPPORT = "support"
    TIPS = "tips"
    QUESTIONS = "questions"
    RESOURCES = "resources"


class PostVisibility(str, enum.Enum):
    """Post visibility settings."""
    PUBLIC = "public"
    MEMBERS_ONLY = "members_only"
    MATCHED_USERS = "matched_users"


class CommunityPost(Base):
    """Community forum post model."""
    
    __tablename__ = "community_posts"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(PostCategory), nullable=False, default=PostCategory.GENERAL)
    visibility = Column(Enum(PostVisibility), nullable=False, default=PostVisibility.PUBLIC)
    is_anonymous = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    is_moderated = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="community_posts")
    replies = relationship("CommunityReply", back_populates="post", cascade="all, delete-orphan")
    flags = relationship("ContentFlag", back_populates="post", cascade="all, delete-orphan")


class CommunityReply(Base):
    """Reply to a community post."""
    
    __tablename__ = "community_replies"
    
    id = Column(String, primary_key=True, index=True)
    post_id = Column(String, ForeignKey("community_posts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    is_moderated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = relationship("CommunityPost", back_populates="replies")
    user = relationship("User", back_populates="community_replies")
    flags = relationship("ContentFlag", back_populates="reply", cascade="all, delete-orphan")


class ContentFlag(Base):
    """Content moderation flag."""
    
    __tablename__ = "content_flags"
    
    id = Column(String, primary_key=True, index=True)
    post_id = Column(String, ForeignKey("community_posts.id"), nullable=True)
    reply_id = Column(String, ForeignKey("community_replies.id"), nullable=True)
    reporter_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")  # pending, reviewed, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    post = relationship("CommunityPost", back_populates="flags")
    reply = relationship("CommunityReply", back_populates="flags")
    reporter = relationship("User", back_populates="content_flags")


class EducationalResource(Base):
    """Educational resource for community."""
    
    __tablename__ = "educational_resources"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    resource_type = Column(String(50), nullable=False)  # article, video, qa, guide
    author = Column(String(255))
    source_url = Column(String(500))
    tags = Column(Text)  # JSON array of tags
    view_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
