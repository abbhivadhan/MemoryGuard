# Backend Core Infrastructure Setup

This document describes the backend core infrastructure that has been set up for the MemoryGuard application.

## Components Implemented

### 1. FastAPI Application with CORS and Middleware

**Location:** `backend/app/main.py`

**Features:**
- FastAPI application with proper configuration
- CORS middleware configured for frontend communication
- Request logging middleware that logs all requests and responses with timing
- Security headers middleware (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS)
- Global exception handler for consistent error responses
- Lifespan events for startup/shutdown operations
- Health check endpoint that verifies database and Redis connections

**Endpoints:**
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint with service status

### 2. Supabase Database with SQLAlchemy

**Location:** `backend/app/core/database.py`

**Features:**
- SQLAlchemy engine configured for Supabase PostgreSQL
- Connection pooling with QueuePool (5 connections, 10 max overflow)
- Pool pre-ping for connection verification
- Connection recycling after 1 hour
- Base model class for all database models
- Database session dependency for FastAPI routes
- Connection health check function
- Event listeners for connection monitoring

**Base Model:** `backend/app/models/base.py`
- UUID primary key
- Automatic timestamps (created_at, updated_at)
- to_dict() method for serialization

**Alembic Migrations:** `backend/alembic/env.py`
- Configured to use settings from config.py
- Auto-imports Base metadata for autogenerate support
- Ready for database migrations

### 3. Redis for Caching and Sessions

**Location:** `backend/app/core/redis.py`

**Features:**
- Redis client wrapper with connection management
- Health check functionality
- Cache utility functions:
  - `get_cache(key)` - Retrieve cached value
  - `set_cache(key, value, expire)` - Store value with expiration
  - `delete_cache(key)` - Delete cached value
  - `clear_cache_pattern(pattern)` - Delete keys matching pattern
- Session management functions:
  - `set_session(session_id, data, expire)` - Store session data
  - `get_session(session_id)` - Retrieve session data
  - `delete_session(session_id)` - Delete session
  - `extend_session(session_id, expire)` - Extend session expiration
- Rate limiting utility:
  - `check_rate_limit(identifier, limit, window)` - Check if within rate limit

### 4. Environment Configuration Management

**Location:** `backend/app/core/config.py`

**Features:**
- Pydantic-based settings with environment variable support
- Three environment configurations:
  - `DevelopmentSettings` - Debug enabled, verbose logging
  - `StagingSettings` - Debug disabled, info logging
  - `ProductionSettings` - Debug disabled, warning logging, stricter rate limits
- Environment-specific properties:
  - `is_development`, `is_staging`, `is_production`
- Production settings validation
- Cached settings instance using `@lru_cache()`

**Configuration Options:**
- Application settings (name, version, debug, environment)
- Supabase database connection
- Redis connection
- JWT security settings
- Google OAuth credentials
- CORS origins
- Rate limiting
- File upload settings
- ML model settings
- Celery configuration
- Logging configuration

## Environment Variables

Copy `.env.example` to `.env` and configure the following:

### Required for Supabase:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### Required for Production:
- `JWT_SECRET` - Must be changed from default
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `ENVIRONMENT=production`
- `DEBUG=False`

## Running the Application

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing the Setup

1. Check the root endpoint:
```bash
curl http://localhost:8000/
```

2. Check health status:
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

## Next Steps

- Task 3: Implement authentication system
- Task 4: Build frontend authentication flow
- Task 5: Create 3D homepage with physics-based animations

## Notes

- The application uses Supabase as the PostgreSQL database provider
- SQLAlchemy is used for ORM and database operations
- Redis is used for caching, sessions, and rate limiting
- All configuration is environment-based and validated for production
- Comprehensive logging is implemented for monitoring and debugging
