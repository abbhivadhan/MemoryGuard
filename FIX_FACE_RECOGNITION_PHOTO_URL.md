# Fix Face Recognition Photo URL Error

## Problem
The face recognition feature is failing with this error:
```
value too long for type character varying(500)
```

The `photo_url` column in the `face_profiles` table is limited to 500 characters, but base64-encoded images are much larger (100KB+).

## Solution
Run the pending database migration that changes `photo_url` from `VARCHAR(500)` to `TEXT`.

## Steps to Fix on Render

### Option 1: Run Migration via Render Shell (Recommended)

1. Go to your Render dashboard
2. Navigate to your backend service
3. Click on "Shell" tab
4. Run these commands:

```bash
cd /opt/render/project/src/backend
alembic upgrade head
```

### Option 2: Run Migration Script

In the Render Shell, run:

```bash
cd /opt/render/project/src
bash backend/run_migrations_render.sh
```

### Option 3: Trigger Redeploy

If you have migrations set to run automatically on deploy:

1. Go to your Render dashboard
2. Click "Manual Deploy" → "Deploy latest commit"
3. This will run migrations as part of the build process

## Verify the Fix

After running migrations, verify the column type changed:

```bash
python3 -c "
from app.core.database import engine
from sqlalchemy import inspect, text

with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'face_profiles' 
        AND column_name = 'photo_url'
    '''))
    for row in result:
        print(f'Column: {row[0]}, Type: {row[1]}, Max Length: {row[2]}')
"
```

Expected output:
```
Column: photo_url, Type: text, Max Length: None
```

## Test the Fix

After migration:

1. Go to the Face Recognition page
2. Try adding a new face profile with a photo
3. The upload should now succeed

## Migration Details

The migration file `010_increase_photo_url_length.py` changes:
- **Before**: `photo_url VARCHAR(500)`
- **After**: `photo_url TEXT` (unlimited length)

This allows storing base64-encoded images directly in the database.

## Alternative: Store Images Externally (Future Enhancement)

For better performance and scalability, consider:
1. Upload images to cloud storage (S3, Cloudinary, etc.)
2. Store only the URL in the database
3. This keeps the database smaller and faster

But for now, the TEXT column will work fine.
