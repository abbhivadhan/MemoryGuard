import { useRef, useEffect } from 'react';
import { motion, useAnimation } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricOrbProps {
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ReactNode;
  color: string;
  index: number;
}

/**
 * Animated metric orb with physics-based floating animation
 * Shows key health metrics with trend indicators
 */
export default function MetricOrb({
  label,
  value,
  trend = 'neutral',
  icon,
  color,
  index
}: MetricOrbProps) {
  const controls = useAnimation();
  const orbRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Continuous floating animation
    controls.start({
      y: [0, -10, 0],
      transition: {
        duration: 3 + index * 0.5,
        repeat: Infinity,
        ease: 'easeInOut',
        delay: index * 0.2
      }
    });
  }, [controls, index]);

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-400" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'from-green-500/20 to-emerald-500/20';
      case 'down':
        return 'from-red-500/20 to-orange-500/20';
      default:
        return 'from-gray-500/20 to-gray-600/20';
    }
  };

  return (
    <motion.div
      ref={orbRef}
      animate={controls}
      whileHover={{ scale: 1.05, y: -15 }}
      whileTap={{ scale: 0.95 }}
      className="relative group cursor-pointer"
    >
      {/* Main card */}
      <div className="relative overflow-hidden rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 p-4 sm:p-5">
        {/* Gradient background */}
        <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-10 group-hover:opacity-20 transition-opacity duration-300`} />

        {/* Trend indicator background */}
        <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${getTrendColor()} rounded-bl-full opacity-50`} />

        {/* Content */}
        <div className="relative z-10">
          {/* Icon and trend */}
          <div className="flex items-start justify-between mb-3">
            <motion.div
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center text-white"
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.6 }}
            >
              {icon}
            </motion.div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 + index * 0.1, type: 'spring', stiffness: 500 }}
            >
              {getTrendIcon()}
            </motion.div>
          </div>

          {/* Value */}
          <motion.div
            className="text-2xl sm:text-3xl font-bold text-white mb-1"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
          >
            {value}
          </motion.div>

          {/* Label */}
          <motion.div
            className="text-xs sm:text-sm text-gray-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 + index * 0.1 }}
          >
            {label}
          </motion.div>
        </div>

        {/* Animated particles */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              className={`absolute w-1 h-1 rounded-full bg-gradient-to-r ${color}`}
              initial={{
                x: Math.random() * 100 + '%',
                y: '100%',
                opacity: 0
              }}
              animate={{
                y: '-20%',
                opacity: [0, 1, 0]
              }}
              transition={{
                duration: 2 + Math.random() * 2,
                repeat: Infinity,
                delay: i * 0.5 + index * 0.2,
                ease: 'easeOut'
              }}
            />
          ))}
        </div>

        {/* Pulse ring on hover */}
        <motion.div
          className={`absolute inset-0 rounded-2xl border-2 bg-gradient-to-br ${color}`}
          initial={{ opacity: 0, scale: 1 }}
          whileHover={{
            opacity: [0, 0.5, 0],
            scale: [1, 1.1, 1.2],
            transition: { duration: 1, repeat: Infinity }
          }}
        />
      </div>

      {/* Glow effect */}
      <motion.div
        className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${color} blur-xl -z-10`}
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 0.3 }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  );
}
