import React, { useMemo } from 'react';
import { HealthMetric } from '../../services/healthService';
import { useAuthStore } from '../../store/authStore';
import { useHealthMetrics } from '../../hooks/useHealthMetrics';
import BrainHealthVisualization from './BrainHealthVisualization';
import BiomarkerChart3D from './BiomarkerChart3D';
import ProgressionTimeline3D from './ProgressionTimeline3D';


interface MetricCategory {
  type: string;
  title: string;
  metrics: HealthMetric[];
  icon: string;
  color: string;
}

const HealthMetrics: React.FC = () => {
  const { user } = useAuthStore();

  // Use custom hook with real-time updates and optimistic mutations
  const { data, isLoading, error, refetch, isFetching } = useHealthMetrics(user?.id);

  const handleRefresh = () => {
    refetch();
  };

  // Group metrics by category
  const categorizedMetrics = useMemo<MetricCategory[]>(() => {
    if (!data?.metrics) return [];

    const categories: Record<string, MetricCategory> = {
      cognitive: {
        type: 'cognitive',
        title: 'Cognitive Function',
        metrics: [],
        icon: '',
        color: 'from-purple-500 to-pink-500',
      },
      biomarker: {
        type: 'biomarker',
        title: 'Biomarkers',
        metrics: [],
        icon: '',
        color: 'from-blue-500 to-cyan-500',
      },
      imaging: {
        type: 'imaging',
        title: 'Brain Imaging',
        metrics: [],
        icon: '',
        color: 'from-green-500 to-emerald-500',
      },
      lifestyle: {
        type: 'lifestyle',
        title: 'Lifestyle Factors',
        metrics: [],
        icon: '',
        color: 'from-orange-500 to-yellow-500',
      },
      cardiovascular: {
        type: 'cardiovascular',
        title: 'Cardiovascular Health',
        metrics: [],
        icon: '',
        color: 'from-red-500 to-rose-500',
      },
    };

    data.metrics.forEach((metric) => {
      if (categories[metric.type]) {
        categories[metric.type].metrics.push(metric);
      }
    });

    return Object.values(categories).filter((cat) => cat.metrics.length > 0);
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-6">
        <h3 className="text-red-400 font-semibold mb-2">Error Loading Health Metrics</h3>
        <p className="text-red-300 text-sm">
          {error instanceof Error ? error.message : 'Failed to load health metrics'}
        </p>
      </div>
    );
  }

  if (!data?.metrics || data.metrics.length === 0) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
        <h3 className="text-xl font-semibold mb-3 text-white">No Health Metrics Yet</h3>
        <p className="text-gray-400 mb-6">
          Start tracking your cognitive health by adding your first health metric. Input real data from medical assessments, lab results, or health monitoring devices.
        </p>
        <button
          onClick={() => console.log('Add health metric clicked')}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
        >
          Add Health Metric
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3">
            Health Metrics Dashboard
            {isFetching && (
              <span className="inline-block w-2 h-2 bg-purple-500 rounded-full animate-pulse"></span>
            )}
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Auto-refreshes every 30 seconds • Real-time updates enabled
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-400">
            Total Metrics: {data.metrics.length}
          </div>
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className={`px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors text-sm flex items-center gap-2 ${
              isFetching ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <span className={isFetching ? 'animate-spin' : ''}>↻</span>
            {isFetching ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* 3D Visualizations */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <BrainHealthVisualization metrics={data.metrics} />
        <BiomarkerChart3D metrics={data.metrics} />
      </div>

      {/* Progression Timeline */}
      <ProgressionTimeline3D metrics={data.metrics} />

      {/* Metrics by Category */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {categorizedMetrics.map((category) => (
          <MetricCategoryCard key={category.type} category={category} />
        ))}
      </div>
    </div>
  );
};

interface MetricCategoryCardProps {
  category: MetricCategory;
}

const MetricCategoryCard: React.FC<MetricCategoryCardProps> = ({ category }) => {
  // Sort metrics by timestamp (most recent first)
  const sortedMetrics = useMemo(() => {
    return [...category.metrics].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [category.metrics]);

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className={`bg-gradient-to-r ${category.color} p-4`}>
        <div>
          <h3 className="text-xl font-bold text-white">{category.title}</h3>
          <p className="text-white/80 text-sm">{category.metrics.length} metrics</p>
        </div>
      </div>

      {/* Metrics List */}
      <div className="p-4 space-y-3">
        {sortedMetrics.slice(0, 5).map((metric) => (
          <MetricItem key={metric.id} metric={metric} />
        ))}
        {sortedMetrics.length > 5 && (
          <button className="w-full text-center text-sm text-purple-400 hover:text-purple-300 py-2">
            View all {sortedMetrics.length} metrics →
          </button>
        )}
      </div>
    </div>
  );
};

interface MetricItemProps {
  metric: HealthMetric;
}

const MetricItem: React.FC<MetricItemProps> = ({ metric }) => {
  const formattedDate = useMemo(() => {
    const date = new Date(metric.timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }, [metric.timestamp]);

  return (
    <div className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg hover:bg-gray-900 transition-colors">
      <div className="flex-1">
        <div className="font-medium text-white">{metric.name}</div>
        <div className="text-xs text-gray-400 mt-1">
          {formattedDate} • {metric.source}
        </div>
      </div>
      <div className="text-right">
        <div className="text-lg font-bold text-white">
          {metric.value.toFixed(2)}
        </div>
        <div className="text-xs text-gray-400">{metric.unit}</div>
      </div>
    </div>
  );
};

export default HealthMetrics;
