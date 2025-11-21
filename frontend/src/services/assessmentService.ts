/**
 * Assessment Service
 * API client for cognitive assessment endpoints
 * Requirements: 12.4
 */

import api from './api';

export interface AssessmentStartRequest {
  type: 'MMSE' | 'MoCA' | 'CDR' | 'ClockDrawing';
}

export interface AssessmentResponseUpdate {
  responses: Record<string, any>;
}

export interface AssessmentCompleteRequest {
  duration?: number;
  notes?: string;
}

export interface Assessment {
  id: string;
  user_id: string;
  type: string;
  status: string;
  score: number | null;
  max_score: number;
  responses: Record<string, any>;
  duration: number | null;
  started_at: string;
  completed_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssessmentListResponse {
  assessments: Assessment[];
  total: number;
}

class AssessmentService {
  /**
   * Start a new cognitive assessment
   */
  async startAssessment(request: AssessmentStartRequest): Promise<Assessment> {
    const response = await api.post('/assessments/start', request);
    return response.data;
  }

  /**
   * Update assessment responses
   */
  async updateResponse(assessmentId: string, request: AssessmentResponseUpdate): Promise<Assessment> {
    const response = await api.put(`/assessments/${assessmentId}/response`, request);
    return response.data;
  }

  /**
   * Complete an assessment and calculate score
   */
  async completeAssessment(assessmentId: string, request: AssessmentCompleteRequest): Promise<Assessment> {
    const response = await api.post(`/assessments/${assessmentId}/complete`, request);
    return response.data;
  }

  /**
   * Get all assessments for a user
   */
  async getUserAssessments(userId: string): Promise<AssessmentListResponse> {
    const response = await api.get(`/assessments/${userId}`);
    return response.data;
  }

  /**
   * Get the latest assessment of a specific type for a user
   */
  async getLatestAssessment(userId: string, assessmentType: string): Promise<Assessment> {
    const response = await api.get(`/assessments/${userId}/latest/${assessmentType}`);
    return response.data;
  }
}

export default new AssessmentService();
