/**
 * Assessment Page
 * Main page for cognitive assessments
 * Requirements: 12.1, 12.2, 12.4
 */

import React, { useState, useEffect, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';
import MMSETest from '../components/cognitive/MMSETestNew';
import MoCATest from '../components/cognitive/MoCATest';
import AssessmentHistory from '../components/cognitive/AssessmentHistory';
import assessmentService from '../services/assessmentService';
import { useAuthStore } from '../store/authStore';
import Scene from '../components/3d/Scene';
import Starfield from '../components/3d/Starfield';

type AssessmentView = 'history' | 'mmse' | 'moca';

const AssessmentPage: React.FC = () => {
  const [view, setView] = useState<AssessmentView>('history');
  const [currentAssessmentId, setCurrentAssessmentId] = useState<string | null>(null);
  const [assessmentStartTime, setAssessmentStartTime] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    if (!user) {
      navigate('/');
    }
  }, [user, navigate]);

  const handleStartAssessment = async (type: 'MMSE' | 'MoCA') => {
    try {
      setLoading(true);
      setError(null);
      
      const assessment = await assessmentService.startAssessment({ type });
      setCurrentAssessmentId(assessment.id);
      setAssessmentStartTime(Date.now()); // Track start time
      setView(type.toLowerCase() as AssessmentView);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start assessment');
      console.error('Error starting assessment:', err);
      alert('Failed to start assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProgress = async (responses: Record<string, any>) => {
    if (!currentAssessmentId) return;

    try {
      await assessmentService.updateResponse(currentAssessmentId, { responses });
    } catch (err) {
      console.error('Error saving progress:', err);
    }
  };

  const handleCompleteAssessment = async (responses: Record<string, any>) => {
    if (!currentAssessmentId) {
      console.error('No assessment ID found');
      alert('Error: No active assessment found');
      return;
    }

    try {
      setLoading(true);
      
      // Calculate duration in seconds
      const duration = assessmentStartTime 
        ? Math.floor((Date.now() - assessmentStartTime) / 1000)
        : 0;
      
      console.log('Completing assessment:', {
        id: currentAssessmentId,
        duration,
        responseCount: Object.keys(responses).length
      });
      
      // Save final responses
      await assessmentService.updateResponse(currentAssessmentId, { responses });
      
      // Complete the assessment
      const result = await assessmentService.completeAssessment(currentAssessmentId, {
        duration,
        notes: `Completed with ${Object.keys(responses).length} responses`
      });

      console.log('Assessment completed successfully:', result);

      // Show success message and return to history
      alert(`Assessment completed successfully! Your score: ${result.score}/${result.max_score}`);
      setView('history');
      setCurrentAssessmentId(null);
      setAssessmentStartTime(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to complete assessment';
      setError(errorMessage);
      console.error('Error completing assessment:', err);
      alert(`Failed to save assessment: ${errorMessage}. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-b from-gray-900 to-black">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-b from-gray-900 to-black">
        <div className="text-red-400 text-2xl mb-4">Error: {error}</div>
        <button
          onClick={() => {
            setError(null);
            setView('history');
          }}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg"
        >
          Return to History
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* 3D Background Scene */}
      <div className="fixed inset-0 z-0">
        <Scene camera={{ position: [0, 0, 8], fov: 75 }} enablePhysics={false}>
          <Suspense fallback={null}>
            <Starfield count={200} />
          </Suspense>
        </Scene>
      </div>

      <div className="relative z-10">
        {/* Navigation */}
        <div className="fixed top-2 sm:top-4 left-2 sm:left-4 z-50">
          {view !== 'history' ? (
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to exit? Your progress has been auto-saved, but the assessment will not be completed.')) {
                  setView('history');
                  setCurrentAssessmentId(null);
                  setAssessmentStartTime(null);
                }
              }}
              className="backdrop-blur-sm bg-white/5 hover:bg-white/10 text-white px-3 sm:px-4 py-2 rounded-lg transition-all duration-200 text-sm sm:text-base touch-target border border-white/10"
            >
              <span className="hidden sm:inline">← Back to History</span>
              <span className="sm:hidden">← Back</span>
            </button>
          ) : (
            <motion.button
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 backdrop-blur-sm bg-white/5 hover:bg-white/10 text-white px-3 sm:px-4 py-2 rounded-lg transition-all duration-200 text-sm sm:text-base touch-target border border-white/10"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="hidden sm:inline">Back to Dashboard</span>
              <span className="sm:hidden">Dashboard</span>
            </motion.button>
          )}
        </div>

        {/* Content */}
        {view === 'history' && (
          <AssessmentHistory
            userId={user.id}
            onStartNewAssessment={(type) => handleStartAssessment(type as 'MMSE' | 'MoCA')}
          />
        )}

        {view === 'mmse' && currentAssessmentId && (
          <MMSETest
            assessmentId={currentAssessmentId}
            onComplete={handleCompleteAssessment}
            onSaveProgress={handleSaveProgress}
          />
        )}

        {view === 'moca' && currentAssessmentId && (
          <MoCATest
            assessmentId={currentAssessmentId}
            onComplete={handleCompleteAssessment}
            onSaveProgress={handleSaveProgress}
          />
        )}
      </div>
    </div>
  );
};

export default AssessmentPage;
