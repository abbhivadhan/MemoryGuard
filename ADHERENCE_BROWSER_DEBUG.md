# Adherence Calculation Browser Debug Guide

## Problem
- ✅ Medications are being logged (visible in "Recent Activity")
- ❌ Adherence percentage shows 0% instead of correct value

## Root Cause
The adherence calculation is likely failing due to a time format mismatch between:
1. When the medication is logged (`taken_time`)
2. When it was scheduled (`scheduled_time`)

## How to Debug in Browser

### Step 1: Open Browser DevTools
1. Open the Memory Assistant page
2. Press `F12` or `Cmd+Option+I` (Mac) to open DevTools
3. Go to the **Network** tab
4. Make sure "Preserve log" is checked

### Step 2: Check Medication Data
1. Refresh the page
2. Look for a request to `/api/v1/medications` or similar
3. Click on it and go to the **Response** tab
4. Look for your medication object

### Step 3: Examine the Data Structure
Look for these fields in the medication object:

```json
{
  "id": "...",
  "name": "Aspirin",
  "schedule": [
    "2024-11-24T09:00:00Z",
    "2024-11-24T21:00:00Z"
  ],
  "adherence_log": [
    {
      "scheduled_time": "2024-11-24T09:00:00Z",
      "taken_time": "2024-11-24T09:05:23.456Z",
      "skipped": false
    }
  ]
}
```

### Step 4: Check for Mismatches
Compare the formats:
- **scheduled_time** format: `____________________`
- **taken_time** format: `____________________`
- Do they match? YES / NO

Common issues:
- ❌ One has timezone (`Z` or `+00:00`), other doesn't
- ❌ One has milliseconds (`.456`), other doesn't
- ❌ One is ISO string, other is timestamp number
- ❌ Dates don't match (logged on wrong day)

### Step 5: Check the Calculation Logic
1. Look for a request to get adherence stats
2. Check what parameters are being sent
3. Check what's being returned

## Expected Behavior

### Correct Data Flow:
1. **Medication Created** → `schedule` array populated with future times
2. **Reminder Triggered** → User sees notification
3. **User Marks as Taken** → Entry added to `adherence_log` with:
   - `scheduled_time`: Matches one of the times in `schedule`
   - `taken_time`: Current time when marked
   - `skipped`: false

4. **Adherence Calculated**:
   ```
   adherence = (taken_count / scheduled_count) * 100
   ```

### What to Look For:
- Are there entries in `adherence_log`? (You said YES)
- Do the `scheduled_time` values match times in `schedule`?
- Are the times within the last 7 days?
- Is `skipped` set to `false`?

## Quick Fixes to Try

### Fix 1: Time Format Normalization
The issue is likely in `frontend/src/services/medicationService.ts` or `backend/app/api/v1/medications.py`.

When logging adherence, ensure both times use the same format:
```typescript
// Frontend - when marking as taken
const logEntry = {
  scheduled_time: scheduledTime.toISOString(),  // Always ISO
  taken_time: new Date().toISOString(),         // Always ISO
  skipped: false
};
```

### Fix 2: Calculation Window
The calculation might be looking at the wrong time window. Check if:
- It's using UTC vs local time
- The 7-day window is calculated correctly
- Timezone offsets are handled

### Fix 3: Database Query
The backend might be filtering out valid logs. Check:
- Are logs being saved to the database?
- Is the query filtering by the correct date range?
- Are timezone conversions correct?

## What to Send Me

If you want me to fix it, send me:

1. **Medication Object** (from Network tab):
```json
{
  "schedule": [...],
  "adherence_log": [...]
}
```

2. **Timestamps**:
- What format is `scheduled_time`?
- What format is `taken_time`?
- Do they match?

3. **Calculation Result**:
- What does the API return for adherence percentage?
- What should it be?

## Files to Check

If you want to fix it yourself:

### Frontend:
- `frontend/src/services/medicationService.ts` - Line ~200-300 (adherence logging)
- `frontend/src/components/memory/AdherenceTracker.tsx` - Display logic

### Backend:
- `backend/app/api/v1/medications.py` - Adherence calculation endpoint
- `backend/app/models/medication.py` - `calculate_adherence_rate()` method (line 77)

## Most Likely Fix

Based on the symptoms, the issue is probably in `backend/app/models/medication.py` line 77-90:

```python
def calculate_adherence_rate(self, days: int = 7) -> float:
    if not self.adherence_log:
        return 0.0
    
    cutoff_time = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
    recent_logs = [
        log for log in self.adherence_log
        if datetime.fromisoformat(log.get("scheduled_time", "")).timestamp() >= cutoff_time
    ]
    
    if not recent_logs:
        return 0.0  # ← THIS IS PROBABLY RETURNING
    
    taken_count = sum(1 for log in recent_logs if not log.get("skipped", True))
    return (taken_count / len(recent_logs)) * 100
```

The `datetime.fromisoformat()` might be failing to parse the time, or the timezone conversion is wrong.

## Next Steps

1. Check the Network tab and send me the actual data
2. Or try the Quick Fix 1 above
3. Or I can write a targeted fix once I see the actual data format
