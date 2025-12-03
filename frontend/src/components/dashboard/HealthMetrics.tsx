import React, { useMemo, useState } from 'react';
import { HealthMetric } from '../../services/healthService';
import { useAuthStore } from '../../store/authStore';
import { useHealthMetrics } from '../../hooks/useHealthMetrics';
import BrainHealthVisualization from './BrainHealthVisualization';
import BiomarkerChart3D from './BiomarkerChart3D';
import ProgressionTimeline3D from './ProgressionTimeline3D';
import { Plus, X } from 'lucide-react';


interface MetricCategory {
  type: string;
  title: string;
  metrics: HealthMetric[];
  icon: string;
  color: string;
}

const HealthMetrics: React.FC = () => {
  const { user } = useAuthStore();
  const [showAddForm, setShowAddForm] = useState(false);

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
      <div className="space-y-6">
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
          <h3 className="text-xl font-semibold mb-3 text-white">No Health Metrics Yet</h3>
          <p className="text-gray-400 mb-6">
            Start tracking your cognitive health by adding your first health metric. Input real data from medical assessments, lab results, or health monitoring devices.
          </p>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors inline-flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add Medical Data
          </button>
        </div>
        
        {showAddForm && (
          <AddMetricForm 
            onClose={() => setShowAddForm(false)} 
            onSuccess={() => {
              setShowAddForm(false);
              refetch();
            }}
          />
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh controls */}
      <div className="flex items-center justify-between flex-wrap gap-4">
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
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors text-sm flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Data
          </button>
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className={`px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors text-sm flex items-center gap-2 ${
              isFetching ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <span className={isFetching ? 'animate-spin' : ''}>⟳</span>
            {isFetching ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Add Metric Form */}
      {showAddForm && (
        <AddMetricForm 
          onClose={() => setShowAddForm(false)} 
          onSuccess={() => {
            setShowAddForm(false);
            refetch();
          }}
        />
      )}

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
            View all {sortedMetrics.length} metrics
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
          {formattedDate} | {metric.source}
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

// Add Metric Form Component
interface AddMetricFormProps {
  onClose: () => void;
  onSuccess: () => void;
}

const AddMetricForm: React.FC<AddMetricFormProps> = ({ onClose, onSuccess }) => {
  const { user } = useAuthStore();
  const [formData, setFormData] = useState({
    type: 'biomarker',
    name: '',
    value: '',
    unit: '',
    source: 'manual',
    notes: '',
    timestamp: new Date().toISOString().split('T')[0]
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const metricTypes = [
    { value: 'cognitive', label: 'Cognitive Function' },
    { value: 'biomarker', label: 'Biomarker' },
    { value: 'imaging', label: 'Brain Imaging' },
    { value: 'lifestyle', label: 'Lifestyle Factor' },
    { value: 'cardiovascular', label: 'Cardiovascular Health' }
  ];

  const commonMetrics: Record<string, Array<{ name: string; unit: string }>> = {
    cognitive: [
      { name: 'MMSE Score', unit: 'points' },
      { name: 'MoCA Score', unit: 'points' },
      { name: 'Memory Test Score', unit: 'points' }
    ],
    biomarker: [
      { name: 'Amyloid Beta 42', unit: 'pg/mL' },
      { name: 'Tau Protein', unit: 'pg/mL' },
      { name: 'P-Tau 181', unit: 'pg/mL' },
      { name: 'Cholesterol', unit: 'mg/dL' },
      { name: 'Glucose', unit: 'mg/dL' }
    ],
    imaging: [
      { name: 'Hippocampal Volume', unit: 'mm³' },
      { name: 'Cortical Thickness', unit: 'mm' },
      { name: 'White Matter Lesions', unit: 'count' }
    ],
    lifestyle: [
      { name: 'Sleep Duration', unit: 'hours' },
      { name: 'Exercise Minutes', unit: 'minutes' },
      { name: 'Social Interaction', unit: 'hours' }
    ],
    cardiovascular: [
      { name: 'Blood Pressure Systolic', unit: 'mmHg' },
      { name: 'Blood Pressure Diastolic', unit: 'mmHg' },
      { name: 'Heart Rate', unit: 'bpm' }
    ]
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/health/metrics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          userId: user?.id,
          type: formData.type,
          name: formData.name,
          value: parseFloat(formData.value),
          unit: formData.unit,
          source: formData.source,
          notes: formData.notes || undefined,
          timestamp: new Date(formData.timestamp).toISOString()
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add metric');
      }

      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add metric');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMetricSelect = (metricName: string) => {
    const metric = commonMetrics[formData.type]?.find(m => m.name === metricName);
    if (metric) {
      setFormData(prev => ({
        ...prev,
        name: metric.name,
        unit: metric.unit
      }));
    }
  };

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white">Add Medical Data</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900/20 border border-red-500 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Metric Type */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Metric Type *
            </label>
            <select
              value={formData.type}
              onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value, name: '', unit: '' }))}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
              required
            >
              {metricTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          {/* Common Metrics Quick Select */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Quick Select
            </label>
            <select
              value=""
              onChange={(e) => handleMetricSelect(e.target.value)}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
            >
              <option value="">-- Select a common metric --</option>
              {commonMetrics[formData.type]?.map(metric => (
                <option key={metric.name} value={metric.name}>{metric.name}</option>
              ))}
            </select>
          </div>

          {/* Metric Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Metric Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., MMSE Score"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
              required
            />
          </div>

          {/* Value */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Value *
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.value}
              onChange={(e) => setFormData(prev => ({ ...prev, value: e.target.value }))}
              placeholder="e.g., 28"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
              required
            />
          </div>

          {/* Unit */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Unit *
            </label>
            <input
              type="text"
              value={formData.unit}
              onChange={(e) => setFormData(prev => ({ ...prev, unit: e.target.value }))}
              placeholder="e.g., points, mg/dL"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
              required
            />
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Date *
            </label>
            <input
              type="date"
              value={formData.timestamp}
              onChange={(e) => setFormData(prev => ({ ...prev, timestamp: e.target.value }))}
              max={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
              required
            />
          </div>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Notes (Optional)
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
            placeholder="Add any additional context or notes..."
            rows={3}
            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500 resize-none"
          />
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-3 justify-end pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Adding...' : 'Add Metric'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default HealthMetrics;
