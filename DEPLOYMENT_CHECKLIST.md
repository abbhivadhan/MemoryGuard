# Quick Deployment Checklist

## Pre-Deployment

### 1. Generate Secrets
```bash
# Generate JWT secret
openssl rand -hex 32

# Generate encryption key (if needed)
openssl rand -hex 32
```

### 2. Gather API Keys
- [ ] Google OAuth Client ID & Secret
- [ ] Google Gemini API Key
- [ ] Sentry DSN (optional)

### 3. Get Frontend URL
- [ ] Your Vercel deployment URL (e.g., `https://your-app.vercel.app`)

## Render Setup

### Step 1: Create Database
1. Go to https://dashboard.render.com/
2. Click "New +" → "PostgreSQL"
3. Name: `memoryguard-db`
4. Plan: Free (or paid)
5. Click "Create Database"
6. **Copy Internal Database URL** → Save for later

### Step 2: Create Redis (Optional)
1. Click "New +" → "Redis"
2. Name: `memoryguard-redis`
3. Plan: Free (or paid)
4. Click "Create Redis"
5. **Copy Internal Redis URL** → Save for later

### Step 3: Deploy Backend
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Configure:
   - **Name**: `memoryguard-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `chmod +x start.sh && ./start.sh`
   - **Plan**: Free (or paid)

### Step 4: Add Environment Variables

Copy and paste these, replacing values in `<>`:

```bash
APP_NAME=MemoryGuard
APP_VERSION=0.1.0
ENVIRONMENT=production
DEBUG=false

DATABASE_URL=<PASTE_INTERNAL_DATABASE_URL_FROM_STEP_1>
REDIS_URL=<PASTE_INTERNAL_REDIS_URL_FROM_STEP_2>
CELERY_BROKER_URL=<PASTE_INTERNAL_REDIS_URL_FROM_STEP_2>/1
CELERY_RESULT_BACKEND=<PASTE_INTERNAL_REDIS_URL_FROM_STEP_2>/2

JWT_SECRET=<PASTE_GENERATED_SECRET_FROM_OPENSSL>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
GOOGLE_REDIRECT_URI=https://<YOUR_RENDER_URL>.onrender.com/api/v1/auth/google/callback

GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL=gemini-pro
GEMINI_MAX_TOKENS=2048
GEMINI_TEMPERATURE=0.7

CORS_ORIGINS=["https://<YOUR_VERCEL_URL>.vercel.app","http://localhost:3000"]

RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_ENABLED=true
MAX_UPLOAD_SIZE=10485760
ML_MODEL_PATH=models/
ML_BATCH_SIZE=32
LOG_LEVEL=INFO
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build to complete (5-10 minutes)
3. Check logs for any errors

## Post-Deployment

### Verify Backend
- [ ] Visit `https://your-backend.onrender.com/`
- [ ] Visit `https://your-backend.onrender.com/docs`
- [ ] Visit `https://your-backend.onrender.com/api/v1/health`

### Update Frontend
1. Go to Vercel Dashboard
2. Settings → Environment Variables
3. Update `VITE_API_URL=https://your-backend.onrender.com`
4. Redeploy frontend

### Test Integration
- [ ] Open frontend
- [ ] Try logging in
- [ ] Test API calls
- [ ] Check browser console for errors

## Troubleshooting

### Build Fails
- Check Render logs
- Verify requirements.txt is correct
- Ensure build.sh has correct permissions

### Database Connection Fails
- Use **Internal Database URL** (not External)
- Check database is running
- Verify DATABASE_URL format

### CORS Errors
- Add Vercel URL to CORS_ORIGINS
- Format: `["https://your-app.vercel.app"]`
- Redeploy after updating

### 502 Bad Gateway
- Check service logs
- Verify start command
- Ensure migrations ran successfully

## Quick Commands

### View Logs
```bash
# In Render Dashboard → Your Service → Logs
```

### Run Migrations Manually
```bash
# In Render Dashboard → Your Service → Shell
alembic upgrade head
```

### Restart Service
```bash
# In Render Dashboard → Your Service → Manual Deploy → Deploy latest commit
```

## Support Resources

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Full Guide: See RENDER_DEPLOYMENT_GUIDE.md
