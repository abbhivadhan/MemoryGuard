import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ReminderList from '../components/memory/ReminderList';
import MedicationReminders from '../components/memory/MedicationReminders';
import MedicationManagement from '../components/memory/MedicationManagement';
import AdherenceTracker from '../components/memory/AdherenceTracker';
import SideEffectsLogger from '../components/memory/SideEffectsLogger';
import DrugInteractionChecker from '../components/memory/DrugInteractionChecker';
import CaregiverAlerts from '../components/memory/CaregiverAlerts';
import DailyRoutineTracker from '../components/memory/DailyRoutineTracker';
import FaceRecognition from '../components/memory/FaceRecognition';
import CaregiverConfig from '../components/memory/CaregiverConfig';

type Tab = 'reminders' | 'medications' | 'med-management' | 'adherence' | 'side-effects' | 'interactions' | 'alerts' | 'routines' | 'faces' | 'caregivers';

const MemoryAssistantPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('reminders');

  const tabs = [
    { id: 'reminders' as Tab, label: 'Reminders' },
    { id: 'medications' as Tab, label: 'Med Reminders' },
    { id: 'med-management' as Tab, label: 'Manage Meds' },
    { id: 'adherence' as Tab, label: 'Adherence' },
    { id: 'side-effects' as Tab, label: 'Side Effects' },
    { id: 'interactions' as Tab, label: 'Interactions' },
    { id: 'alerts' as Tab, label: 'Caregiver Alerts' },
    { id: 'routines' as Tab, label: 'Daily Routine' },
    { id: 'faces' as Tab, label: 'Face Recognition' },
    { id: 'caregivers' as Tab, label: 'Caregivers' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            Memory Assistant
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Your personal companion for daily tasks, reminders, and staying connected with loved
            ones
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8 overflow-x-auto">
          <div className="bg-white rounded-lg shadow-md p-2 inline-flex gap-2 flex-wrap justify-center">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg transition-all text-sm ${
                  activeTab === tab.id
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'reminders' && <ReminderList />}
          {activeTab === 'medications' && <MedicationReminders />}
          {activeTab === 'med-management' && <MedicationManagement />}
          {activeTab === 'adherence' && <AdherenceTracker />}
          {activeTab === 'side-effects' && <SideEffectsLogger />}
          {activeTab === 'interactions' && <DrugInteractionChecker />}
          {activeTab === 'alerts' && <CaregiverAlerts />}
          {activeTab === 'routines' && <DailyRoutineTracker />}
          {activeTab === 'faces' && <FaceRecognition />}
          {activeTab === 'caregivers' && <CaregiverConfig />}
        </motion.div>
      </div>
    </div>
  );
};

export default MemoryAssistantPage;
