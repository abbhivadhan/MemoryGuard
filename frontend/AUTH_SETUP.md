# Frontend Authentication Setup

This document describes the frontend authentication implementation for MemoryGuard.

## Overview

The authentication system uses Google OAuth 2.0 for user authentication, with JWT tokens for session management. The implementation includes:

- Google OAuth button component
- Zustand state management for auth state
- Protected route wrapper for authenticated pages
- API client with automatic token refresh
- Token storage and management utilities

## Architecture

### Components

1. **GoogleAuthButton** (`src/components/auth/GoogleAuthButton.tsx`)
   - Renders Google Sign-In button
   - Handles OAuth callback
   - Integrates with auth store

2. **ProtectedRoute** (`src/components/auth/ProtectedRoute.tsx`)
   - Wraps protected pages
   - Checks authentication status
   - Redirects to login if not authenticated

### Services

1. **authService** (`src/services/authService.ts`)
   - API calls for authentication endpoints
   - Token storage utilities
   - User information retrieval

2. **apiClient** (`src/services/api.ts`)
   - Axios instance with interceptors
   - Automatic token refresh on 401
   - Request/response error handling

### State Management

**authStore** (`src/store/authStore.ts`)
- Zustand store with persistence
- Authentication state (user, isAuthenticated, isLoading, error)
- Actions: login, logout, refreshToken, fetchCurrentUser

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the frontend directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Google OAuth Client ID:

```
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure OAuth consent screen
6. Add authorized JavaScript origins:
   - `http://localhost:3000` (development)
   - Your production domain
7. Copy the Client ID to your `.env` file

### 4. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Usage

### Authentication Flow

1. User clicks "Sign in with Google" button on home page
2. Google OAuth popup appears
3. User authenticates with Google
4. Google returns JWT token
5. Frontend sends token to backend `/api/v1/auth/google`
6. Backend verifies token and returns access/refresh tokens
7. Frontend stores tokens and redirects to dashboard

### Token Management

- **Access Token**: Stored in localStorage, expires in 15 minutes
- **Refresh Token**: Stored in HTTP-only cookie, expires in 7 days
- Automatic refresh on 401 responses
- Manual refresh available via `refreshToken()` action

### Protected Routes

Wrap any route that requires authentication:

```tsx
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <DashboardPage />
    </ProtectedRoute>
  }
/>
```

### Using Auth Store

```tsx
import { useAuthStore } from '../store/authStore';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuthStore();

  // Check if user is authenticated
  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  // Access user information
  return <div>Welcome, {user?.name}!</div>;
}
```

### Making Authenticated API Calls

```tsx
import apiClient from '../services/api';

// API client automatically adds Authorization header
const response = await apiClient.get('/health/metrics');
```

## API Endpoints

### POST /api/v1/auth/google
Authenticate with Google OAuth token

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
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

### POST /api/v1/auth/refresh
Refresh access token using refresh token from cookie

**Response:**
```json
{
  "access_token": "new_jwt_access_token",
  "token_type": "bearer"
}
```

### POST /api/v1/auth/logout
Logout user and clear refresh token cookie

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### GET /api/v1/auth/me
Get current user information

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "User Name",
  "createdAt": "2025-01-01T00:00:00Z"
}
```

## Security Features

1. **HTTP-only Cookies**: Refresh tokens stored in HTTP-only cookies to prevent XSS
2. **Automatic Token Refresh**: Access tokens refreshed automatically on expiration
3. **CORS Configuration**: Proper CORS setup with credentials support
4. **Token Validation**: Backend validates all tokens before processing requests
5. **Secure Storage**: Sensitive data stored securely

## Troubleshooting

### Google Sign-In Button Not Appearing

- Check that `VITE_GOOGLE_CLIENT_ID` is set in `.env`
- Verify Google OAuth credentials are configured correctly
- Check browser console for errors
- Ensure authorized JavaScript origins include your domain

### 401 Unauthorized Errors

- Check that access token is being sent in Authorization header
- Verify backend is running and accessible
- Check token expiration
- Try logging out and logging in again

### Token Refresh Failing

- Verify refresh token cookie is being sent
- Check backend `/auth/refresh` endpoint is working
- Ensure `withCredentials: true` is set in axios config
- Check CORS configuration allows credentials

### CORS Errors

- Verify backend CORS configuration includes frontend origin
- Check that `withCredentials: true` is set in API client
- Ensure cookies are allowed in browser settings

## Testing

To test the authentication flow:

1. Start backend server: `cd backend && uvicorn app.main:app --reload`
2. Start frontend server: `cd frontend && npm run dev`
3. Navigate to `http://localhost:3000`
4. Click "Sign in with Google"
5. Complete Google authentication
6. Verify redirect to dashboard
7. Check that user information is displayed
8. Test logout functionality

## Next Steps

- Implement additional protected pages
- Add role-based access control
- Implement password reset flow (if adding email/password auth)
- Add multi-factor authentication
- Implement session timeout warnings
- Add remember me functionality
