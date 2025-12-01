#!/bin/bash
set -e

echo "🔧 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "🗄️  Running database migrations..."
alembic upgrade head

echo "✅ Build complete!"
