"""Pydantic schemas for community features."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PostCategory(str, Enum):
    """Post category types."""
    GENERAL = "general"
    SUPPORT = "support"
    TIPS = "tips"
    QUESTIONS = "questions"
    RESOURCES = "resources"


class PostVisibility(str, Enum):
    """Post visibility settings."""
    PUBLIC = "public"
    MEMBERS_ONLY = "members_only"
    MATCHED_USERS = "matched_users"


class CommunityPostCreate(BaseModel):
    """Schema for creating a community post."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    category: PostCategory = PostCategory.GENERAL
    visibility: PostVisibility = PostVisibility.PUBLIC
    is_anonymous: bool = False


class CommunityReplyCreate(BaseModel):
    """Schema for creating a reply."""
    content: str = Field(..., min_length=1)
    is_anonymous: bool = False


class ContentFlagCreate(BaseModel):
    """Schema for flagging content."""
    reason: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class UserInfo(BaseModel):
    """Basic user information for display."""
    id: str
    name: str
    is_anonymous: bool = False
    
    class Config:
        from_attributes = True


class CommunityReplyResponse(BaseModel):
    """Schema for reply response."""
    id: str
    post_id: str
    user: UserInfo
    content: str
    is_flagged: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommunityPostResponse(BaseModel):
    """Schema for post response."""
    id: str
    user: UserInfo
    title: str
    content: str
    category: PostCategory
    visibility: PostVisibility
    is_flagged: bool
    view_count: int
    reply_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommunityPostDetail(CommunityPostResponse):
    """Schema for detailed post with replies."""
    replies: List[CommunityReplyResponse] = []
    
    class Config:
        from_attributes = True


class EducationalResourceResponse(BaseModel):
    """Schema for educational resource."""
    id: str
    title: str
    description: Optional[str]
    content: str
    resource_type: str
    author: Optional[str]
    source_url: Optional[str]
    tags: Optional[str]
    view_count: int
    is_featured: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserMatchResponse(BaseModel):
    """Schema for user matching results."""
    user_id: str
    match_score: float
    match_reasons: List[str]
    risk_profile_similarity: Optional[float] = None
    disease_stage_match: Optional[bool] = None
