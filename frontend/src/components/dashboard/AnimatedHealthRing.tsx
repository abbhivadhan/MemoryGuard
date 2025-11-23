import { useEffect } from 'react';
import { motion, useAnimation } from 'framer-motion';

interface AnimatedHealthRingProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  label?: string;
  delay?: number;
}

/**
 * Animated circular progress ring with physics-based animation
 * Shows health metrics in a visually appealing way
 */
export default function AnimatedHealthRing({
  percentage,
  size = 120,
  strokeWidth = 8,
  color = '#06b6d4',
  label,
  delay = 0
}: AnimatedHealthRingProps) {
  const controls = useAnimation();
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  useEffect(() => {
    // Animate the ring with spring physics
    controls.start({
      strokeDashoffset: offset,
      transition: {
        type: 'spring',
        stiffness: 50,
        damping: 20,
        delay
      }
    });
  }, [controls, offset, delay]);

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
          fill="none"
        />

        {/* Animated progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={controls}
          style={{
            filter: `drop-shadow(0 0 8px ${color})`
          }}
        />

        {/* Glow effect */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth / 2}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference, opacity: 0 }}
          animate={{
            strokeDashoffset: offset,
            opacity: [0, 0.5, 0],
            transition: {
              strokeDashoffset: {
                type: 'spring',
                stiffness: 50,
                damping: 20,
                delay
              },
              opacity: {
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }
            }
          }}
          style={{
            filter: `blur(4px)`
          }}
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.div
          className="text-2xl font-bold text-white"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{
            type: 'spring',
            stiffness: 200,
            damping: 15,
            delay: delay + 0.3
          }}
        >
          {percentage}%
        </motion.div>
        {label && (
          <motion.div
            className="text-xs text-gray-400 mt-1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: delay + 0.5 }}
          >
            {label}
          </motion.div>
        )}
      </div>

      {/* Pulse effect */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          background: `radial-gradient(circle, ${color}40 0%, transparent 70%)`
        }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.5, 0, 0.5]
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
          delay
        }}
      />
    </div>
  );
}
