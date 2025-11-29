/**
 * Provider Dashboard Component
 * Main dashboard for healthcare providers to view patient data
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  getPatientDashboard,
  PatientDashboardData,
} from '../../services/providerService';
import { Activity, Brain, Pill, TrendingUp, Calendar, AlertCircle } from 'lucide-react';
import ClinicalNotes from './ClinicalNotes';
import ReportGenerator from './ReportGenerator';

const ProviderDashboard: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<PatientDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (patientId) {
      loadDashboardData();
    }
  }, [patientId]);

  const loadDashboardData = async () => {
    if (!patientId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await getPatientDashboard(patientId);
      setDashboardData(data);
    } catch (err: any) {
      console.error('Error loading patient dashboard:', err);
      setError(err.response?.data?.detail || 'Failed to load patient data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading patient data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="bg-red-500/20 border border-red-500 rounded-lg p-6 max-w-md">
          <div className="flex items-center gap-3 text-red-400">
            <AlertCircle className="w-6 h-6" />
            <div>
              <h3 className="font-semibold">Error</h3>
              <p className="text-sm">{error}</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/provider/patients')}
            className="mt-4 w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg transition-colors"
          >
            Back to Patients
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { patient, health_overview, recent_assessments, recent_health_metrics, active_medications, recent_predictions } = dashboardData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/provider/patients')}
            className="text-purple-400 hover:text-purple-300 mb-4 flex items-center gap-2"
          >
            ← Back to Patients
          </button>
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h1 className="text-3xl font-bold text-white mb-2">{patient.name}</h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300">
              <div>
                <span className="text-gray-400">Email:</span> {patient.email}
              </div>
              <div>
                <span className="text-gray-400">Date of Birth:</span>{' '}
                {patient.date_of_birth
                  ? new Date(patient.date_of_birth).toLocaleDateString()
                  : 'Not provided'}
              </div>
              <div>
                <span className="text-gray-400">APOE Genotype:</span>{' '}
                {patient.apoe_genotype || 'Not tested'}
              </div>
            </div>
          </div>
        </div>

        {/* Health Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Cognitive Scores */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="w-8 h-8 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Cognitive Status</h3>
            </div>
            <div className="space-y-2">
              {health_overview.latest_mmse_score !== null && (
                <div>
                  <div className="text-sm text-gray-400">MMSE Score</div>
                  <div className="text-2xl font-bold text-white">
                    {health_overview.latest_mmse_score}/30
                  </div>
                </div>
              )}
              {health_overview.latest_moca_score !== null && (
                <div>
                  <div className="text-sm text-gray-400">MoCA Score</div>
                  <div className="text-2xl font-bold text-white">
                    {health_overview.latest_moca_score}/30
                  </div>
                </div>
              )}
              {health_overview.latest_mmse_score === null && health_overview.latest_moca_score === null && (
                <div className="text-gray-400">No assessments yet</div>
              )}
            </div>
          </div>

          {/* Risk Score */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-8 h-8 text-orange-400" />
              <h3 className="text-lg font-semibold text-white">Risk Assessment</h3>
            </div>
            {health_overview.latest_risk_score !== null ? (
              <div>
                <div className="text-sm text-gray-400">Risk Score</div>
                <div className="text-2xl font-bold text-white">
                  {(health_overview.latest_risk_score * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Last updated:{' '}
                  {health_overview.last_prediction_date
                    ? new Date(health_overview.last_prediction_date).toLocaleDateString()
                    : 'N/A'}
                </div>
              </div>
            ) : (
              <div className="text-gray-400">No predictions yet</div>
            )}
          </div>

          {/* Medication Adherence */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <div className="flex items-center gap-3 mb-4">
              <Pill className="w-8 h-8 text-green-400" />
              <h3 className="text-lg font-semibold text-white">Medication</h3>
            </div>
            {health_overview.medication_adherence_rate !== null ? (
              <div>
                <div className="text-sm text-gray-400">Adherence Rate</div>
                <div className="text-2xl font-bold text-white">
                  {health_overview.medication_adherence_rate.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {active_medications.length} active medication(s)
                </div>
              </div>
            ) : (
              <div className="text-gray-400">No medications tracked</div>
            )}
          </div>

          {/* Last Activity */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="w-8 h-8 text-blue-400" />
              <h3 className="text-lg font-semibold text-white">Activity</h3>
            </div>
            <div>
              <div className="text-sm text-gray-400">Last Active</div>
              <div className="text-lg font-semibold text-white">
                {new Date(patient.last_active).toLocaleDateString()}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {new Date(patient.last_active).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>

        {/* Recent Data Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Assessments */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Recent Assessments
            </h3>
            {recent_assessments.length > 0 ? (
              <div className="space-y-3">
                {recent_assessments.map((assessment) => (
                  <div
                    key={assessment.id}
                    className="bg-white/5 rounded-lg p-4 border border-white/10"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="font-semibold text-white">{assessment.test_type}</div>
                      <div className="text-sm text-gray-400">
                        {new Date(assessment.completed_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-purple-400">
                      {assessment.total_score}/{assessment.max_score}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400 text-center py-8">No assessments recorded</div>
            )}
          </div>

          {/* Active Medications */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Pill className="w-5 h-5" />
              Active Medications
            </h3>
            {active_medications.length > 0 ? (
              <div className="space-y-3">
                {active_medications.map((medication) => (
                  <div
                    key={medication.id}
                    className="bg-white/5 rounded-lg p-4 border border-white/10"
                  >
                    <div className="font-semibold text-white mb-1">{medication.name}</div>
                    <div className="text-sm text-gray-400">
                      {medication.dosage} - {medication.frequency}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400 text-center py-8">No active medications</div>
            )}
          </div>

          {/* Recent Health Metrics */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Recent Health Metrics
            </h3>
            {recent_health_metrics.length > 0 ? (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {recent_health_metrics.map((metric) => (
                  <div
                    key={metric.id}
                    className="bg-white/5 rounded-lg p-3 border border-white/10 flex justify-between items-center"
                  >
                    <div>
                      <div className="text-sm font-medium text-white">{metric.metric_name}</div>
                      <div className="text-xs text-gray-400">
                        {new Date(metric.recorded_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-lg font-semibold text-purple-400">
                      {metric.value} {metric.unit}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400 text-center py-8">No health metrics recorded</div>
            )}
          </div>

          {/* Recent Predictions */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Risk Predictions
            </h3>
            {recent_predictions.length > 0 ? (
              <div className="space-y-3">
                {recent_predictions.map((prediction) => (
                  <div
                    key={prediction.id}
                    className="bg-white/5 rounded-lg p-4 border border-white/10"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="text-sm text-gray-400">
                        {new Date(prediction.created_at).toLocaleDateString()}
                      </div>
                      <div className="px-2 py-1 rounded text-xs font-semibold bg-orange-500/20 text-orange-400">
                        {prediction.risk_category}
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {(prediction.risk_score * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400 text-center py-8">No predictions available</div>
            )}
          </div>
        </div>

        {/* Report Generator Section */}
        <div className="mt-6">
          <ReportGenerator patientId={patientId || ''} patientName={patient.name} />
        </div>

        {/* Clinical Notes Section */}
        <div className="mt-6">
          <ClinicalNotes patientId={patientId || ''} />
        </div>
      </div>
    </div>
  );
};

export default ProviderDashboard;
