# Emergency Contacts Schema Fix

## The Real Problem

The emergency contacts were **NOT being saved** because the `MedicalInfo` Pydantic schema in the backend was missing the `emergency_contacts` field!

### What Was Happening

1. Frontend sends medical info with `emergency_contacts`:
   ```json
   {
     "medications": ["Aspirin"],
     "allergies": ["Penicillin"],
     "blood_type": "O+",
     "emergency_contacts": [
       {
         "name": "Jane Doe",
         "phone": "+1-555-0101",
         "relationship": "Spouse"
       }
     ]
   }
   ```

2. Backend receives the request but **Pydantic validation strips out `emergency_contacts`** because it's not in the schema

3. Backend saves medical info **WITHOUT** emergency contacts:
   ```json
   {
     "medications": ["Aspirin"],
     "allergies": ["Penicillin"],
     "blood_type": "O+"
     // emergency_contacts is missing!
   }
   ```

4. QR code generation can't find contacts because they were never saved

## The Fix

### Added `emergency_contacts` to MedicalInfo Schema

**File**: `backend/app/api/v1/emergency.py`

**Before**:
```python
class MedicalInfo(BaseModel):
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    blood_type: Optional[str] = None
    emergency_notes: Optional[str] = None
    # emergency_contacts is MISSING!
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
    emergency_contacts: Optional[List[EmergencyContactInfo]] = None  # NOW INCLUDED!
```

### Updated GET Endpoint

Also updated the GET endpoint to ensure `emergency_contacts` field always exists:

```python
if latest_alert and latest_alert.medical_info:
    # Ensure emergency_contacts field exists
    medical_info = latest_alert.medical_info
    if isinstance(medical_info, dict) and 'emergency_contacts' not in medical_info:
        medical_info['emergency_contacts'] = []
    return medical_info

return {
    "medications": [],
    "allergies": [],
    "conditions": [],
    "blood_type": "",
    "emergency_notes": "",
    "emergency_contacts": []  # Always include this field
}
```

## Testing

### Quick Test

1. **Restart the backend** (important - schema changes require restart):
   ```bash
   # Stop the backend (Ctrl+C)
   # Start it again
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Clear old data** (optional but recommended):
   - Login to the app
   - Go to Emergency page
   - Edit Medical Information
   - Clear any existing data

3. **Add new emergency contact**:
   - Click "+ Add Contact"
   - Name: "Test Contact"
   - Phone: "+1-555-1234"
   - Relationship: "Friend"
   - Click "Save Changes"

4. **Verify it was saved**:
   - Refresh the page
   - The contact should still be there

5. **Generate QR Code**:
   - Click "Generate QR Code"
   - The contact should appear in the QR code

### Verify with Debug Endpoint

```bash
# Get your auth token from browser dev tools
TOKEN="your_token_here"

# Check what's saved
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/emergency/medical-info/debug | jq
```

Look for:
- `emergency_contacts_from_medical_info_count` should be > 0
- `emergency_contacts_from_medical_info` should contain your contacts

## Why This Happened

Pydantic (FastAPI's validation library) is **strict by default**. When you define a schema, it only accepts fields that are explicitly defined. Any extra fields in the request are silently ignored.

This is actually a **security feature** to prevent injection attacks, but it means you must explicitly define all fields you want to accept.

## Summary

The issue was NOT in the QR code generation logic - that was working fine. The issue was that emergency contacts were never being saved in the first place because the Pydantic schema was rejecting them.

**Fix**: Added `emergency_contacts` field to the `MedicalInfo` schema so the backend accepts and saves it.

**Result**: Emergency contacts are now properly saved and will appear in the QR code.
