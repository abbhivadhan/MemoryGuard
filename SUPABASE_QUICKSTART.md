# Supabase Quick Start Guide

Get up and running with Supabase PostgreSQL in 5 minutes.

## Step 1: Create Supabase Project (2 minutes)

1. Go to https://supabase.com and sign up/login
2. Click **"New Project"**
3. Fill in:
   - **Name**: `memoryguard`
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Select closest to you
4. Click **"Create new project"**
5. Wait ~2 minutes for provisioning

## Step 2: Get Connection String (1 minute)

1. In your Supabase dashboard, go to **Settings** (gear icon)
2. Click **Database** in the left sidebar
3. Scroll to **Connection string** section
4. Select **URI** tab
5. Copy the connection string
6. Replace `[YOUR-PASSWORD]` with your actual database password

Example:
```
postgresql://postgres:mypassword123@db.abcdefghijk.supabase.co:5432/postgres
```

## Step 3: Configure Application (1 minute)

### Option A: Using .env file (Recommended)

1. Copy the example file:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `backend/.env` and update:
   ```bash
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
   ```

### Option B: Using Docker Compose

1. Create `.env` file in project root:
   ```bash
   echo "DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres" > .env
   ```

2. Use Supabase docker-compose:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.supabase.yml up
   ```

## Step 4: Run Migrations (1 minute)

Create database tables:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

Or with Docker:

```bash
docker-compose exec backend alembic upgrade head
```

## Step 5: Verify Setup (30 seconds)

Run the verification script:

```bash
cd backend
python scripts/verify_supabase.py
```

You should see:
```
✅ Connection successful!
✅ Database Info
✅ Tables
✅ Migrations
✅ CRUD Operations

🎉 All checks passed! Supabase is configured correctly.
```

## Done! 🎉

Your application is now using Supabase PostgreSQL!

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Supabase Dashboard**: https://app.supabase.com

## View Your Data

1. Go to your Supabase dashboard
2. Click **Table Editor** in the left sidebar
3. Browse your tables:
   - `users` - User accounts
   - `health_metrics` - Health data
   - `predictions` - ML predictions
   - And more...

## Troubleshooting

### Connection Failed

**Problem**: Can't connect to Supabase

**Solutions**:
1. Check your internet connection
2. Verify DATABASE_URL is correct (no typos)
3. Ensure password doesn't have special characters (or URL encode them)
4. Check Supabase project isn't paused (free tier pauses after 7 days inactivity)

### Password Issues

**Problem**: Authentication failed

**Solutions**:
1. Reset password in Supabase dashboard: Settings → Database → Reset database password
2. URL encode special characters in password:
   - `@` → `%40`
   - `#` → `%23`
   - `$` → `%24`
   - `&` → `%26`

### Tables Not Found

**Problem**: No tables in database

**Solution**: Run migrations:
```bash
cd backend
alembic upgrade head
```

### Project Paused

**Problem**: "Project is paused" error

**Solution**: 
1. Go to Supabase dashboard
2. Click **"Restore project"**
3. Wait 1-2 minutes
4. Try connecting again

## Next Steps

- **Add data**: Use the API or Supabase Table Editor
- **Monitor**: Check Supabase dashboard for connection stats
- **Backup**: Supabase automatically backs up daily (free tier)
- **Scale**: Upgrade plan if you need more connections/storage

## Need Help?

- **Detailed Guide**: See `backend/SUPABASE_SETUP.md`
- **Supabase Docs**: https://supabase.com/docs
- **Discord**: https://discord.supabase.com
- **GitHub Issues**: [Your repo issues]

## Cost

**Free Tier Includes**:
- 500 MB database
- 2 GB bandwidth
- 60 concurrent connections
- 7-day backup retention
- Unlimited API requests

Perfect for development and small projects!
