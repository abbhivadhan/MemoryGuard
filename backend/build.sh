#!/bin/bash
set -e

echo "🔧 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "✅ Build complete!"
echo "ℹ️  Database migrations will run on startup"
