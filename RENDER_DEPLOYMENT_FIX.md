# Render Deployment Fix - CORS_ORIGINS Error

## Issue Summary
Deployment on Render was failing with a Pydantic settings error when parsing the `CORS_ORIGINS` environment variable.

## Error Message
```
pydantic_settings.exceptions.SettingsError: error parsing value for field "CORS_ORIGINS" from source "EnvSettingsSource"
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

## Root Cause
Pydantic's `BaseSettings` was attempting to parse `CORS_ORIGINS` (defined as `List[str]`) as JSON. When Render set this as an empty string or plain text, JSON parsing failed.

## Fix Applied

### Code Changes
Modified `backend/app/core/config.py` to add custom validators:

```python
from pydantic import field_validator
from typing import Union

class Settings(BaseSettings):
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if not v or v.strip() == '':
                return ["http://localhost:3000"]
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
```

Similar validator added for `ALLOWED_UPLOAD_EXTENSIONS`.

### Configuration Format
Updated environment variable format from JSON arrays to comma-separated strings:

**Before (JSON - doesn't work in Render):**
```
CORS_ORIGINS=["https://example.com","http://localhost:3000"]
```

**After (Comma-separated - works in Render):**
```
CORS_ORIGINS=https://example.com,http://localhost:3000
```

## How to Fix Your Render Deployment

### Step 1: Update Environment Variables in Render Dashboard

Go to your Render service → Environment tab and update:

```bash
# CORS Origins (comma-separated, no brackets)
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# File Extensions (comma-separated, no brackets)
ALLOWED_UPLOAD_EXTENSIONS=.dcm,.nii,.nii.gz,.jpg,.png
```

### Step 2: Redeploy

The service should automatically redeploy when you save the environment variables. If not, trigger a manual deploy.

### Step 3: Verify

Check the logs to ensure the service starts without errors:
```
==> Running '/opt/render/project/src/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Testing Locally

Test the fix works with various formats:

```bash
# Test with empty value
CORS_ORIGINS="" python3 -c "from app.core.config import get_settings; print(get_settings().CORS_ORIGINS)"
# Output: ['http://localhost:3000']

# Test with comma-separated
CORS_ORIGINS="https://a.com,https://b.com" python3 -c "from app.core.config import get_settings; print(get_settings().CORS_ORIGINS)"
# Output: ['https://a.com', 'https://b.com']

# Test with single value
CORS_ORIGINS="https://example.com" python3 -c "from app.core.config import get_settings; print(get_settings().CORS_ORIGINS)"
# Output: ['https://example.com']
```

## Files Modified
- ✅ `backend/app/core/config.py` - Added validators
- ✅ `backend/.env.example` - Updated format documentation
- ✅ `backend/.env.production.template` - Updated format examples

## Backward Compatibility
The fix maintains backward compatibility:
- ✅ JSON arrays in local `.env` files still work
- ✅ Comma-separated strings work (Render format)
- ✅ Empty strings default to localhost
- ✅ Single values work

## Additional Notes

### Why This Happened
Render's environment variable system treats all values as plain strings. When Pydantic sees a `List[str]` type, it tries to parse the string as JSON. This works in some platforms but not in Render's environment.

### Best Practice
For cloud deployments, use simple string formats (comma-separated) rather than JSON for list-type environment variables. This ensures compatibility across different platforms.

### Related Environment Variables
The same pattern was applied to:
- `CORS_ORIGINS` - List of allowed CORS origins
- `ALLOWED_UPLOAD_EXTENSIONS` - List of allowed file extensions

Both now accept comma-separated strings or JSON arrays.
