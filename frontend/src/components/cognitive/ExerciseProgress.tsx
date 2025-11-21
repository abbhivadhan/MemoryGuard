import React, { useState, useEffect } from 'react';
import { exerciseService, UserExerciseProgress } from '../../services/exerciseService';

const ExerciseProgress: React.FC = () => {
  const [progress, setProgress] = useState<UserExerciseProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    loadProgress();
  }, [timeRange]);

  const loadProgress = async () => {
    try {
      setLoading(true);
      const data = await exerciseService.getUserProgress(timeRange);
      setProgress(data);
    } catch (error) {
      console.error('Failed to load progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const formatType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (!progress) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">No progress data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <div className="flex justify-end">
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={365}>Last year</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6">
          <div className="text-purple-200 text-sm font-medium mb-2">
            Total Exercises
          </div>
          <div className="text-4xl font-bold text-white">
            {progress.total_exercises_completed}
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-6">
          <div className="text-blue-200 text-sm font-medium mb-2">
            Time Spent
          </div>
          <div className="text-4xl font-bold text-white">
            {formatTime(progress.total_time_spent)}
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-6">
          <div className="text-green-200 text-sm font-medium mb-2">
            Exercise Types
          </div>
          <div className="text-4xl font-bold text-white">
            {Object.keys(progress.exercises_by_type).length}
          </div>
        </div>
      </div>

      {/* Exercises by Type */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">
          Exercises by Type
        </h3>
        <div className="space-y-4">
          {Object.entries(progress.exercises_by_type).map(([type, count]) => {
            const avgScore = progress.average_scores_by_type[type] || 0;
            return (
              <div key={type} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300 font-medium">
                    {formatType(type)}
                  </span>
                  <span className="text-gray-400 text-sm">
                    {count} completed
                  </span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-purple-500 h-2 rounded-full transition-all"
                      style={{ width: `${(avgScore / 100) * 100}%` }}
                    />
                  </div>
                  <span className="text-white font-semibold min-w-[60px] text-right">
                    {avgScore.toFixed(1)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Exercise Stats */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">
          Individual Exercise Performance
        </h3>
        <div className="space-y-4">
          {progress.exercise_stats.map((stat) => (
            <div key={stat.exercise_id} className="bg-gray-700 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="text-white font-semibold">{stat.exercise_name}</h4>
                  <p className="text-gray-400 text-sm">{formatType(stat.exercise_type)}</p>
                </div>
                <span className="bg-purple-600 text-white text-xs px-3 py-1 rounded-full">
                  {stat.current_difficulty}
                </span>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-400">Attempts</div>
                  <div className="text-white font-semibold">{stat.total_attempts}</div>
                </div>
                <div>
                  <div className="text-gray-400">Avg Score</div>
                  <div className="text-white font-semibold">{stat.average_score.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-gray-400">Best Score</div>
                  <div className="text-white font-semibold">{stat.best_score.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-gray-400">Improvement</div>
                  <div className={`font-semibold ${stat.improvement_rate >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {stat.improvement_rate >= 0 ? '+' : ''}{stat.improvement_rate.toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Performances */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">
          Recent Activity
        </h3>
        <div className="space-y-3">
          {progress.recent_performances.slice(0, 5).map((perf) => (
            <div key={perf.id} className="flex items-center justify-between bg-gray-700 rounded-lg p-3">
              <div className="flex-1">
                <div className="text-white font-medium">
                  Score: {perf.score.toFixed(1)} / {perf.max_score}
                </div>
                <div className="text-gray-400 text-sm">
                  {new Date(perf.created_at).toLocaleDateString()} • {perf.difficulty}
                </div>
              </div>
              {perf.time_taken && (
                <div className="text-gray-400 text-sm">
                  {Math.floor(perf.time_taken / 60)}:{(perf.time_taken % 60).toString().padStart(2, '0')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ExerciseProgress;
