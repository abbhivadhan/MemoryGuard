import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';

/**
 * Physics-based loading screen for dashboard
 * Shows animated brain icon with particle effects
 */
export default function DashboardLoader() {
  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
      {/* Animated background gradient */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-cyan-900/20 to-pink-900/20"
        animate={{
          opacity: [0.3, 0.6, 0.3]
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />

      {/* Particle effects */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400 rounded-full"
            initial={{
              x: '50%',
              y: '50%',
              opacity: 0
            }}
            animate={{
              x: `${Math.random() * 100}%`,
              y: `${Math.random() * 100}%`,
              opacity: [0, 1, 0]
            }}
            transition={{
              duration: 2 + Math.random() * 2,
              repeat: Infinity,
              delay: i * 0.1,
              ease: 'easeOut'
            }}
          />
        ))}
      </div>

      {/* Main loader content */}
      <div className="relative z-10 flex flex-col items-center gap-8">
        {/* Animated brain icon */}
        <motion.div
          className="relative"
          animate={{
            y: [0, -20, 0]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        >
          {/* Outer ring */}
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-cyan-400/30"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 0, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeOut'
            }}
            style={{
              width: 120,
              height: 120,
              left: '50%',
              top: '50%',
              x: '-50%',
              y: '-50%'
            }}
          />

          {/* Middle ring */}
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-purple-400/30"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 0, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeOut',
              delay: 0.3
            }}
            style={{
              width: 120,
              height: 120,
              left: '50%',
              top: '50%',
              x: '-50%',
              y: '-50%'
            }}
          />

          {/* Inner ring */}
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-pink-400/30"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 0, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeOut',
              delay: 0.6
            }}
            style={{
              width: 120,
              height: 120,
              left: '50%',
              top: '50%',
              x: '-50%',
              y: '-50%'
            }}
          />

          {/* Brain icon */}
          <motion.div
            className="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center"
            animate={{
              rotate: [0, 360]
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: 'linear'
            }}
          >
            <Brain className="w-12 h-12 text-white" />
          </motion.div>

          {/* Glow effect */}
          <motion.div
            className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 blur-xl"
            animate={{
              opacity: [0.3, 0.6, 0.3],
              scale: [0.8, 1.2, 0.8]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
            style={{
              width: 120,
              height: 120,
              left: '50%',
              top: '50%',
              x: '-50%',
              y: '-50%'
            }}
          />
        </motion.div>

        {/* Loading text */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <motion.h2
            className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-2"
            animate={{
              opacity: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          >
            Loading Dashboard
          </motion.h2>
          <p className="text-gray-400 text-sm">Preparing your cognitive health data...</p>
        </motion.div>

        {/* Loading dots */}
        <div className="flex gap-2">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-3 h-3 rounded-full bg-cyan-400"
              animate={{
                y: [0, -10, 0],
                opacity: [0.3, 1, 0.3]
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * 0.2,
                ease: 'easeInOut'
              }}
            />
          ))}
        </div>

        {/* Progress bar */}
        <div className="w-64 h-1 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
            initial={{ width: '0%' }}
            animate={{ width: '100%' }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          />
        </div>
      </div>
    </div>
  );
}
