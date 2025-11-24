# QR Code Emergency Contacts - Final Fix

## Problem Identified

The emergency contacts weren't showing in the QR code because there are **TWO separate systems** for storing contacts:

1. **Emergency Contacts Table** (`emergency_contacts`) - Separate table for emergency contacts
2. **Medical Info** (`emergency_alerts.medical_info`) - JSON field that can also store contacts

When you click "+ Add Contact" in the Medical Info card, it saves contacts to the `medical_info` JSON field, NOT to the `emergency_contacts` table.

The QR code generator was ONLY looking in the `emergency_contacts` table, so it couldn't find the contacts you added through the Medical Info form.

## The Fix

Modified `backend/app/api/v1/emergency.py` to check BOTH locations:

1. First checks the `emergency_contacts` table (proper emergency contacts)
2. If no contacts found there, checks the `medical_info` field from the latest alert
3. Uses whichever source has contacts

### Code Changes

```python
# After getting medical info from latest alert
medical_info_contacts = latest_alert.medical_info.get("emergency_contacts", [])
if medical_info_contacts and len(medical_info_contacts) > 0:
    logger.info(f"Found {len(medical_info_contacts)} contacts in medical_info")
    # If no contacts from emergency_contacts table, use these
    if not medical_info['emergency_contacts']:
        medical_info['emergency_contacts'] = medical_info_contacts
        logger.info("Using contacts from medical_info since emergency_contacts table is empty")
```

## How to Test

1. **Go to Emergency page**
2. **Click "Edit" on the Medical Info card**
3. **Click "+ Add Contact"**
4. **Enter contact details** in the prompts:
   - Name: John Doe
   - Phone: +1-555-0123
   - Relationship: Spouse
5. **Click "Save"** (IMPORTANT - must save!)
6. **Click "Generate QR Code"**
7. **Scan the QR code** - you should now see:
   ```
   EMERGENCY CONTACTS:
   1. John Doe
      (Spouse)
      Tel: +1-555-0123
   ```

## Important Notes

- You MUST click "Save" after adding contacts
- The contacts are saved as part of medical info, not as separate emergency contacts
- The QR code now checks both locations for contacts

## Why This Happened

The app has two ways to manage emergency contacts:
1. Through the Medical Info form (what you were using)
2. Through a dedicated Emergency Contacts API (not exposed in UI yet)

The QR code was only checking method #2, but you were using method #1.

## Future Improvement

Consider adding a dedicated "Emergency Contacts" section in the UI that:
- Saves directly to the `emergency_contacts` table
- Has a proper form (not just prompts)
- Shows validation errors
- Allows editing existing contacts

This would be cleaner than storing contacts in the medical_info JSON field.

## Verification

After the fix, check the backend logs when generating QR code. You should see:
```
INFO: Found 0 emergency contacts for user <id>
INFO: Found X contacts in medical_info
INFO: Using contacts from medical_info since emergency_contacts table is empty
```

This confirms the fix is working.
