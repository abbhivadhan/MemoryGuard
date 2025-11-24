# Reminder Not Saving - Troubleshooting Guide

## Quick Checks

### 1. Check Browser Console

Open the browser DevTools (F12) and go to the Console tab. When you try to create a reminder, look for:
- Red error messages
- Failed network requests
- Validation errors

### 2. Check Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Try to create a reminder
4. Find the POST request to `/api/v1/reminders/`
5. Click on it and check:
   - **Status**: Should be 201 (Created)
   - **Payload**: The data being sent
   - **Response**: The server's response

### 3. Check Backend Logs

Look at the terminal where the backend is running. When you try to create a reminder, you should see:
- The POST request being received
- Any validation errors
- Database errors (if any)

## Common Issues

### Issue 1: Date/Time Format

**Symptom**: Error about invalid datetime format

**Solution**: The frontend sends datetime in ISO format. Make sure the `scheduled_time` field is a valid ISO datetime string.

**Check**: In browser console, look for the actual data being sent:
```javascript
// Should look like:
{
  "scheduled_time": "2025-11-24T10:30:00.000Z"
}
```

### Issue 2: Missing Required Fields

**Symptom**: 422 Validation Error

**Solution**: Check that all required fields are provided:
- `title` (required)
- `reminder_type` (required)
- `scheduled_time` (required)
- `frequency` (required)

### Issue 3: Authentication

**Symptom**: 401 Unauthorized error

**Solution**: 
1. Check if you're logged in
2. Check if the access token is in localStorage
3. Try logging out and logging back in

### Issue 4: Database Connection

**Symptom**: 500 Internal Server Error

**Solution**: Check backend logs for database connection errors

## Manual Test

Try creating a reminder with curl:

```bash
# Get your token from browser DevTools > Application > Local Storage
TOKEN="your_token_here"

# Create a reminder
curl -X POST http://localhost:8000/api/v1/reminders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Reminder",
    "description": "Testing reminder creation",
    "reminder_type": "custom",
    "scheduled_time": "2025-11-24T10:00:00Z",
    "frequency": "once",
    "send_notification": true
  }'
```

Expected response (201 Created):
```json
{
  "id": "...",
  "user_id": "...",
  "title": "Test Reminder",
  ...
}
```

## Check Database

Verify if reminders are actually being saved:

```bash
psql postgresql://memoryguard:memoryguard@localhost:5432/memoryguard \
  -c "SELECT id, title, scheduled_time, created_at FROM reminders ORDER BY created_at DESC LIMIT 5;"
```

## What to Report

If the issue persists, please provide:

1. **Browser Console Errors**: Screenshot or copy the error messages
2. **Network Request Details**: 
   - Request payload
   - Response status and body
3. **Backend Logs**: Any error messages from the terminal
4. **Steps to Reproduce**: Exact steps you took to create the reminder

## Likely Causes

Based on the emergency contacts issue, the most likely causes are:

1. ✅ **Schema mismatch**: A field in the frontend doesn't match the backend schema (FIXED for emergency contacts)
2. **Validation error**: The data format doesn't match what the backend expects
3. **Database constraint**: A database constraint is preventing the insert
4. **Authentication issue**: The user token is invalid or expired

## Next Steps

1. Try creating a reminder in the UI
2. Check the browser console for errors
3. Check the Network tab for the request/response
4. Share the error details so I can fix it
