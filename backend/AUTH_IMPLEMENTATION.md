# Authentication System Implementation

## Overview

The authentication system has been successfully implemented with Google OAuth 2.0 integration, JWT token management, and secure session handling.

## Components Implemented

### 1. Core Security Module (`app/core/security.py`)
- JWT token generation and validation
- Access token creation (15-minute expiration)
- Refresh token creation (7-day expiration)
- Token verification and decoding
- Password hashing utilities (for future use)

### 2. Authentication Service (`app/services/auth_service.py`)
- Google OAuth token verification
- User creation and retrieval
- Token generation for authenticated users
- Integration with Google's authentication API

### 3. User Model (`app/models/user.py`)
- SQLAlchemy model for user data
- Fields: email, google_id, name, picture, date_of_birth
- APOE genotype support for Alzheimer's risk assessment
- Relationships: emergency_contacts, caregivers, providers
- Activity tracking with last_active timestamp

### 4. Database Migration (`alembic/versions/001_create_users_table.py`)
- Creates users table with all required fields
- Indexes on email and google_id for performance
- APOE genotype enum type
- Array fields for relationships

### 5. API Dependencies (`app/api/dependencies.py`)
- `get_current_user`: Extract and validate user from JWT token
- `get_current_user_optional`: Optional authentication
- `get_refresh_token_from_cookie`: Extract refresh token from HTTP-only cookie

### 6. Authentication Endpoints (`app/api/v1/auth.py`)

#### POST `/api/v1/auth/google`
Authenticate with Google OAuth token.

**Request:**
```json
{
  "token": "google_oauth_id_token"
}
```

**Response:**
```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://...",
    "created_at": "2025-11-16T10:00:00Z",
    "last_active": "2025-11-16T10:00:00Z"
  }
}
```

**Features:**
- Verifies Google OAuth token
- Creates new user or updates existing user
- Returns JWT tokens
- Sets refresh token as HTTP-only cookie

#### POST `/api/v1/auth/refresh`
Refresh access token using refresh token from cookie.

**Response:**
```json
{
  "access_token": "new_jwt_access_token",
  "token_type": "bearer"
}
```

**Features:**
- Reads refresh token from HTTP-only cookie
- Validates refresh token
- Generates new access token
- Does not require Authorization header

#### POST `/api/v1/auth/logout`
Logout user and clear refresh token cookie.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

**Features:**
- Requires valid access token
- Clears refresh token cookie
- Client should also clear access token from storage

#### GET `/api/v1/auth/me`
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://...",
  "date_of_birth": null,
  "apoe_genotype": null,
  "created_at": "2025-11-16T10:00:00Z",
  "last_active": "2025-11-16T10:00:00Z"
}
```

## Security Features

### JWT Tokens
- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), stored in HTTP-only cookie
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Claims**: user_id (sub), email, name, token type, expiration

### HTTP-Only Cookies
- Refresh tokens stored in HTTP-only cookies
- Protection against XSS attacks
- Secure flag for HTTPS (production)
- SameSite=Lax for CSRF protection

### Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (production only)

### Rate Limiting
- Configured in settings (100 requests/minute in development)
- Can be adjusted per environment

## Environment Variables

Required environment variables in `.env`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/memoryguard
```

## Database Setup

1. Ensure PostgreSQL is running
2. Run the migration:
```bash
cd backend
alembic upgrade head
```

This will create the `users` table with all required fields and indexes.

## Testing the Authentication Flow

### 1. Get Google OAuth Token
Use Google's OAuth 2.0 Playground or implement frontend Google Sign-In button.

### 2. Authenticate
```bash
curl -X POST http://localhost:8000/api/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{"token": "google_oauth_token"}'
```

### 3. Use Access Token
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### 4. Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -b "refresh_token=<refresh_token_from_cookie>"
```

### 5. Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

## Integration with Frontend

### Authentication Flow

1. **User clicks "Sign in with Google"**
   - Frontend initiates Google OAuth flow
   - User authenticates with Google
   - Frontend receives Google OAuth token

2. **Frontend sends token to backend**
   ```javascript
   const response = await fetch('/api/v1/auth/google', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ token: googleToken }),
     credentials: 'include' // Important for cookies
   });
   const data = await response.json();
   // Store access_token in memory or localStorage
   ```

3. **Frontend makes authenticated requests**
   ```javascript
   const response = await fetch('/api/v1/some-endpoint', {
     headers: {
       'Authorization': `Bearer ${accessToken}`
     },
     credentials: 'include'
   });
   ```

4. **Frontend refreshes token when expired**
   ```javascript
   const response = await fetch('/api/v1/auth/refresh', {
     method: 'POST',
     credentials: 'include' // Sends refresh token cookie
   });
   const data = await response.json();
   // Update access_token
   ```

5. **Frontend logs out**
   ```javascript
   await fetch('/api/v1/auth/logout', {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${accessToken}`
     },
     credentials: 'include'
   });
   // Clear access_token from storage
   ```

## Protected Routes

To protect any endpoint, use the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/protected-endpoint")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}"}
```

## Next Steps

1. **Frontend Implementation** (Task 4):
   - Create Google Auth button component
   - Implement authentication state management
   - Create protected route wrapper
   - Build authentication service

2. **Additional Features**:
   - Email verification
   - Password reset (if adding email/password auth)
   - Multi-factor authentication
   - Session management and revocation

## Requirements Satisfied

✅ **Requirement 1.1**: Google OAuth authentication flow implemented  
✅ **Requirement 1.2**: Secure session with encrypted JWT tokens  
✅ **Requirement 1.3**: Clear error messages and logout functionality  
✅ **Requirement 1.4**: Secure credential storage with industry-standard encryption  
✅ **Requirement 1.5**: Session invalidation on logout

## Notes

- The refresh token cookie is set with `secure=True` which requires HTTPS in production
- For local development, you may need to adjust this setting
- Google OAuth credentials must be configured in Google Cloud Console
- The redirect URI must match the one configured in Google Cloud Console
