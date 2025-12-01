#!/usr/bin/env bash
set -e

echo "🔍 Checking Python environment..."
which python
python --version

echo "📦 Checking installed packages..."
pip list | grep -E "(alembic|gunicorn|uvicorn)" || echo "Packages not found!"

echo "🗄️  Running database migrations..."
alembic upgrade head

echo "🚀 Starting Gunicorn server..."
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
