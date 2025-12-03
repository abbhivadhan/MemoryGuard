/**
 * Caregiver Page - Main page for caregiver features
 * 
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
 */
import React, { useState, Suspense } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import CaregiverDashboard from '../components/caregiver/CaregiverDashboard';
import ActivityMonitor from '../components/caregiver/ActivityMonitor';
import AlertSystem from '../components/caregiver/AlertSystem';
import ActivityLogViewer from '../components/caregiver/ActivityLogViewer';
import MedicationLogEditor from '../components/caregiver/MedicationLogEditor';
import AssessmentManager from '../components/caregiver/AssessmentManager';
import Scene from '../components/3d/Scene';
import Starfield from '../components/3d/Starfield';
import { ArrowLeft, Users, Activity, Bell, FileText, Pill } from 'lucide-react';

type TabType = 'dashboard' | 'activity' | 'alerts' | 'assessments' | 'log' | 'medications';

const CaregiverPage: React.FC = () => {
  const { patientId } = useParams<{ patientId?: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>(patientId ? 'activity' : 'dashboard');
  const [patientName] = useState('Patient');

  const tabs = [
    { id: 'dashboard' as TabType, label: 'Dashboard', icon: Users },
    { id: 'activity' as TabType, label: 'Activity Monitor', icon: Activity, requiresPatient: true },
    { id: 'alerts' as TabType, label: 'Alerts', icon: Bell },
    { id: 'assessments' as TabType, label: 'Assessments', icon: FileText, requiresPatient: true },
    { id: 'medications' as TabType, label: 'Medication Logs', icon: Pill },
    { id: 'log' as TabType, label: 'Activity Log', icon: FileText, requiresPatient: true },
  ];

  const renderContent = () => {
    if (activeTab === 'dashboard') {
      return <CaregiverDashboard />;
    }

    if (!patientId && (activeTab === 'activity' || activeTab === 'log' || activeTab === 'assessments')) {
      return (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="backdrop-blur-xl bg-white/5 rounded-2xl p-12 text-center border border-white/10"
        >
          <div className="text-gray-300 text-lg mb-4">
            Please select a patient from the dashboard to view their activity
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab('dashboard')}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg"
          >
            Go to Dashboard
          </motion.button>
        </motion.div>
      );
    }

    switch (activeTab) {
      case 'activity':
        return patientId ? <ActivityMonitor patientId={patientId} /> : null;
      case 'alerts':
        return <AlertSystem />;
      case 'assessments':
        return patientId ? <AssessmentManager patientId={patientId} /> : null;
      case 'medications':
        return <MedicationLogEditor patientId={patientId} />;
      case 'log':
        return patientId ? (
          <ActivityLogViewer patientId={patientId} patientName={patientName} />
        ) : null;
      default:
        return <CaregiverDashboard />;
    }
  };

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
              className="p-3 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400 }}
            >
              <Users className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold text-blue-50">
              Caregiver Portal
            </h1>
          </div>
          {patientId && (
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-lg text-gray-400"
            >
              Monitoring: {patientName}
            </motion.p>
          )}
          {!patientId && (
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-lg text-gray-400 max-w-2xl mx-auto"
            >
              Monitor patient activity, receive alerts, and manage care
            </motion.p>
          )}
        </motion.div>

        {/* Tab Navigation with glass morphism */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8 flex justify-center overflow-x-auto px-2"
        >
          <div className="inline-flex gap-2 p-2 backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 min-w-min">
            {tabs.map((tab) => {
              const isDisabled = tab.requiresPatient && !patientId;
              const Icon = tab.icon;
              
              return (
                <motion.button
                  key={tab.id}
                  whileHover={!isDisabled ? { scale: 1.05 } : {}}
                  whileTap={!isDisabled ? { scale: 0.95 } : {}}
                  onClick={() => !isDisabled && setActiveTab(tab.id)}
                  disabled={isDisabled}
                  className={`relative px-4 sm:px-6 py-3 rounded-xl font-medium transition-all text-sm sm:text-base whitespace-nowrap overflow-hidden flex items-center gap-2 ${
                    activeTab === tab.id
                      ? 'text-gray-900'
                      : isDisabled
                      ? 'text-gray-600 cursor-not-allowed'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {activeTab === tab.id && (
                    <motion.div
                      layoutId="activeCaregiverTab"
                      className="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                  <Icon className="w-4 h-4 relative z-10" />
                  <span className="relative z-10">{tab.label}</span>
                </motion.button>
              );
            })}
          </div>
        </motion.div>

        {/* Tab Content with AnimatePresence */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default CaregiverPage;
