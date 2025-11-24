import React, { useState, useEffect } from 'react';
import { reminderService, ReminderCreate, Reminder } from '../../services/memoryService';
import { motion, AnimatePresence } from 'framer-motion';

interface MedicationSchedule {
  medication_name: string;
  dosage: string;
  times: string[]; // Array of times like ["08:00", "20:00"]
  days: number[]; // Days of week [0-6]
}

const MedicationReminders: React.FC = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);

  const [newMedication, setNewMedication] = useState<MedicationSchedule>({
    medication_name: '',
    dosage: '',
    times: ['08:00'],
    days: [0, 1, 2, 3, 4, 5, 6],
  });

  useEffect(() => {
    loadMedicationReminders();
  }, []);

  const loadMedicationReminders = async () => {
    try {
      setLoading(true);
      const data = await reminderService.getReminders({
        reminder_type: 'medication',
        is_active: true,
      });
      setReminders(data.reminders);
    } catch (error) {
      console.error('Failed to load medication reminders:', error);
    } finally {
      setLoading(false);
    }
  };

  const createMedicationReminders = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // First, create or update the medication record
      const { medicationService } = await import('../../services/medicationService');
      
      // Check if medication already exists
      const medsData = await medicationService.getMedications(true);
      let medication = medsData.medications.find(m => m.name === newMedication.medication_name);
      
      // Generate schedule times for the next 30 days
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
      
      if (!medication) {
        // Create new medication
        medication = await medicationService.createMedication({
          name: newMedication.medication_name,
          dosage: newMedication.dosage,
          frequency: `${newMedication.times.length}x daily`,
          schedule: schedule,
          instructions: 'Created from reminders',
        });
        console.log(`Created medication: ${medication.name} with ${schedule.length} scheduled doses`);
      } else {
        // Update existing medication schedule
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

        // If the time has passed today, schedule for tomorrow
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

  const handleCompleteReminder = async (reminderId: string) => {
    try {
      // Find the reminder to get medication info
      const reminder = reminders.find(r => r.id === reminderId);
      if (!reminder) return;

      // Complete the reminder
      await reminderService.completeReminder(reminderId);

      // Also log the medication adherence if it's a medication reminder
      if (reminder.reminder_type === 'medication') {
        try {
          // Extract medication name from title (format: "Take {medication_name}")
          const medName = reminder.title.replace('Take ', '');
          
          // Get all medications to find the matching one
          const { medicationService } = await import('../../services/medicationService');
          const medsData = await medicationService.getMedications(true);
          let medication = medsData.medications.find(m => m.name === medName);
          
          // If medication doesn't exist, create it
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
            // Log the medication as taken
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
          // Don't fail the whole operation if logging fails
        }
      }

      loadMedicationReminders();
    } catch (error) {
      console.error('Failed to complete reminder:', error);
    }
  };

  const handleDeleteReminder = async (reminderId: string) => {
    if (window.confirm('Are you sure you want to delete this medication reminder?')) {
      try {
        await reminderService.deleteReminder(reminderId);
        loadMedicationReminders();
      } catch (error) {
        console.error('Failed to delete reminder:', error);
      }
    }
  };

  const addTimeSlot = () => {
    setNewMedication({
      ...newMedication,
      times: [...newMedication.times, '12:00'],
    });
  };

  const removeTimeSlot = (index: number) => {
    setNewMedication({
      ...newMedication,
      times: newMedication.times.filter((_, i) => i !== index),
    });
  };

  const updateTimeSlot = (index: number, value: string) => {
    const newTimes = [...newMedication.times];
    newTimes[index] = value;
    setNewMedication({
      ...newMedication,
      times: newTimes,
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-blue-50">Medication Reminders</h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-gradient-to-r from-teal-500 to-cyan-500 text-white rounded-lg hover:from-teal-600 hover:to-cyan-600 transition-all shadow-lg"
        >
          {showAddForm ? 'Cancel' : '+ Add Medication'}
        </button>
      </div>

      {/* Add medication form */}
      <AnimatePresence>
        {showAddForm && (
          <motion.form
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            onSubmit={createMedicationReminders}
            className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4 text-blue-50">Add Medication Schedule</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Medication Name *
                </label>
                <input
                  type="text"
                  required
                  value={newMedication.medication_name}
                  onChange={(e) =>
                    setNewMedication({ ...newMedication, medication_name: e.target.value })
                  }
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Aspirin"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Dosage *</label>
                <input
                  type="text"
                  required
                  value={newMedication.dosage}
                  onChange={(e) => setNewMedication({ ...newMedication, dosage: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 100mg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Reminder Times *
                </label>
                {newMedication.times.map((time, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="time"
                      required
                      value={time}
                      onChange={(e) => updateTimeSlot(index, e.target.value)}
                      className="flex-1 px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    {newMedication.times.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeTimeSlot(index)}
                        className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addTimeSlot}
                  className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  + Add Time
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Days of Week
                </label>
                <div className="flex gap-2">
                  {dayNames.map((day, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => {
                        const days = newMedication.days;
                        if (days.includes(index)) {
                          setNewMedication({
                            ...newMedication,
                            days: days.filter((d) => d !== index),
                          });
                        } else {
                          setNewMedication({
                            ...newMedication,
                            days: [...days, index].sort(),
                          });
                        }
                      }}
                      className={`px-3 py-2 rounded-lg transition-colors ${
                        newMedication.days.includes(index)
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-600 text-white'
                      }`}
                    >
                      {day}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-gradient-to-r from-teal-500 to-cyan-500 text-white rounded-lg hover:from-teal-600 hover:to-cyan-600 transition-all shadow-lg"
              >
                Create Reminders
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>

      {/* Medication reminders list */}
      <div className="space-y-4">
        <AnimatePresence>
          {reminders.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12 backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg"
            >
              <p className="text-xl mb-2 text-white">No medication reminders</p>
              <p className="text-sm text-gray-400">Add your first medication to get started</p>
            </motion.div>
          ) : (
            reminders.map((reminder) => (
              <motion.div
                key={reminder.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-4 border-l-4 ${
                  reminder.is_completed ? 'border-green-500 opacity-60' : 'border-blue-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">💊</span>
                      <span className="px-2 py-1 rounded text-xs text-white bg-blue-500">
                        Medication
                      </span>
                      <span className="px-2 py-1 rounded text-xs bg-gray-600 text-white">
                        {reminder.frequency}
                      </span>
                    </div>

                    <h3
                      className={`text-lg font-semibold mb-1 ${
                        reminder.is_completed ? 'line-through text-gray-500' : 'text-blue-50'
                      }`}
                    >
                      {reminder.title}
                    </h3>

                    {reminder.description && (
                      <p className="text-gray-400 text-sm mb-2">{reminder.description}</p>
                    )}

                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>{formatTime(reminder.scheduled_time)}</span>
                      {reminder.is_completed && reminder.completed_at && (
                        <span className="text-green-400">
                          ✓ Taken {formatTime(reminder.completed_at)}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 ml-4">
                    {!reminder.is_completed && (() => {
                      const scheduledTime = new Date(reminder.scheduled_time);
                      const now = new Date();
                      const isFuture = scheduledTime > now;
                      
                      return (
                        <button
                          onClick={() => handleCompleteReminder(reminder.id)}
                          disabled={isFuture}
                          className={`px-3 py-1 rounded transition-colors text-sm ${
                            isFuture
                              ? 'bg-gray-500 text-gray-300 cursor-not-allowed opacity-50'
                              : 'bg-green-500 text-white hover:bg-green-600'
                          }`}
                          title={isFuture ? 'Cannot mark as taken before scheduled time' : 'Mark as taken'}
                        >
                          {isFuture ? 'Not Due Yet' : 'Mark Taken'}
                        </button>
                      );
                    })()}
                    <button
                      onClick={() => handleDeleteReminder(reminder.id)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default MedicationReminders;
