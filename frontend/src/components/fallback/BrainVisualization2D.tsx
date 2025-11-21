/**
 * 2D Brain Visualization Fallback
 * Provides 2D visualization when WebGL is not supported
 * Requirements: 10.4, 7.6
 */

import React from 'react';
import { motion } from 'framer-motion';

interface BrainVisualization2DProps {
  deterioration?: number;
  className?: string;
}

const BrainVisualization2D: React.FC<BrainVisualization2DProps> = ({
  deterioration = 0,
  className = '',
}) => {
  const healthPercentage = Math.round((1 - deterioration) * 100);
  
  return (
    <div className={`relative w-full h-64 flex items-center justify-center ${className}`}>
      {/* Brain outline */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="relative w-48 h-48"
      >
        {/* Main brain circle */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-purple-500/30 to-cyan-500/30 border-2 border-purple-400/50" />
        
        {/* Health indicator */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: 'spring' }}
              className="text-4xl font-bold text-white mb-2"
            >
              {healthPercentage}%
            </motion.div>
            <div className="text-sm text-gray-300">Brain Health</div>
          </div>
        </div>
        
        {/* Animated particles */}
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 rounded-full bg-cyan-400"
            style={{
              left: `${50 + 40 * Math.cos((i * Math.PI * 2) / 8)}%`,
              top: `${50 + 40 * Math.sin((i * Math.PI * 2) / 8)}%`,
            }}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.2,
            }}
          />
        ))}
      </motion.div>
    </div>
  );
};

export default BrainVisualization2D;
