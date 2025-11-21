"""
Authentication service for handling Google OAuth and user authentication.
"""
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations"""
    
    @staticmethod
    async def verify_google_token(token: str) -> Dict[str, Any]:
        """
        Verify Google OAuth token and extract user information.
        
        Args:
            token: Google OAuth ID token
            
        Returns:
            Dictionary containing user information from Google
            
        Raises:
            HTTPException: If token verification fails
        """
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Extract user information
            user_info = {
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'google_id': idinfo.get('sub'),
                'picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False)
            }
            
            logger.info(f"Successfully verified Google token for user: {user_info['email']}")
            return user_info
            
        except ValueError as e:
            logger.error(f"Google token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during Google token verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify Google token"
            )
    
    @staticmethod
    def get_or_create_user(db: Session, user_info: Dict[str, Any]) -> User:
        """
        Get existing user or create new user from Google OAuth information.
        
        Args:
            db: Database session
            user_info: User information from Google OAuth
            
        Returns:
            User model instance
        """
        # Check if user exists
        user = db.query(User).filter(User.email == user_info['email']).first()
        
        if user:
            # Update user information if needed
            user.name = user_info['name']
            user.picture = user_info.get('picture')
            user.last_active = db.query(User).filter(User.id == user.id).first().updated_at
            db.commit()
            db.refresh(user)
            logger.info(f"Existing user logged in: {user.email}")
        else:
            # Create new user
            user = User(
                email=user_info['email'],
                name=user_info['name'],
                google_id=user_info['google_id'],
                picture=user_info.get('picture')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created: {user.email}")
        
        return user
    
    @staticmethod
    def create_tokens_for_user(user: User) -> Dict[str, str]:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: User model instance
            
        Returns:
            Dictionary containing access_token and refresh_token
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User UUID as string
            
        Returns:
            User model instance or None
        """
        return db.query(User).filter(User.id == user_id).first()
