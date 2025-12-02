#!/bin/bash
# Run this in Render Shell to manually run migrations

set -e

echo "Running database migrations..."
cd /opt/render/project/src/backend
alembic upgrade head

echo "✅ Migrations complete!"
echo ""
echo "Checking tables..."
python3 -c "
from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Found {len(tables)} tables:')
for table in sorted(tables):
    print(f'  - {table}')
"
