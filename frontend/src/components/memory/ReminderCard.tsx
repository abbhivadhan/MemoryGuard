import React, { useState } from 'react';
import { Reminder, reminderService } from '../../services/memoryService';
import { motion } from 'framer-motion';

interface ReminderCardProps {
  reminder: Reminder;
  onUpdate: () => void;
}

const ReminderCard: React.FC<ReminderCardProps> = ({ reminder, onUpdate }) => {
  const [isCompleting, setIsCompleting] = useState(false);

  const handleComplete = async () => {
    try {
      setIsCompleting(true);
      await reminderService.completeReminder(reminder.id);
      onUpdate();
    } catch (error) {
      console.error('Failed to complete reminder:', error);
    } finally {
      setIsCompleting(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this reminder?')) {
      try {
        await reminderService.deleteReminder(reminder.id);
        onUpdate();
      } catch (error) {
        console.error('Failed to delete reminder:', error);
      }
    }
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

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'medication':
        return 'bg-blue-500';
      case 'appointment':
        return 'bg-purple-500';
      case 'routine':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'medication':
        return '💊';
      case 'appointment':
        return '📅';
      case 'routine':
        return '✓';
      default:
        return '🔔';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`bg-white rounded-lg shadow-md p-4 border-l-4 ${
        reminder.is_completed ? 'border-green-500 opacity-60' : 'border-blue-500'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{getTypeIcon(reminder.reminder_type)}</span>
            <span
              className={`px-2 py-1 rounded text-xs text-white ${getTypeColor(
                reminder.reminder_type
              )}`}
            >
              {reminder.reminder_type}
            </span>
            {reminder.frequency !== 'once' && (
              <span className="px-2 py-1 rounded text-xs bg-gray-200 text-gray-700">
                {reminder.frequency}
              </span>
            )}
          </div>

          <h3
            className={`text-lg font-semibold mb-1 ${
              reminder.is_completed ? 'line-through text-gray-500' : 'text-gray-800'
            }`}
          >
            {reminder.title}
          </h3>

          {reminder.description && (
            <p className="text-gray-600 text-sm mb-2">{reminder.description}</p>
          )}

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>⏰ {formatTime(reminder.scheduled_time)}</span>
            {reminder.is_completed && reminder.completed_at && (
              <span className="text-green-600">
                ✓ Completed {formatTime(reminder.completed_at)}
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2 ml-4">
          {!reminder.is_completed && (
            <button
              onClick={handleComplete}
              disabled={isCompleting}
              className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 transition-colors text-sm disabled:opacity-50"
            >
              {isCompleting ? 'Completing...' : 'Complete'}
            </button>
          )}
          <button
            onClick={handleDelete}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm"
          >
            Delete
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default ReminderCard;
