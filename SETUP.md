# MemoryGuard Setup Guide

This guide will help you set up the MemoryGuard development environment.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git**

For local development without Docker:
- **Node.js** (version 20 or higher)
- **Python** (version 3.11 or higher)
- **PostgreSQL** (version 15 or higher)
- **Redis** (version 7 or higher)

## Quick Start with Docker (Recommended)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd memoryguard
```

### 2. Configure Environment Variables

Copy the example environment file and update it with your configuration:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and update the following:
- `JWT_SECRET`: Generate a secure random string
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

### 3. Run the Setup Script

Make the setup script executable and run it:

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Check for Docker and Docker Compose
- Build all Docker images
- Start all services
- Display service status

### 4. Access the Application

Once setup is complete, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Manual Docker Setup

If you prefer to run commands manually:

### 1. Build Docker Images

```bash
docker-compose build
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. View Logs

```bash
docker-compose logs -f
```

### 4. Stop Services

```bash
docker-compose down
```

## Local Development Setup (Without Docker)

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Start the development server:
```bash
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

### Database Setup (Local Development)

1. Install PostgreSQL 15 and create a database:
```sql
CREATE DATABASE memoryguard;
CREATE USER memoryguard WITH PASSWORD 'memoryguard';
GRANT ALL PRIVILEGES ON DATABASE memoryguard TO memoryguard;
```

2. Run database migrations:
```bash
cd backend
alembic upgrade head
```

### Redis Setup (Local Development)

Install and start Redis:

```bash
# On macOS with Homebrew:
brew install redis
brew services start redis

# On Ubuntu/Debian:
sudo apt-get install redis-server
sudo systemctl start redis
```

## Verifying the Setup

### Check Service Health

```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Common Issues and Solutions

### Port Already in Use

If you get a "port already in use" error:

```bash
# Find the process using the port
lsof -i :3000  # or :8000, :5432, :6379

# Kill the process
kill -9 <PID>
```

### Docker Build Fails

If Docker build fails:

```bash
# Clean up Docker resources
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Database Connection Issues

If the backend can't connect to the database:

1. Check that PostgreSQL is running:
```bash
docker-compose ps postgres
```

2. Check the DATABASE_URL in backend/.env

3. Restart the backend service:
```bash
docker-compose restart backend
```

### Frontend Can't Connect to Backend

1. Check that the backend is running:
```bash
curl http://localhost:8000/health
```

2. Check CORS settings in `backend/app/main.py`

3. Verify the API URL in frontend Vite config

## Development Workflow

### Making Changes

1. **Frontend Changes**: 
   - Edit files in `frontend/src/`
   - Changes will hot-reload automatically

2. **Backend Changes**:
   - Edit files in `backend/app/`
   - Changes will auto-reload with uvicorn

### Running Tests

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest
```

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Next Steps

1. Review the [README.md](README.md) for project overview
2. Check the API documentation at http://localhost:8000/docs
3. Explore the codebase structure
4. Start implementing features from the task list

## Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Review this setup guide
4. Check the project documentation

## Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec backend bash

# Rebuild and restart
docker-compose up -d --build

# Clean everything
docker-compose down -v
make clean
```
