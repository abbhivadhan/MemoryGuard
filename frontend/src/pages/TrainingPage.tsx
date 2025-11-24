import React, { useState, Suspense } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Dumbbell } from 'lucide-react';
import { Exercise } from '../services/exerciseService';
import ExerciseLibrary from '../components/cognitive/ExerciseLibrary';
import ExerciseProgress from '../components/cognitive/ExerciseProgress';
import ExercisePlayer from '../components/cognitive/ExercisePlayer';
import ExerciseMLInsights from '../components/cognitive/ExerciseMLInsights';
import Scene from '../components/3d/Scene';
import Starfield from '../components/3d/Starfield';

const TrainingPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [activeTab, setActiveTab] = useState<'library' | 'progress' | 'insights'>('library');

  const handleSelectExercise = (exercise: Exercise) => {
    setSelectedExercise(exercise);
  };

  const handleExerciseComplete = () => {
    setSelectedExercise(null);
    setActiveTab('progress');
    // Force a re-render by updating a key
    window.dispatchEvent(new Event('exerciseCompleted'));
  };

  const handleExitExercise = () => {
    setSelectedExercise(null);
  };

  if (selectedExercise) {
    return (
      <ExercisePlayer
        exercise={selectedExercise}
        onComplete={handleExerciseComplete}
        onExit={handleExitExercise}
      />
    );
  }

  const tabs = [
    { id: 'library' as const, label: 'Exercise Library' },
    { id: 'progress' as const, label: 'My Progress' },
    { id: 'insights' as const, label: 'ML Insights' },
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
              className="p-3 bg-gradient-to-br from-purple-500 to-violet-500 rounded-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400 }}
            >
              <Dumbbell className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold text-blue-50">
              Cognitive Training
            </h1>
          </div>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Engage in exercises designed to maintain and improve cognitive function
          </p>
        </motion.div>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center mb-8"
        >
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-2 inline-flex gap-2">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-6 py-3 rounded-xl transition-all text-sm font-medium relative overflow-hidden ${
                  activeTab === tab.id ? 'text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTrainingTab"
                    className="absolute inset-0 bg-gradient-to-r from-purple-500 to-violet-500 rounded-xl"
                    transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <span className="relative z-10">{tab.label}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {activeTab === 'library' && (
            <ExerciseLibrary onSelectExercise={handleSelectExercise} />
          )}
          {activeTab === 'progress' && <ExerciseProgress />}
          {activeTab === 'insights' && <ExerciseMLInsights />}
        </motion.div>
      </div>
    </div>
  );
};

export default TrainingPage;
