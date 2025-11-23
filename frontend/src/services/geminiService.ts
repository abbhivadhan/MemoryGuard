/**
 * Gemini AI Service
 * 
 * Frontend service for interacting with Gemini AI endpoints
 */

import api from './api';

export interface HealthInsightsRequest {
  user_data: Record<string, any>;
  focus_areas?: string[];
}

export interface HealthInsightsResponse {
  insights: string[];
  recommendations: string[];
  warnings: string[];
  next_steps: string[];
}

export interface ChatRequest {
  message: string;
  conversation_history?: Array<{ role: string; content: string }>;
  user_context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  conversation_id?: string;
}

export interface AssessmentAnalysisRequest {
  assessment_type: string;
  responses: Record<string, any>;
  score: number;
  max_score: number;
}

export interface AssessmentAnalysisResponse {
  feedback: string;
  strengths: string[];
  areas_for_improvement: string[];
  suggestions: string[];
}

export interface PredictionExplanationRequest {
  prediction_data: Record<string, any>;
  user_friendly?: boolean;
}

export interface PredictionExplanationResponse {
  explanation: string;
}

export interface GeminiStatus {
  available: boolean;
  model?: string;
}

class GeminiService {
  /**
   * Generate personalized health insights
   */
  async generateHealthInsights(
    request: HealthInsightsRequest
  ): Promise<HealthInsightsResponse> {
    try {
      const response = await api.post<HealthInsightsResponse>(
        '/gemini/health-insights',
        request
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 503) {
        // Service unavailable - return fallback
        return {
          insights: ['AI insights are currently unavailable. Please consult your healthcare provider.'],
          recommendations: ['Maintain regular cognitive activities', 'Stay physically active', 'Get adequate sleep'],
          warnings: ['This is a fallback response. For personalized insights, please try again later.'],
          next_steps: ['Consult with your healthcare provider for personalized recommendations']
        };
      }
      throw error;
    }
  }

  /**
   * Chat with the health assistant
   */
  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>('/gemini/chat', request);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 503) {
        return {
          response: "I'm currently unavailable. Please consult with your healthcare provider for medical advice."
        };
      }
      throw error;
    }
  }

  /**
   * Analyze cognitive assessment results
   */
  async analyzeAssessment(
    request: AssessmentAnalysisRequest
  ): Promise<AssessmentAnalysisResponse> {
    try {
      const response = await api.post<AssessmentAnalysisResponse>(
        '/gemini/analyze-assessment',
        request
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 503) {
        return {
          feedback: 'Assessment analysis is currently unavailable. Please consult your healthcare provider.',
          strengths: [],
          areas_for_improvement: [],
          suggestions: []
        };
      }
      throw error;
    }
  }

  /**
   * Get plain-language explanation of ML prediction
   */
  async explainPrediction(
    request: PredictionExplanationRequest
  ): Promise<PredictionExplanationResponse> {
    try {
      const response = await api.post<PredictionExplanationResponse>(
        '/gemini/explain-prediction',
        request
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 503) {
        return {
          explanation: 'Prediction explanation is currently unavailable. Please consult your healthcare provider.'
        };
      }
      throw error;
    }
  }

  /**
   * Check Gemini AI service status
   */
  async getStatus(): Promise<GeminiStatus> {
    try {
      const response = await api.get<GeminiStatus>('/gemini/status');
      return response.data;
    } catch (error) {
      return { available: false };
    }
  }
}

export default new GeminiService();
