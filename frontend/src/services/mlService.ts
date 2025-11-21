import apiClient from './api';

export interface PredictionResponse {
  id: number;
  user_id: number;
  prediction: number | null;
  probability: number | null;
  confidence_score: number | null;
  confidence_interval_lower: number | null;
  confidence_interval_upper: number | null;
  risk_level: string | null;
  model_version: string | null;
  status: string;
  created_at: string;
  completed_at: string | null;
  metadata: Record<string, any> | null;
  message: string | null;
}

export interface ExplanationResponse {
  prediction_id: number;
  top_features: Array<{ feature: string; shap_value: number }>;
  positive_contributors: Array<{ feature: string; contribution: number }>;
  negative_contributors: Array<{ feature: string; contribution: number }>;
  explanation_text: string;
  shap_values: Record<string, number> | null;
}

export interface ForecastResponse {
  user_id: number;
  forecasts: Record<string, {
    metrics: Record<string, number>;
    risk_score: number;
  }>;
  progression_rates: Record<string, number>;
  confidence_level: number;
  generated_at: string;
}

export interface PredictionRequest {
  user_id?: number;
  health_metrics?: Record<string, number>;
}

export interface ForecastRequest {
  user_id?: number;
  current_metrics: Record<string, number>;
  forecast_months?: number[];
}

class MLService {
  /**
   * Create a new prediction
   */
  async createPrediction(data: PredictionRequest): Promise<PredictionResponse> {
    const response = await apiClient.post('/ml/predict', data);
    return response.data;
  }

  /**
   * Get predictions for a user
   */
  async getUserPredictions(userId: number): Promise<PredictionResponse[]> {
    const response = await apiClient.get(`/ml/predictions/${userId}`);
    return response.data.predictions || [];
  }

  /**
   * Get the latest prediction for a user
   */
  async getLatestPrediction(userId: number): Promise<PredictionResponse | null> {
    const predictions = await this.getUserPredictions(userId);
    if (predictions.length === 0) return null;
    
    // Sort by created_at descending and return the first one
    return predictions.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )[0];
  }

  /**
   * Get explanation for a prediction
   */
  async getExplanation(predictionId: number): Promise<ExplanationResponse> {
    const response = await apiClient.get(`/ml/explain/${predictionId}`);
    return response.data;
  }

  /**
   * Get progression forecast
   */
  async getForecast(data: ForecastRequest): Promise<ForecastResponse> {
    const response = await apiClient.post('/ml/forecast', data);
    return response.data;
  }
}

export const mlService = new MLService();
export default mlService;
