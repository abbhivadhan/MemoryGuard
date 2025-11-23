import React, { useState, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Pill, ArrowLeft, Activity, AlertTriangle, Shield, Bell } from 'lucide-react';
import MedicationManagement from '../components/memory/MedicationManagement';
import MedicationReminders from '../components/memory/MedicationReminders';
import AdherenceTracker from '../components/memory/AdherenceTracker';
import SideEffectsLogger from '../components/memory/SideEffectsLogger';
import DrugInteractionChecker from '../components/memory/DrugInteractionChecker';
import Scene from '../components/3d/Scene';
import Starfield from '../components/3d/Starfield';

type Tab = 'manage' | 'reminders' | 'adherence' | 'side-effects' | 'interactions';

const MedicationsPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<Tab>('manage');

  const tabs = [
    { id: 'manage' as Tab, label: 'Manage Meds', icon: <Pill className="w-4 h-4" /> },
    { id: 'reminders' as Tab, label: 'Reminders', icon: <Bell className="w-4 h-4" /> },
    { id: 'adherence' as Tab, label: 'Adherence', icon: <Activity className="w-4 h-4" /> },
    { id: 'side-effects' as Tab, label: 'Side Effects', icon: <AlertTriangle className="w-4 h-4" /> },
    { id: 'interactions' as Tab, label: 'Interactions', icon: <Shield className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* 3D Background Scene */}
      <div className="fixed inset-0 z-0">
        <Scene camera={{ position: [0, 0, 8], fov: 75 }} enablePhysics={false}>
          <Suspense fallback={null}>
            <Starfield count={200} />
          </Suspense>
        </Scene>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Back Button */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => navigate('/dashboard')}
          className="mb-6 flex items-center gap-2 text-gray-300 hover:text-white transition-colors backdrop-blur-sm bg-white/5 px-4 py-2 rounded-lg border border-white/10"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Dashboard</span>
        </motion.button>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <motion.div 
              className="p-3 bg-gradient-to-br from-teal-500 to-cyan-500 rounded-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400 }}
            >
              <Pill className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold text-blue-50">
              Medication Management
            </h1>
          </div>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Track your medications, set reminders, monitor adherence, and check for interactions
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center mb-8 overflow-x-auto"
        >
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-2 inline-flex gap-2 flex-wrap justify-center">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-4 py-3 rounded-xl transition-all text-sm flex items-center gap-2 relative overflow-hidden ${
                  activeTab === tab.id
                    ? 'text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTabMeds"
                    className="absolute inset-0 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-xl"
                    transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <span className="relative z-10">{tab.icon}</span>
                <span className="relative z-10 font-medium">{tab.label}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6"
          >
            {activeTab === 'manage' && <MedicationManagement />}
            {activeTab === 'reminders' && <MedicationReminders />}
            {activeTab === 'adherence' && <AdherenceTracker />}
            {activeTab === 'side-effects' && <SideEffectsLogger />}
            {activeTab === 'interactions' && <DrugInteractionChecker />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default MedicationsPage;
