import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Clock, Award, Target, Calendar, BarChart3, Activity } from 'lucide-react';
import { exerciseService, UserExerciseProgress } from '../../services/exerciseService';

const ExerciseProgress: React.FC = () => {
  const [progress, setProgress] = useState<UserExerciseProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    loadProgress();
    
    // Listen for exercise completion events
    const handleExerciseCompleted = () => {
      loadProgress();
    };
    
    window.addEventListener('exerciseCompleted', handleExerciseCompleted);
    
    return () => {
      window.removeEventListener('exerciseCompleted', handleExerciseCompleted);
    };
  }, [timeRange]);

  const loadProgress = async () => {
    try {
      setLoading(true);
      const data = await exerciseService.getUserProgress(timeRange);
      setProgress(data);
    } catch (error) {
      console.error('Failed to load progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const formatType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (!progress) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-16 backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10"
      >
        <Activity className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400 text-lg mb-2">No progress data available</p>
        <p className="text-gray-500 text-sm">Complete some exercises to see your progress</p>
      </motion.div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div className="flex items-center gap-2 text-gray-400">
          <Calendar className="w-5 h-5" />
          <span className="text-sm font-medium">Viewing progress for:</span>
        </div>
        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={loadProgress}
            disabled={loading}
            className="bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl px-4 py-2.5 text-sm font-medium transition-all disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </motion.button>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="bg-white/5 border border-white/10 text-white rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
        </div>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          whileHover={{ scale: 1.02 }}
          className="backdrop-blur-xl bg-gradient-to-br from-purple-600/20 to-purple-800/20 rounded-2xl p-6 border border-purple-500/30"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Target className="w-5 h-5 text-purple-400" />
            </div>
            <div className="text-purple-200 text-sm font-medium">
              Total Exercises
            </div>
          </div>
          <div className="text-4xl font-bold text-white mb-1">
            {progress.total_exercises_completed}
          </div>
          <div className="text-purple-300 text-xs">
            Completed sessions
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          whileHover={{ scale: 1.02 }}
          className="backdrop-blur-xl bg-gradient-to-br from-blue-600/20 to-blue-800/20 rounded-2xl p-6 border border-blue-500/30"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Clock className="w-5 h-5 text-blue-400" />
            </div>
            <div className="text-blue-200 text-sm font-medium">
              Time Spent
            </div>
          </div>
          <div className="text-4xl font-bold text-white mb-1">
            {formatTime(progress.total_time_spent)}
          </div>
          <div className="text-blue-300 text-xs">
            Training duration
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          whileHover={{ scale: 1.02 }}
          className="backdrop-blur-xl bg-gradient-to-br from-green-600/20 to-green-800/20 rounded-2xl p-6 border border-green-500/30"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <BarChart3 className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-green-200 text-sm font-medium">
              Exercise Types
            </div>
          </div>
          <div className="text-4xl font-bold text-white mb-1">
            {Object.keys(progress.exercises_by_type).length}
          </div>
          <div className="text-green-300 text-xs">
            Different categories
          </div>
        </motion.div>
      </div>

      {/* Exercises by Type */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10"
      >
        <div className="flex items-center gap-2 mb-6">
          <BarChart3 className="w-5 h-5 text-purple-400" />
          <h3 className="text-xl font-bold text-white">
            Performance by Exercise Type
          </h3>
        </div>
        <div className="space-y-5">
          {Object.entries(progress.exercises_by_type).map(([type, count], index) => {
            const avgScore = progress.average_scores_by_type[type] || 0;
            return (
              <motion.div
                key={type}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="space-y-2"
              >
                <div className="flex justify-between items-center">
                  <span className="text-gray-200 font-medium">
                    {formatType(type)}
                  </span>
                  <span className="text-gray-400 text-sm">
                    {count} completed
                  </span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1 bg-white/5 rounded-full h-3 overflow-hidden border border-white/10">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${avgScore}%` }}
                      transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                      className="bg-gradient-to-r from-purple-500 to-violet-500 h-3 rounded-full"
                    />
                  </div>
                  <span className="text-white font-bold min-w-[60px] text-right">
                    {avgScore.toFixed(1)}%
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Exercise Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10"
      >
        <div className="flex items-center gap-2 mb-6">
          <Award className="w-5 h-5 text-purple-400" />
          <h3 className="text-xl font-bold text-white">
            Individual Exercise Performance
          </h3>
        </div>
        <div className="space-y-4">
          {progress.exercise_stats.map((stat, index) => (
            <motion.div
              key={stat.exercise_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 + index * 0.05 }}
              whileHover={{ scale: 1.01 }}
              className="bg-white/5 rounded-xl p-5 border border-white/10 hover:border-purple-500/50 transition-all"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="text-white font-semibold text-lg">{stat.exercise_name}</h4>
                  <p className="text-gray-400 text-sm">{formatType(stat.exercise_type)}</p>
                </div>
                <span className="bg-gradient-to-r from-purple-600 to-violet-600 text-white text-xs px-3 py-1.5 rounded-full font-semibold">
                  {stat.current_difficulty}
                </span>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                  <div className="text-gray-400 text-xs mb-1 flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    Attempts
                  </div>
                  <div className="text-white font-bold text-lg">{stat.total_attempts}</div>
                </div>
                <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                  <div className="text-gray-400 text-xs mb-1 flex items-center gap-1">
                    <BarChart3 className="w-3 h-3" />
                    Avg Score
                  </div>
                  <div className="text-white font-bold text-lg">{stat.average_score.toFixed(1)}</div>
                </div>
                <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                  <div className="text-gray-400 text-xs mb-1 flex items-center gap-1">
                    <Award className="w-3 h-3" />
                    Best Score
                  </div>
                  <div className="text-white font-bold text-lg">{stat.best_score.toFixed(1)}</div>
                </div>
                <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                  <div className="text-gray-400 text-xs mb-1 flex items-center gap-1">
                    {stat.improvement_rate >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    Improvement
                  </div>
                  <div className={`font-bold text-lg ${stat.improvement_rate >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {stat.improvement_rate >= 0 ? '+' : ''}{stat.improvement_rate.toFixed(1)}%
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Recent Performances */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10"
      >
        <div className="flex items-center gap-2 mb-6">
          <Activity className="w-5 h-5 text-purple-400" />
          <h3 className="text-xl font-bold text-white">
            Recent Activity
          </h3>
        </div>
        <div className="space-y-3">
          {progress.recent_performances.slice(0, 5).map((perf, index) => (
            <motion.div
              key={perf.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.9 + index * 0.05 }}
              className="flex items-center justify-between bg-white/5 rounded-xl p-4 border border-white/5 hover:border-purple-500/50 transition-all"
            >
              <div className="flex-1">
                <div className="text-white font-semibold mb-1">
                  Score: {perf.score.toFixed(1)} / {perf.max_score}
                </div>
                <div className="flex items-center gap-3 text-gray-400 text-sm">
                  <span>{new Date(perf.created_at).toLocaleDateString()}</span>
                  <span className="w-1 h-1 bg-gray-600 rounded-full"></span>
                  <span className="capitalize">{perf.difficulty}</span>
                </div>
              </div>
              {perf.time_taken && (
                <div className="flex items-center gap-2 text-gray-400 bg-white/5 px-3 py-2 rounded-lg">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm font-medium">
                    {Math.floor(perf.time_taken / 60)}:{(perf.time_taken % 60).toString().padStart(2, '0')}
                  </span>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default ExerciseProgress;
