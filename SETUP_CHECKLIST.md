# Setup Checklist

Complete setup guide for MemoryGuard with Supabase PostgreSQL.

## ✅ Pre-Setup

- [ ] Docker and Docker Compose installed
- [ ] Node.js 20+ installed (for local development)
- [ ] Python 3.11+ installed (for local development)
- [ ] Git repository cloned
- [ ] Code editor ready (VS Code recommended)

## ✅ Supabase Setup (5 minutes)

### Step 1: Create Project
- [ ] Go to https://supabase.com
- [ ] Sign up or log in
- [ ] Click "New Project"
- [ ] Enter project name: `memoryguard`
- [ ] Choose strong database password
- [ ] Select region closest to you
- [ ] Click "Create new project"
- [ ] Wait ~2 minutes for provisioning

### Step 2: Get Credentials
- [ ] Go to Settings → Database
- [ ] Copy connection string (URI format)
- [ ] Replace `[YOUR-PASSWORD]` with actual password
- [ ] Save connection string securely

### Step 3: Get API Keys (Optional)
- [ ] Go to Settings → API
- [ ] Copy `anon` `public` key
- [ ] Copy `service_role` key (keep secret!)
- [ ] Save keys securely

## ✅ Backend Configuration

### Step 1: Environment Setup
- [ ] Navigate to backend directory: `cd backend`
- [ ] Copy example env: `cp .env.example .env`
- [ ] Open `.env` in editor
- [ ] Update `DATABASE_URL` with Supabase connection string
- [ ] Update `SUPABASE_URL` (optional)
- [ ] Update `SUPABASE_KEY` (optional)
- [ ] Update `SUPABASE_SERVICE_KEY` (optional)
- [ ] Set `JWT_SECRET` (generate with: `openssl rand -hex 32`)
- [ ] Configure Google OAuth credentials (if using)

### Step 2: Install Dependencies
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate venv: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
- [ ] Install packages: `pip install -r requirements.txt`

### Step 3: Database Setup
- [ ] Run migrations: `alembic upgrade head`
- [ ] Verify connection: `python scripts/verify_supabase.py`
- [ ] Check for "All checks passed!" message

### Step 4: Test Backend
- [ ] Start server: `uvicorn app.main:app --reload`
- [ ] Open browser: http://localhost:8000
- [ ] Check API docs: http://localhost:8000/docs
- [ ] Test health endpoint: http://localhost:8000/api/v1/health

## ✅ Frontend Configuration

### Step 1: Environment Setup
- [ ] Navigate to frontend: `cd frontend`
- [ ] Copy example env: `cp .env.example .env`
- [ ] Open `.env` in editor
- [ ] Update `VITE_API_URL` if needed (default: http://localhost:8000)
- [ ] Update Google OAuth client ID (if using)

### Step 2: Install Dependencies
- [ ] Install packages: `npm install`

### Step 3: Test Frontend
- [ ] Start dev server: `npm run dev`
- [ ] Open browser: http://localhost:3000
- [ ] Check homepage loads
- [ ] Test 3D animations work

## ✅ Docker Setup (Alternative)

### Option 1: Local PostgreSQL
- [ ] Ensure `.env` files configured
- [ ] Start services: `docker-compose up -d`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Verify all services running: `docker-compose ps`

### Option 2: Supabase PostgreSQL
- [ ] Create `.env` in project root with DATABASE_URL
- [ ] Start services: `docker-compose -f docker-compose.yml -f docker-compose.supabase.yml up -d`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Verify all services running: `docker-compose ps`

### Run Migrations in Docker
- [ ] Execute: `docker-compose exec backend alembic upgrade head`
- [ ] Verify: `docker-compose exec backend python scripts/verify_supabase.py`

## ✅ Google OAuth Setup (Optional)

### Step 1: Google Cloud Console
- [ ] Go to https://console.cloud.google.com
- [ ] Create new project or select existing
- [ ] Enable Google+ API
- [ ] Go to Credentials
- [ ] Create OAuth 2.0 Client ID
- [ ] Add authorized redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
- [ ] Copy Client ID and Client Secret

### Step 2: Configure Application
- [ ] Update `GOOGLE_CLIENT_ID` in backend/.env
- [ ] Update `GOOGLE_CLIENT_SECRET` in backend/.env
- [ ] Update `VITE_GOOGLE_CLIENT_ID` in frontend/.env
- [ ] Restart backend and frontend

### Step 3: Test OAuth
- [ ] Open frontend: http://localhost:3000
- [ ] Click "Sign in with Google"
- [ ] Complete OAuth flow
- [ ] Verify user created in Supabase Table Editor

## ✅ Celery Setup (For ML Processing)

### Step 1: Redis
- [ ] Ensure Redis running (included in docker-compose)
- [ ] Test connection: `redis-cli ping` (should return PONG)

### Step 2: Start Worker
- [ ] Navigate to backend: `cd backend`
- [ ] Start worker: `celery -A celery_worker worker --loglevel=info`
- [ ] Check for "ready" message

### Step 3: Test Celery
- [ ] Create ML prediction via API
- [ ] Check Celery logs for task processing
- [ ] Verify prediction completed in database

## ✅ Verification

### Backend Health Checks
- [ ] API health: http://localhost:8000/api/v1/health
- [ ] ML health: http://localhost:8000/api/v1/ml/health
- [ ] Database connection: `python scripts/verify_supabase.py`

### Frontend Health Checks
- [ ] Homepage loads: http://localhost:3000
- [ ] 3D animations render
- [ ] Navigation works
- [ ] No console errors

### Database Checks
- [ ] Open Supabase dashboard
- [ ] Go to Table Editor
- [ ] Verify tables exist:
  - [ ] users
  - [ ] health_metrics
  - [ ] assessments
  - [ ] medications
  - [ ] emergency_contacts
  - [ ] predictions
- [ ] Check alembic_version table

### Integration Tests
- [ ] Create user account (via Google OAuth)
- [ ] Add health metrics
- [ ] Create ML prediction
- [ ] View prediction results
- [ ] Check data in Supabase Table Editor

## ✅ Production Checklist

### Security
- [ ] Change JWT_SECRET to secure random value
- [ ] Update all default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set DEBUG=False
- [ ] Review and set rate limits

### Database
- [ ] Verify Supabase backups enabled
- [ ] Set up monitoring alerts
- [ ] Review connection pool settings
- [ ] Add database indexes for performance
- [ ] Enable Row Level Security (optional)

### Deployment
- [ ] Set ENVIRONMENT=production
- [ ] Configure production URLs
- [ ] Set up CI/CD pipeline
- [ ] Configure logging
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure monitoring (Datadog, etc.)

### Documentation
- [ ] Update README with production URLs
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures

## ✅ Troubleshooting

If you encounter issues, check:

### Connection Issues
- [ ] DATABASE_URL is correct
- [ ] Supabase project is active (not paused)
- [ ] Internet connection working
- [ ] Firewall not blocking connections

### Migration Issues
- [ ] Alembic installed: `pip install alembic`
- [ ] Database accessible
- [ ] Correct permissions
- [ ] No conflicting migrations

### Docker Issues
- [ ] Docker daemon running
- [ ] Ports not already in use (3000, 8000, 5432, 6379)
- [ ] Sufficient disk space
- [ ] Docker Compose version compatible

### Frontend Issues
- [ ] Node modules installed: `npm install`
- [ ] Correct Node version (20+)
- [ ] Backend API accessible
- [ ] No CORS errors

### Backend Issues
- [ ] Python version correct (3.11+)
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Environment variables set

## 📚 Resources

- **Quick Start**: `SUPABASE_QUICKSTART.md`
- **Detailed Setup**: `backend/SUPABASE_SETUP.md`
- **Integration Guide**: `backend/SUPABASE_INTEGRATION.md`
- **ML System**: `backend/ML_SYSTEM.md`
- **Celery Setup**: `backend/CELERY_SETUP.md`
- **API Docs**: http://localhost:8000/docs

## 🎉 Success!

Once all items are checked, your MemoryGuard application is fully set up and ready to use!

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Supabase: https://app.supabase.com

Happy coding! 🚀
