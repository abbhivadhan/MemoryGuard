# Fix Zero Adherence - Quick Action Guide

## The Problem

Adherence showing 0% because old medications don't have the `schedule` field populated.

## The Solution (3 Steps)

### Step 1: Delete Old Medications

1. Go to **Memory Assistant** → **Medication Management** tab
2. Click **Delete** on each medication showing 0% adherence
3. Confirm deletion

### Step 2: Recreate Medications (Using Fixed Code)

1. Go to **Memory Assistant** → **Medication Reminders** tab
2. Click **"+ Add Medication"**
3. Fill in the form:
   - **Medication Name**: e.g., "Aspirin"
   - **Dosage**: e.g., "100mg"
   - **Reminder Times**: Add times (e.g., 08:00 and 20:00)
   - **Days of Week**: Select all days (Mon-Sun)
4. Click **"Create Reminders"**

**What happens**: The fixed code now creates a medication record with a 30-day schedule (60 doses for 2×/day)

### Step 3: Mark Reminders as Taken

1. Find the reminder in the list
2. Click **"Mark Taken"**
3. Go to **Adherence** tab
4. Click **"Refresh"**

**Expected Result**: Adherence should now show a percentage > 0%

## Verify It's Working

Open browser console (F12) and look for these messages:

**When creating medication**:
```
Created medication: Aspirin with 60 scheduled doses
```

**When marking as taken**:
```
Logged medication adherence for Aspirin
```

**In Adherence tab**:
- Total Scheduled: 14 (for 7 days × 2 doses/day)
- Total Taken: 1
- Adherence Rate: 7.1%

## Why This Fixes It

**Before**: 
- Medications had empty `schedule` field
- Backend calculated: `total_scheduled = 0`
- Result: `adherence_rate = 0 / 0 = 0%`

**After**:
- Medications have populated `schedule` field with 60 doses
- Backend calculated: `total_scheduled = 14` (for 7 days)
- Result: `adherence_rate = 1 / 14 = 7.1%`

## Still Not Working?

1. **Check browser console** for errors
2. **Check Network tab** (F12 → Network):
   - Look for `POST /api/v1/medications/` response
   - Verify `schedule` array has entries
3. **Hard refresh** the page: Cmd+Shift+R or Ctrl+Shift+R
4. **See detailed debugging**: [ADHERENCE_BROWSER_DEBUG.md](ADHERENCE_BROWSER_DEBUG.md)

## Key Point

**You must delete and recreate medications** created before the fix. The old medications don't have schedules and can't calculate adherence correctly.
