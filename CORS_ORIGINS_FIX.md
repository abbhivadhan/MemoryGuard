# CORS_ORIGINS Configuration Fix

## Problem
The deployment was failing with:
```
pydantic_settings.exceptions.SettingsError: error parsing value for field "CORS_ORIGINS" from source "EnvSettingsSource"
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

## Root Cause
Pydantic was trying to parse `CORS_ORIGINS` as JSON, but Render environment variables were set as plain strings or empty values, causing JSON parsing to fail.

## Solution
Updated `backend/app/core/config.py` to accept both string and list formats for `CORS_ORIGINS` and `ALLOWED_UPLOAD_EXTENSIONS`:

1. Added custom validators that handle:
   - Empty strings → defaults to `["http://localhost:3000"]`
   - Comma-separated strings → splits into list
   - Lists → passes through unchanged

2. Updated environment variable format in templates to use comma-separated strings instead of JSON arrays.

## How to Configure in Render

### Option 1: Comma-Separated String (Recommended)
```
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

### Option 2: Leave Empty (Uses Default)
```
CORS_ORIGINS=
```
This will default to `["http://localhost:3000"]`

### Option 3: Single Origin
```
CORS_ORIGINS=https://your-frontend.vercel.app
```

## Files Changed
- `backend/app/core/config.py` - Added validators for list fields
- `backend/.env.example` - Updated documentation
- `backend/.env.production.template` - Updated format examples

## Testing
Tested with various input formats:
- Empty string ✓
- Single URL ✓
- Comma-separated URLs ✓
- List format (for local .env files) ✓

## Next Steps
1. Update your Render environment variables to use comma-separated format
2. Redeploy the backend service
3. Verify the application starts successfully
