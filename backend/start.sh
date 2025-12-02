#!/bin/bash

echo "🚀 Starting MemoryGuard Backend..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    exit 1
fi

echo "✅ Database URL configured"

# Initialize database (creates tables and runs migrations)
echo "🗄️  Initializing database..."
cd /opt/render/project/src/backend

python init_db.py
if [ $? -eq 0 ]; then
    echo "✅ Database initialization successful"
else
    echo "❌ Database initialization failed"
    echo "⚠️  Attempting to start server anyway..."
fi

# Use Gunicorn with Uvicorn workers for production
echo "🌐 Starting web server..."
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
