/**
 * Assessment History Component
 * Display past assessment scores and trends over time
 * Requirements: 12.4, 12.7
 */

import React, { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { LineChart, Line as RechartsLine, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import EmptyState, { EmptyStateIcons } from '../ui/EmptyState';
import MedicalDisclaimer from '../ui/MedicalDisclaimer';

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
      const response = await fetch(`/api/v1/assessments/${userId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch assessments');
      }

      const data = await response.json();
      setAssessments(data.assessments || []);
      setError(null);
    } catch (err) {
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
    <div className="w-full min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-8">
      <div className="container mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Assessment History</h1>
          <p className="text-gray-400">Track your cognitive assessment scores over time</p>
        </div>

        {/* Medical Disclaimer */}
        <div className="mb-8">
          <MedicalDisclaimer type="assessment" compact />
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {assessmentTypes.map(type => {
            const stats = getStatistics(type);
            if (!stats) return null;

            return (
              <div key={type} className={`rounded-lg p-6 border-2 ${getScoreBgColor(stats.latest!, stats.maxScore)}`}>
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
                    className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-all duration-200"
                  >
                    Take {type} Test
                  </button>
                )}
              </div>
            );
          })}
        </div>

        {/* Trend Chart */}
        {chartData.length > 0 && (
          <div className="bg-gray-800 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">Score Trends</h2>
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
          </div>
        )}

        {/* Filter */}
        <div className="mb-6">
          <label className="text-gray-400 mr-4">Filter by type:</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Types</option>
            {assessmentTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        {/* Assessment List */}
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-900">
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
                  <tr key={assessment.id} className="hover:bg-gray-700 transition-colors">
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
        </div>

        {/* New Assessment Buttons */}
        {onStartNewAssessment && (
          <div className="mt-8 flex gap-4 justify-center">
            <button
              onClick={() => onStartNewAssessment('MMSE')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
            >
              Start MMSE Test
            </button>
            <button
              onClick={() => onStartNewAssessment('MoCA')}
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
            >
              Start MoCA Test
            </button>
          </div>
        )}
      </div>

      {/* 3D Background */}
      <div className="fixed inset-0 -z-10 opacity-10">
        <Canvas camera={{ position: [0, 0, 5] }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.3} />
          <mesh>
            <icosahedronGeometry args={[2, 1]} />
            <meshStandardMaterial color="#6366F1" wireframe />
          </mesh>
        </Canvas>
      </div>
    </div>
  );
};

export default AssessmentHistory;
