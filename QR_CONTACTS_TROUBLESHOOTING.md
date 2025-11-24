# QR Code Emergency Contacts Troubleshooting Guide

## Problem
QR code shows "EMERGENCY CONTACTS: None listed" even though you've added emergency contacts through the UI.

## Quick Diagnosis

### Option 1: Use Browser DevTools (Easiest)

1. **Open the Emergency page** in your browser
2. **Open DevTools** (F12 or Right-click → Inspect)
3. **Go to Console tab**
4. **Click "Generate QR Code" button**
5. **Look at the Network tab** → Find the request to `/api/v1/emergency/medical-info/qr-code`
6. **Click on that request** → Go to "Response" tab
7. **Check the response** - it should show the data being sent to QR generator

### Option 2: Check Backend Logs

1. **Look at your backend terminal** where `uvicorn` is running
2. **Click "Generate QR Code"** in the UI
3. **Look for these log lines**:
   ```
   INFO: Generating QR code for user <user-id>
   INFO: Found X emergency contacts for user <user-id>
   INFO: Built medical_info with X contacts
   ```

If it says "Found 0 emergency contacts", the contacts aren't in the database.

### Option 3: Use the Debug API Endpoint

**In your browser console**, run:
```javascript
// Get your auth token
const token = localStorage.getItem('token') || localStorage.getItem('auth_token');

// Call debug endpoint
fetch('http://localhost:8000/api/v1/emergency/medical-info/debug', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(data => console.log('Debug data:', data));
```

This will show you exactly what's in the database.

## Common Causes & Solutions

### Cause 1: Contacts Not Saved to Database

**How to check**: Debug endpoint shows `emergency_contacts_count: 0`

**Why it happens**:
- Form validation failed silently
- Network error when saving
- Backend error when saving

**Solution**:
1. Open DevTools → Network tab
2. Try adding a contact again
3. Look for POST request to `/api/v1/emergency/contacts`
4. Check if it returns 201 (success) or an error
5. If error, check the error message

### Cause 2: Contacts Marked as Inactive

**How to check**: Debug endpoint shows contacts but with `active: false`

**Why it happens**:
- Contacts were deleted (soft delete)
- Database migration issue

**Solution**:
Delete and re-add the contacts through the UI.

### Cause 3: Wrong User ID

**How to check**: You see contacts in the UI but debug endpoint shows 0

**Why it happens**:
- Multiple user accounts
- Session/token issue

**Solution**:
1. Log out completely
2. Clear browser cache/local storage
3. Log back in
4. Add contacts again

### Cause 4: Database Not Running

**How to check**: Backend shows connection errors

**Solution**:
```bash
# Start PostgreSQL and Redis
docker-compose up postgres redis -d

# Check if they're running
docker ps
```

## Step-by-Step Fix

### Step 1: Verify Contact is in UI

1. Go to Emergency page
2. Scroll to "Emergency Contacts" section
3. Do you see your contact listed?
   - **YES**: Go to Step 2
   - **NO**: Add the contact again

### Step 2: Check if Contact is in Database

Run this in browser console:
```javascript
const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
fetch('http://localhost:8000/api/v1/emergency/contacts', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(contacts => {
  console.log(`Found ${contacts.length} contacts:`, contacts);
});
```

- **If 0 contacts**: The UI isn't saving properly. Check Step 3.
- **If contacts exist**: Go to Step 4.

### Step 3: Fix Contact Saving

1. Open DevTools → Console
2. Try adding a contact
3. Look for any JavaScript errors
4. Check Network tab for failed requests
5. If you see errors, share them

### Step 4: Verify QR Generation Gets Contacts

Run this in browser console:
```javascript
const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
fetch('http://localhost:8000/api/v1/emergency/medical-info/debug', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(data => {
  console.log('Emergency contacts in database:', data.emergency_contacts_count);
  console.log('Contacts:', data.emergency_contacts);
});
```

- **If 0 contacts**: Database query issue. Check Step 5.
- **If contacts exist**: QR generation should work. Try generating again.

### Step 5: Check Backend Logs

When you generate QR code, you should see:
```
INFO: Generating QR code for user abc-123
INFO: Found 1 emergency contacts for user abc-123
INFO: Built medical_info with 1 contacts
INFO: Emergency contacts data: [{'name': 'John Doe', 'phone': '+1-555-0123', ...}]
```

If you see:
```
WARNING: No emergency contacts found in medical_info!
WARNING: Query returned 1 contacts from database
```

This means contacts exist but aren't being added to medical_info. This is a bug in the code.

## Nuclear Option: Reset Everything

If nothing works:

1. **Delete all contacts**:
   ```javascript
   const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
   fetch('http://localhost:8000/api/v1/emergency/contacts', {
     headers: { 'Authorization': `Bearer ${token}` }
   })
   .then(r => r.json())
   .then(contacts => {
     contacts.forEach(contact => {
       fetch(`http://localhost:8000/api/v1/emergency/contacts/${contact.id}`, {
         method: 'DELETE',
         headers: { 'Authorization': `Bearer ${token}` }
       });
     });
   });
   ```

2. **Restart backend**:
   ```bash
   # Ctrl+C to stop
   # Then start again
   uvicorn app.main:app --reload --port 8000
   ```

3. **Clear browser cache**:
   - DevTools → Application → Clear storage → Clear site data

4. **Refresh page** and add contacts again

5. **Generate QR code**

## What to Share if Still Broken

If it still doesn't work, share:

1. **Output of debug endpoint**:
   ```javascript
   const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
   fetch('http://localhost:8000/api/v1/emergency/medical-info/debug', {
     headers: { 'Authorization': `Bearer ${token}` }
   })
   .then(r => r.json())
   .then(data => console.log(JSON.stringify(data, null, 2)));
   ```

2. **Backend logs** when generating QR code (copy the relevant lines)

3. **Screenshot** of the Emergency page showing the contact

4. **Network tab** screenshot showing the QR code generation request/response

## Expected Working State

When everything works:

1. **UI shows contact**: ✓
2. **GET /emergency/contacts returns contact**: ✓
3. **Debug endpoint shows contact**: ✓
4. **Backend logs show "Found 1 emergency contacts"**: ✓
5. **QR code includes contact info**: ✓

If any step fails, that's where the problem is.
