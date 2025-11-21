# Frontend Authentication Integration Guide

## Overview

Task 4 "Build frontend authentication flow" has been successfully completed. This document provides a quick start guide for testing and using the authentication system.

## What Was Implemented

### Components
1. **GoogleAuthButton** - Google OAuth sign-in button with callback handling
2. **ProtectedRoute** - Route wrapper for authenticated pages
3. **HomePage** - Landing page with authentication
4. **DashboardPage** - Protected dashboard demonstrating auth

### Services
1. **authService** - API calls for authentication endpoints
2. **apiClient** - Axios instance with automatic token refresh

### State Management
1. **authStore** - Zustand store for authentication state with persistence

## Quick Start

### 1. Setup Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable Google+ API
4. Create OAuth 2.0 Client ID
5. Add authorized JavaScript origins:
   - `http://localhost:3000`
6. Copy the Client ID

### 2. Configure Environment

```bash
cd frontend
cp .env.example .env
```

Edit `.env`:
```
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Install Dependencies

```bash
cd frontend
npm install
```

### 4. Start Backend

```bash
cd backend
# Ensure virtual environment is activated
uvicorn app.main:app --reload
```

Backend should be running on `http://localhost:8000`

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Testing the Authentication Flow

### Test 1: Login Flow
1. Navigate to `http://localhost:3000`
2. Click "Sign in with Google"
3. Complete Google authentication
4. Verify redirect to `/dashboard`
5. Verify user information displays

### Test 2: Protected Routes
1. Open new incognito window
2. Try to access `http://localhost:3000/dashboard`
3. Verify redirect to home page
4. Login and verify access granted

### Test 3: Logout
1. From dashboard, click "Logout"
2. Verify redirect to home page
3. Try accessing dashboard again
4. Verify redirect to home page

### Test 4: Session Persistence
1. Login to the application
2. Refresh the page
3. Verify you remain logged in
4. Close and reopen browser
5. Navigate to dashboard
6. Verify session persists

## API Endpoints

The frontend integrates with these backend endpoints:

- `POST /api/v1/auth/google` - Google OAuth authentication
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user info

## Using Authentication in New Components

### Check Authentication Status

```tsx
import { useAuthStore } from '../store/authStore';

function MyComponent() {
  const { isAuthenticated, user } = useAuthStore();
  
  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }
  
  return <div>Welcome, {user?.name}!</div>;
}
```

### Make Authenticated API Calls

```tsx
import apiClient from '../services/api';

async function fetchData() {
  try {
    const response = await apiClient.get('/health/metrics');
    return response.data;
  } catch (error) {
    console.error('API error:', error);
  }
}
```

### Protect a New Route

```tsx
import ProtectedRoute from './components/auth/ProtectedRoute';

<Route
  path="/my-protected-page"
  element={
    <ProtectedRoute>
      <MyProtectedPage />
    </ProtectedRoute>
  }
/>
```

### Logout User

```tsx
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

function LogoutButton() {
  const { logout } = useAuthStore();
  const navigate = useNavigate();
  
  const handleLogout = async () => {
    await logout();
    navigate('/');
  };
  
  return <button onClick={handleLogout}>Logout</button>;
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  HomePage    │  │  Dashboard   │  │ Other Pages  │  │
│  │  (Public)    │  │ (Protected)  │  │ (Protected)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┼──────────────────┘          │
│                           │                             │
│  ┌────────────────────────▼──────────────────────────┐  │
│  │         GoogleAuthButton / ProtectedRoute         │  │
│  └────────────────────────┬──────────────────────────┘  │
└───────────────────────────┼─────────────────────────────┘
                            │
                ┌───────────▼───────────┐
                │     Auth Store        │
                │     (Zustand)         │
                └───────────┬───────────┘
                            │
                ┌───────────▼───────────┐
                │    Auth Service       │
                └───────────┬───────────┘
                            │
                ┌───────────▼───────────┐
                │     API Client        │
                │  (Axios + Refresh)    │
                └───────────┬───────────┘
                            │
                            │ HTTP/HTTPS
                            │
                ┌───────────▼───────────┐
                │   Backend API         │
                │  /api/v1/auth/*       │
                └───────────────────────┘
```

## Token Flow

### Initial Login
```
1. User clicks Google Sign-In
2. Google OAuth popup → User authenticates
3. Google returns JWT token
4. Frontend → POST /api/v1/auth/google { token }
5. Backend verifies token with Google
6. Backend creates/updates user in database
7. Backend generates access + refresh tokens
8. Backend returns tokens + user info
9. Frontend stores access token in localStorage
10. Backend sets refresh token in HTTP-only cookie
11. Frontend updates auth store
12. Frontend redirects to dashboard
```

### Authenticated Request
```
1. Component makes API call via apiClient
2. Request interceptor adds Authorization header
3. Request sent to backend
4. Backend validates token
5. Backend processes request
6. Response returned to frontend
```

### Token Refresh
```
1. API request returns 401 Unauthorized
2. Response interceptor catches error
3. POST /api/v1/auth/refresh (with cookie)
4. Backend validates refresh token
5. Backend generates new access token
6. Frontend stores new access token
7. Original request retried with new token
8. Response returned to component
```

### Logout
```
1. User clicks logout
2. Frontend → POST /api/v1/auth/logout
3. Backend clears refresh token cookie
4. Frontend clears access token from localStorage
5. Frontend clears auth store
6. Frontend redirects to home page
```

## Security Features

1. **Access Token**: Short-lived (15 min), stored in localStorage
2. **Refresh Token**: Long-lived (7 days), HTTP-only cookie (XSS protection)
3. **Automatic Refresh**: Transparent token renewal on expiration
4. **CORS**: Configured with credentials support
5. **Token Validation**: Backend validates all tokens
6. **Secure Cookies**: HTTP-only, Secure, SameSite attributes

## Troubleshooting

### Google Sign-In Button Not Showing
- Check `VITE_GOOGLE_CLIENT_ID` is set in `.env`
- Verify Google OAuth credentials are configured
- Check browser console for errors
- Ensure authorized origins include `http://localhost:3000`

### 401 Errors
- Verify backend is running
- Check access token is being sent
- Try logging out and back in
- Check backend logs for token validation errors

### CORS Errors
- Verify backend CORS allows `http://localhost:3000`
- Check `withCredentials: true` in API client
- Ensure cookies are enabled in browser

### Token Refresh Failing
- Check refresh token cookie is being sent
- Verify backend `/auth/refresh` endpoint works
- Check cookie settings (httpOnly, secure, sameSite)
- Ensure backend CORS allows credentials

## Files Created

```
frontend/
├── src/
│   ├── components/auth/
│   │   ├── GoogleAuthButton.tsx      ✅ Google OAuth button
│   │   └── ProtectedRoute.tsx        ✅ Route protection
│   ├── pages/
│   │   ├── HomePage.tsx              ✅ Landing page
│   │   └── DashboardPage.tsx         ✅ Protected dashboard
│   ├── services/
│   │   ├── api.ts                    ✅ API client
│   │   └── authService.ts            ✅ Auth service
│   ├── store/
│   │   └── authStore.ts              ✅ Auth state
│   └── App.tsx                       ✅ Updated with routing
├── .env.example                      ✅ Environment template
├── AUTH_SETUP.md                     ✅ Setup documentation
└── FRONTEND_AUTH_VERIFICATION.md     ✅ Verification doc
```

## Requirements Met

✅ **Requirement 1.1**: Google OAuth authentication flow  
✅ **Requirement 1.2**: JWT token management with refresh  
✅ **Requirement 1.4**: Secure session with authentication checks  
✅ **Requirement 1.5**: Logout functionality with token cleanup  

## Next Steps

With authentication complete, you can now:

1. Build additional protected pages
2. Integrate with health metrics API
3. Implement ML prediction dashboard
4. Add cognitive assessment features
5. Create memory assistant tools

## Support

For detailed setup instructions, see:
- `frontend/AUTH_SETUP.md` - Comprehensive setup guide
- `frontend/FRONTEND_AUTH_VERIFICATION.md` - Implementation details
- `backend/AUTH_IMPLEMENTATION.md` - Backend auth documentation

## Summary

✅ All subtasks completed  
✅ TypeScript compilation successful  
✅ Production build successful  
✅ All requirements satisfied  
✅ Ready for integration with other features  

The frontend authentication system is production-ready and fully integrated with the backend authentication API.
