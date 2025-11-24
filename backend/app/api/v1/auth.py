"""
Authentication API endpoints.
Handles Google OAuth, token refresh, and logout.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_refresh_token, create_access_token
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user, get_refresh_token_from_cookie
from app.models.user import User
from app.core.audit import audit_logger
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _get_request_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Request/Response models
class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication"""
    token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "google_oauth_id_token_here"
            }
        }


class TokenResponse(BaseModel):
    """Response model for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict
    is_new_user: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "is_new_user": False,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "name": "John Doe"
                }
            }
        }


class RefreshTokenResponse(BaseModel):
    """Response model for token refresh"""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class DevLoginRequest(BaseModel):
    """Request model for dev login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "abbhivadhan279@gmail.com",
                "password": "123456"
            }
        }


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str
    name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "name": "John Doe"
            }
        }


class LoginRequest(BaseModel):
    """Request model for email/password login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


@router.post("/dev-login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def dev_login(
    login_request: DevLoginRequest,
    response: Response,
    request: Request
):
    """
    DEV ONLY: Simple login without database for testing.
    
    Hardcoded credentials:
    - Email: abbhivadhan279@gmail.com
    - Password: 123456
    
    This endpoint bypasses database and creates a mock user for development.
    """
    import os
    from datetime import datetime
    from app.core.security import create_access_token, create_refresh_token
    
    # Check if in development mode
    if os.getenv("ENVIRONMENT", "development") != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev login only available in development mode"
        )
    
    # Hardcoded dev credentials
    if login_request.email != "abbhivadhan279@gmail.com" or login_request.password != "123456":
        audit_logger.log_auth_event(
            action="dev_login",
            result="failure",
            ip=_get_request_ip(request),
            metadata={"reason": "invalid_credentials"},
            request_id=getattr(request.state, "request_id", None),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create mock user data
    user_data = {
        "id": "00000000-0000-0000-0000-000000000001",  # Valid UUID for dev user
        "email": "abbhivadhan279@gmail.com",
        "name": "Dev User",
        "created_at": datetime.utcnow().isoformat(),
        "last_active": datetime.utcnow().isoformat()
    }
    
    # Create tokens
    token_data = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "name": user_data["name"]
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Set refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # False for local dev
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    audit_logger.log_auth_event(
        action="dev_login",
        result="success",
        user_id=user_data["id"],
        email=user_data["email"],
        ip=_get_request_ip(request),
        metadata={"provider": "dev"},
        request_id=getattr(request.state, "request_id", None),
    )
    logger.info(f"Dev user logged in: {user_data['email']}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_data,
        is_new_user=False
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_request: RegisterRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.
    
    This endpoint:
    1. Validates the email is not already registered
    2. Hashes the password securely
    3. Creates a new user in the database
    4. Generates JWT access and refresh tokens
    5. Sets refresh token as HTTP-only cookie
    
    Args:
        register_request: User registration data
        response: FastAPI response object for setting cookies
        request: FastAPI request object
        db: Database session
        
    Returns:
        TokenResponse with access token, refresh token, and user info
        
    Raises:
        HTTPException: If email is already registered or validation fails
    """
    try:
        # Check if user already exists
        existing_user = AuthService.get_user_by_email(db, register_request.email)
        if existing_user:
            audit_logger.log_auth_event(
                action="register",
                result="failure",
                email=register_request.email,
                ip=_get_request_ip(request),
                metadata={"reason": "email_already_exists"},
                request_id=getattr(request.state, "request_id", None),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user with hashed password
        user = AuthService.create_user_with_password(
            db=db,
            email=register_request.email,
            password=register_request.password,
            name=register_request.name or register_request.email.split('@')[0]
        )
        
        # Create JWT tokens
        tokens = AuthService.create_tokens_for_user(user)
        
        # Set refresh token as HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        audit_logger.log_auth_event(
            action="register",
            result="success",
            user_id=str(user.id),
            email=user.email,
            ip=_get_request_ip(request),
            metadata={"provider": "email"},
            request_id=getattr(request.state, "request_id", None),
        )
        logger.info(f"New user registered: {user.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user.to_dict(),
            is_new_user=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_auth_event(
            action="register",
            result="error",
            email=register_request.email,
            ip=_get_request_ip(request),
            metadata={"reason": str(e)},
            request_id=getattr(request.state, "request_id", None),
        )
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_request: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login user with email and password.
    
    This endpoint:
    1. Validates the email and password
    2. Generates JWT access and refresh tokens
    3. Sets refresh token as HTTP-only cookie
    
    Args:
        login_request: User login credentials
        response: FastAPI response object for setting cookies
        request: FastAPI request object
        db: Database session
        
    Returns:
        TokenResponse with access token, refresh token, and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user_metadata = {"id": None, "email": login_request.email}
    
    try:
        # Authenticate user
        user = AuthService.authenticate_user(
            db=db,
            email=login_request.email,
            password=login_request.password
        )
        
        if not user:
            audit_logger.log_auth_event(
                action="login",
                result="failure",
                email=login_request.email,
                ip=_get_request_ip(request),
                metadata={"reason": "invalid_credentials"},
                request_id=getattr(request.state, "request_id", None),
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_metadata["id"] = str(user.id)
        
        # Create JWT tokens
        tokens = AuthService.create_tokens_for_user(user)
        
        # Set refresh token as HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        audit_logger.log_auth_event(
            action="login",
            result="success",
            user_id=user_metadata["id"],
            email=user_metadata["email"],
            ip=_get_request_ip(request),
            metadata={"provider": "email"},
            request_id=getattr(request.state, "request_id", None),
        )
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user.to_dict(),
            is_new_user=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_auth_event(
            action="login",
            result="error",
            user_id=user_metadata["id"],
            email=user_metadata["email"],
            ip=_get_request_ip(request),
            metadata={"reason": str(e)},
            request_id=getattr(request.state, "request_id", None),
        )
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/google", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def google_auth(
    auth_request: GoogleAuthRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth token.
    
    This endpoint:
    1. Verifies the Google OAuth token
    2. Creates or updates the user in the database
    3. Generates JWT access and refresh tokens
    4. Sets refresh token as HTTP-only cookie
    
    Args:
        auth_request: Google OAuth token
        response: FastAPI response object for setting cookies
        db: Database session
        
    Returns:
        TokenResponse with access token, refresh token, and user info
        
    Raises:
        HTTPException: If Google token verification fails
    """
    user_metadata = {"id": None, "email": None}
    
    try:
        # Verify Google token and get user info
        user_info = await AuthService.verify_google_token(auth_request.token)
        
        # Get or create user
        user, is_new_user = AuthService.get_or_create_user(db, user_info)
        user_metadata["id"] = str(user.id)
        user_metadata["email"] = user.email
        
        # Create JWT tokens
        tokens = AuthService.create_tokens_for_user(user)
        
        # Set refresh token as HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        audit_logger.log_auth_event(
            action="google_login",
            result="success",
            user_id=user_metadata["id"],
            email=user_metadata["email"],
            ip=_get_request_ip(request),
            metadata={"provider": "google", "is_new_user": is_new_user},
            request_id=getattr(request.state, "request_id", None),
        )
        logger.info(f"User authenticated successfully: {user.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user.to_dict(),
            is_new_user=is_new_user
        )
        
    except HTTPException as exc:
        audit_logger.log_auth_event(
            action="google_login",
            result="failure",
            user_id=user_metadata["id"],
            email=user_metadata["email"],
            ip=_get_request_ip(request),
            metadata={"reason": exc.detail},
            request_id=getattr(request.state, "request_id", None),
        )
        raise
    except Exception as e:
        audit_logger.log_auth_event(
            action="google_login",
            result="error",
            user_id=user_metadata["id"],
            email=user_metadata["email"],
            ip=_get_request_ip(request),
            metadata={"reason": str(e)},
            request_id=getattr(request.state, "request_id", None),
        )
        logger.error(f"Authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: Request,
    refresh_token: str = Depends(get_refresh_token_from_cookie),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token from HTTP-only cookie.
    
    This endpoint:
    1. Validates the refresh token from cookie
    2. Generates a new access token
    3. Returns the new access token
    
    Args:
        refresh_token: Refresh token from HTTP-only cookie
        db: Database session
        
    Returns:
        RefreshTokenResponse with new access token
        
    Raises:
        HTTPException: If refresh token is invalid or user not found
    """
    user_id = None
    
    try:
        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        user = AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name
        }
        access_token = create_access_token(token_data)
        
        audit_logger.log_auth_event(
            action="refresh",
            result="success",
            user_id=str(user.id),
            email=user.email,
            ip=_get_request_ip(request),
            request_id=getattr(request.state, "request_id", None),
        )
        logger.info(f"Token refreshed for user: {user.email}")
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer"
        )
        
    except HTTPException as exc:
        audit_logger.log_auth_event(
            action="refresh",
            result="failure",
            user_id=user_id,
            ip=_get_request_ip(request),
            metadata={"reason": exc.detail},
            request_id=getattr(request.state, "request_id", None),
        )
        raise
    except Exception as e:
        audit_logger.log_auth_event(
            action="refresh",
            result="error",
            user_id=user_id,
            ip=_get_request_ip(request),
            metadata={"reason": str(e)},
            request_id=getattr(request.state, "request_id", None),
        )
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Logout user by clearing refresh token cookie.
    
    This endpoint:
    1. Validates the user is authenticated
    2. Clears the refresh token cookie
    3. Returns success message
    
    Note: The client should also clear the access token from local storage.
    
    Args:
        response: FastAPI response object for clearing cookies
        current_user: Current authenticated user
        
    Returns:
        MessageResponse with logout confirmation
    """
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    audit_logger.log_auth_event(
        action="logout",
        result="success",
        user_id=str(current_user.id),
        email=current_user.email,
        ip=_get_request_ip(request),
        request_id=getattr(request.state, "request_id", None),
    )
    logger.info(f"User logged out: {current_user.email}")
    
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=dict, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    This endpoint returns the profile information of the currently
    authenticated user based on their JWT token.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile information
    """
    return current_user.to_dict()
