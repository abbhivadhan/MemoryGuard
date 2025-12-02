/**
 * Assessment History Component
 * Display past assessment scores and trends over time
 * Requirements: 12.4, 12.7
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line as RechartsLine, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import EmptyState, { EmptyStateIcons } from '../ui/EmptyState';
import MedicalDisclaimer from '../ui/MedicalDisclaimer';
import assessmentService from '../../services/assessmentService';

interface Assessment {
  id: string;
  user_id: string;
  type: string;
  status: string;
  score: number | null;
  max_score: number;
  duration: number | null;
  started_at: string;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

interface AssessmentHistoryProps {
  userId: string;
  onStartNewAssessment?: (type: string) => void;
}

const AssessmentHistory: React.FC<AssessmentHistoryProps> = ({ userId, onStartNewAssessment }) => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string>('all');

  useEffect(() => {
    fetchAssessments();
  }, [userId]);

  const fetchAssessments = async () => {
    try {
      setLoading(true);
      const data = await assessmentService.getUserAssessments(userId);
      setAssessments(data.assessments || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching assessments:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Filter assessments by type
  const filteredAssessments = selectedType === 'all'
    ? assessments
    : assessments.filter(a => a.type === selectedType);

  // Group assessments by type for chart data
  const getChartData = () => {
    const completedAssessments = assessments.filter(a => a.status === 'completed' && a.score !== null);
    
    // Sort by completion date
    const sorted = [...completedAssessments].sort((a, b) => 
      new Date(a.completed_at!).getTime() - new Date(b.completed_at!).getTime()
    );

    // Create data points for each assessment type
    const dataMap = new Map<string, any>();
    
    sorted.forEach(assessment => {
      const date = new Date(assessment.completed_at!).toLocaleDateString();
      
      if (!dataMap.has(date)) {
        dataMap.set(date, { date });
      }
      
      const dataPoint = dataMap.get(date);
      dataPoint[assessment.type] = assessment.score;
    });

    return Array.from(dataMap.values());
  };

  const chartData = getChartData();

  // Get unique assessment types
  const assessmentTypes = Array.from(new Set(assessments.map(a => a.type)));

  // Calculate statistics
  const getStatistics = (type: string) => {
    const typeAssessments = assessments.filter(a => a.type === type && a.status === 'completed' && a.score !== null);
    
    if (typeAssessments.length === 0) {
      return null;
    }

    const scores = typeAssessments.map(a => a.score!);
    const latest = typeAssessments[typeAssessments.length - 1];
    const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    const highest = Math.max(...scores);
    const lowest = Math.min(...scores);

    return {
      count: typeAssessments.length,
      latest: latest.score,
      average: average.toFixed(1),
      highest,
      lowest,
      maxScore: latest.max_score
    };
  };

  const getScoreColor = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 90) return 'text-green-400';
    if (percentage >= 75) return 'text-yellow-400';
    if (percentage >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBgColor = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 90) return 'bg-green-500/20 border-green-500';
    if (percentage >= 75) return 'bg-yellow-500/20 border-yellow-500';
    if (percentage >= 60) return 'bg-orange-500/20 border-orange-500';
    return 'bg-red-500/20 border-red-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white text-xl">Loading assessment history...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-400 text-xl">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen text-white px-4 sm:px-8 py-8 pt-20 sm:pt-24">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl sm:text-5xl font-bold mb-3 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Assessment History
          </h1>
          <p className="text-gray-400 text-lg">Track your cognitive assessment scores over time</p>
        </motion.div>

        {/* Medical Disclaimer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <MedicalDisclaimer type="assessment" compact />
        </motion.div>

        {/* Statistics Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {assessmentTypes.map((type, index) => {
            const stats = getStatistics(type);
            if (!stats) return null;

            return (
              <motion.div
                key={type}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className={`backdrop-blur-md bg-white/5 rounded-xl p-6 border-2 ${getScoreBgColor(stats.latest!, stats.maxScore)} hover:bg-white/10 transition-all duration-300`}
              >
                <h3 className="text-xl font-bold mb-2">{type}</h3>
                <div className="space-y-2">
                  <div>
                    <span className="text-gray-400 text-sm">Latest Score:</span>
                    <div className={`text-3xl font-bold ${getScoreColor(stats.latest!, stats.maxScore)}`}>
                      {stats.latest}/{stats.maxScore}
                    </div>
                  </div>
                  <div className="text-sm text-gray-400">
                    <div>Average: {stats.average}</div>
                    <div>Highest: {stats.highest}</div>
                    <div>Total Tests: {stats.count}</div>
                  </div>
                </div>
                {onStartNewAssessment && (
                  <button
                    onClick={() => onStartNewAssessment(type)}
                    className="mt-4 w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
                  >
                    Take {type} Test
                  </button>
                )}
              </motion.div>
            );
          })}
        </motion.div>

        {/* Trend Chart */}
        {chartData.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="backdrop-blur-md bg-white/5 rounded-xl p-6 mb-8 border border-white/10"
          >
            <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Score Trends</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  labelStyle={{ color: '#F3F4F6' }}
                />
                <Legend />
                {assessmentTypes.map((type, index) => {
                  const colors = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B'];
                  return (
                    <RechartsLine
                      key={type}
                      type="monotone"
                      dataKey={type}
                      stroke={colors[index % colors.length]}
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  );
                })}
              </LineChart>
            </ResponsiveContainer>
          </motion.div>
        )}

        {/* Filter */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mb-6"
        >
          <label className="text-gray-400 mr-4">Filter by type:</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="backdrop-blur-md bg-white/5 text-white px-4 py-2 rounded-lg border border-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500 hover:bg-white/10 transition-all"
          >
            <option value="all">All Types</option>
            {assessmentTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </motion.div>

        {/* Assessment List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="backdrop-blur-md bg-white/5 rounded-xl overflow-hidden border border-white/10"
        >
          <table className="w-full">
            <thead className="backdrop-blur-md bg-white/5 border-b border-white/10">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Duration</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {filteredAssessments.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8">
                    <EmptyState
                      icon={EmptyStateIcons.NoAssessments}
                      title="No Assessments Found"
                      description="Start your first cognitive assessment to track your cognitive health over time. Regular assessments help monitor changes and provide valuable data for analysis."
                      action={onStartNewAssessment ? {
                        label: 'Start Assessment',
                        onClick: () => onStartNewAssessment('MMSE'),
                      } : undefined}
                      className="py-0"
                    />
                  </td>
                </tr>
              ) : (
                filteredAssessments.map((assessment) => (
                  <tr key={assessment.id} className="hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="font-medium">{assessment.type}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {assessment.score !== null ? (
                        <span className={`text-lg font-bold ${getScoreColor(assessment.score, assessment.max_score)}`}>
                          {assessment.score}/{assessment.max_score}
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        assessment.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        assessment.status === 'in_progress' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {assessment.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-400">
                      {assessment.duration ? `${Math.floor(assessment.duration / 60)}m ${assessment.duration % 60}s` : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-400">
                      {assessment.completed_at
                        ? new Date(assessment.completed_at).toLocaleDateString()
                        : new Date(assessment.started_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </motion.div>

        {/* New Assessment Buttons */}
        {onStartNewAssessment && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="mt-8 flex flex-col sm:flex-row gap-4 justify-center"
          >
            <button
              onClick={() => onStartNewAssessment('MMSE')}
              className="backdrop-blur-md bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-8 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 border border-white/20"
            >
              Start MMSE Test
            </button>
            <button
              onClick={() => onStartNewAssessment('MoCA')}
              className="backdrop-blur-md bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-8 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 border border-white/20"
            >
              Start MoCA Test
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default AssessmentHistory;
