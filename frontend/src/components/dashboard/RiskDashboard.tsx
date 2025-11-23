import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import RiskAssessment from './RiskAssessment';
import SHAPExplanation from './SHAPExplanation';
import RiskExplanation from './RiskExplanation';
import ProgressionForecast from './ProgressionForecast';
import { mlService, PredictionResponse } from '../../services/mlService';
import { useAuthStore } from '../../store/authStore';

interface RiskDashboardProps {
  userId?: number | string;
}

export default function RiskDashboard({ userId }: RiskDashboardProps) {
  const { user } = useAuthStore();
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentMetrics, setCurrentMetrics] = useState<Record<string, number> | null>(null);

  const effectiveUserId = userId || user?.id;

  useEffect(() => {
    if (effectiveUserId) {
      loadPrediction();
    }
  }, [effectiveUserId]);

  const loadPrediction = async () => {
    if (!effectiveUserId) return;

    setLoading(true);
    setError(null);

    try {
      const userIdNum = typeof effectiveUserId === 'string' ? parseInt(effectiveUserId) : effectiveUserId;
      const latestPrediction = await mlService.getLatestPrediction(userIdNum);
      setPrediction(latestPrediction);

      // Extract current metrics from prediction metadata if available
      if (latestPrediction?.metadata?.input_features) {
        setCurrentMetrics(latestPrediction.metadata.input_features);
      }
    } catch (err) {
      console.error('Error loading prediction:', err);
      setError('Failed to load risk assessment data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-400 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading risk assessment...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gray-800 rounded-lg p-8 text-center">
            <div className="text-red-400 mb-4">
              <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-xl font-semibold">{error}</p>
            </div>
            <button
              onClick={loadPrediction}
              className="mt-4 px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors text-white font-medium"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-800 rounded-lg p-8 text-center"
          >
            <div className="text-gray-400 mb-6">
              <svg className="w-20 h-20 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h2 className="text-2xl font-bold text-white mb-2">No Risk Assessment Available</h2>
              <p className="text-lg mb-4">
                Complete your health metrics and cognitive assessments to generate a comprehensive risk assessment.
              </p>
            </div>
            
            <div className="bg-gray-900 rounded-lg p-6 max-w-2xl mx-auto text-left">
              <h3 className="text-lg font-semibold text-white mb-4">To get started:</h3>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-cyan-400 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Complete cognitive assessments (MMSE, MoCA)</span>
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-cyan-400 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Input your health metrics (biomarkers, lifestyle factors)</span>
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-cyan-400 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Upload medical imaging data (optional)</span>
                </li>
              </ul>
            </div>

            <div className="mt-8 flex justify-center space-x-4">
              <button
                onClick={() => window.location.href = '/dashboard'}
                className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors text-white font-medium"
              >
                Go to Dashboard
              </button>
              <button
                onClick={() => window.location.href = '/assessments'}
                className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-white font-medium"
              >
                Take Assessment
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            Alzheimer's Risk Assessment Dashboard
          </h1>
          <p className="text-gray-400 text-lg">
            Comprehensive analysis powered by advanced machine learning
          </p>
        </motion.div>

        {/* Risk Assessment Overview */}
        <RiskAssessment userId={effectiveUserId} prediction={prediction} />

        {/* Plain Language Explanation */}
        <RiskExplanation predictionId={prediction.id} prediction={prediction} />

        {/* SHAP Feature Importance */}
        <SHAPExplanation predictionId={prediction.id} />

        {/* Progression Forecast */}
        {currentMetrics && (
          <ProgressionForecast userId={effectiveUserId} currentMetrics={currentMetrics} />
        )}

        {/* Action Items */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 border border-purple-700/50 rounded-lg p-6"
        >
          <h2 className="text-2xl font-bold text-white mb-4">Recommended Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <button className="bg-gray-800 hover:bg-gray-700 rounded-lg p-4 text-left transition-colors group">
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-10 h-10 bg-cyan-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-white font-semibold">View Recommendations</h3>
              </div>
              <p className="text-gray-400 text-sm">Get personalized lifestyle and health recommendations</p>
            </button>

            <button className="bg-gray-800 hover:bg-gray-700 rounded-lg p-4 text-left transition-colors group">
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h3 className="text-white font-semibold">Schedule Follow-up</h3>
              </div>
              <p className="text-gray-400 text-sm">Set up your next cognitive assessment</p>
            </button>

            <button className="bg-gray-800 hover:bg-gray-700 rounded-lg p-4 text-left transition-colors group">
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-white font-semibold">Share with Provider</h3>
              </div>
              <p className="text-gray-400 text-sm">Export report for your healthcare provider</p>
            </button>
          </div>
        </motion.div>

        {/* Footer Note */}
        <div className="text-center text-gray-500 text-sm py-4">
          <p>
            Last updated: {new Date(prediction.created_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </p>
        </div>
      </div>
    </div>
  );
}
