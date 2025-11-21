/**
 * Recommendation service for personalized health recommendations
 */

import api from './api';

export interface ResearchCitation {
  title: string;
  authors: string;
  journal: string;
  year: number;
  doi: string;
  summary: string;
}

export interface Recommendation {
  id: string;
  user_id: string;
  category: 'diet' | 'exercise' | 'sleep' | 'cognitive' | 'social';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  research_citations: ResearchCitation[];
  evidence_strength: string | null;
  is_active: boolean;
  adherence_score: number | null;
  generated_from_risk_factors: Record<string, number>;
  target_metrics: string[];
  generated_at: string;
  last_updated: string;
}

export interface AdherenceRecord {
  id: string;
  recommendation_id: string;
  user_id: string;
  date: string;
  completed: boolean;
  notes: string | null;
  outcome_metrics: Record<string, number> | null;
}

export interface AdherenceStats {
  total_records: number;
  completed: number;
  adherence_rate: number;
  by_category: Record<string, {
    total: number;
    completed: number;
    adherence_rate: number;
  }>;
}

class RecommendationService {
  /**
   * Generate recommendations based on risk factors
   */
  async generateRecommendations(
    riskFactors: Record<string, number>,
    currentMetrics: Record<string, number>
  ): Promise<Recommendation[]> {
    const response = await api.post('/recommendations/generate', {
      risk_factors: riskFactors,
      current_metrics: currentMetrics
    });
    return response.data;
  }

  /**
   * Get recommendations for current user
   */
  async getRecommendations(
    category?: string,
    activeOnly: boolean = true
  ): Promise<Recommendation[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    params.append('active_only', activeOnly.toString());
    
    const response = await api.get(`/recommendations?${params.toString()}`);
    return response.data;
  }

  /**
   * Track adherence to a recommendation
   */
  async trackAdherence(
    recommendationId: string,
    completed: boolean,
    notes?: string,
    outcomeMetrics?: Record<string, number>
  ): Promise<AdherenceRecord> {
    const response = await api.post('/recommendations/adherence', {
      recommendation_id: recommendationId,
      completed,
      notes,
      outcome_metrics: outcomeMetrics
    });
    return response.data;
  }

  /**
   * Get adherence statistics
   */
  async getAdherenceStats(days: number = 30): Promise<AdherenceStats> {
    const response = await api.get(`/recommendations/adherence/stats?days=${days}`);
    return response.data;
  }

  /**
   * Update recommendations based on new metrics
   */
  async updateRecommendations(
    newMetrics: Record<string, number>
  ): Promise<Recommendation[]> {
    const response = await api.post('/recommendations/update', newMetrics);
    return response.data;
  }
}

export default new RecommendationService();
