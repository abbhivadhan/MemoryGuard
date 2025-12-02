# CORS Configuration Fix

## Problem
The backend is rejecting OPTIONS preflight requests from the frontend, causing 400 errors.

## Solution
Add the CORS_ORIGINS environment variable in Render dashboard.

## Steps

### 1. Go to Render Dashboard
- Navigate to https://dashboard.render.com
- Select your `memoryguard-backend` service

### 2. Add Environment Variable
- Go to **Environment** tab
- Click **Add Environment Variable**
- Add:
  ```
  Key: CORS_ORIGINS
  Value: https://memoryguard-frontend.onrender.com,http://localhost:3000,http://localhost:5173
  ```

### 3. Save and Redeploy
- Click **Save Changes**
- The service will automatically redeploy

## Alternative: Allow All Origins (Testing Only)
For quick testing (NOT for production):
```
Key: CORS_ORIGINS
Value: *
```

## Verify It Works
After redeployment, try registering again. The OPTIONS requests should return 200 OK instead of 400.

## Current Status
✅ Database tables created successfully (26 tables)
✅ Server is running on https://memoryguard-backend.onrender.com
❌ CORS blocking frontend requests (needs environment variable)

## What's Next
Once CORS is configured, your registration should work end-to-end!
