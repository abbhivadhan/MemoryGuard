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
        // Fetch latest assessment for cognitive score
        const assessmentsResponse = await api.get('/assessments', {
          params: { limit: 1, sort: '-created_at' }
        });
        const latestAssessment = assessmentsResponse.data.assessments?.[0];
        const cognitiveScore = latestAssessment?.total_score || null;

        // Fetch risk prediction
        const riskResponse = await api.get('/ml/predict/risk');
        const riskLevel = riskResponse.data.risk_category || null;

        // Fetch exercise sessions for active days (last 30 days)
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
        const activeDays = uniqueDays.size;

        // Fetch recommendations for goals
        const recommendationsResponse = await api.get('/recommendations');
        const recommendations = recommendationsResponse.data.recommendations || [];
        const completedRecs = recommendations.filter((r: any) => r.status === 'completed');
        const goalsCompleted = completedRecs.length;
        const goalsTotal = recommendations.length;

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
