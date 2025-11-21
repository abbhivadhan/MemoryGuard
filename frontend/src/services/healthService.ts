import apiClient from './api';

export interface HealthMetric {
  id: string;
  userId: string;
  type: 'cognitive' | 'biomarker' | 'imaging' | 'lifestyle' | 'cardiovascular';
  name: string;
  value: number;
  unit: string;
  timestamp: string;
  source: 'manual' | 'assessment' | 'device' | 'lab';
}

export interface HealthMetricsResponse {
  metrics: HealthMetric[];
  total: number;
}

export const healthService = {
  // Get all health metrics for a user
  getHealthMetrics: async (userId: string): Promise<HealthMetricsResponse> => {
    const response = await apiClient.get(`/health/metrics/${userId}`);
    return response.data;
  },

  // Get health metrics by type
  getHealthMetricsByType: async (userId: string, type: string): Promise<HealthMetricsResponse> => {
    const response = await apiClient.get(`/health/metrics/${userId}/${type}`);
    return response.data;
  },

  // Add a new health metric
  addHealthMetric: async (metric: Omit<HealthMetric, 'id'>): Promise<HealthMetric> => {
    const response = await apiClient.post('/health/metrics', metric);
    return response.data;
  },

  // Update a health metric
  updateHealthMetric: async (id: string, metric: Partial<HealthMetric>): Promise<HealthMetric> => {
    const response = await apiClient.put(`/health/metrics/${id}`, metric);
    return response.data;
  },

  // Delete a health metric
  deleteHealthMetric: async (id: string): Promise<void> => {
    await apiClient.delete(`/health/metrics/${id}`);
  },
};
