import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, TrendingUp, TrendingDown, ArrowRight, Activity, 
  AlertTriangle, Lightbulb, RefreshCw, CheckCircle, Target,
  BarChart3, Zap, Award
} from 'lucide-react';
import { exerciseService } from '../../services/exerciseService';

const ExerciseMLInsights: React.FC = () => {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    loadInsights();
  }, [timeRange]);

  const loadInsights = async () => {
    try {
      setLoading(true);
      const data = await exerciseService.getMLInsights(timeRange);
      setInsights(data);
    } catch (error) {
      console.error('Failed to load ML insights:', error);
      setInsights(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncToML = async () => {
    try {
      setSyncing(true);
      setSyncSuccess(false);
      const result = await exerciseService.syncToHealthMetrics(timeRange);
      if (result.success) {
        setSyncSuccess(true);
        setTimeout(() => setSyncSuccess(false), 3000);
        loadInsights();
      }
    } catch (error) {
      console.error('Failed to sync data:', error);
    } finally {
      setSyncing(false);
    }
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

  if (!insights || !insights.trends) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-16 backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10"
      >
        <Brain className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400 text-lg mb-2">No insights available yet</p>
        <p className="text-gray-500 text-sm mb-4">Complete some exercises to generate ML insights</p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => window.location.reload()}
          className="bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 text-white px-6 py-3 rounded-xl text-sm font-semibold transition-all shadow-lg"
        >
          Refresh
        </motion.button>
      </motion.div>
    );
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return TrendingUp;
      case 'declining':
        return TrendingDown;
      case 'stable':
        return ArrowRight;
      default:
        return Activity;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'declining':
        return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'stable':
        return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
      default:
        return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  const TrendIcon = insights?.trends?.trend ? getTrendIcon(insights.trends.trend) : Activity;

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div className="flex items-center gap-2 text-gray-400">
          <Brain className="w-5 h-5" />
          <span className="text-sm font-medium">ML Analysis Period:</span>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="bg-white/5 border border-white/10 text-white rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </motion.div>

      {/* Cognitive Score */}
      {insights?.cognitive_score !== null && insights?.cognitive_score !== undefined && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="backdrop-blur-xl bg-gradient-to-br from-purple-600/20 to-purple-800/20 rounded-2xl p-8 border border-purple-500/30"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-500/20 rounded-xl">
                <Brain className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold text-white">
                Cognitive Performance Score
              </h3>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSyncToML}
              disabled={syncing || syncSuccess}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                syncSuccess
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                  : 'bg-white/10 hover:bg-white/20 text-white border border-white/20'
              } disabled:opacity-50`}
            >
              {syncing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Syncing...
                </>
              ) : syncSuccess ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Synced!
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Sync to ML System
                </>
              )}
            </motion.button>
          </div>
          
          <div className="flex items-end gap-4 mb-3">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', delay: 0.2 }}
              className="text-6xl font-bold text-white"
            >
              {insights.cognitive_score.toFixed(1)}
            </motion.div>
            <div className="text-purple-300 text-lg font-medium mb-2">/ 100</div>
          </div>
          
          <p className="text-purple-200 text-sm">
            Based on your last {timeRange} days of cognitive training performance
          </p>
        </motion.div>
      )}

      {/* Performance Trends */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10"
      >
        <div className="flex items-center gap-2 mb-6">
          <BarChart3 className="w-5 h-5 text-purple-400" />
          <h3 className="text-xl font-bold text-white">
            Performance Trends
          </h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.02 }}
            className={`rounded-xl p-5 border ${getTrendColor(insights?.trends?.trend || 'stable')}`}
          >
            <div className="flex items-center gap-3 mb-3">
              <TrendIcon className="w-6 h-6" />
              <span className="text-lg font-bold capitalize">
                {insights?.trends?.trend || 'No data'}
              </span>
            </div>
            <p className="text-gray-400 text-sm">Overall Trend</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.35 }}
            whileHover={{ scale: 1.02 }}
            className="bg-white/5 rounded-xl p-5 border border-white/10"
          >
            <div className="flex items-center gap-2 mb-3">
              <Target className="w-5 h-5 text-purple-400" />
              <div className={`text-2xl font-bold ${(insights?.trends?.improvement_rate || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {(insights?.trends?.improvement_rate || 0) >= 0 ? '+' : ''}
                {(insights?.trends?.improvement_rate || 0).toFixed(1)}%
              </div>
            </div>
            <p className="text-gray-400 text-sm">Improvement Rate</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            whileHover={{ scale: 1.02 }}
            className="bg-white/5 rounded-xl p-5 border border-white/10"
          >
            <div className="flex items-center gap-2 mb-3">
              <Award className="w-5 h-5 text-purple-400" />
              <div className="text-2xl font-bold text-white">
                {(insights?.trends?.consistency || 0).toFixed(1)}%
              </div>
            </div>
            <p className="text-gray-400 text-sm">Consistency Score</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.45 }}
            whileHover={{ scale: 1.02 }}
            className="bg-white/5 rounded-xl p-5 border border-white/10"
          >
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-5 h-5 text-purple-400" />
              <div className="text-2xl font-bold text-white">
                {insights?.trends?.total_sessions || 0}
              </div>
            </div>
            <p className="text-gray-400 text-sm">Total Sessions</p>
          </motion.div>
        </div>

        {/* Additional Metrics */}
        {insights?.trends?.average_score !== undefined && insights?.trends?.recent_average !== undefined && (
          <div className="mt-6 grid grid-cols-2 gap-4 p-4 bg-white/5 rounded-xl border border-white/5">
            <div>
              <div className="text-gray-400 text-xs mb-1">Average Score</div>
              <div className="text-white font-bold text-lg">{insights.trends.average_score.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Recent Average</div>
              <div className="text-white font-bold text-lg">{insights.trends.recent_average.toFixed(1)}</div>
            </div>
          </div>
        )}
      </motion.div>

      {/* Decline Indicators */}
      {insights?.decline_indicators?.has_concerns && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="backdrop-blur-xl bg-yellow-900/20 border border-yellow-600/50 rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
            </div>
            <h3 className="text-xl font-bold text-yellow-400">
              Areas for Attention
            </h3>
          </div>
          
          <div className="space-y-4">
            {insights.decline_indicators.concerns.map((concern: string, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="bg-white/5 rounded-xl p-4 border border-yellow-500/20"
              >
                <p className="text-yellow-300 font-medium mb-3 flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>{concern}</span>
                </p>
                {insights.decline_indicators.recommendations[index] && (
                  <div className="flex items-start gap-2 text-gray-300 text-sm bg-white/5 rounded-lg p-3">
                    <Lightbulb className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                    <span>{insights.decline_indicators.recommendations[index]}</span>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Recommendations */}
      {insights?.recommendations && insights.recommendations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Lightbulb className="w-5 h-5 text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-white">
              Personalized Recommendations
            </h3>
          </div>
          
          <div className="space-y-3">
            {insights.recommendations.map((rec: any, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + index * 0.05 }}
                whileHover={{ scale: 1.01 }}
                className="bg-white/5 rounded-xl p-4 border border-white/10 hover:border-purple-500/50 transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="text-white font-semibold flex items-center gap-2">
                    <Target className="w-4 h-4 text-purple-400" />
                    {rec.type.split('_').map((w: string) => 
                      w.charAt(0).toUpperCase() + w.slice(1)
                    ).join(' ')}
                  </h4>
                  <span className="text-xs text-gray-400 bg-white/5 px-3 py-1 rounded-full border border-white/10">
                    {rec.reason}
                  </span>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">{rec.suggestion}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="backdrop-blur-xl bg-blue-900/20 border border-blue-600/50 rounded-2xl p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <Brain className="w-5 h-5 text-blue-400" />
          </div>
          <h3 className="text-lg font-bold text-blue-400">
            How ML Insights Help
          </h3>
        </div>
        <p className="text-gray-300 text-sm mb-3">
          Your cognitive training performance is analyzed using machine learning to:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="flex items-start gap-2 text-gray-300 text-sm">
            <CheckCircle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            <span>Track cognitive function trends over time</span>
          </div>
          <div className="flex items-start gap-2 text-gray-300 text-sm">
            <CheckCircle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            <span>Identify early signs of cognitive changes</span>
          </div>
          <div className="flex items-start gap-2 text-gray-300 text-sm">
            <CheckCircle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            <span>Provide personalized exercise recommendations</span>
          </div>
          <div className="flex items-start gap-2 text-gray-300 text-sm">
            <CheckCircle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            <span>Contribute to Alzheimer's risk assessment</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ExerciseMLInsights;
