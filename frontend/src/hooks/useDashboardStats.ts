import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

interface DashboardStats {
  cognitiveScore: number | null;
  riskLevel: string | null;
  activeDays: number;
  goalsCompleted: number;
  goalsTotal: number;
}

/**
 * Hook to fetch real dashboard statistics
 * Fetches data from multiple endpoints and aggregates them
 */
export function useDashboardStats(userId?: string) {
  return useQuery({
    queryKey: ['dashboardStats', userId],
    queryFn: async (): Promise<DashboardStats> => {
      if (!userId) {
        return {
          cognitiveScore: null,
          riskLevel: null,
          activeDays: 0,
          goalsCompleted: 0,
          goalsTotal: 0
        };
      }

      try {
        let cognitiveScore = null;
        let riskLevel = null;
        let activeDays = 0;
        let goalsCompleted = 0;
        let goalsTotal = 0;

        // Fetch latest assessment for cognitive score
        try {
          const assessmentsResponse = await api.get('/assessments', {
            params: { limit: 1, sort: '-created_at' }
          });
          const latestAssessment = assessmentsResponse.data.assessments?.[0];
          cognitiveScore = latestAssessment?.total_score || null;
        } catch (err) {
          console.log('Could not fetch assessments:', err);
        }

        // Fetch latest prediction for risk level
        try {
          const predictionsResponse = await api.get(`/ml/predictions/${userId}`);
          const predictions = predictionsResponse.data.predictions || [];
          if (predictions.length > 0) {
            const latestPrediction = predictions.sort((a: any, b: any) => 
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            )[0];
            riskLevel = latestPrediction.risk_category || null;
          }
        } catch (err) {
          console.log('Could not fetch predictions:', err);
        }

        // Fetch exercise sessions for active days (last 30 days)
        try {
          const thirtyDaysAgo = new Date();
          thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
          const exercisesResponse = await api.get('/exercises/sessions', {
            params: { 
              start_date: thirtyDaysAgo.toISOString(),
              limit: 100
            }
          });
          const sessions = exercisesResponse.data.sessions || [];
          const uniqueDays = new Set(
            sessions.map((s: any) => new Date(s.created_at).toDateString())
          );
          activeDays = uniqueDays.size;
        } catch (err) {
          console.log('Could not fetch exercise sessions:', err);
        }

        // Fetch recommendations for goals
        try {
          const recommendationsResponse = await api.get('/recommendations');
          const recommendations = recommendationsResponse.data.recommendations || [];
          const completedRecs = recommendations.filter((r: any) => r.status === 'completed');
          goalsCompleted = completedRecs.length;
          goalsTotal = recommendations.length;
        } catch (err) {
          console.log('Could not fetch recommendations:', err);
        }

        return {
          cognitiveScore,
          riskLevel,
          activeDays,
          goalsCompleted,
          goalsTotal
        };
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        // Return empty stats on error
        return {
          cognitiveScore: null,
          riskLevel: null,
          activeDays: 0,
          goalsCompleted: 0,
          goalsTotal: 0
        };
      }
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000 // Refetch every 5 minutes
  });
}
