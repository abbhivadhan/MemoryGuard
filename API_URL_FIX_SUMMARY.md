# API URL Double Prefix Fix

## Problem
The frontend was making API calls with doubled `/api/v1` prefixes, resulting in 404 errors:
- `/api/v1/api/v1/health-metrics` (should be `/api/v1/health/metrics`)
- `/api/v1/api/v1/caregivers/invite` (should be `/api/v1/caregivers/invite`)

## Root Cause
Some components were using `fetch` directly with:
```typescript
fetch(`${import.meta.env.VITE_API_URL}/api/v1/endpoint`, ...)
```

Since `VITE_API_URL` is already set to `/api/v1`, this created the doubled path.

## Files Fixed

### 1. `frontend/src/components/dashboard/HealthMetrics.tsx`
**Line 449** - Fixed the add health metric endpoint:
- **Before:** `${import.meta.env.VITE_API_URL}/api/v1/health-metrics`
- **After:** `${import.meta.env.VITE_API_URL}/health/metrics`
- Also fixed token key from `'token'` to `'access_token'`

### 2. `frontend/src/components/memory/CaregiverConfig.tsx`
Fixed three endpoints:

**Line 47** - Load caregivers:
- **Before:** `${import.meta.env.VITE_API_URL}/api/v1/caregivers/my-caregivers`
- **After:** `${import.meta.env.VITE_API_URL}/caregivers/my-caregivers`

**Line 82** - Invite caregiver:
- **Before:** `${import.meta.env.VITE_API_URL}/api/v1/caregivers/invite`
- **After:** `${import.meta.env.VITE_API_URL}/caregivers/invite`

**Line 138** - Delete caregiver:
- **Before:** `${import.meta.env.VITE_API_URL}/api/v1/caregivers/${relationshipId}`
- **After:** `${import.meta.env.VITE_API_URL}/caregivers/${relationshipId}`

All also fixed token key from `'token'` to `'access_token'`

## Correct API Paths
The backend routes are registered as:
- `/api/v1/health/metrics` - Health metrics endpoints
- `/api/v1/caregivers` - Caregiver management endpoints

## Best Practice
Components should either:
1. Use the `api` client from `services/api.ts` (recommended)
2. If using `fetch` directly, only append the endpoint path without `/api/v1` prefix

## Testing
After these fixes:
- ✅ Adding health metrics should work
- ✅ Inviting caregivers should work
- ✅ Loading caregiver list should work
- ✅ Removing caregivers should work
