import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Float, Sphere, MeshDistortMaterial } from '@react-three/drei';
import { motion } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import HealthMetrics from '../components/dashboard/HealthMetrics';
import RiskDashboard from '../components/dashboard/RiskDashboard';
import { 
  Brain, Activity, Heart, Pill, Users, AlertCircle, 
  Calendar, Dumbbell, BookOpen, Camera, LogOut, Menu, X 
} from 'lucide-react';

type TabType = 'overview' | 'risk' | 'health';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: () => void;
  gradient: string;
}

const FloatingOrb: React.FC<{ position: [number, number, number]; color: string }> = ({ position, color }) => {
  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <Sphere args={[0.5, 32, 32]} position={position}>
        <MeshDistortMaterial
          color={color}
          attach="material"
          distort={0.4}
          speed={2}
          roughness={0.2}
          metalness={0.8}
        />
      </Sphere>
    </Float>
  );
};

const Background3D: React.FC = () => {
  return (
    <div className="fixed inset-0 -z-10">
      <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#8b5cf6" />
        <FloatingOrb position={[-2, 2, -2]} color="#06b6d4" />
        <FloatingOrb position={[2, -1, -3]} color="#8b5cf6" />
        <FloatingOrb position={[0, 1, -4]} color="#ec4899" />
        <FloatingOrb position={[-3, -2, -2]} color="#3b82f6" />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
      </Canvas>
    </div>
  );
};

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, icon, onClick, gradient }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -5 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`relative overflow-hidden rounded-xl sm:rounded-2xl p-4 sm:p-5 md:p-6 cursor-pointer backdrop-blur-xl bg-white/10 border border-white/20 shadow-2xl group touch-target`}
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-20 transition-opacity duration-300`} />
      <div className="relative z-10">
        <div className="mb-3 sm:mb-4 text-cyan-400 group-hover:text-cyan-300 transition-colors">
          <div className="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10">
            {icon}
          </div>
        </div>
        <h3 className="text-lg sm:text-xl font-bold mb-1.5 sm:mb-2 text-white">{title}</h3>
        <p className="text-gray-300 text-xs sm:text-sm leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
};

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
      title: 'Risk Assessment',
      description: 'ML-powered early detection and progression forecasting with SHAP explanations',
      icon: <Brain className="w-10 h-10" />,
      onClick: () => setActiveTab('risk'),
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      title: 'Memory Assistant',
      description: 'Daily reminders, routines, face recognition, and memory aids',
      icon: <Calendar className="w-10 h-10" />,
      onClick: () => navigate('/memory-assistant'),
      gradient: 'from-cyan-500 to-blue-500'
    },
    {
      title: 'Cognitive Assessment',
      description: 'Take MMSE, MoCA, and other standardized cognitive tests',
      icon: <Activity className="w-10 h-10" />,
      onClick: () => navigate('/assessment'),
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      title: 'Cognitive Training',
      description: 'Brain games and exercises with ML-powered difficulty adaptation',
      icon: <Dumbbell className="w-10 h-10" />,
      onClick: () => navigate('/training'),
      gradient: 'from-orange-500 to-red-500'
    },
    {
      title: 'Medical Imaging',
      description: 'Upload and analyze brain MRI scans with 3D visualization',
      icon: <Camera className="w-10 h-10" />,
      onClick: () => navigate('/imaging'),
      gradient: 'from-indigo-500 to-purple-500'
    },
    {
      title: 'Health Metrics',
      description: 'Track biomarkers, vitals, and health data over time',
      icon: <Heart className="w-10 h-10" />,
      onClick: () => setActiveTab('health'),
      gradient: 'from-red-500 to-pink-500'
    },
    {
      title: 'Medications',
      description: 'Track adherence, side effects, and drug interactions',
      icon: <Pill className="w-10 h-10" />,
      onClick: () => navigate('/memory-assistant'),
      gradient: 'from-teal-500 to-cyan-500'
    },
    {
      title: 'Recommendations',
      description: 'Personalized lifestyle and intervention recommendations',
      icon: <BookOpen className="w-10 h-10" />,
      onClick: () => navigate('/recommendations'),
      gradient: 'from-yellow-500 to-orange-500'
    },
    {
      title: 'Community',
      description: 'Connect with others, share experiences, and access resources',
      icon: <Users className="w-10 h-10" />,
      onClick: () => navigate('/community'),
      gradient: 'from-blue-500 to-indigo-500'
    },
    {
      title: 'Caregiver Portal',
      description: 'Monitor patient activity and receive alerts',
      icon: <Users className="w-10 h-10" />,
      onClick: () => navigate('/caregiver'),
      gradient: 'from-violet-500 to-purple-500'
    },
    {
      title: 'Emergency System',
      description: 'Quick access to emergency contacts, SOS, and safe return home',
      icon: <AlertCircle className="w-10 h-10" />,
      onClick: () => navigate('/emergency'),
      gradient: 'from-red-600 to-orange-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white overflow-hidden">
      <Background3D />
      
      {/* Navigation */}
      <nav className="relative z-20 backdrop-blur-xl bg-black/30 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                MemoryGuard
              </h1>
            </motion.div>
            
            <div className="hidden md:flex items-center gap-6">
              <span className="text-gray-300">
                {user?.name || user?.email}
              </span>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-600/80 hover:bg-red-600 rounded-lg transition-colors backdrop-blur-sm"
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
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden backdrop-blur-xl bg-black/50 border-t border-white/10 p-4"
          >
            <div className="flex flex-col gap-4">
              <span className="text-gray-300">{user?.name || user?.email}</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-600/80 rounded-lg"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </motion.div>
        )}
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 md:py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 sm:mb-10 md:mb-12 text-center"
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent px-2">
            Welcome back, {user?.name?.split(' ')[0]}
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-gray-300 px-4">
            Your comprehensive cognitive health dashboard
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8 sm:mb-10 md:mb-12 flex justify-center overflow-x-auto px-2"
        >
          <div className="inline-flex gap-1 sm:gap-2 p-1.5 sm:p-2 backdrop-blur-xl bg-white/10 rounded-xl sm:rounded-2xl border border-white/20 min-w-min">
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
                className={`px-3 sm:px-4 md:px-6 py-2 sm:py-2.5 md:py-3 rounded-lg sm:rounded-xl font-medium transition-all text-sm sm:text-base whitespace-nowrap touch-target ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-white/10'
                }`}
              >
                <span className="hidden sm:inline">{tab.label}</span>
                <span className="sm:hidden">{tab.shortLabel}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 md:gap-6">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <FeatureCard {...feature} />
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'risk' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="backdrop-blur-xl bg-white/5 rounded-xl sm:rounded-2xl p-4 sm:p-5 md:p-6 border border-white/10"
          >
            <RiskDashboard userId={user?.id} />
          </motion.div>
        )}

        {activeTab === 'health' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="backdrop-blur-xl bg-white/5 rounded-xl sm:rounded-2xl p-4 sm:p-5 md:p-6 border border-white/10"
          >
            <HealthMetrics />
          </motion.div>
        )}
      </main>
    </div>
  );
};

export default DashboardPage;
