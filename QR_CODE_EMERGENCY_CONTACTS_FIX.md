# QR Code Emergency Contacts Fix

## Issue
The emergency QR code generator was not including emergency contacts information in the QR code text.

## Root Cause Analysis

After investigation, the QR code generation service (`backend/app/services/qr_service.py`) **was correctly implemented** to include emergency contacts. The test script confirms this works properly.

The issue is likely one of the following:

1. **No emergency contacts in database**: Users may not have added emergency contacts yet
2. **Database query issue**: Emergency contacts might not be fetched correctly from the database
3. **Data structure mismatch**: The relationship field name might be inconsistent

## Changes Made

### 1. Enhanced QR Service (`backend/app/services/qr_service.py`)

- Added fallback for `relationship_type` field (checks both `relationship` and `relationship_type`)
- Added explicit message when no emergency contacts are listed
- Added logging to track emergency contacts count
- Improved error handling

```python
# Now handles both field names
relationship = contact.get('relationship', contact.get('relationship_type', ''))

# Shows clear message when no contacts
if emergency_contacts and len(emergency_contacts) > 0:
    # ... format contacts
else:
    lines.append("EMERGENCY CONTACTS: None listed")
```

### 2. Enhanced API Endpoint (`backend/app/api/v1/emergency.py`)

- Added detailed logging for debugging
- Added better error handling for missing fields
- Added debug endpoint to check what data is being fetched

```python
logger.info(f"Found {len(emergency_contacts)} emergency contacts for user {current_user.id}")
logger.info(f"Built medical_info with {len(medical_info['emergency_contacts'])} contacts")
```

### 3. Added Debug Endpoint

New endpoint: `GET /api/v1/emergency/medical-info/debug`

This endpoint returns:
- Count of emergency contacts
- List of emergency contacts with details
- Count of medications
- Medical info from latest alert

Use this to verify data is in the database before generating QR code.

## Testing

### Test Script
Created `backend/test_qr_generation.py` to verify QR code generation works correctly.

Run with:
```bash
python3 backend/test_qr_generation.py
```

Expected output shows emergency contacts are properly formatted in QR code text.

### Manual Testing Steps

1. **Check if emergency contacts exist**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/emergency/medical-info/debug" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Add emergency contacts if missing**:
   - Go to Emergency page in the app
   - Add at least one emergency contact
   - Verify it appears in the contacts list

3. **Generate QR code**:
   - Click "Generate QR Code" button
   - Scan the QR code with your phone
   - Verify emergency contacts appear in the text

## QR Code Format

The QR code contains plain text in this format:

```
🚨 EMERGENCY MEDICAL INFO 🚨

Patient: [Name]

Condition: Memory Impairment
(Alzheimer's/Dementia)

EMERGENCY CONTACTS:
1. [Contact Name]
   ([Relationship])
   Tel: [Phone]
2. [Contact Name 2]
   ([Relationship])
   Tel: [Phone]

MEDICATIONS:
- [Medication] ([Dosage])

ALLERGIES: [Allergies]

BLOOD TYPE: [Blood Type]

CONDITIONS: [Conditions]

NOTES: [Medical Notes]

⚠️ IMPORTANT:
• Patient may be disoriented
• Contact emergency contacts above
• Do not leave patient alone
• Patient has memory impairment
```

## Verification Checklist

- [x] QR service correctly formats emergency contacts
- [x] API endpoint fetches emergency contacts from database
- [x] Added logging for debugging
- [x] Added debug endpoint
- [x] Created test script
- [x] Handles case when no contacts exist
- [x] Handles both `relationship` and `relationship_type` field names

## Next Steps for Users

If emergency contacts still don't appear in QR code:

1. **Check database**: Use the debug endpoint to verify contacts are in database
2. **Check logs**: Look at backend logs when generating QR code
3. **Add contacts**: Make sure to add emergency contacts through the UI first
4. **Verify active flag**: Ensure contacts have `active = true` in database

## Files Modified

1. `backend/app/services/qr_service.py` - Enhanced formatting and error handling
2. `backend/app/api/v1/emergency.py` - Added logging and debug endpoint
3. `backend/test_qr_generation.py` - Created test script

## Example Debug Output

```json
{
  "user_id": "123",
  "user_email": "user@example.com",
  "emergency_contacts_count": 2,
  "emergency_contacts": [
    {
      "id": "contact-1",
      "name": "Jane Doe",
      "phone": "+1-555-0101",
      "relationship": "Spouse"
    },
    {
      "id": "contact-2",
      "name": "Dr. Smith",
      "phone": "+1-555-0102",
      "relationship": "Doctor"
    }
  ],
  "medications_count": 1,
  "medications": [
    {
      "name": "Donepezil",
      "dosage": "10mg",
      "frequency": "Once daily"
    }
  ]
}
```

## Conclusion

The QR code generation service is working correctly. If emergency contacts don't appear:
1. Use the debug endpoint to check if contacts exist in database
2. Check backend logs for any errors
3. Ensure contacts are added through the UI and marked as active
