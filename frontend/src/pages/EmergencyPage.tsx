import React, { useState, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import MedicalInfoCard from '../components/emergency/MedicalInfoCard';
import SafeReturnHome from '../components/emergency/SafeReturnHome';
import AlertSettings from '../components/emergency/AlertSettings';
import Scene from '../components/3d/Scene';
import Starfield from '../components/3d/Starfield';
import { AlertCircle, ArrowLeft, Shield, MapPin, Bell, CheckCircle } from 'lucide-react';

type TabType = 'medical-info' | 'navigation' | 'alerts';

const EmergencyPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('medical-info');

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
              className="p-3 bg-gradient-to-br from-red-600 to-orange-600 rounded-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400 }}
            >
              <AlertCircle className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold text-blue-50">
              Emergency Response
            </h1>
          </div>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Manage emergency contacts, medical information, and safety features
          </p>
        </motion.div>

        {/* Emergency Alert Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8 backdrop-blur-xl bg-red-600/10 border-2 border-red-500/50 rounded-2xl p-6"
        >
          <div className="flex items-start gap-4">
            <motion.div
              animate={{ 
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                repeatType: "reverse"
              }}
            >
              <Shield className="h-8 w-8 text-red-400 flex-shrink-0" />
            </motion.div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-red-300 mb-2">
                Emergency SOS Button Available
              </h3>
              <p className="text-red-200 text-sm mb-4">
                The red SOS button in the bottom-right corner is always available. Press
                it to immediately alert your emergency contacts with your location and
                medical information.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                <div className="flex items-center gap-2 backdrop-blur-sm bg-white/5 px-3 py-2 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                  <span className="text-red-200">GPS Location Sharing</span>
                </div>
                <div className="flex items-center gap-2 backdrop-blur-sm bg-white/5 px-3 py-2 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                  <span className="text-red-200">Medical Info Included</span>
                </div>
                <div className="flex items-center gap-2 backdrop-blur-sm bg-white/5 px-3 py-2 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                  <span className="text-red-200">Instant Notifications</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Tab Navigation with glass morphism */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8 flex justify-center overflow-x-auto px-2"
        >
          <div className="inline-flex gap-2 p-2 backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 min-w-min">
            {[
              { id: 'medical-info' as TabType, label: 'Medical Information', icon: Shield },
              { id: 'navigation' as TabType, label: 'Safe Return Home', icon: MapPin },
              { id: 'alerts' as TabType, label: 'Alert Settings', icon: Bell }
            ].map((tab) => (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-4 sm:px-6 py-3 rounded-xl font-medium transition-all text-sm sm:text-base whitespace-nowrap overflow-hidden flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'text-gray-900'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeEmergencyTab"
                    className="absolute inset-0 bg-gradient-to-r from-red-600 to-orange-600 rounded-xl"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <tab.icon className="w-4 h-4 relative z-10" />
                <span className="relative z-10">{tab.label}</span>
              </motion.button>
            ))}
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
            className="max-w-4xl mx-auto"
          >
            {activeTab === 'medical-info' && <MedicalInfoCard />}
            {activeTab === 'navigation' && <SafeReturnHome />}
            {activeTab === 'alerts' && <AlertSettings />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default EmergencyPage;
