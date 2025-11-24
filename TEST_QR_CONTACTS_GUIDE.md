# Quick Test Guide: QR Code Emergency Contacts

## Quick Test (Manual)

1. **Start the backend** (if not already running):
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start the frontend** (if not already running):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Login** to the application at http://localhost:3000

4. **Navigate** to the Emergency page

5. **Edit Medical Information**:
   - Click "Edit" on the Medical Information card
   - Add at least one emergency contact:
     - Name: "Jane Doe"
     - Phone: "+1-555-0101"
     - Relationship: "Spouse"
   - Add some medications, allergies, etc. (optional)
   - Click "Save Changes"

6. **Generate QR Code**:
   - Click "Generate QR Code" button
   - Wait for the QR code to appear in the modal

7. **Verify**:
   - The QR code should display
   - Download the QR code
   - Scan it with your phone's camera
   - Verify that "Jane Doe" and the phone number appear in the scanned text

## Quick Test (Automated)

```bash
cd backend
python test_qr_contacts_fix.py
```

This will automatically:
- Login as dev user
- Add test medical info with contacts
- Generate QR code
- Verify the process works

## Debug Endpoint

To check what data will be in the QR code:

```bash
# Get your auth token first (from browser dev tools or login response)
TOKEN="your_token_here"

# Call the debug endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/emergency/medical-info/debug | jq
```

This shows:
- How many contacts are in the database table
- How many contacts are in medical_info
- Which source will be used for QR code
- Full medical info that will be encoded

## Expected Behavior

### Before Fix
- ❌ Emergency contacts saved via Medical Info form don't appear in QR code
- ❌ QR code only shows "EMERGENCY CONTACTS: None listed"

### After Fix
- ✅ Emergency contacts saved via Medical Info form appear in QR code
- ✅ QR code shows contact names, phone numbers, and relationships
- ✅ Contacts from emergency_contacts table (if any) take priority
- ✅ Falls back to medical_info contacts if table is empty

## Troubleshooting

### QR Code Still Shows No Contacts

1. **Check the debug endpoint** to see what data is available:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/emergency/medical-info/debug
   ```

2. **Check backend logs** for errors:
   ```bash
   # Look for lines like:
   # "Found X contacts from emergency_contacts table"
   # "Found Y contacts from medical_info"
   # "Using Z contacts for QR code"
   ```

3. **Verify medical info was saved**:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/emergency/medical-info
   ```

4. **Check if emergency_contacts field exists** in the response

### Backend Not Starting

Make sure you have all dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Not Connecting

Check that:
- Backend is running on http://localhost:8000
- Frontend is running on http://localhost:3000
- CORS is enabled in backend

## What Changed

The fix modifies how emergency contacts are retrieved for QR code generation:

**Old Logic**:
1. Get contacts from table
2. Build medical_info with those contacts
3. Later, check if medical_info has contacts (too late!)

**New Logic**:
1. Get contacts from table
2. Get contacts from medical_info
3. Choose which to use (prefer table, fallback to medical_info)
4. Build medical_info with chosen contacts

This ensures contacts saved via the Medical Info form are properly included in the QR code.
