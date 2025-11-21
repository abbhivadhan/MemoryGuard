/**
 * Recommendation Card component
 * Requirements: 15.2, 15.3, 15.4
 */

import React, { useState } from 'react';
import { Recommendation } from '../../services/recommendationService';

interface RecommendationCardProps {
  recommendation: Recommendation;
  onTrackAdherence: (recommendationId: string, completed: boolean) => void;
  onShowTutorial: (category: 'diet' | 'exercise' | 'sleep' | 'cognitive' | 'social') => void;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  onTrackAdherence,
  onShowTutorial
}) => {
  const [showCitations, setShowCitations] = useState(false);
  const [trackingToday, setTrackingToday] = useState(false);

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      diet: '🥗',
      exercise: '🏃',
      sleep: '😴',
      cognitive: '🧠',
      social: '👥'
    };
    return icons[category] || '📋';
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: 'bg-gray-600',
      medium: 'bg-blue-600',
      high: 'bg-orange-600',
      critical: 'bg-red-600'
    };
    return colors[priority] || 'bg-gray-600';
  };

  const getEvidenceColor = (strength: string | null) => {
    if (!strength) return 'text-gray-400';
    const colors: Record<string, string> = {
      strong: 'text-green-400',
      moderate: 'text-yellow-400',
      limited: 'text-orange-400'
    };
    return colors[strength] || 'text-gray-400';
  };

  const handleTrackAdherence = async (completed: boolean) => {
    setTrackingToday(true);
    await onTrackAdherence(recommendation.id, completed);
    setTrackingToday(false);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">{getCategoryIcon(recommendation.category)}</span>
          <div>
            <h3 className="text-xl font-bold text-white">
              {recommendation.title}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              <span className={`px-2 py-1 rounded text-xs font-medium text-white ${getPriorityColor(recommendation.priority)}`}>
                {recommendation.priority.toUpperCase()}
              </span>
              {recommendation.evidence_strength && (
                <span className={`text-xs font-medium ${getEvidenceColor(recommendation.evidence_strength)}`}>
                  {recommendation.evidence_strength} evidence
                </span>
              )}
            </div>
          </div>
        </div>
        {recommendation.adherence_score !== null && (
          <div className="text-right">
            <div className="text-2xl font-bold text-white">
              {(recommendation.adherence_score * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-400">adherence</div>
          </div>
        )}
      </div>

      {/* Description */}
      <p className="text-gray-300 mb-4 leading-relaxed">
        {recommendation.description}
      </p>

      {/* Target Metrics */}
      {recommendation.target_metrics.length > 0 && (
        <div className="mb-4">
          <div className="text-sm text-gray-400 mb-2">Target Metrics:</div>
          <div className="flex flex-wrap gap-2">
            {recommendation.target_metrics.map((metric, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs"
              >
                {metric.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Research Citations */}
      {recommendation.research_citations.length > 0 && (
        <div className="mb-4">
          <button
            onClick={() => setShowCitations(!showCitations)}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            {showCitations ? '▼' : '▶'} View Research ({recommendation.research_citations.length} studies)
          </button>
          
          {showCitations && (
            <div className="mt-3 space-y-3">
              {recommendation.research_citations.map((citation, index) => (
                <div key={index} className="bg-gray-700 rounded p-3">
                  <div className="font-medium text-white text-sm mb-1">
                    {citation.title}
                  </div>
                  <div className="text-xs text-gray-400 mb-2">
                    {citation.authors} • {citation.journal} ({citation.year})
                  </div>
                  <p className="text-xs text-gray-300 mb-2">
                    {citation.summary}
                  </p>
                  {citation.doi && (
                    <a
                      href={`https://doi.org/${citation.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      DOI: {citation.doi} →
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-2">
        <button
          onClick={() => handleTrackAdherence(true)}
          disabled={trackingToday}
          className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          ✓ Completed Today
        </button>
        <button
          onClick={() => handleTrackAdherence(false)}
          disabled={trackingToday}
          className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          ✗ Skipped Today
        </button>
        <button
          onClick={() => onShowTutorial(recommendation.category as any)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          📚 Tutorial
        </button>
      </div>
    </div>
  );
};

export default RecommendationCard;
