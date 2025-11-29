import React, { useState, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import HealthMetrics from '../components/dashboard/HealthMetrics';
import RiskDashboard from '../components/dashboard/RiskDashboard';
import MedicalDisclaimer from '../components/ui/MedicalDisclaimer';
import ErrorBoundary from '../components/ui/ErrorBoundary';
import Scene from '../components/3d/Scene';
import BrainModel from '../components/3d/BrainModel';
import Starfield from '../components/3d/Starfield';
import PhysicsCard from '../components/dashboard/PhysicsCard.tsx';
import MetricOrb from '../components/dashboard/MetricOrb';
import { useDashboardStats } from '../hooks/useDashboardStats';
import { 
  Brain, Activity, Heart, Pill, Users, AlertCircle, 
  Calendar, Dumbbell, BookOpen, Camera, LogOut, Menu, X,
  Shield, Zap, Target
} from 'lucide-react';

type TabType = 'overview' | 'risk' | 'health';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout, isNewUser } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Fetch real dashboard stats
  const { data: stats, isLoading: statsLoading } = useDashboardStats(user?.id);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const features = [
    {
      id: 'risk',
      title: 'Risk Assessment',
      description: 'ML-powered early detection and progression forecasting',
      icon: <Brain className="w-full h-full" />,
      onClick: () => setActiveTab('risk'),
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      id: 'assessment',
      title: 'Cognitive Assessment',
      description: 'Standardized cognitive tests and tracking',
      icon: <Activity className="w-full h-full" />,
      onClick: () => navigate('/assessment'),
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      id: 'training',
      title: 'Cognitive Training',
      description: 'Brain games with adaptive difficulty',
      icon: <Dumbbell className="w-full h-full" />,
      onClick: () => navigate('/training'),
      gradient: 'from-orange-500 to-red-500'
    },
    {
      id: 'imaging',
      title: 'Medical Imaging',
      description: 'Brain scan analysis and 3D visualization',
      icon: <Camera className="w-full h-full" />,
      onClick: () => navigate('/imaging'),
      gradient: 'from-indigo-500 to-purple-500'
    },
    {
      id: 'health',
      title: 'Health Metrics',
      description: 'Track biomarkers and vitals over time',
      icon: <Heart className="w-full h-full" />,
      onClick: () => setActiveTab('health'),
      gradient: 'from-red-500 to-pink-500'
    },
    {
      id: 'memory-assistant',
      title: 'Memory Assistant',
      description: 'Reminders, routines, and caregiver support',
      icon: <Calendar className="w-full h-full" />,
      onClick: () => navigate('/memory-assistant'),
      gradient: 'from-blue-500 to-indigo-500'
    },
    {
      id: 'medications',
      title: 'Medications',
      description: 'Track adherence and interactions',
      icon: <Pill className="w-full h-full" />,
      onClick: () => navigate('/medications'),
      gradient: 'from-teal-500 to-cyan-500'
    },
    {
      id: 'face-recognition',
      title: 'Face Recognition',
      description: 'Remember important people in your life',
      icon: <Users className="w-full h-full" />,
      onClick: () => navigate('/face-recognition'),
      gradient: 'from-pink-500 to-rose-500'
    },
    {
      id: 'recommendations',
      title: 'Recommendations',
      description: 'Personalized lifestyle interventions',
      icon: <BookOpen className="w-full h-full" />,
      onClick: () => navigate('/recommendations'),
      gradient: 'from-yellow-500 to-orange-500'
    },
    {
      id: 'community',
      title: 'Community',
      description: 'Connect and share experiences',
      icon: <Users className="w-full h-full" />,
      onClick: () => navigate('/community'),
      gradient: 'from-blue-500 to-indigo-500'
    },
    {
      id: 'caregivers',
      title: 'Caregiver Management',
      description: 'Configure caregiver access and alerts',
      icon: <Users className="w-full h-full" />,
      onClick: () => navigate('/caregivers'),
      gradient: 'from-violet-500 to-purple-500'
    },
    {
      id: 'caregiver',
      title: 'Caregiver Portal',
      description: 'Monitor patient activity and receive alerts',
      icon: <Users className="w-full h-full" />,
      onClick: () => navigate('/caregiver'),
      gradient: 'from-purple-500 to-indigo-500'
    },
    {
      id: 'emergency',
      title: 'Emergency System',
      description: 'Quick access to emergency contacts',
      icon: <AlertCircle className="w-full h-full" />,
      onClick: () => navigate('/emergency'),
      gradient: 'from-red-600 to-orange-600'
    }
  ];

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* 3D Background Scene - Brain model with starfield */}
      <div className="fixed inset-0 z-0">
        <Scene camera={{ position: [0, 0, 8], fov: 75 }} enablePhysics={false}>
          <Suspense fallback={null}>
            <Starfield count={200} />
            <group scale={2.5}>
              <BrainModel position={[0, 0, -5]} deterioration={0} />
            </group>
          </Suspense>
        </Scene>
      </div>
      
      {/* Navigation */}
      <nav className="relative z-20 backdrop-blur-xl bg-black/30 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <h1 className="text-2xl font-bold text-blue-50">
                MemoryGuard
              </h1>
            </motion.div>
            
            <div className="hidden md:flex items-center gap-6">
              <span className="text-gray-300 text-sm">
                {user?.name || user?.email}
              </span>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 rounded-lg transition-all backdrop-blur-sm"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </motion.button>
            </div>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden backdrop-blur-xl bg-black/50 border-t border-white/10 overflow-hidden"
            >
              <div className="p-4 flex flex-col gap-4">
                <span className="text-gray-300 text-sm">{user?.name || user?.email}</span>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600/20 border border-red-500/30 rounded-lg"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 md:py-12">
        {/* Header with animated gradient */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 sm:mb-10 md:mb-12"
        >
          <div className="text-center mb-6">
            <motion.h2 
              className="text-4xl sm:text-5xl md:text-6xl font-bold mb-3 sm:mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <span className="text-blue-50">
                {isNewUser 
                  ? `Welcome, ${user?.name?.split(' ')[0]}` 
                  : `Welcome back, ${user?.name?.split(' ')[0]}`}
              </span>
            </motion.h2>
            <motion.p 
              className="text-base sm:text-lg md:text-xl text-gray-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              Your cognitive health dashboard
            </motion.p>
          </div>

          {/* Quick Stats with real data */}
          {!statsLoading && stats && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <MetricOrb
                  label="Cognitive Score"
                  value={stats.cognitiveScore ? `${Math.round(stats.cognitiveScore)}%` : 'N/A'}
                  trend={stats.cognitiveScore ? 'neutral' : undefined}
                  icon={<Brain className="w-5 h-5" />}
                  color="from-purple-500 to-pink-500"
                  index={0}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
              >
                <MetricOrb
                  label="Risk Level"
                  value={stats.riskLevel || 'Unknown'}
                  trend="neutral"
                  icon={<Shield className="w-5 h-5" />}
                  color="from-green-500 to-emerald-500"
                  index={1}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <MetricOrb
                  label="Active Days"
                  value={stats.activeDays.toString()}
                  trend={stats.activeDays > 0 ? 'up' : 'neutral'}
                  icon={<Zap className="w-5 h-5" />}
                  color="from-cyan-500 to-blue-500"
                  index={2}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
              >
                <MetricOrb
                  label="Goals Met"
                  value={`${stats.goalsCompleted}/${stats.goalsTotal}`}
                  trend={stats.goalsCompleted > 0 ? 'up' : 'neutral'}
                  icon={<Target className="w-5 h-5" />}
                  color="from-orange-500 to-red-500"
                  index={3}
                />
              </motion.div>
            </div>
          )}
        </motion.div>

        {/* Medical Disclaimer */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <MedicalDisclaimer type="general" compact />
        </motion.div>

        {/* Tab Navigation with glass morphism */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mb-8 sm:mb-10 md:mb-12 flex justify-center overflow-x-auto px-2"
        >
          <div className="inline-flex gap-2 p-2 backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 min-w-min">
            {[
              { id: 'overview' as TabType, label: 'Overview', shortLabel: 'Overview' },
              { id: 'risk' as TabType, label: 'Risk Assessment', shortLabel: 'Risk' },
              { id: 'health' as TabType, label: 'Health Metrics', shortLabel: 'Health' }
            ].map((tab) => (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-4 sm:px-6 md:px-8 py-3 rounded-xl font-medium transition-all text-sm sm:text-base whitespace-nowrap overflow-hidden ${
                  activeTab === tab.id
                    ? 'text-gray-900'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-blue-50 rounded-xl"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <span className="relative z-10 hidden sm:inline">{tab.label}</span>
                <span className="relative z-10 sm:hidden">{tab.shortLabel}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Tab Content with AnimatePresence */}
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 md:gap-6">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.05 * index }}
                  >
                    <PhysicsCard {...feature} />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'risk' && (
            <motion.div
              key="risk"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
              className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10"
            >
              <RiskDashboard userId={user?.id} />
            </motion.div>
          )}

          {activeTab === 'health' && (
            <motion.div
              key="health"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
              className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10"
            >
              <ErrorBoundary>
                <HealthMetrics />
              </ErrorBoundary>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default DashboardPage;
