# ✅ Backend is Now Ready to Start!

All dependencies are installed and configured. Here's how to start:

## Quick Start

### Option 1: Start Backend Only (Fastest)

```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal open. You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Option 2: Start Everything with Docker

```bash
# From project root
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

## Verify Backend is Running

Open in browser or use curl:

```bash
# Test 1: Root endpoint
curl http://localhost:8000

# Expected: {"message": "MemoryGuard API", "version": "0.1.0", ...}

# Test 2: Health check
curl http://localhost:8000/health

# Test 3: API docs
open http://localhost:8000/docs
```

## What Was Fixed

1. ✅ Installed all Python dependencies (pydantic-settings, fastapi, etc.)
2. ✅ Updated requirements.txt for Python 3.13 compatibility
3. ✅ Fixed DATABASE_URL format in .env
4. ✅ Fixed CORS_ORIGINS format (must be JSON array)
5. ✅ Added Celery configuration

## Current Configuration

Your `backend/.env` is now configured with:

- **Database**: Local PostgreSQL (you'll need to start it)
- **Redis**: Local Redis (you'll need to start it)
- **Google OAuth**: Your credentials are set
- **CORS**: Allows localhost:5173 and localhost:3000

## Next Steps

### 1. Start Database (Choose One)

**Option A: Docker (Easiest)**
```bash
docker-compose up -d postgres redis
```

**Option B: Local PostgreSQL**
```bash
# Mac with Homebrew
brew services start postgresql
brew services start redis

# Or use Docker for just database
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=memoryguard postgres:15
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. Run Database Migrations

```bash
cd backend
python3 -m alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_create_users_table
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_create_health_data_tables
```

### 3. Start Backend

```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start Frontend (In Another Terminal)

```bash
cd frontend
npm install  # if not done already
npm run dev
```

### 5. Test Authentication

1. Open http://localhost:5173 (or :3000)
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Should redirect to dashboard

## Troubleshooting

### "Connection refused" to database

**Problem**: PostgreSQL not running

**Fix**:
```bash
# Start with Docker
docker-compose up -d postgres

# Or check if running locally
psql -U postgres -d memoryguard -c "SELECT 1"
```

### "Connection refused" to Redis

**Problem**: Redis not running

**Fix**:
```bash
# Start with Docker
docker-compose up -d redis

# Or check if running locally
redis-cli ping  # Should return PONG
```

### Google OAuth not working

**Problem**: Invalid credentials or redirect URI

**Fix**:
1. Go to https://console.cloud.google.com/apis/credentials
2. Edit your OAuth 2.0 Client ID
3. Add authorized redirect URIs:
   - `http://localhost:8000/api/v1/auth/google/callback`
   - `http://localhost:5173`
   - `http://localhost:3000`
4. Save and wait 5 minutes for changes to propagate

### Port 8000 already in use

**Problem**: Another process using port 8000

**Fix**:
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

## Complete Startup Sequence

```bash
# Terminal 1: Start services
docker-compose up -d postgres redis

# Terminal 2: Start backend
cd backend
python3 -m uvicorn app.main:app --reload

# Terminal 3: Start frontend
cd frontend
npm run dev

# Terminal 4: (Optional) Start Celery worker
cd backend
celery -A celery_worker worker --loglevel=info
```

## Verify Everything Works

1. ✅ Backend: http://localhost:8000
2. ✅ API Docs: http://localhost:8000/docs
3. ✅ Frontend: http://localhost:5173
4. ✅ Health: http://localhost:8000/health

## Summary

Your backend is now ready! Just need to:
1. Start PostgreSQL and Redis (docker-compose up -d postgres redis)
2. Run migrations (alembic upgrade head)
3. Start backend (uvicorn app.main:app --reload)
4. Start frontend (npm run dev)

Then you can test Google OAuth login! 🎉
