import api from './api';

export interface Exercise {
  id: string;
  name: string;
  description?: string;
  type: 'memory_game' | 'pattern_recognition' | 'problem_solving';
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  instructions?: string;
  config?: Record<string, any>;
  created_at: string;
}

export interface ExercisePerformance {
  id: string;
  user_id: string;
  exercise_id: string;
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  score: number;
  max_score: number;
  time_taken?: number;
  completed: boolean;
  performance_data?: Record<string, any>;
  created_at: string;
}

export interface ExerciseStats {
  exercise_id: string;
  exercise_name: string;
  exercise_type: string;
  total_attempts: number;
  average_score: number;
  best_score: number;
  average_time?: number;
  current_difficulty: string;
  improvement_rate: number;
}

export interface UserExerciseProgress {
  total_exercises_completed: number;
  total_time_spent: number;
  exercises_by_type: Record<string, number>;
  average_scores_by_type: Record<string, number>;
  recent_performances: ExercisePerformance[];
  exercise_stats: ExerciseStats[];
}

export const exerciseService = {
  // Get exercise library
  getExerciseLibrary: async (type?: string, difficulty?: string): Promise<Exercise[]> => {
    const params = new URLSearchParams();
    if (type) params.append('type', type);
    if (difficulty) params.append('difficulty', difficulty);
    
    const response = await api.get(`/exercises/library?${params.toString()}`);
    return response.data;
  },

  // Get specific exercise
  getExercise: async (exerciseId: string): Promise<Exercise> => {
    const response = await api.get(`/exercises/library/${exerciseId}`);
    return response.data;
  },

  // Record performance
  recordPerformance: async (performance: {
    exercise_id: string;
    difficulty: string;
    score: number;
    max_score: number;
    time_taken?: number;
    completed?: boolean;
    performance_data?: Record<string, any>;
  }): Promise<ExercisePerformance> => {
    const response = await api.post('/exercises/performances', performance);
    return response.data;
  },

  // Get user performances
  getUserPerformances: async (exerciseId?: string, limit?: number): Promise<ExercisePerformance[]> => {
    const params = new URLSearchParams();
    if (exerciseId) params.append('exercise_id', exerciseId);
    if (limit) params.append('limit', limit.toString());
    
    const response = await api.get(`/exercises/performances?${params.toString()}`);
    return response.data;
  },

  // Get exercise stats
  getExerciseStats: async (exerciseId: string): Promise<ExerciseStats> => {
    const response = await api.get(`/exercises/stats/${exerciseId}`);
    return response.data;
  },

  // Get user progress
  getUserProgress: async (days?: number): Promise<UserExerciseProgress> => {
    const params = days ? `?days=${days}` : '';
    const response = await api.get(`/exercises/progress${params}`);
    return response.data;
  },

  // Get recommended difficulty
  getRecommendedDifficulty: async (exerciseId: string): Promise<{
    recommended_difficulty: string;
    current_difficulty: string;
    recent_average_score: number;
  }> => {
    const response = await api.get(`/exercises/recommended-difficulty/${exerciseId}`);
    return response.data;
  },

  // Get ML insights from exercise data
  getMLInsights: async (days?: number): Promise<{
    cognitive_score: number | null;
    trends: {
      trend: string;
      slope: number;
      improvement_rate: number;
      consistency: number;
      average_score: number;
      recent_average: number;
      total_sessions: number;
    };
    decline_indicators: {
      has_concerns: boolean;
      concerns: string[];
      recommendations: string[];
    };
    recommendations: Array<{
      type: string;
      reason: string;
      suggestion: string;
    }>;
  }> => {
    const params = days ? `?days=${days}` : '';
    const response = await api.get(`/exercises/ml-insights${params}`);
    return response.data;
  },

  // Sync exercise data to health metrics for ML predictions
  syncToHealthMetrics: async (days?: number): Promise<{
    success: boolean;
    message: string;
    metric_id?: string;
    cognitive_score?: number;
  }> => {
    const params = days ? `?days=${days}` : '';
    const response = await api.post(`/exercises/sync-to-health-metrics${params}`);
    return response.data;
  }
};
