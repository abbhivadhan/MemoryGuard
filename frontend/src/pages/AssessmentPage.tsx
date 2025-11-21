/**
 * Assessment Page
 * Main page for cognitive assessments
 * Requirements: 12.1, 12.2, 12.4
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MMSETest from '../components/cognitive/MMSETest';
import MoCATest from '../components/cognitive/MoCATest';
import AssessmentHistory from '../components/cognitive/AssessmentHistory';
import assessmentService from '../services/assessmentService';
import { useAuthStore } from '../store/authStore';

type AssessmentView = 'history' | 'mmse' | 'moca';

const AssessmentPage: React.FC = () => {
  const [view, setView] = useState<AssessmentView>('history');
  const [currentAssessmentId, setCurrentAssessmentId] = useState<string | null>(null);
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
      setView(type.toLowerCase() as AssessmentView);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start assessment');
      console.error('Error starting assessment:', err);
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
    if (!currentAssessmentId) return;

    try {
      setLoading(true);
      
      // Save final responses
      await assessmentService.updateResponse(currentAssessmentId, { responses });
      
      // Complete the assessment
      const startTime = Date.now();
      await assessmentService.completeAssessment(currentAssessmentId, {
        duration: Math.floor((Date.now() - startTime) / 1000)
      });

      // Show success message and return to history
      alert('Assessment completed successfully!');
      setView('history');
      setCurrentAssessmentId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete assessment');
      console.error('Error completing assessment:', err);
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
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      {/* Navigation */}
      {view !== 'history' && (
        <div className="fixed top-2 sm:top-4 left-2 sm:left-4 z-50">
          <button
            onClick={() => {
              if (window.confirm('Are you sure you want to exit? Your progress will be saved.')) {
                setView('history');
                setCurrentAssessmentId(null);
              }
            }}
            className="bg-gray-800 hover:bg-gray-700 text-white px-3 sm:px-4 py-2 rounded-lg transition-all duration-200 text-sm sm:text-base touch-target"
          >
            <span className="hidden sm:inline">← Back to History</span>
            <span className="sm:hidden">← Back</span>
          </button>
        </div>
      )}

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
  );
};

export default AssessmentPage;
