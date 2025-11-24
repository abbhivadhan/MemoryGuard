/**
 * Recommendations Dashboard component
 * Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, TrendingUp, CheckCircle2, Layers, AlertCircle, Loader2, LogIn } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import recommendationService, { Recommendation, AdherenceStats } from '../../services/recommendationService';
import RecommendationCard from './RecommendationCard';
import RecommendationTutorial3D from './RecommendationTutorial3D';

const RecommendationsDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [adherenceStats, setAdherenceStats] = useState<AdherenceStats | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [showTutorial, setShowTutorial] = useState(false);
  const [tutorialCategory, setTutorialCategory] = useState<'diet' | 'exercise' | 'sleep' | 'cognitive' | 'social'>('exercise');

  const categories = [
    { value: 'all', label: 'All Categories', icon: Layers },
    { value: 'diet', label: 'Diet', icon: Activity },
    { value: 'exercise', label: 'Exercise', icon: Activity },
    { value: 'sleep', label: 'Sleep', icon: Activity },
    { value: 'cognitive', label: 'Cognitive', icon: Activity },
    { value: 'social', label: 'Social', icon: Activity }
  ];

  useEffect(() => {
    loadData();
  }, [selectedCategory]);

  const loadData = async () => {
    await Promise.all([
      loadRecommendations(),
      loadAdherenceStats()
    ]);
  };

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      setIsAuthError(false);
      const category = selectedCategory === 'all' ? undefined : selectedCategory;
      const data = await recommendationService.getRecommendations(category);
      setRecommendations(data);
    } catch (error: any) {
      console.error('Error loading recommendations:', error);
      
      // For 403/401 errors, just show empty state instead of error
      // This handles the case where user is logged in but has no recommendations
      if (error.response?.status === 401 || error.response?.status === 403) {
        // Set empty recommendations array to show the empty state
        setRecommendations([]);
        setError(null);
      } else {
        // For other errors, show the error message
        setError(error.response?.data?.detail || 'Failed to load recommendations');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadAdherenceStats = async () => {
    try {
      const stats = await recommendationService.getAdherenceStats(30);
      setAdherenceStats(stats);
    } catch (error) {
      console.error('Error loading adherence stats:', error);
    }
  };

  const handleTrackAdherence = async (recommendationId: string, completed: boolean) => {
    try {
      await recommendationService.trackAdherence(recommendationId, completed);
      await loadData();
    } catch (error) {
      console.error('Error tracking adherence:', error);
    }
  };

  const handleShowTutorial = (category: 'diet' | 'exercise' | 'sleep' | 'cognitive' | 'social') => {
    setTutorialCategory(category);
    setShowTutorial(true);
  };

  if (showTutorial) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-6xl mx-auto">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowTutorial(false)}
            className="mb-4 px-6 py-3 backdrop-blur-md bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-all font-medium"
          >
            Back to Recommendations
          </motion.button>
          <div className="h-[600px]">
            <RecommendationTutorial3D
              category={tutorialCategory}
              onComplete={() => setShowTutorial(false)}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Adherence Stats */}
      {adherenceStats && adherenceStats.total_records > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
        >
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-white/20 transition-all">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-400 text-sm font-medium">Overall Adherence</div>
              <TrendingUp className="w-5 h-5 text-blue-400" />
            </div>
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              {(adherenceStats.adherence_rate * 100).toFixed(0)}%
            </div>
            <div className="text-gray-500 text-xs mt-1 uppercase tracking-wide">
              Last 30 days
            </div>
          </div>
          
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-white/20 transition-all">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-400 text-sm font-medium">Total Activities</div>
              <Activity className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-4xl font-bold text-white">
              {adherenceStats.total_records}
            </div>
            <div className="text-gray-500 text-xs mt-1 uppercase tracking-wide">
              Tracked
            </div>
          </div>
          
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-white/20 transition-all">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-400 text-sm font-medium">Completed</div>
              <CheckCircle2 className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-4xl font-bold text-green-400">
              {adherenceStats.completed}
            </div>
            <div className="text-gray-500 text-xs mt-1 uppercase tracking-wide">
              Activities
            </div>
          </div>
          
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-white/20 transition-all">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-400 text-sm font-medium">Active Categories</div>
              <Layers className="w-5 h-5 text-purple-400" />
            </div>
            <div className="text-4xl font-bold text-white">
              {Object.keys(adherenceStats.by_category).length}
            </div>
            <div className="text-gray-500 text-xs mt-1 uppercase tracking-wide">
              Categories
            </div>
          </div>
        </motion.div>
      )}

      {/* Category Filter */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap gap-3 mb-8"
      >
        {categories.map((cat) => {
          const Icon = cat.icon;
          return (
            <motion.button
              key={cat.value}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedCategory(cat.value)}
              className={`px-5 py-2.5 rounded-lg font-medium transition-all flex items-center gap-2 ${
                selectedCategory === cat.value
                  ? 'bg-blue-600 text-white border border-blue-500 shadow-lg shadow-blue-500/50'
                  : 'backdrop-blur-md bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10 hover:border-white/20'
              }`}
            >
              <Icon className="w-4 h-4" />
              {cat.label}
            </motion.button>
          );
        })}
      </motion.div>

      {/* Error State */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="backdrop-blur-md bg-red-500/10 border border-red-500/30 rounded-xl p-6 mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-red-400" />
              <div>
                <div className="text-red-400 font-semibold">
                  {isAuthError ? 'Authentication Required' : 'Error Loading Recommendations'}
                </div>
                <div className="text-red-300 text-sm mt-1">{error}</div>
              </div>
            </div>
            {isAuthError && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/')}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all border border-blue-500 flex items-center gap-2"
              >
                <LogIn className="w-4 h-4" />
                Go to Login
              </motion.button>
            )}
          </div>
        </motion.div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="text-center py-20">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-lg">Loading recommendations...</p>
        </div>
      ) : recommendations.length === 0 ? (
        /* Empty State */
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center py-20 backdrop-blur-md bg-white/5 border border-white/10 rounded-xl"
        >
          <div className="max-w-2xl mx-auto px-6">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Activity className="w-10 h-10 text-blue-400" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">No Recommendations Yet</h3>
            <p className="text-gray-400 mb-8 leading-relaxed">
              Personalized recommendations are generated based on your health assessments and risk predictions. 
              To get started, complete a cognitive assessment or health risk evaluation.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/assessment')}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all border border-blue-500"
              >
                Take Assessment
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 backdrop-blur-md bg-white/5 hover:bg-white/10 text-white rounded-lg font-medium transition-all border border-white/10 hover:border-white/20"
              >
                Go to Dashboard
              </motion.button>
            </div>
          </div>
        </motion.div>
      ) : (
        /* Recommendations Grid */
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          {recommendations.map((recommendation, index) => (
            <motion.div
              key={recommendation.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <RecommendationCard
                recommendation={recommendation}
                onTrackAdherence={handleTrackAdherence}
                onShowTutorial={handleShowTutorial}
              />
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
};

export default RecommendationsDashboard;
