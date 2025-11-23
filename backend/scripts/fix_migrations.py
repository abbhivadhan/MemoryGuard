#!/usr/bin/env python3
"""
Quick script to complete all migrations by stamping them as done.
The tables are already created, we just need to mark them in alembic.
"""
from app.core.database import engine
from sqlalchemy import text

# Just stamp all migrations as complete
import subprocess
subprocess.run(["alembic", "stamp", "head"], cwd="/Users/abbhivadhan/Desktop/AI4A/backend")
print("All migrations marked as complete")
