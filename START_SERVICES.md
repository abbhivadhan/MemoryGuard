# Quick Start Services

## The Problem

You're getting "network error" because the backend API server is not running.

## Solution: Start the Backend

### Option 1: Using Docker (Recommended - Easiest)

```bash
# From project root directory
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f backend
```

This will start:
- ✅ Backend API (port 8000)
- ✅ Frontend (port 3000)
- ✅ PostgreSQL database
- ✅ Redis
- ✅ Celery worker

### Option 2: Run Backend Manually

```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Keep this terminal open - you should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

```bash
# Terminal 2: Start Frontend
cd frontend
npm run dev

# Keep this terminal open - you should see:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

## Verify Backend is Running

Open your browser or use curl:

```bash
# Test 1: Root endpoint
curl http://localhost:8000

# Expected response:
# {
#   "message": "MemoryGuard API",
#   "version": "0.1.0",
#   "status": "running"
# }

# Test 2: Health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy" or "degraded",
#   "services": {...}
# }
```

Or open in browser:
- http://localhost:8000 - Should show API info
- http://localhost:8000/docs - Should show Swagger API documentation

## Fix Google OAuth

Your `backend/.env` has a placeholder for Google Client Secret:

```bash
GOOGLE_CLIENT_SECRET=your-google-client-secret-here  # ❌ This won't work
```

### Get Real Google OAuth Credentials:

1. Go to https://console.cloud.google.com/
2. Create a project or select existing
3. Go to "APIs & Services" → "Credentials"
4. Create "OAuth 2.0 Client ID"
5. Add these authorized origins:
   - `http://localhost:5173`
   - `http://localhost:3000`
   - `http://localhost:8000`
6. Add these redirect URIs:
   - `http://localhost:8000/api/v1/auth/google/callback`
   - `http://localhost:5173`
7. Copy the Client ID and Client Secret
8. Update `backend/.env`:
   ```bash
   GOOGLE_CLIENT_ID=YOUR_REAL_CLIENT_ID.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=YOUR_REAL_CLIENT_SECRET
   ```
9. Update `frontend/.env`:
   ```bash
   VITE_GOOGLE_CLIENT_ID=YOUR_REAL_CLIENT_ID.apps.googleusercontent.com
   ```
10. Restart backend and frontend

## Complete Startup Sequence

```bash
# 1. Start all services with Docker
docker-compose up -d

# 2. Wait 10 seconds for services to start

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. Check backend is healthy
curl http://localhost:8000/health

# 5. Open frontend
open http://localhost:3000
# or
open http://localhost:5173

# 6. Try logging in with Google
```

## If Still Having Issues

### Check What's Running

```bash
# Check Docker containers
docker-compose ps

# Check ports
lsof -i :8000  # Backend should be here
lsof -i :5173  # Frontend (Vite)
lsof -i :3000  # Frontend (alternative)
```

### View Logs

```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend
docker-compose logs -f frontend
```

### Restart Everything

```bash
# Stop all
docker-compose down

# Start fresh
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Summary

**To fix "network error":**

1. ✅ Start backend: `docker-compose up -d` or `uvicorn app.main:app --reload`
2. ✅ Verify backend running: `curl http://localhost:8000`
3. ✅ Configure Google OAuth with real credentials
4. ✅ Restart services after config changes
5. ✅ Try logging in again

**The main issue is the backend is not running!** Start it first, then authentication will work.
