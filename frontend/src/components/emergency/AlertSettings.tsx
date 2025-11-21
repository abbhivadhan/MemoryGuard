import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface AlertThresholds {
  medicationAdherence: number;
  routineMissed: number;
  cognitiveDecline: number;
  inactivityHours: number;
}

const AlertSettings: React.FC = () => {
  const [thresholds, setThresholds] = useState<AlertThresholds>({
    medicationAdherence: 80,
    routineMissed: 3,
    cognitiveDecline: 20,
    inactivityHours: 48,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // In a real implementation, this would save to the backend
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to save alert settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-white mb-4">Alert Thresholds</h3>
      <p className="text-gray-400 text-sm mb-6">
        Configure when you want to receive proactive alerts about concerning patterns.
      </p>

      <div className="space-y-6">
        {/* Medication Adherence */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Medication Adherence Threshold
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="50"
              max="100"
              step="5"
              value={thresholds.medicationAdherence}
              onChange={(e) =>
                setThresholds({
                  ...thresholds,
                  medicationAdherence: parseInt(e.target.value),
                })
              }
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-white font-semibold w-16 text-right">
              {thresholds.medicationAdherence}%
            </span>
          </div>
          <p className="text-gray-500 text-xs mt-1">
            Alert when adherence falls below this percentage over 7 days
          </p>
        </div>

        {/* Routine Missed */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Missed Routine Items
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={thresholds.routineMissed}
              onChange={(e) =>
                setThresholds({
                  ...thresholds,
                  routineMissed: parseInt(e.target.value),
                })
              }
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-white font-semibold w-16 text-right">
              {thresholds.routineMissed}
            </span>
          </div>
          <p className="text-gray-500 text-xs mt-1">
            Alert when this many routine items are missed in 7 days
          </p>
        </div>

        {/* Cognitive Decline */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Cognitive Score Decline
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="10"
              max="50"
              step="5"
              value={thresholds.cognitiveDecline}
              onChange={(e) =>
                setThresholds({
                  ...thresholds,
                  cognitiveDecline: parseInt(e.target.value),
                })
              }
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-white font-semibold w-16 text-right">
              {thresholds.cognitiveDecline}%
            </span>
          </div>
          <p className="text-gray-500 text-xs mt-1">
            Alert when test scores decline by this percentage
          </p>
        </div>

        {/* Inactivity */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Inactivity Period
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="12"
              max="96"
              step="12"
              value={thresholds.inactivityHours}
              onChange={(e) =>
                setThresholds({
                  ...thresholds,
                  inactivityHours: parseInt(e.target.value),
                })
              }
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-white font-semibold w-16 text-right">
              {thresholds.inactivityHours}h
            </span>
          </div>
          <p className="text-gray-500 text-xs mt-1">
            Alert when no app activity detected for this many hours
          </p>
        </div>
      </div>

      {/* Save Button */}
      <div className="mt-8 flex items-center gap-4">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </button>

        {saveSuccess && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 text-green-400"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span className="text-sm font-medium">Settings saved!</span>
          </motion.div>
        )}
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <h4 className="text-blue-300 font-semibold text-sm mb-1">
              Proactive Monitoring
            </h4>
            <p className="text-blue-200 text-xs">
              The system automatically monitors these patterns and sends alerts to your
              emergency contacts and caregivers when thresholds are exceeded. This helps
              ensure early intervention when concerning patterns are detected.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertSettings;
