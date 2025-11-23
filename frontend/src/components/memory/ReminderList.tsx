import React, { useState, useEffect } from 'react';
import { Reminder, reminderService, ReminderCreate } from '../../services/memoryService';
import ReminderCard from './ReminderCard';
import { motion, AnimatePresence } from 'framer-motion';
import EmptyState, { EmptyStateIcons } from '../ui/EmptyState';

const ReminderList: React.FC = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('active');

  // Check if user is authenticated
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No access token found. Please log in again.');
      alert('Your session has expired. Please log in again.');
      window.location.href = '/';
    }
  }, []);

  const [newReminder, setNewReminder] = useState<ReminderCreate>({
    title: '',
    description: '',
    reminder_type: 'custom',
    scheduled_time: '',
    frequency: 'once',
    send_notification: true,
  });

  useEffect(() => {
    loadReminders();
  }, [filter]);

  const loadReminders = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      
      if (filter === 'active') {
        filters.is_active = true;
        filters.is_completed = false;
      } else if (filter === 'completed') {
        filters.is_completed = true;
      }

      const data = await reminderService.getReminders(filters);
      setReminders(data.reminders);
    } catch (error: any) {
      console.error('Failed to load reminders:', error);
      if (error.response?.status === 401) {
        alert('Your session has expired. Please log in again.');
        window.location.href = '/';
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Validate required fields
      if (!newReminder.title || !newReminder.scheduled_time) {
        alert('Please fill in all required fields (Title and Scheduled Time)');
        return;
      }

      // Convert datetime-local string to ISO string
      const scheduledDate = new Date(newReminder.scheduled_time);
      
      // Check if date is valid
      if (isNaN(scheduledDate.getTime())) {
        alert('Invalid date/time. Please select a valid date and time.');
        return;
      }

      const reminderData = {
        ...newReminder,
        scheduled_time: scheduledDate.toISOString(),
        description: newReminder.description || undefined, // Send undefined instead of empty string
      };
      
      console.log('Creating reminder with data:', reminderData);
      
      await reminderService.createReminder(reminderData);
      setShowCreateForm(false);
      setNewReminder({
        title: '',
        description: '',
        reminder_type: 'custom',
        scheduled_time: '',
        frequency: 'once',
        send_notification: true,
      });
      loadReminders();
      alert('Reminder created successfully!');
    } catch (error: any) {
      console.error('Failed to create reminder:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create reminder';
      alert(`Failed to create reminder: ${errorMessage}`);
    }
  };

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
        <h2 className="text-3xl font-bold text-blue-50">Reminders</h2>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all shadow-lg"
        >
          {showCreateForm ? 'Cancel' : '+ New Reminder'}
        </motion.button>
      </div>

      {/* Filter tabs */}
      <div className="flex justify-center mb-6">
        <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-2 inline-flex gap-2">
          {[
            { id: 'active' as const, label: 'Active' },
            { id: 'completed' as const, label: 'Completed' },
            { id: 'all' as const, label: 'All' },
          ].map((tab) => (
            <motion.button
              key={tab.id}
              onClick={() => setFilter(tab.id)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-6 py-2 rounded-xl transition-all text-sm font-medium relative overflow-hidden ${
                filter === tab.id ? 'text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              {filter === tab.id && (
                <motion.div
                  layoutId="activeReminderFilter"
                  className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl"
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                />
              )}
              <span className="relative z-10">{tab.label}</span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Create form */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.form
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            onSubmit={handleCreateReminder}
            className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4">Create New Reminder</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  required
                  value={newReminder.title}
                  onChange={(e) => setNewReminder({ ...newReminder, title: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Take morning medication"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={newReminder.description}
                  onChange={(e) => setNewReminder({ ...newReminder, description: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={2}
                  placeholder="Additional details..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Type *</label>
                <select
                  value={newReminder.reminder_type}
                  onChange={(e) =>
                    setNewReminder({
                      ...newReminder,
                      reminder_type: e.target.value as any,
                    })
                  }
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="medication">Medication</option>
                  <option value="appointment">Appointment</option>
                  <option value="routine">Routine</option>
                  <option value="custom">Custom</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Frequency *
                </label>
                <select
                  value={newReminder.frequency}
                  onChange={(e) =>
                    setNewReminder({
                      ...newReminder,
                      frequency: e.target.value as any,
                    })
                  }
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="once">Once</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Scheduled Time *
                </label>
                <input
                  type="datetime-local"
                  required
                  value={newReminder.scheduled_time}
                  onChange={(e) =>
                    setNewReminder({ ...newReminder, scheduled_time: e.target.value })
                  }
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-4">
              <motion.button
                type="button"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all border border-white/10"
              >
                Cancel
              </motion.button>
              <motion.button
                type="submit"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all shadow-lg"
              >
                Create Reminder
              </motion.button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>

      {/* Reminders list */}
      <div className="space-y-4">
        <AnimatePresence>
          {reminders.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-gray-800 rounded-lg"
            >
              <EmptyState
                icon={EmptyStateIcons.NoReminders}
                title="No Reminders Found"
                description="Create reminders for medications, appointments, daily tasks, and important events. Stay organized and never miss what matters."
                action={{
                  label: 'Create Reminder',
                  onClick: () => setShowCreateForm(true),
                }}
              />
            </motion.div>
          ) : (
            reminders.map((reminder) => (
              <ReminderCard key={reminder.id} reminder={reminder} onUpdate={loadReminders} />
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ReminderList;
