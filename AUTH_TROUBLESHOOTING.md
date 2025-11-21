# Authentication Troubleshooting Guide

## Current Issues

### 1. Network Error - Backend Not Running ❌

**Problem**: Frontend cannot connect to backend API

**Solution**: Start the backend server

```bash
cd backend

# Option 1: Direct Python
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Docker
cd ..
docker-compose up backend
```

**Verify**: Open http://localhost:8000 - you should see:
```json
{
  "message": "MemoryGuard API",
  "version": "0.1.0",
  "status": "running"
}
```

### 2. Google OAuth Not Configured ❌

**Problem**: `GOOGLE_CLIENT_SECRET` is set to placeholder value

**Current in backend/.env**:
```bash
GOOGLE_CLIENT_SECRET=your-google-client-secret-here  # ❌ Not real
```

**Solution**: Get real Google OAuth credentials

#### Step-by-Step Google OAuth Setup:

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create/Select Project**
   - Click "Select a project" → "New Project"
   - Name: `memoryguard` or your choice
   - Click "Create"

3. **Enable Google+ API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "MemoryGuard Web Client"

5. **Configure OAuth Consent Screen** (if prompted)
   - User Type: "External"
   - App name: "MemoryGuard"
   - User support email: your email
   - Developer contact: your email
   - Click "Save and Continue"
   - Scopes: Add `email`, `profile`, `openid`
   - Test users: Add your email
   - Click "Save and Continue"

6. **Add Authorized Origins and Redirect URIs**
   
   **Authorized JavaScript origins**:
   ```
   http://localhost:5173
   http://localhost:3000
   http://localhost:8000
   ```
   
   **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/v1/auth/google/callback
   http://localhost:5173
   http://localhost:3000
   ```

7. **Copy Credentials**
   - Copy "Client ID" (looks like: `xxxxx.apps.googleusercontent.com`)
   - Copy "Client secret" (looks like: `GOCSPX-xxxxx`)

8. **Update Environment Files**

   **backend/.env**:
   ```bash
   GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=YOUR_ACTUAL_CLIENT_SECRET
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
   ```

   **frontend/.env**:
   ```bash
   VITE_GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com
   ```

### 3. Database Not Configured ❌

**Problem**: Database URL points to local PostgreSQL instead of Supabase

**Current in backend/.env**:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/memoryguard
```

**Solution**: Update to use Supabase or start local PostgreSQL

#### Option A: Use Supabase (Recommended)

1. Get your Supabase connection string from dashboard
2. Update `backend/.env`:
   ```bash
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
   ```

#### Option B: Use Local PostgreSQL

1. Start PostgreSQL with Docker:
   ```bash
   docker-compose up postgres
   ```

2. Keep current DATABASE_URL in `backend/.env`

### 4. Redis Not Running ❌

**Problem**: Redis connection may fail

**Solution**: Start Redis

```bash
# With Docker
docker-compose up redis

# Or install locally (Mac)
brew install redis
brew services start redis
```

## Quick Fix Steps

### 1. Start All Services with Docker (Easiest)

```bash
# From project root
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

This starts:
- PostgreSQL (local database)
- Redis (caching)
- Backend (FastAPI)
- Frontend (React)
- Celery Worker (ML processing)

### 2. Configure Google OAuth

Follow steps above to get real credentials and update `.env` files.

### 3. Run Database Migrations

```bash
# If using Docker
docker-compose exec backend alembic upgrade head

# If running locally
cd backend
alembic upgrade head
```

### 4. Restart Services

```bash
# Docker
docker-compose restart backend frontend

# Or locally
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

## Verification Steps

### 1. Check Backend is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "0.1.0",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### 2. Check Frontend is Running

Open: http://localhost:5173 or http://localhost:3000

You should see the homepage with 3D animations.

### 3. Test Google OAuth

1. Click "Sign in with Google" button
2. Google popup should appear
3. Select your Google account
4. Should redirect back and log you in

### 4. Check Browser Console

Open browser DevTools (F12) → Console tab

**Good signs**:
- No red errors
- API calls to `http://localhost:8000/api/v1/...`
- Successful responses (200 status)

**Bad signs**:
- `ERR_CONNECTION_REFUSED` → Backend not running
- `401 Unauthorized` → Auth not configured
- `CORS error` → CORS not configured properly

## Common Errors and Solutions

### Error: "Network Error"

**Cause**: Backend not running or wrong URL

**Fix**:
1. Start backend: `docker-compose up backend`
2. Check `frontend/.env` has correct `VITE_API_URL=http://localhost:8000/api/v1`
3. Verify backend is accessible: `curl http://localhost:8000`

### Error: "Invalid Google token"

**Cause**: Google Client ID/Secret mismatch or not configured

**Fix**:
1. Verify `GOOGLE_CLIENT_ID` matches in both frontend and backend `.env`
2. Verify `GOOGLE_CLIENT_SECRET` is real (not placeholder)
3. Check Google Cloud Console credentials are correct
4. Ensure redirect URIs are configured in Google Console

### Error: "CORS policy blocked"

**Cause**: CORS not configured for frontend origin

**Fix**:
1. Check `backend/.env` has: `CORS_ORIGINS=http://localhost:5173,http://localhost:3000`
2. Restart backend after changing CORS settings
3. Clear browser cache and reload

### Error: "Database connection failed"

**Cause**: Database not running or wrong connection string

**Fix**:
1. Start database: `docker-compose up postgres` or use Supabase
2. Verify `DATABASE_URL` in `backend/.env`
3. Run migrations: `alembic upgrade head`
4. Test connection: `python backend/scripts/verify_supabase.py`

### Error: "Redis connection failed"

**Cause**: Redis not running

**Fix**:
1. Start Redis: `docker-compose up redis`
2. Verify `REDIS_URL` in `backend/.env`
3. Test: `redis-cli ping` (should return PONG)

## Complete Working Configuration

### backend/.env (Example)

```bash
# Application
APP_NAME=MemoryGuard
DEBUG=True
ENVIRONMENT=development

# Database (choose one)
# Option 1: Local PostgreSQL
DATABASE_URL=postgresql://memoryguard:memoryguard@localhost:5432/memoryguard

# Option 2: Supabase
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=your-super-secret-key-change-this
JWT_ALGORITHM=HS256

# Google OAuth (MUST BE REAL VALUES)
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_actual_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### frontend/.env (Example)

```bash
# Google OAuth (MUST MATCH BACKEND)
VITE_GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com

# API URL
VITE_API_URL=http://localhost:8000/api/v1
```

## Testing Authentication Flow

### 1. Manual Test

```bash
# 1. Start backend
cd backend
uvicorn app.main:app --reload

# 2. In another terminal, start frontend
cd frontend
npm run dev

# 3. Open browser to http://localhost:5173
# 4. Click "Sign in with Google"
# 5. Complete OAuth flow
# 6. Should see dashboard
```

### 2. API Test

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test auth endpoint (will fail without valid Google token)
curl -X POST http://localhost:8000/api/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{"token": "fake_token"}'
```

## Still Having Issues?

### Enable Debug Logging

**Backend** (`backend/.env`):
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

**Frontend** (Browser Console):
- Open DevTools (F12)
- Go to Network tab
- Filter by "XHR" or "Fetch"
- Watch API calls and responses

### Check Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Or if running locally, check terminal output
```

### Verify Ports

```bash
# Check if ports are in use
lsof -i :8000  # Backend
lsof -i :5173  # Frontend (Vite)
lsof -i :3000  # Frontend (alternative)
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
```

## Need Help?

1. Check all environment variables are set correctly
2. Ensure all services are running
3. Check browser console for errors
4. Check backend logs for errors
5. Verify Google OAuth credentials are correct
6. Try clearing browser cache and localStorage

## Quick Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173 or :3000
- [ ] PostgreSQL or Supabase database accessible
- [ ] Redis running
- [ ] Google OAuth credentials configured (real values, not placeholders)
- [ ] CORS configured correctly
- [ ] Database migrations run
- [ ] No errors in browser console
- [ ] No errors in backend logs

Once all items are checked, authentication should work!
