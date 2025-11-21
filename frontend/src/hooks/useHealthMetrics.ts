import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { healthService, HealthMetric } from '../services/healthService';

export const useHealthMetrics = (userId: string | undefined) => {
  const queryClient = useQueryClient();

  // Fetch health metrics
  const query = useQuery({
    queryKey: ['healthMetrics', userId],
    queryFn: () => healthService.getHealthMetrics(userId!),
    enabled: !!userId,
    refetchInterval: 30000, // Auto-refresh every 30 seconds
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    staleTime: 10000, // Consider data stale after 10 seconds
  });

  // Add health metric mutation
  const addMetric = useMutation({
    mutationFn: (metric: Omit<HealthMetric, 'id'>) =>
      healthService.addHealthMetric(metric),
    onMutate: async (newMetric) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['healthMetrics', userId] });

      // Snapshot previous value
      const previousMetrics = queryClient.getQueryData(['healthMetrics', userId]);

      // Optimistically update
      queryClient.setQueryData(['healthMetrics', userId], (old: any) => {
        if (!old) return old;
        return {
          ...old,
          metrics: [
            ...old.metrics,
            { ...newMetric, id: `temp-${Date.now()}` },
          ],
          total: old.total + 1,
        };
      });

      return { previousMetrics };
    },
    onError: (_err, _newMetric, context) => {
      // Rollback on error
      if (context?.previousMetrics) {
        queryClient.setQueryData(['healthMetrics', userId], context.previousMetrics);
      }
    },
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['healthMetrics', userId] });
    },
  });

  // Update health metric mutation
  const updateMetric = useMutation({
    mutationFn: ({ id, metric }: { id: string; metric: Partial<HealthMetric> }) =>
      healthService.updateHealthMetric(id, metric),
    onMutate: async ({ id, metric }) => {
      await queryClient.cancelQueries({ queryKey: ['healthMetrics', userId] });

      const previousMetrics = queryClient.getQueryData(['healthMetrics', userId]);

      queryClient.setQueryData(['healthMetrics', userId], (old: any) => {
        if (!old) return old;
        return {
          ...old,
          metrics: old.metrics.map((m: HealthMetric) =>
            m.id === id ? { ...m, ...metric } : m
          ),
        };
      });

      return { previousMetrics };
    },
    onError: (_err, _variables, context) => {
      if (context?.previousMetrics) {
        queryClient.setQueryData(['healthMetrics', userId], context.previousMetrics);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['healthMetrics', userId] });
    },
  });

  // Delete health metric mutation
  const deleteMetric = useMutation({
    mutationFn: (id: string) => healthService.deleteHealthMetric(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['healthMetrics', userId] });

      const previousMetrics = queryClient.getQueryData(['healthMetrics', userId]);

      queryClient.setQueryData(['healthMetrics', userId], (old: any) => {
        if (!old) return old;
        return {
          ...old,
          metrics: old.metrics.filter((m: HealthMetric) => m.id !== id),
          total: old.total - 1,
        };
      });

      return { previousMetrics };
    },
    onError: (_err, _id, context) => {
      if (context?.previousMetrics) {
        queryClient.setQueryData(['healthMetrics', userId], context.previousMetrics);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['healthMetrics', userId] });
    },
  });

  return {
    ...query,
    addMetric,
    updateMetric,
    deleteMetric,
  };
};
