import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import AnimatedHealthRing from './AnimatedHealthRing';
import DataWave from './DataWave';

interface Stat {
  label: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  percentage?: number;
}

interface StatsPanelProps {
  stats: Stat[];
  title?: string;
}

/**
 * Enhanced stats panel with physics-based animations
 * Displays multiple health metrics with visual indicators
 */
export default function StatsPanel({ stats, title }: StatsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 p-6"
    >
      {/* Background wave effect */}
      <div className="absolute inset-0 opacity-30">
        <DataWave color="#06b6d4" amplitude={20} frequency={0.015} speed={0.03} />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {title && (
          <motion.h3
            className="text-xl font-bold text-white mb-6 flex items-center gap-2"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Activity className="w-5 h-5 text-cyan-400" />
            {title}
          </motion.h3>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <StatCard key={index} stat={stat} index={index} />
          ))}
        </div>
      </div>
    </motion.div>
  );
}

interface StatCardProps {
  stat: Stat;
  index: number;
}

function StatCard({ stat, index }: StatCardProps) {
  const getTrendIcon = () => {
    if (stat.trend === 'up') {
      return <TrendingUp className="w-4 h-4 text-green-400" />;
    } else if (stat.trend === 'down') {
      return <TrendingDown className="w-4 h-4 text-red-400" />;
    }
    return null;
  };

  const getTrendColor = () => {
    if (stat.trend === 'up') return 'text-green-400';
    if (stat.trend === 'down') return 'text-red-400';
    return 'text-gray-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        delay: index * 0.1,
        type: 'spring',
        stiffness: 200,
        damping: 20
      }}
      whileHover={{ scale: 1.05, y: -5 }}
      className="relative group"
    >
      <div className="relative overflow-hidden rounded-xl bg-white/5 border border-white/10 p-4 backdrop-blur-sm">
        {/* Hover gradient */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        />

        {/* Content */}
        <div className="relative z-10">
          {/* Label */}
          <div className="text-sm text-gray-400 mb-2">{stat.label}</div>

          {/* Value and trend */}
          <div className="flex items-end justify-between mb-3">
            <motion.div
              className="text-3xl font-bold text-white"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 + 0.2 }}
            >
              {stat.value}
            </motion.div>

            {stat.change !== undefined && (
              <motion.div
                className={`flex items-center gap-1 text-sm ${getTrendColor()}`}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{
                  delay: index * 0.1 + 0.3,
                  type: 'spring',
                  stiffness: 400
                }}
              >
                {getTrendIcon()}
                <span>{Math.abs(stat.change)}%</span>
              </motion.div>
            )}
          </div>

          {/* Progress ring if percentage is provided */}
          {stat.percentage !== undefined && (
            <div className="flex justify-center mt-4">
              <AnimatedHealthRing
                percentage={stat.percentage}
                size={80}
                strokeWidth={6}
                color="#06b6d4"
                delay={index * 0.1 + 0.4}
              />
            </div>
          )}
        </div>

        {/* Animated border on hover */}
        <motion.div
          className="absolute inset-0 rounded-xl border-2 border-cyan-400/50"
          initial={{ opacity: 0, scale: 0.95 }}
          whileHover={{
            opacity: [0, 1, 0],
            scale: [0.95, 1, 1.05],
            transition: { duration: 1, repeat: Infinity }
          }}
        />
      </div>

      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-500 blur-xl -z-10"
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 0.2 }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  );
}
