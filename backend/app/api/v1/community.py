"""Community API endpoints for forum and educational resources."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.community_post import (
    CommunityPost, CommunityReply, ContentFlag, EducationalResource,
    PostCategory, PostVisibility
)
from app.schemas.community import (
    CommunityPostCreate, CommunityPostResponse, CommunityPostDetail,
    CommunityReplyCreate, CommunityReplyResponse,
    ContentFlagCreate, EducationalResourceResponse,
    UserMatchResponse, UserInfo
)

router = APIRouter()


def _get_user_info(user: User, is_anonymous: bool) -> UserInfo:
    """Get user info for display, respecting anonymity."""
    if is_anonymous:
        return UserInfo(
            id="anonymous",
            name="Anonymous User",
            is_anonymous=True
        )
    return UserInfo(
        id=str(user.id),
        name=user.name,
        is_anonymous=False
    )


def _post_to_response(post: CommunityPost, db: Session) -> CommunityPostResponse:
    """Convert post model to response schema."""
    user = db.query(User).filter(User.id == post.user_id).first()
    reply_count = db.query(CommunityReply).filter(CommunityReply.post_id == post.id).count()
    
    return CommunityPostResponse(
        id=str(post.id),
        user=_get_user_info(user, post.is_anonymous),
        title=post.title,
        content=post.content,
        category=post.category,
        visibility=post.visibility,
        is_flagged=post.is_flagged,
        view_count=post.view_count,
        reply_count=reply_count,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


def _reply_to_response(reply: CommunityReply, db: Session) -> CommunityReplyResponse:
    """Convert reply model to response schema."""
    user = db.query(User).filter(User.id == reply.user_id).first()
    
    return CommunityReplyResponse(
        id=str(reply.id),
        post_id=str(reply.post_id),
        user=_get_user_info(user, reply.is_anonymous),
        content=reply.content,
        is_flagged=reply.is_flagged,
        created_at=reply.created_at,
        updated_at=reply.updated_at
    )


@router.get("/posts", response_model=List[CommunityPostResponse])
async def get_posts(
    category: Optional[PostCategory] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get community posts with optional filtering.
    
    - **category**: Filter by post category
    - **skip**: Number of posts to skip (pagination)
    - **limit**: Maximum number of posts to return
    """
    from sqlalchemy import cast, Text as TextType
    
    query = db.query(CommunityPost).filter(CommunityPost.is_moderated == False)
    
    # Filter by category - cast to text to avoid enum issues
    if category:
        query = query.filter(cast(CommunityPost.category, TextType) == category.value)
    
    # Filter by visibility - cast to text to avoid enum issues
    query = query.filter(
        (cast(CommunityPost.visibility, TextType) == 'public') |
        (cast(CommunityPost.visibility, TextType) == 'members_only')
    )
    
    posts = query.order_by(CommunityPost.created_at.desc()).offset(skip).limit(limit).all()
    
    return [_post_to_response(post, db) for post in posts]


@router.get("/posts/{post_id}", response_model=CommunityPostDetail)
async def get_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific post with all replies.
    
    - **post_id**: ID of the post to retrieve
    """
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.is_moderated:
        raise HTTPException(status_code=403, detail="Post has been removed by moderators")
    
    # Increment view count
    post.view_count += 1
    db.commit()
    
    # Get replies
    replies = db.query(CommunityReply).filter(
        CommunityReply.post_id == post_id,
        CommunityReply.is_moderated == False
    ).order_by(CommunityReply.created_at.asc()).all()
    
    user = db.query(User).filter(User.id == post.user_id).first()
    reply_responses = [_reply_to_response(reply, db) for reply in replies]
    
    return CommunityPostDetail(
        id=str(post.id),
        user=_get_user_info(user, post.is_anonymous),
        title=post.title,
        content=post.content,
        category=post.category,
        visibility=post.visibility,
        is_flagged=post.is_flagged,
        view_count=post.view_count,
        reply_count=len(replies),
        created_at=post.created_at,
        updated_at=post.updated_at,
        replies=reply_responses
    )


@router.post("/posts", response_model=CommunityPostResponse, status_code=201)
async def create_post(
    post_data: CommunityPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new community post.
    
    - **title**: Post title
    - **content**: Post content
    - **category**: Post category (general, support, tips, questions, resources)
    - **visibility**: Who can see the post (public, members_only, matched_users)
    - **is_anonymous**: Whether to post anonymously
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        post = CommunityPost(
            id=str(uuid.uuid4()),
            user_id=current_user.id,  # Use UUID directly, not string
            title=post_data.title,
            content=post_data.content,
            category=post_data.category.value if hasattr(post_data.category, 'value') else post_data.category,
            visibility=post_data.visibility.value if hasattr(post_data.visibility, 'value') else post_data.visibility,
            is_anonymous=post_data.is_anonymous
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        logger.info(f"Created community post {post.id} by user {current_user.id}")
        
        return _post_to_response(post, db)
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.post("/posts/{post_id}/reply", response_model=CommunityReplyResponse, status_code=201)
async def create_reply(
    post_id: str,
    reply_data: CommunityReplyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reply to a community post.
    
    - **post_id**: ID of the post to reply to
    - **content**: Reply content
    - **is_anonymous**: Whether to reply anonymously
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Check if post exists
        post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.is_moderated:
            raise HTTPException(status_code=403, detail="Cannot reply to moderated post")
        
        reply = CommunityReply(
            id=str(uuid.uuid4()),
            post_id=post_id,
            user_id=current_user.id,  # Use UUID directly, not string
            content=reply_data.content,
            is_anonymous=reply_data.is_anonymous
        )
        
        db.add(reply)
        db.commit()
        db.refresh(reply)
        
        logger.info(f"Created reply {reply.id} to post {post_id} by user {current_user.id}")
        
        return _reply_to_response(reply, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reply: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create reply: {str(e)}")


@router.delete("/posts/{post_id}", status_code=200)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a post. Only the post author can delete their own posts.
    
    - **post_id**: ID of the post to delete
    """
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if current user is the author (compare UUIDs properly)
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    # Delete associated replies and flags
    db.query(CommunityReply).filter(CommunityReply.post_id == post_id).delete()
    db.query(ContentFlag).filter(ContentFlag.post_id == post_id).delete()
    
    # Delete the post
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}


@router.post("/posts/{post_id}/flag", status_code=201)
async def flag_post(
    post_id: str,
    flag_data: ContentFlagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Flag a post for moderation.
    
    - **post_id**: ID of the post to flag
    - **reason**: Reason for flagging
    - **description**: Optional detailed description
    """
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    flag = ContentFlag(
        id=str(uuid.uuid4()),
        post_id=post_id,
        reporter_user_id=current_user.id,  # Use UUID directly
        reason=flag_data.reason,
        description=flag_data.description
    )
    
    db.add(flag)
    post.is_flagged = True
    db.commit()
    
    return {"message": "Post flagged for review"}


@router.post("/replies/{reply_id}/flag", status_code=201)
async def flag_reply(
    reply_id: str,
    flag_data: ContentFlagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Flag a reply for moderation.
    
    - **reply_id**: ID of the reply to flag
    - **reason**: Reason for flagging
    - **description**: Optional detailed description
    """
    reply = db.query(CommunityReply).filter(CommunityReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    flag = ContentFlag(
        id=str(uuid.uuid4()),
        reply_id=reply_id,
        reporter_user_id=current_user.id,  # Use UUID directly
        reason=flag_data.reason,
        description=flag_data.description
    )
    
    db.add(flag)
    reply.is_flagged = True
    db.commit()
    
    return {"message": "Reply flagged for review"}


@router.get("/resources", response_model=List[EducationalResourceResponse])
async def get_resources(
    resource_type: Optional[str] = None,
    featured_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get educational resources.
    
    - **resource_type**: Filter by type (article, video, qa, guide)
    - **featured_only**: Only return featured resources
    - **skip**: Number of resources to skip (pagination)
    - **limit**: Maximum number of resources to return
    """
    query = db.query(EducationalResource)
    
    if resource_type:
        query = query.filter(EducationalResource.resource_type == resource_type)
    
    if featured_only:
        query = query.filter(EducationalResource.is_featured == True)
    
    resources = query.order_by(
        EducationalResource.is_featured.desc(),
        EducationalResource.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return resources


@router.get("/resources/{resource_id}", response_model=EducationalResourceResponse)
async def get_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific educational resource.
    
    - **resource_id**: ID of the resource to retrieve
    """
    resource = db.query(EducationalResource).filter(
        EducationalResource.id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Increment view count
    resource.view_count += 1
    db.commit()
    
    return resource


@router.get("/match-users", response_model=List[UserMatchResponse])
async def match_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Find users with similar risk profiles or disease stages.
    
    This endpoint matches users based on:
    - Similar risk assessment scores
    - Similar disease stage
    - Similar APOE genotype
    - Similar age range
    """
    from app.models.prediction import Prediction
    from app.models.assessment import Assessment
    
    # Get current user's latest prediction
    user_prediction = db.query(Prediction).filter(
        Prediction.user_id == str(current_user.id)
    ).order_by(Prediction.created_at.desc()).first()
    
    # Get current user's latest assessment
    user_assessment = db.query(Assessment).filter(
        Assessment.user_id == str(current_user.id)
    ).order_by(Assessment.completed_at.desc()).first()
    
    if not user_prediction and not user_assessment:
        return []
    
    matches = []
    
    # Find users with similar profiles
    other_users = db.query(User).filter(User.id != current_user.id).limit(50).all()
    
    for other_user in other_users:
        match_score = 0.0
        match_reasons = []
        risk_similarity = None
        stage_match = False
        
        # Check risk profile similarity
        if user_prediction:
            other_prediction = db.query(Prediction).filter(
                Prediction.user_id == str(other_user.id)
            ).order_by(Prediction.created_at.desc()).first()
            
            if other_prediction:
                risk_diff = abs(user_prediction.risk_score - other_prediction.risk_score)
                if risk_diff < 0.2:  # Similar risk within 20%
                    match_score += 0.4
                    risk_similarity = 1.0 - risk_diff
                    match_reasons.append("Similar risk profile")
        
        # Check disease stage similarity
        if user_assessment:
            other_assessment = db.query(Assessment).filter(
                Assessment.user_id == str(other_user.id)
            ).order_by(Assessment.completed_at.desc()).first()
            
            if other_assessment:
                score_diff = abs(user_assessment.score - other_assessment.score)
                if score_diff < 5:  # Similar cognitive scores
                    match_score += 0.3
                    stage_match = True
                    match_reasons.append("Similar cognitive function")
        
        # Check APOE genotype
        if current_user.apoe_genotype and other_user.apoe_genotype:
            if current_user.apoe_genotype == other_user.apoe_genotype:
                match_score += 0.2
                match_reasons.append("Same APOE genotype")
        
        # Check age similarity
        if current_user.date_of_birth and other_user.date_of_birth:
            age_diff_days = abs((current_user.date_of_birth - other_user.date_of_birth).days)
            if age_diff_days < 3650:  # Within 10 years
                match_score += 0.1
                match_reasons.append("Similar age")
        
        if match_score > 0.3:  # Minimum threshold for matching
            matches.append(UserMatchResponse(
                user_id=str(other_user.id),
                match_score=match_score,
                match_reasons=match_reasons,
                risk_profile_similarity=risk_similarity,
                disease_stage_match=stage_match
            ))
    
    # Sort by match score
    matches.sort(key=lambda x: x.match_score, reverse=True)
    
    return matches[:10]  # Return top 10 matches


@router.get("/social-feed")
async def get_social_feed(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get real social media posts from Alzheimer's organizations via RSS feeds.
    
    - **limit**: Maximum number of posts to return (1-50)
    
    Returns posts from:
    - Alzheimer's Association
    - National Institute on Aging
    - Alzheimer's Research UK
    """
    from app.services.social_media_service import get_social_media_posts
    
    try:
        posts = get_social_media_posts(db, limit)
        return {"posts": posts, "count": len(posts)}
    except Exception as e:
        # Return empty list if RSS feeds fail
        return {"posts": [], "count": 0, "error": str(e)}
