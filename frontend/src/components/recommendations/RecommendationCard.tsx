/**
 * Recommendation Card component
 * Requirements: 15.2, 15.3, 15.4
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, BookOpen, ChevronDown, ChevronRight, Target, Award, Utensils, Activity, Moon, Brain, Users, FileText } from 'lucide-react';
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

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: 'bg-gray-600 border-gray-500',
      medium: 'bg-blue-600 border-blue-500',
      high: 'bg-orange-600 border-orange-500',
      critical: 'bg-red-600 border-red-500'
    };
    return colors[priority] || 'bg-gray-600 border-gray-500';
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

  const getCategoryIcon = (category: string) => {
    // Return Lucide icon components
    const iconMap: Record<string, any> = {
      diet: Utensils,
      exercise: Activity,
      sleep: Moon,
      cognitive: Brain,
      social: Users
    };
    return iconMap[category] || FileText;
  };

  const handleTrackAdherence = async (completed: boolean) => {
    setTrackingToday(true);
    try {
      await onTrackAdherence(recommendation.id, completed);
    } catch (error) {
      console.error('Error tracking adherence:', error);
    } finally {
      setTrackingToday(false);
    }
  };

  const CategoryIcon = getCategoryIcon(recommendation.category);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 shadow-lg hover:shadow-2xl hover:border-white/20 transition-all"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg">
              <CategoryIcon className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-xl font-bold text-white">
              {recommendation.title}
            </h3>
          </div>
          <div className="flex items-center flex-wrap gap-2">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white border ${getPriorityColor(recommendation.priority)}`}>
              {recommendation.priority.toUpperCase()} PRIORITY
            </span>
            {recommendation.evidence_strength && (
              <span className={`text-xs font-medium flex items-center gap-1 ${getEvidenceColor(recommendation.evidence_strength)}`}>
                <Award className="w-3 h-3" />
                {recommendation.evidence_strength.toUpperCase()} EVIDENCE
              </span>
            )}
          </div>
        </div>
        {recommendation.adherence_score !== null && (
          <div className="text-right ml-4">
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              {(recommendation.adherence_score * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-400 uppercase tracking-wide">Adherence</div>
          </div>
        )}
      </div>

      {/* Description */}
      <p className="text-gray-300 mb-4 leading-relaxed">
        {recommendation.description}
      </p>

      {/* Target Metrics */}
      {recommendation.target_metrics && recommendation.target_metrics.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
            <Target className="w-4 h-4" />
            <span className="font-medium">Target Metrics:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {recommendation.target_metrics.map((metric, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-white/5 border border-white/10 text-gray-300 rounded-full text-xs font-medium"
              >
                {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Research Citations */}
      {recommendation.research_citations && recommendation.research_citations.length > 0 && (
        <div className="mb-4">
          <button
            onClick={() => setShowCitations(!showCitations)}
            className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors font-medium"
          >
            {showCitations ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            View Research ({recommendation.research_citations.length} {recommendation.research_citations.length === 1 ? 'study' : 'studies'})
          </button>
          
          {showCitations && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-3 space-y-3"
            >
              {recommendation.research_citations.map((citation, index) => (
                <div key={index} className="bg-white/5 border border-white/10 rounded-lg p-4">
                  <div className="font-semibold text-white text-sm mb-2">
                    {citation.title}
                  </div>
                  <div className="text-xs text-gray-400 mb-2">
                    {citation.authors} • {citation.journal} ({citation.year})
                  </div>
                  <p className="text-xs text-gray-300 mb-2 leading-relaxed">
                    {citation.summary}
                  </p>
                  {citation.doi && (
                    <a
                      href={`https://doi.org/${citation.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-400 hover:text-blue-300 font-medium inline-flex items-center gap-1"
                    >
                      DOI: {citation.doi}
                      <span>→</span>
                    </a>
                  )}
                </div>
              ))}
            </motion.div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleTrackAdherence(true)}
          disabled={trackingToday}
          className="flex-1 px-4 py-3 bg-green-600/80 hover:bg-green-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2 border border-green-500/50"
        >
          <CheckCircle className="w-4 h-4" />
          Completed Today
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleTrackAdherence(false)}
          disabled={trackingToday}
          className="flex-1 px-4 py-3 bg-gray-600/80 hover:bg-gray-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2 border border-gray-500/50"
        >
          <XCircle className="w-4 h-4" />
          Skipped Today
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onShowTutorial(recommendation.category as any)}
          className="px-4 py-3 bg-blue-600/80 hover:bg-blue-600 text-white rounded-lg transition-all font-medium flex items-center justify-center gap-2 border border-blue-500/50"
        >
          <BookOpen className="w-4 h-4" />
          Tutorial
        </motion.button>
      </div>
    </motion.div>
  );
};

export default RecommendationCard;
