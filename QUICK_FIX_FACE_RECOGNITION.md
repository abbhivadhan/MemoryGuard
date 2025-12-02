# Quick Fix: Face Recognition Photo Upload Error

## The Problem
Face profile creation is failing with:
```
value too long for type character varying(500)
```

The database column `photo_url` is too small for base64-encoded images.

## Quick Fix (Choose One Method)

### Method 1: Run Python Script (Easiest)
In Render Shell:
```bash
cd /opt/render/project/src/backend
python3 scripts/fix_face_photo_url.py
```

### Method 2: Run Alembic Migration
In Render Shell:
```bash
cd /opt/render/project/src/backend
alembic upgrade head
```

### Method 3: Direct SQL
In Render Shell with psql access:
```bash
cd /opt/render/project/src/backend
psql $DATABASE_URL -f fix_photo_url_column.sql
```

### Method 4: Manual SQL
Connect to your database and run:
```sql
ALTER TABLE face_profiles ALTER COLUMN photo_url TYPE TEXT;
```

## How to Access Render Shell

1. Go to https://dashboard.render.com
2. Select your backend service
3. Click "Shell" in the top menu
4. Run one of the commands above

## Verify It Worked

After running the fix, test by:
1. Going to the Face Recognition page
2. Uploading a photo
3. Should now work without errors

## What Changed

- **Before**: `photo_url VARCHAR(500)` - max 500 characters
- **After**: `photo_url TEXT` - unlimited length

This allows storing base64-encoded images (typically 50KB-200KB).

## Need Help?

If you get errors, check:
1. Database connection is working
2. You have write permissions
3. The `face_profiles` table exists

Run this to check:
```bash
python3 -c "from app.core.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```
