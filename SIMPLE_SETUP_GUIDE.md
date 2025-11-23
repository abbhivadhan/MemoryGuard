# Simple Setup Guide - Get Running in 5 Minutes

This guide gets your MemoryGuard system running quickly using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- Git repository cloned
- That's it!

## Quick Start (Recommended)

The easiest way to run everything is with Docker Compose:

```bash
# 1. Start database and Redis services
docker-compose up postgres redis -d

# 2. Wait 10 seconds for services to be ready
sleep 10

# 3. Run database migrations
cd backend
python -m alembic upgrade head

# 4. Start the backend (in one terminal)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Start the frontend (in another terminal)
cd frontend
npm install  # First time only
npm run dev
```

Open your browser to http://localhost:5173 and you're ready!

## What's Running

After following the quick start:

✅ **PostgreSQL** - Database on port 5432  
✅ **Redis** - Cache/queue on port 6379  
✅ **Backend API** - FastAPI on port 8000  
✅ **Frontend** - React app on port 5173  

## Verify Everything Works

```bash
# Check database connection
docker exec -it memoryguard-postgres psql -U memoryguard -d memoryguard -c "SELECT version();"

# Check Redis
docker exec -it memoryguard-redis redis-cli ping

# Check backend API
curl http://localhost:8000/health

# Check frontend
# Open http://localhost:5173 in your browser
```

## Common Issues & Fixes

### Issue: Port 5432 already in use

If you have PostgreSQL already running locally:

```bash
# Option A: Stop your local PostgreSQL
brew services stop postgresql@15  # macOS
sudo systemctl stop postgresql    # Linux

# Option B: Use a different port in docker-compose.yml
# Change "5432:5432" to "5433:5432" and update DATABASE_URL
```

### Issue: Port 6379 already in use

If you have Redis already running:

```bash
# Stop local Redis
brew services stop redis  # macOS
sudo systemctl stop redis # Linux
```

### Issue: Migration errors with enum types

If you see enum type conflicts:

```bash
# Reset the database
docker-compose down -v
docker-compose up postgres redis -d
sleep 10
cd backend
python -m alembic upgrade head
```

### Issue: Frontend won't start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## Alternative: Run Everything in Docker

If you prefer to run everything containerized:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Note: The frontend will be on port 3000 instead of 5173 when using Docker.

## Development Workflow

Once everything is running:

1. **Backend changes** - Auto-reload is enabled, just save your files
2. **Frontend changes** - Vite hot-reload is enabled, just save your files
3. **Database changes** - Create a new migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

## Stopping Services

```bash
# Stop Docker services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

## Next Steps

Once running, you can:

- Login with Google OAuth at http://localhost:5173
- Explore the API docs at http://localhost:8000/docs
- Check the health dashboard
- Upload health metrics
- Try cognitive assessments

## Need More Help?

- **Full setup guide**: See SETUP.md
- **Supabase setup**: See SUPABASE_QUICKSTART.md
- **Authentication issues**: See AUTH_TROUBLESHOOTING.md
- **Database migrations**: See backend/MIGRATIONS.md
