# Medication Adherence - Exact Code Changes

## File 1: backend/app/api/v1/medications.py

### Function: get_adherence_stats()

**Location**: Line ~200

**What Changed**: The calculation of `total_scheduled`, `total_taken`, and `adherence_rate`

**Before**:
```python
# Calculate adherence for the specified period
from datetime import timezone
cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)

recent_logs = [
    log for log in (medication.adherence_log or [])
    if datetime.fromisoformat(log.get("scheduled_time", "")).replace(tzinfo=timezone.utc) >= cutoff_time
]

total_scheduled = len(recent_logs)  # ❌ Only counts logged entries
total_taken = sum(1 for log in recent_logs if not log.get("skipped", True))
total_skipped = sum(1 for log in recent_logs if log.get("skipped", False))

adherence_rate = (total_taken / total_scheduled * 100) if total_scheduled > 0 else 0.0
```

**After**:
```python
# Calculate adherence for the specified period
from datetime import timezone
now = datetime.now(timezone.utc)
cutoff_time = now - timedelta(days=days)

# Get scheduled doses from the medication's schedule within the period
scheduled_doses = []
if medication.schedule:
    for scheduled_time in medication.schedule:
        # Ensure timezone-aware
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
        
        # Only count doses within the period and in the past
        if cutoff_time <= scheduled_time <= now:
            scheduled_doses.append(scheduled_time)

# If no schedule is defined, try to infer from adherence log
if not scheduled_doses and medication.adherence_log:
    for log in medication.adherence_log:
        try:
            scheduled_time = datetime.fromisoformat(log.get("scheduled_time", ""))
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            if cutoff_time <= scheduled_time <= now:
                scheduled_doses.append(scheduled_time)
        except (ValueError, TypeError):
            continue

total_scheduled = len(scheduled_doses)  # ✅ Counts from schedule field

# Count taken and skipped from adherence log
recent_logs = []
if medication.adherence_log:
    for log in medication.adherence_log:
        try:
            scheduled_time = datetime.fromisoformat(log.get("scheduled_time", ""))
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            if cutoff_time <= scheduled_time <= now:
                recent_logs.append(log)
        except (ValueError, TypeError):
            continue

total_taken = sum(1 for log in recent_logs if not log.get("skipped", False) and log.get("taken_time"))
total_skipped = sum(1 for log in recent_logs if log.get("skipped", False))

# Calculate adherence rate
adherence_rate = (total_taken / total_scheduled * 100) if total_scheduled > 0 else 0.0
```

**Key Changes**:
1. ✅ Now gets `scheduled_doses` from `medication.schedule` field
2. ✅ Filters by time period (cutoff_time to now)
3. ✅ Falls back to adherence_log if schedule is empty
4. ✅ Better error handling with try/except
5. ✅ Fixed timezone handling

---

## File 2: frontend/src/components/memory/MedicationReminders.tsx

### Change 1: handleCompleteReminder()

**Location**: Line ~50

**What Changed**: Auto-create medication if it doesn't exist

**Before**:
```typescript
const handleCompleteReminder = async (reminderId: string) => {
  try {
    const reminder = reminders.find(r => r.id === reminderId);
    if (!reminder) return;

    await reminderService.completeReminder(reminderId);

    if (reminder.reminder_type === 'medication') {
      try {
        const medName = reminder.title.replace('Take ', '');
        const { medicationService } = await import('../../services/medicationService');
        const medsData = await medicationService.getMedications(true);
        const medication = medsData.medications.find(m => m.name === medName);
        
        if (medication) {  // ❌ Only logs if medication exists
          await medicationService.logMedication(medication.id, {
            scheduled_time: reminder.scheduled_time,
            taken_time: new Date().toISOString(),
            skipped: false,
            notes: 'Logged from reminder',
          });
        }
      } catch (logError) {
        console.error('Failed to log medication adherence:', logError);
      }
    }

    loadMedicationReminders();
  } catch (error) {
    console.error('Failed to complete reminder:', error);
  }
};
```

**After**:
```typescript
const handleCompleteReminder = async (reminderId: string) => {
  try {
    const reminder = reminders.find(r => r.id === reminderId);
    if (!reminder) return;

    await reminderService.completeReminder(reminderId);

    if (reminder.reminder_type === 'medication') {
      try {
        const medName = reminder.title.replace('Take ', '');
        const { medicationService } = await import('../../services/medicationService');
        const medsData = await medicationService.getMedications(true);
        let medication = medsData.medications.find(m => m.name === medName);
        
        // ✅ Auto-create medication if it doesn't exist
        if (!medication) {
          console.log(`Creating medication record for: ${medName}`);
          const dosage = reminder.description?.replace('Dosage: ', '') || 'As prescribed';
          medication = await medicationService.createMedication({
            name: medName,
            dosage: dosage,
            frequency: reminder.frequency || 'daily',
            schedule: [reminder.scheduled_time],
            instructions: 'Created from reminder',
          });
        }
        
        if (medication) {
          await medicationService.logMedication(medication.id, {
            scheduled_time: reminder.scheduled_time,
            taken_time: new Date().toISOString(),
            skipped: false,
            notes: 'Logged from reminder',
          });
          console.log(`Logged medication adherence for ${medName}`);
        }
      } catch (logError) {
        console.error('Failed to log medication adherence:', logError);
      }
    }

    loadMedicationReminders();
  } catch (error) {
    console.error('Failed to complete reminder:', error);
  }
};
```

**Key Changes**:
1. ✅ Changed `const medication` to `let medication` to allow reassignment
2. ✅ Added auto-creation logic if medication not found
3. ✅ Added console logging for debugging
4. ✅ Extracts dosage from reminder description

---

### Change 2: createMedicationReminders()

**Location**: Line ~70

**What Changed**: Generate 30-day schedule and create medication record

**Before**:
```typescript
const createMedicationReminders = async (e: React.FormEvent) => {
  e.preventDefault();

  try {
    // ❌ Only creates reminders, no medication record
    const today = new Date();
    const promises = newMedication.times.map(async (time) => {
      const [hours, minutes] = time.split(':').map(Number);
      const scheduledTime = new Date(today);
      scheduledTime.setHours(hours, minutes, 0, 0);

      if (scheduledTime < today) {
        scheduledTime.setDate(scheduledTime.getDate() + 1);
      }

      const reminderData: ReminderCreate = {
        title: `Take ${newMedication.medication_name}`,
        description: `Dosage: ${newMedication.dosage}`,
        reminder_type: 'medication',
        scheduled_time: scheduledTime.toISOString(),
        frequency: 'daily',
        send_notification: true,
      };

      return reminderService.createReminder(reminderData);
    });

    await Promise.all(promises);

    setShowAddForm(false);
    setNewMedication({
      medication_name: '',
      dosage: '',
      times: ['08:00'],
      days: [0, 1, 2, 3, 4, 5, 6],
    });
    loadMedicationReminders();
  } catch (error) {
    console.error('Failed to create medication reminders:', error);
    alert('Failed to create medication reminders. Please try again.');
  }
};
```

**After**:
```typescript
const createMedicationReminders = async (e: React.FormEvent) => {
  e.preventDefault();

  try {
    // ✅ First, create or update the medication record
    const { medicationService } = await import('../../services/medicationService');
    
    // Check if medication already exists
    const medsData = await medicationService.getMedications(true);
    let medication = medsData.medications.find(m => m.name === newMedication.medication_name);
    
    // ✅ Generate schedule times for the next 30 days
    const schedule: string[] = [];
    const today = new Date();
    for (let day = 0; day < 30; day++) {
      const date = new Date(today);
      date.setDate(date.getDate() + day);
      
      // Check if this day is in the selected days
      if (newMedication.days.includes(date.getDay())) {
        newMedication.times.forEach(time => {
          const [hours, minutes] = time.split(':').map(Number);
          const scheduledTime = new Date(date);
          scheduledTime.setHours(hours, minutes, 0, 0);
          schedule.push(scheduledTime.toISOString());
        });
      }
    }
    
    // ✅ Create or update medication with schedule
    if (!medication) {
      medication = await medicationService.createMedication({
        name: newMedication.medication_name,
        dosage: newMedication.dosage,
        frequency: `${newMedication.times.length}x daily`,
        schedule: schedule,
        instructions: 'Created from reminders',
      });
      console.log(`Created medication: ${medication.name} with ${schedule.length} scheduled doses`);
    } else {
      await medicationService.updateMedication(medication.id, {
        schedule: schedule,
      });
      console.log(`Updated medication: ${medication.name} with ${schedule.length} scheduled doses`);
    }

    // Create a reminder for each scheduled time (next occurrence)
    const promises = newMedication.times.map(async (time) => {
      const [hours, minutes] = time.split(':').map(Number);
      const scheduledTime = new Date(today);
      scheduledTime.setHours(hours, minutes, 0, 0);

      if (scheduledTime < today) {
        scheduledTime.setDate(scheduledTime.getDate() + 1);
      }

      const reminderData: ReminderCreate = {
        title: `Take ${newMedication.medication_name}`,
        description: `Dosage: ${newMedication.dosage}`,
        reminder_type: 'medication',
        scheduled_time: scheduledTime.toISOString(),
        frequency: 'daily',
        send_notification: true,
      };

      return reminderService.createReminder(reminderData);
    });

    await Promise.all(promises);

    setShowAddForm(false);
    setNewMedication({
      medication_name: '',
      dosage: '',
      times: ['08:00'],
      days: [0, 1, 2, 3, 4, 5, 6],
    });
    loadMedicationReminders();
  } catch (error) {
    console.error('Failed to create medication reminders:', error);
    alert('Failed to create medication reminders. Please try again.');
  }
};
```

**Key Changes**:
1. ✅ Import medicationService
2. ✅ Check if medication exists
3. ✅ Generate 30-day schedule array
4. ✅ Respect selected days of week
5. ✅ Create or update medication with schedule
6. ✅ Added console logging
7. ✅ Then create reminders (existing logic)

---

## Summary of Changes

### Backend (1 file, 1 function)
- **File**: `backend/app/api/v1/medications.py`
- **Function**: `get_adherence_stats()`
- **Change**: Calculate `total_scheduled` from `medication.schedule` instead of `adherence_log`

### Frontend (1 file, 2 functions)
- **File**: `frontend/src/components/memory/MedicationReminders.tsx`
- **Function 1**: `handleCompleteReminder()` - Auto-create medication if missing
- **Function 2**: `createMedicationReminders()` - Generate 30-day schedule

### Impact
- ✅ Adherence percentage now shows correct values
- ✅ Medications auto-created when marking reminders as taken
- ✅ Schedule field populated with 30 days of doses
- ✅ Stats calculated correctly: (taken / scheduled) × 100

### Lines of Code Changed
- Backend: ~50 lines modified
- Frontend: ~80 lines added/modified
- Total: ~130 lines changed

### No Breaking Changes
- All changes are backward compatible
- Existing medications continue to work
- Falls back to adherence_log if schedule is empty
