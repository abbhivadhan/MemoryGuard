#!/bin/bash
# Script to run Alembic migrations

set -e

echo "Running database migrations..."

# Check if we're in a Docker container or local environment
if [ -f /.dockerenv ]; then
    echo "Running in Docker container"
    cd /app
else
    echo "Running in local environment"
    cd "$(dirname "$0")"
fi

# Run migrations
alembic upgrade head

echo "Migrations completed successfully!"
