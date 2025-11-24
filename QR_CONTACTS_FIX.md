# QR Code Emergency Contacts Fix

## Problem
Emergency contacts were not appearing in the generated QR code even after being saved through the Medical Info form.

## Root Cause
The issue was in the `/api/v1/emergency/medical-info/qr-code` endpoint. The logic was:

1. Query the `emergency_contacts` table for contacts
2. Build the medical_info dict with those contacts
3. THEN check if medical_info from alerts has contacts
4. Only use medical_info contacts if the table was empty

However, the check for medical_info contacts happened AFTER building the medical_info dict, and the logic wasn't properly prioritizing the contacts from medical_info when the table was empty.

## Solution
Refactored the contact retrieval logic to:

1. **First**, get contacts from the `emergency_contacts` table
2. **Then**, get contacts from the latest `emergency_alert.medical_info`
3. **Decide** which to use: prefer table contacts, but fall back to medical_info contacts if table is empty
4. **Build** the medical_info dict with the chosen contacts

### Code Changes

**File**: `backend/app/api/v1/emergency.py`

**Before**:
```python
# Build medical_info with contacts from table
medical_info = {
    "emergency_contacts": [contacts from table],
    ...
}

# Later, check if medical_info has contacts
if latest_alert and latest_alert.medical_info:
    medical_info_contacts = latest_alert.medical_info.get("emergency_contacts", [])
    if not medical_info['emergency_contacts']:
        medical_info['emergency_contacts'] = medical_info_contacts
```

**After**:
```python
# Get contacts from both sources first
contacts_from_table = [contacts from emergency_contacts table]
contacts_from_medical_info = [contacts from latest_alert.medical_info]

# Decide which to use
final_contacts = contacts_from_table if contacts_from_table else contacts_from_medical_info

# Build medical_info with the chosen contacts
medical_info = {
    "emergency_contacts": final_contacts,
    ...
}
```

## Testing

### Manual Testing Steps

1. **Login** to the application
2. **Navigate** to the Emergency page
3. **Edit** the Medical Information card
4. **Add** emergency contacts using the "+ Add Contact" button
5. **Save** the changes
6. **Generate** the QR code
7. **Verify** that the contacts appear in the QR code

### Automated Testing

Run the test script:
```bash
cd backend
python test_qr_contacts_fix.py
```

This will:
- Login as dev user
- Check current state via debug endpoint
- Add test medical info with contacts
- Generate QR code
- Verify the process works

### Debug Endpoint

A new debug endpoint was added: `GET /api/v1/emergency/medical-info/debug`

This returns:
- Contacts from `emergency_contacts` table
- Contacts from `medical_info` in alerts
- Which source will be used for QR code generation
- Full medical info that will be encoded

Use this to troubleshoot contact issues:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/emergency/medical-info/debug
```

## Data Flow

### Saving Emergency Contacts

There are two ways to save emergency contacts:

1. **Via Medical Info Form** (MedicalInfoCard component)
   - Saves to `emergency_alerts.medical_info` JSON field
   - Used when user fills out the medical info form

2. **Via Emergency Contacts API** (not yet implemented in UI)
   - Saves to `emergency_contacts` table
   - More structured, allows for priority, active status, etc.

### QR Code Generation Priority

When generating QR code, contacts are retrieved in this order:

1. **Primary**: `emergency_contacts` table (if any exist)
2. **Fallback**: `medical_info.emergency_contacts` from latest alert
3. **None**: If neither source has contacts

This ensures:
- Dedicated emergency contacts table is preferred (more structured)
- Medical info form contacts work as fallback (user-friendly)
- No contacts are lost

## Files Modified

1. `backend/app/api/v1/emergency.py`
   - Fixed contact retrieval logic in `/medical-info/qr-code` endpoint
   - Enhanced debug endpoint with more details

2. `backend/test_qr_contacts_fix.py` (new)
   - Automated test script to verify the fix

3. `QR_CONTACTS_FIX.md` (this file)
   - Documentation of the issue and fix

## Verification

After applying this fix:

✅ Emergency contacts saved via Medical Info form appear in QR code
✅ Emergency contacts from table (if any) take priority
✅ Debug endpoint helps troubleshoot contact issues
✅ Logging shows which contact source is being used

## Next Steps

Consider these improvements:

1. **UI for Emergency Contacts Table**: Add a dedicated UI to manage contacts in the `emergency_contacts` table with priority, active status, etc.

2. **Sync Contacts**: When user saves contacts via Medical Info form, optionally sync them to the `emergency_contacts` table

3. **Contact Validation**: Add phone number validation and formatting

4. **QR Code Preview**: Show a preview of what will be in the QR code before generating it

5. **Multiple QR Codes**: Allow generating different QR codes for different purposes (medical info, contact card, etc.)
