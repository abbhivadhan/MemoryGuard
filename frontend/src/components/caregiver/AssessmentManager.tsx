import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trash2, Eye, Calendar, TrendingUp } from 'lucide-react';

interface Assessment {
  id: string;
  type: string;
  score: number;
  max_score: number;
  completed_at: string;
  duration: number;
}

interface AssessmentManagerProps {
  patientId?: string;
}

const AssessmentManager: React.FC<AssessmentManagerProps> = ({ patientId }) => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);

  useEffect(() => {
    if (patientId) {
      loadAssessments();
    }
  }, [patientId]);

  const loadAssessments = async () => {
    if (!patientId) return;
    
    setLoading(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/assessments/user/${patientId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAssessments(data);
      }
    } catch (error) {
      console.error('Failed to load assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAssessment = async (assessmentId: string) => {
    if (!window.confirm('Are you sure you want to delete this assessment? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/assessments/${assessmentId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (response.ok) {
        setAssessments(assessments.filter((a) => a.id !== assessmentId));
        setSelectedAssessment(null);
      } else {
        alert('Failed to delete assessment');
      }
    } catch (error) {
      console.error('Failed to delete assessment:', error);
      alert('Failed to delete assessment');
    }
  };

  const getScoreColor = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'text-green-400';
    if (percentage >= 60) return 'text-yellow-400';
    if (percentage >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBgColor = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'from-green-500/20 to-emerald-500/20 border-green-500/30';
    if (percentage >= 60) return 'from-yellow-500/20 to-amber-500/20 border-yellow-500/30';
    if (percentage >= 40) return 'from-orange-500/20 to-red-500/20 border-orange-500/30';
    return 'from-red-500/20 to-rose-500/20 border-red-500/30';
  };

  if (!patientId) {
    return (
      <div className="backdrop-blur-xl bg-white/5 rounded-2xl p-12 text-center border border-white/10">
        <p className="text-gray-300 text-lg">
          Please select a patient from the dashboard to view their assessments
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="backdrop-blur-xl bg-white/5 rounded-2xl p-12 text-center border border-white/10">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
        <p className="text-gray-300 mt-4">Loading assessments...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-blue-50">Cognitive Assessments</h3>
            <p className="text-gray-400 mt-1">
              View and manage patient assessment history
            </p>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <TrendingUp className="w-5 h-5" />
            <span>{assessments.length} total assessments</span>
          </div>
        </div>

        {assessments.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">No assessments found for this patient</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {assessments.map((assessment) => (
              <motion.div
                key={assessment.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`backdrop-blur-xl bg-gradient-to-br ${getScoreBgColor(
                  assessment.score,
                  assessment.max_score
                )} rounded-xl p-5 border cursor-pointer hover:scale-105 transition-transform`}
                onClick={() => setSelectedAssessment(assessment)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="text-lg font-bold text-blue-50">{assessment.type}</h4>
                    <div className="flex items-center gap-2 text-sm text-gray-400 mt-1">
                      <Calendar className="w-4 h-4" />
                      {new Date(assessment.completed_at).toLocaleDateString()}
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteAssessment(assessment.id);
                    }}
                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex items-baseline gap-2 mb-2">
                  <span
                    className={`text-4xl font-bold ${getScoreColor(
                      assessment.score,
                      assessment.max_score
                    )}`}
                  >
                    {assessment.score}
                  </span>
                  <span className="text-xl text-gray-400">/ {assessment.max_score}</span>
                </div>

                <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
                  <div
                    className={`h-2 rounded-full ${
                      (assessment.score / assessment.max_score) * 100 >= 80
                        ? 'bg-green-500'
                        : (assessment.score / assessment.max_score) * 100 >= 60
                        ? 'bg-yellow-500'
                        : (assessment.score / assessment.max_score) * 100 >= 40
                        ? 'bg-orange-500'
                        : 'bg-red-500'
                    }`}
                    style={{
                      width: `${(assessment.score / assessment.max_score) * 100}%`,
                    }}
                  />
                </div>

                <div className="flex items-center justify-between text-sm text-gray-400">
                  <span>Duration: {Math.round(assessment.duration / 60)}min</span>
                  <div className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    <span>View Details</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {selectedAssessment && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h4 className="text-xl font-bold text-blue-50">
                {selectedAssessment.type} Assessment Details
              </h4>
              <p className="text-gray-400 mt-1">
                Completed on{' '}
                {new Date(selectedAssessment.completed_at).toLocaleString()}
              </p>
            </div>
            <button
              onClick={() => setSelectedAssessment(null)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="backdrop-blur-xl bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-sm text-gray-400 mb-1">Score</div>
              <div
                className={`text-3xl font-bold ${getScoreColor(
                  selectedAssessment.score,
                  selectedAssessment.max_score
                )}`}
              >
                {selectedAssessment.score} / {selectedAssessment.max_score}
              </div>
              <div className="text-sm text-gray-400 mt-1">
                {Math.round(
                  (selectedAssessment.score / selectedAssessment.max_score) * 100
                )}
                % accuracy
              </div>
            </div>

            <div className="backdrop-blur-xl bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-sm text-gray-400 mb-1">Duration</div>
              <div className="text-3xl font-bold text-blue-400">
                {Math.round(selectedAssessment.duration / 60)}
              </div>
              <div className="text-sm text-gray-400 mt-1">minutes</div>
            </div>

            <div className="backdrop-blur-xl bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-sm text-gray-400 mb-1">Test Type</div>
              <div className="text-2xl font-bold text-purple-400">
                {selectedAssessment.type}
              </div>
              <div className="text-sm text-gray-400 mt-1">Cognitive Assessment</div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default AssessmentManager;
