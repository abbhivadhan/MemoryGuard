import React, { useState, useEffect } from 'react';
import { exerciseService } from '../../services/exerciseService';

const ExerciseMLInsights: React.FC = () => {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setLoading(true);
      const data = await exerciseService.getMLInsights(30);
      setInsights(data);
    } catch (error) {
      console.error('Failed to load ML insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncToML = async () => {
    try {
      setSyncing(true);
      const result = await exerciseService.syncToHealthMetrics(30);
      if (result.success) {
        alert('Exercise data synced successfully! Your cognitive training performance will now be included in ML predictions.');
        loadInsights();
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error('Failed to sync data:', error);
      alert('Failed to sync data. Please try again.');
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">No insights available</p>
      </div>
    );
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return '📈';
      case 'declining':
        return '📉';
      case 'stable':
        return '➡️';
      default:
        return '❓';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return 'text-green-400';
      case 'declining':
        return 'text-red-400';
      case 'stable':
        return 'text-blue-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Cognitive Score */}
      {insights.cognitive_score !== null && (
        <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white">
              Exercise-Based Cognitive Score
            </h3>
            <button
              onClick={handleSyncToML}
              disabled={syncing}
              className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
            >
              {syncing ? 'Syncing...' : 'Sync to ML System'}
            </button>
          </div>
          <div className="text-5xl font-bold text-white mb-2">
            {insights.cognitive_score.toFixed(1)}
          </div>
          <p className="text-purple-200 text-sm">
            Based on your last 30 days of cognitive training
          </p>
        </div>
      )}

      {/* Performance Trends */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">
          Performance Trends
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{getTrendIcon(insights.trends.trend)}</span>
              <span className={`text-lg font-semibold ${getTrendColor(insights.trends.trend)}`}>
                {insights.trends.trend.charAt(0).toUpperCase() + insights.trends.trend.slice(1)}
              </span>
            </div>
            <p className="text-gray-400 text-sm">Overall Trend</p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-white mb-2">
              {insights.trends.improvement_rate >= 0 ? '+' : ''}
              {insights.trends.improvement_rate.toFixed(1)}%
            </div>
            <p className="text-gray-400 text-sm">Improvement Rate</p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-white mb-2">
              {insights.trends.consistency.toFixed(1)}%
            </div>
            <p className="text-gray-400 text-sm">Consistency Score</p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-white mb-2">
              {insights.trends.total_sessions}
            </div>
            <p className="text-gray-400 text-sm">Total Sessions</p>
          </div>
        </div>
      </div>

      {/* Decline Indicators */}
      {insights.decline_indicators.has_concerns && (
        <div className="bg-yellow-900/30 border border-yellow-600 rounded-xl p-6">
          <h3 className="text-xl font-bold text-yellow-400 mb-4">
            ⚠️ Areas for Attention
          </h3>
          
          <div className="space-y-4">
            {insights.decline_indicators.concerns.map((concern: string, index: number) => (
              <div key={index} className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-yellow-300 font-medium mb-2">{concern}</p>
                {insights.decline_indicators.recommendations[index] && (
                  <p className="text-gray-300 text-sm">
                    💡 {insights.decline_indicators.recommendations[index]}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {insights.recommendations.length > 0 && (
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">
            Personalized Recommendations
          </h3>
          
          <div className="space-y-3">
            {insights.recommendations.map((rec: any, index: number) => (
              <div key={index} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-white font-semibold">
                    {rec.type.split('_').map((w: string) => 
                      w.charAt(0).toUpperCase() + w.slice(1)
                    ).join(' ')}
                  </h4>
                  <span className="text-xs text-gray-400 bg-gray-600 px-2 py-1 rounded">
                    {rec.reason}
                  </span>
                </div>
                <p className="text-gray-300 text-sm">{rec.suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-900/30 border border-blue-600 rounded-xl p-6">
        <h3 className="text-lg font-bold text-blue-400 mb-2">
          How This Helps
        </h3>
        <p className="text-gray-300 text-sm">
          Your cognitive training performance is analyzed using machine learning to:
        </p>
        <ul className="list-disc list-inside text-gray-300 text-sm mt-2 space-y-1">
          <li>Track cognitive function trends over time</li>
          <li>Identify early signs of cognitive changes</li>
          <li>Provide personalized exercise recommendations</li>
          <li>Contribute to Alzheimer's risk assessment when synced</li>
        </ul>
      </div>
    </div>
  );
};

export default ExerciseMLInsights;
