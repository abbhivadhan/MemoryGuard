# Render Deployment Guide

This guide walks you through deploying your MemoryGuard backend on Render with a PostgreSQL database.

## Prerequisites

- Frontend already deployed on Vercel ✓
- Render account (free tier available)
- GitHub repository with your code
- Environment variables ready

## Step 1: Prepare Backend for Deployment

### 1.1 Create Production Requirements File

Your `backend/requirements.txt` is already production-ready.

### 1.2 Update Dockerfile (if needed)

Your existing Dockerfile is good, but let's ensure it's optimized for production:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start the application
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 1.3 Create a Build Script

Create `backend/build.sh`:

```bash
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
alembic upgrade head

echo "Build complete!"
```

### 1.4 Create Start Script

Create `backend/start.sh`:

```bash
#!/bin/bash
set -e

echo "Starting application..."
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

## Step 2: Set Up PostgreSQL Database on Render

1. **Go to Render Dashboard** → https://dashboard.render.com/

2. **Create New PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `memoryguard-db`
   - Database: `memoryguard`
   - User: `memoryguard` (auto-generated)
   - Region: Choose closest to your users
   - Plan: Free (or paid for production)
   - Click "Create Database"

3. **Get Database Connection Details**:
   - After creation, go to database dashboard
   - Copy the **Internal Database URL** (for backend connection)
   - Format: `postgresql://user:password@hostname:5432/database`

## Step 3: Set Up Redis on Render (Optional but Recommended)

1. **Create Redis Instance**:
   - Click "New +" → "Redis"
   - Name: `memoryguard-redis`
   - Region: Same as database
   - Plan: Free (or paid)
   - Click "Create Redis"

2. **Get Redis Connection URL**:
   - Copy the **Internal Redis URL**
   - Format: `redis://hostname:6379`

## Step 4: Deploy Backend Web Service

1. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

2. **Configure Service**:
   - **Name**: `memoryguard-backend`
   - **Region**: Same as database
   - **Branch**: `main` (or your production branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `chmod +x start.sh && ./start.sh`
   - **Plan**: Free (or paid for production)

3. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable" and add:

   ```bash
   # Application
   APP_NAME=MemoryGuard
   APP_VERSION=0.1.0
   ENVIRONMENT=production
   DEBUG=false

   # Database (use Internal Database URL from Step 2)
   DATABASE_URL=<YOUR_RENDER_POSTGRES_INTERNAL_URL>

   # Redis (use Internal Redis URL from Step 3)
   REDIS_URL=<YOUR_RENDER_REDIS_INTERNAL_URL>
   CELERY_BROKER_URL=<YOUR_RENDER_REDIS_INTERNAL_URL>/1
   CELERY_RESULT_BACKEND=<YOUR_RENDER_REDIS_INTERNAL_URL>/2

   # Security (IMPORTANT: Generate new secret!)
   JWT_SECRET=<GENERATE_WITH: openssl rand -hex 32>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7

   # Google OAuth
   GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
   GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
   GOOGLE_REDIRECT_URI=https://your-backend.onrender.com/api/v1/auth/google/callback

   # Google Gemini AI
   GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
   GEMINI_MODEL=gemini-pro
   GEMINI_MAX_TOKENS=2048
   GEMINI_TEMPERATURE=0.7

   # CORS (use your Vercel frontend URL)
   CORS_ORIGINS=["https://your-frontend.vercel.app","http://localhost:3000"]

   # Rate Limiting
   RATE_LIMIT_PER_MINUTE=60
   RATE_LIMIT_ENABLED=true

   # File Upload
   MAX_UPLOAD_SIZE=10485760
   ALLOWED_UPLOAD_EXTENSIONS=[".dcm",".nii",".nii.gz",".jpg",".png"]

   # ML Model Settings
   ML_MODEL_PATH=models/
   ML_BATCH_SIZE=32

   # Logging
   LOG_LEVEL=INFO

   # Sentry (optional)
   SENTRY_DSN=<YOUR_SENTRY_DSN>
   SENTRY_ENABLED=true
   SENTRY_TRACES_SAMPLE_RATE=0.1
   ```

4. **Create Service**:
   - Click "Create Web Service"
   - Render will automatically build and deploy

## Step 5: Deploy Celery Worker (Optional)

If you need background task processing:

1. **Create Background Worker**:
   - Click "New +" → "Background Worker"
   - Connect same repository
   - **Name**: `memoryguard-celery-worker`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A celery_worker worker --loglevel=info`

2. **Add Same Environment Variables** as the web service

## Step 6: Update Frontend Environment Variables

Update your Vercel frontend environment variables:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables

2. Update `VITE_API_URL`:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

3. Redeploy frontend to apply changes

## Step 7: Run Database Migrations

Migrations should run automatically via the build script, but if needed:

1. Go to Render Dashboard → Your Web Service
2. Click "Shell" tab
3. Run: `alembic upgrade head`

## Step 8: Verify Deployment

1. **Check Service Health**:
   - Visit: `https://your-backend.onrender.com/`
   - Should return: `{"message": "MemoryGuard API", "status": "running"}`

2. **Check API Docs**:
   - Visit: `https://your-backend.onrender.com/docs`
   - Should show FastAPI Swagger UI

3. **Test Database Connection**:
   - Visit: `https://your-backend.onrender.com/api/v1/health`

4. **Test from Frontend**:
   - Open your Vercel frontend
   - Try logging in or making API calls

## Troubleshooting

### Issue: Build Fails

**Solution**: Check build logs in Render dashboard
- Ensure all dependencies in requirements.txt are correct
- Check Python version compatibility

### Issue: Database Connection Fails

**Solution**: 
- Verify DATABASE_URL is the Internal Database URL
- Check database is in same region as web service
- Ensure database is running (check Render dashboard)

### Issue: CORS Errors

**Solution**:
- Add your Vercel URL to CORS_ORIGINS
- Format: `["https://your-app.vercel.app"]`
- Redeploy after updating

### Issue: 502 Bad Gateway

**Solution**:
- Check service logs for errors
- Ensure PORT environment variable is used (Render sets this automatically)
- Verify start command uses `--bind 0.0.0.0:$PORT`

### Issue: Migrations Don't Run

**Solution**:
- Manually run in Shell: `alembic upgrade head`
- Check alembic.ini has correct database URL pattern
- Ensure migrations directory is included in deployment

## Production Checklist

- [ ] Database created and connected
- [ ] Redis created and connected (if using)
- [ ] All environment variables set
- [ ] JWT_SECRET is unique and secure
- [ ] CORS_ORIGINS includes Vercel URL
- [ ] Google OAuth redirect URI updated
- [ ] Database migrations run successfully
- [ ] Health endpoint returns 200
- [ ] Frontend can connect to backend
- [ ] SSL/HTTPS working (automatic on Render)
- [ ] Logs are accessible and readable
- [ ] Error tracking configured (Sentry)

## Monitoring & Maintenance

### View Logs
- Render Dashboard → Your Service → Logs tab
- Real-time log streaming available

### Database Backups
- Render automatically backs up paid PostgreSQL databases
- Free tier: Manual backups recommended

### Scaling
- Render Dashboard → Your Service → Settings
- Upgrade plan for more resources
- Add more worker instances if needed

### Updates
- Push to GitHub → Render auto-deploys
- Or manually trigger deploy in Render dashboard

## Cost Optimization

### Free Tier Limits
- Web Service: Spins down after 15 min inactivity
- Database: 1GB storage, 97 hours/month
- Redis: 25MB storage

### Recommendations
- Use paid tier for production ($7/month web service)
- Paid database for better performance and backups
- Monitor usage in Render dashboard

## Next Steps

1. Set up custom domain (optional)
2. Configure monitoring and alerts
3. Set up CI/CD pipeline
4. Add health checks and uptime monitoring
5. Configure backup strategy
6. Set up staging environment

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- FastAPI Docs: https://fastapi.tiangolo.com
