# Final QR Contacts Test Guide

## What Was Fixed

The emergency contacts were not being saved because the `MedicalInfo` Pydantic schema was missing the `emergency_contacts` field. Pydantic was silently dropping this field from incoming requests.

**Fix Applied**: Added `emergency_contacts` field to the schema.

## IMPORTANT: Restart Backend

**You MUST restart the backend for this fix to take effect!**

```bash
# Stop the backend (Ctrl+C in the terminal running it)
# Then start it again:
cd backend
uvicorn app.main:app --reload
```

## Step-by-Step Test

### 1. Restart Backend (Critical!)

```bash
# In the backend terminal, press Ctrl+C to stop
# Then run:
uvicorn app.main:app --reload
```

Wait for: `Application startup complete`

### 2. Open Frontend

Navigate to: http://localhost:3000

### 3. Login

Use the dev login or your Google account

### 4. Go to Emergency Page

Click on "Emergency" in the navigation

### 5. Edit Medical Information

- Scroll to the "Emergency Medical Information" card
- Click "Edit" button

### 6. Add Emergency Contact

- Click "+ Add Contact"
- Enter:
  - Name: "Jane Doe"
  - Phone: "+1-555-0101"
  - Relationship: "Spouse"
- Click OK for each prompt

### 7. Add More Info (Optional)

- Blood Type: "O+"
- Medications: Click "+ Add" and enter "Aspirin 81mg"
- Allergies: Click "+ Add" and enter "Penicillin"

### 8. Save Changes

- Click "Save Changes" button
- Wait for "Medical information saved successfully!" message

### 9. Verify Data Persists

- Refresh the page (F5)
- The emergency contact should still be visible
- If it's gone, the backend wasn't restarted or there's another issue

### 10. Generate QR Code

- Click "Generate QR Code" button
- Wait for the QR code to appear in the modal

### 11. Verify QR Code Content

- Download the QR code (click "Download" button)
- Scan it with your phone's camera app
- You should see:
  ```
  🚨 EMERGENCY MEDICAL INFO 🚨
  
  Patient: [Your Name]
  
  Condition: Memory Impairment
  (Alzheimer's/Dementia)
  
  EMERGENCY CONTACTS:
  1. Jane Doe
     (Spouse)
     Tel: +1-555-0101
  
  MEDICATIONS:
  - Aspirin 81mg
  
  ALLERGIES: Penicillin
  
  BLOOD TYPE: O+
  ```

## Troubleshooting

### Contact Still Not Showing

1. **Check if backend was restarted**:
   - Look for "Application startup complete" in backend terminal
   - If not, restart it

2. **Check browser console for errors**:
   - Open DevTools (F12)
   - Go to Console tab
   - Look for red errors when saving

3. **Check network request**:
   - Open DevTools (F12)
   - Go to Network tab
   - Click "Save Changes"
   - Find the PUT request to `/api/v1/emergency/medical-info`
   - Click on it
   - Check "Payload" tab - should include `emergency_contacts`
   - Check "Response" tab - should echo back the contacts

4. **Use debug endpoint**:
   ```bash
   # Get token from browser DevTools > Application > Local Storage
   TOKEN="your_token_here"
   
   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/emergency/medical-info/debug | jq
   ```
   
   Look for:
   - `emergency_contacts_from_medical_info_count` > 0
   - `emergency_contacts_from_medical_info` array with your contacts

### QR Code Shows "None listed"

If the QR code shows "EMERGENCY CONTACTS: None listed":

1. Verify contacts were saved (step 9 above)
2. Check debug endpoint (step 4 in troubleshooting)
3. Check backend logs for errors during QR generation
4. Look for log lines like:
   - "Found X contacts from medical_info"
   - "Using Y contacts for QR code"

### Backend Errors

If you see errors in the backend terminal:

1. **Pydantic validation error**: Backend wasn't restarted
2. **Database error**: Check database connection
3. **Import error**: Check all dependencies are installed

## What Changed

### Files Modified

1. **backend/app/api/v1/emergency.py**:
   - Added `EmergencyContactInfo` schema
   - Added `emergency_contacts` field to `MedicalInfo` schema
   - Updated GET endpoint to always include `emergency_contacts` field

### Schema Changes

**Before**:
```python
class MedicalInfo(BaseModel):
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    blood_type: Optional[str] = None
    emergency_notes: Optional[str] = None
```

**After**:
```python
class EmergencyContactInfo(BaseModel):
    name: str
    phone: str
    relationship: Optional[str] = None

class MedicalInfo(BaseModel):
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    blood_type: Optional[str] = None
    emergency_notes: Optional[str] = None
    emergency_contacts: Optional[List[EmergencyContactInfo]] = None
```

## Success Criteria

✅ Emergency contact can be added via UI
✅ Contact persists after page refresh
✅ Contact appears in QR code when scanned
✅ Multiple contacts can be added
✅ Contact information is readable in QR code

## Next Steps After Success

Once this works, consider:

1. **Add validation**: Phone number format validation
2. **Add more fields**: Email, address for contacts
3. **Sync to table**: Optionally sync to `emergency_contacts` table
4. **Edit contacts**: Allow editing existing contacts (not just delete/add)
5. **Contact priority**: Allow reordering contacts by importance
