import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ReminderList from '../memory/ReminderList';
import MedicationReminders from '../memory/MedicationReminders';
import MedicationManagement from '../memory/MedicationManagement';
import AdherenceTracker from '../memory/AdherenceTracker';
import SideEffectsLogger from '../memory/SideEffectsLogger';
import DrugInteractionChecker from '../memory/DrugInteractionChecker';
import CaregiverAlerts from '../memory/CaregiverAlerts';
import DailyRoutineTracker from '../memory/DailyRoutineTracker';
import FaceRecognition from '../memory/FaceRecognition';
import CaregiverConfig from '../memory/CaregiverConfig';

type Tab = 'reminders' | 'medications' | 'med-management' | 'adherence' | 'side-effects' | 'interactions' | 'alerts' | 'routines' | 'faces' | 'caregivers';

const MemoryAssistant: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('reminders');

  const tabs = [
    { id: 'reminders' as Tab, label: 'Reminders'},
    { id: 'medications' as Tab, label: 'Med Reminders'},
    { id: 'med-management' as Tab, label: 'Manage Meds'},
    { id: 'adherence' as Tab, label: 'Adherence'},
    { id: 'side-effects' as Tab, label: 'Side Effects'},
    { id: 'interactions' as Tab, label: 'Interactions'},
    { id: 'alerts' as Tab, label: 'Caregiver Alerts'},
    { id: 'routines' as Tab, label: 'Daily Routine'},
    { id: 'faces' as Tab, label: 'Face Recognition'},
    { id: 'caregivers' as Tab, label: 'Caregivers'},
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-6"
      >
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">
          Memory Assistant
        </h2>
        <p className="text-gray-300 text-sm md:text-base">
          Your personal companion for daily tasks, reminders, and staying connected
        </p>
      </motion.div>

      {/* Tab Navigation */}
      <div className="flex justify-center mb-6 overflow-x-auto">
        <div className="backdrop-blur-xl bg-white/10 rounded-xl p-2 inline-flex gap-2 flex-wrap justify-center border border-white/20">
          {tabs.map((tab) => (
            <motion.button
              key={tab.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 sm:px-4 py-2 rounded-lg transition-all text-sm whitespace-nowrap flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg'
                  : 'text-gray-300 hover:text-white hover:bg-white/10'
              }`}
            >
              <span className="font-medium">{tab.label}</span>
            </motion.button>
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
        className="backdrop-blur-xl bg-white/5 rounded-xl p-4 sm:p-6 border border-white/10"
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
  );
};

export default MemoryAssistant;



