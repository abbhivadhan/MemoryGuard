/**
 * Recommendations Dashboard component
 * Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
 */

import React, { useState, useEffect } from 'react';
import recommendationService, { Recommendation, AdherenceStats } from '../../services/recommendationService';
import RecommendationCard from './RecommendationCard';
import RecommendationTutorial3D from './RecommendationTutorial3D';

const RecommendationsDashboard: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [adherenceStats, setAdherenceStats] = useState<AdherenceStats | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [showTutorial, setShowTutorial] = useState(false);
  const [tutorialCategory, setTutorialCategory] = useState<'diet' | 'exercise' | 'sleep' | 'cognitive' | 'social'>('exercise');

  const categories = [
    { value: 'all', label: 'All' },
    { value: 'diet', label: 'Diet' },
    { value: 'exercise', label: 'Exercise' },
    { value: 'sleep', label: 'Sleep' },
    { value: 'cognitive', label: 'Cognitive' },
    { value: 'social', label: 'Social' }
  ];

  useEffect(() => {
    loadRecommendations();
    loadAdherenceStats();
  }, [selectedCategory]);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const category = selectedCategory === 'all' ? undefined : selectedCategory;
      const data = await recommendationService.getRecommendations(category);
      setRecommendations(data);
    } catch (error) {
      console.error('Error loading recommendations:', error);
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
      await loadAdherenceStats();
      await loadRecommendations();
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
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <button
            onClick={() => setShowTutorial(false)}
            className="mb-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            ← Back to Recommendations
          </button>
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
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Personalized Recommendations
          </h1>
          <p className="text-gray-400">
            Evidence-based recommendations tailored to your health profile
          </p>
        </div>

        {/* Adherence Stats */}
        {adherenceStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-gray-400 text-sm mb-1">Overall Adherence</div>
              <div className="text-3xl font-bold text-white">
                {(adherenceStats.adherence_rate * 100).toFixed(0)}%
              </div>
              <div className="text-gray-500 text-sm mt-1">
                Last 30 days
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-gray-400 text-sm mb-1">Total Activities</div>
              <div className="text-3xl font-bold text-white">
                {adherenceStats.total_records}
              </div>
              <div className="text-gray-500 text-sm mt-1">
                Tracked
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-gray-400 text-sm mb-1">Completed</div>
              <div className="text-3xl font-bold text-green-500">
                {adherenceStats.completed}
              </div>
              <div className="text-gray-500 text-sm mt-1">
                Activities
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-gray-400 text-sm mb-1">Active Categories</div>
              <div className="text-3xl font-bold text-white">
                {Object.keys(adherenceStats.by_category).length}
              </div>
              <div className="text-gray-500 text-sm mt-1">
                Categories
              </div>
            </div>
          </div>
        )}

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 mb-6">
          {categories.map((cat) => (
            <button
              key={cat.value}
              onClick={() => setSelectedCategory(cat.value)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedCategory === cat.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Recommendations Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="text-gray-400 mt-4">Loading recommendations...</p>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="text-center py-12 bg-gray-800 rounded-lg">
            <p className="text-gray-400 text-lg">No recommendations available</p>
            <p className="text-gray-500 mt-2">
              Complete a health assessment to receive personalized recommendations
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {recommendations.map((recommendation) => (
              <RecommendationCard
                key={recommendation.id}
                recommendation={recommendation}
                onTrackAdherence={handleTrackAdherence}
                onShowTutorial={handleShowTutorial}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationsDashboard;
