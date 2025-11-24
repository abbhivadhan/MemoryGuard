# Testing QR Code Emergency Contacts

## Issue
QR code shows "Emergency contacts: None listed" even though contacts have been added.

## Diagnosis Steps

### Step 1: Check if backend is running
```bash
curl http://localhost:8000/health
```

### Step 2: Use the debug endpoint to check what data exists

First, get your auth token from the browser:
1. Open browser DevTools (F12)
2. Go to Application → Local Storage
3. Find your auth token

Then run:
```bash
curl -X GET "http://localhost:8000/api/v1/emergency/medical-info/debug" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

This will show you:
- How many emergency contacts are in the database
- List of all contacts with details
- How many medications exist
- Medical info from alerts

### Step 3: Check the backend logs

When you click "Generate QR Code", check the backend terminal for logs like:
```
Found X emergency contacts for user...
Built medical_info with X contacts
```

## Common Issues and Solutions

### Issue 1: Contacts not in database
**Symptom**: Debug endpoint shows `emergency_contacts_count: 0`

**Solution**: 
1. Go to Emergency page
2. Click "Add Emergency Contact"
3. Fill in all required fields (name, phone, relationship)
4. Make sure to click Save
5. Verify the contact appears in the list

### Issue 2: Contacts marked as inactive
**Symptom**: Debug endpoint shows contacts but they have `active: false`

**Solution**:
The contacts might have been soft-deleted. Check the database or re-add them.

### Issue 3: Wrong user ID
**Symptom**: Debug endpoint shows contacts for a different user

**Solution**:
Make sure you're logged in with the correct account. Try logging out and back in.

### Issue 4: Database connection issue
**Symptom**: Backend logs show database connection errors

**Solution**:
```bash
# Start the database
docker-compose up postgres redis -d

# Or if using Supabase, check your DATABASE_URL in backend/.env
```

## Quick Fix

If contacts still don't appear after checking above:

1. **Delete and re-add the contact**:
   - Go to Emergency page
   - Delete the existing contact
   - Add it again with all fields filled
   - Generate QR code again

2. **Check the actual QR code generation**:
   - Open browser DevTools → Network tab
   - Click "Generate QR Code"
   - Look at the POST request to `/api/v1/emergency/medical-info/qr-code`
   - Check the response to see what data was sent to the QR generator

3. **Restart the backend**:
   ```bash
   # Stop the backend (Ctrl+C)
   # Start it again
   uvicorn app.main:app --reload --port 8000
   ```

## Expected Debug Output

When working correctly, the debug endpoint should return:
```json
{
  "user_id": "your-user-id",
  "user_email": "your@email.com",
  "emergency_contacts_count": 1,
  "emergency_contacts": [
    {
      "id": "contact-id",
      "name": "John Doe",
      "phone": "+1-555-0123",
      "relationship": "Spouse"
    }
  ],
  "medications_count": 0,
  "medications": []
}
```

## Testing the Fix

After following the steps above:

1. Use the debug endpoint to verify contacts exist
2. Generate QR code
3. Scan QR code with your phone
4. You should see:
   ```
   EMERGENCY CONTACTS:
   1. John Doe
      (Spouse)
      Tel: +1-555-0123
   ```

## Still Not Working?

If contacts still don't appear:

1. Share the output of the debug endpoint
2. Share the backend logs when generating QR code
3. Check if you can see the contacts in the Emergency page UI
4. Try adding a new contact with a different name

The issue is likely that:
- Contacts aren't being saved to the database
- Contacts are being saved with `active = false`
- There's a user ID mismatch
