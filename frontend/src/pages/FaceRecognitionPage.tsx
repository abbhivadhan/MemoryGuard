import React, { Suspense } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Users, ArrowLeft } from 'lucide-react';
import FaceRecognition from '../components/memory/FaceRecognition';
import Scene from '../components/3d/Scene';
import Starfield from '../components/3d/Starfield';

const FaceRecognitionPage: React.FC = () => {
  const navigate = useNavigate();

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
              className="p-3 bg-gradient-to-br from-pink-500 to-rose-500 rounded-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400 }}
            >
              <Users className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold text-blue-50">
              Face Recognition
            </h1>
          </div>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Remember important people in your life with AI-powered face recognition
          </p>
        </motion.div>

        {/* Face Recognition Component */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <FaceRecognition />
        </motion.div>
      </div>
    </div>
  );
};

export default FaceRecognitionPage;
