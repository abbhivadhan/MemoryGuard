import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { medicationService } from '../../services/medicationService';
import { useAuthStore } from '../../store/authStore';

interface AdherenceAlert {
  medication_id: string;
  medication_name: string;
  adherence_rate: number;
  alert_level: 'warning' | 'critical';
}

interface AlertCheckResult {
  user_id: string;
  should_alert: boolean;
  low_adherence_medications: AdherenceAlert[];
  checked_at: string;
}

const CaregiverAlerts: React.FC = () => {
  const [alertData, setAlertData] = useState<AlertCheckResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    checkAdherence();

    // Set up auto-refresh every 5 minutes if enabled
    let interval: number | null = null;
    if (autoRefresh) {
      interval = window.setInterval(() => {
        checkAdherence();
      }, 5 * 60 * 1000); // 5 minutes
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const checkAdherence = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      const result = await medicationService.checkAdherenceAlert(user.id);
      setAlertData(result);
    } catch (error) {
      console.error('Failed to check adherence:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAlertColorClass = (level: string) => {
    switch (level) {
      case 'critical':
        return 'bg-red-100 border-red-500 text-red-800';
      case 'warning':
        return 'bg-yellow-100 border-yellow-500 text-yellow-800';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-800';
    }
  };

  const getAlertIcon = (level: string) => {
    switch (level) {
      case 'critical':
        return '🚨';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const sendCaregiverNotification = async (alertData: AdherenceAlert) => {
    // In a real implementation, this would send an email/SMS to caregivers
    // For now, we'll just show a confirmation
    const message = `Alert: ${alertData.medication_name} adherence is ${alertData.adherence_rate.toFixed(
      1
    )}% (${alertData.alert_level} level). Patient may need assistance with medication management.`;

    if (
      window.confirm(
        `Send this alert to caregivers?\n\n${message}\n\nNote: In production, this would send via email/SMS.`
      )
    ) {
      window.alert('Alert notification sent to caregivers (simulated)');
    }
  };

  if (loading && !alertData) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-800 mb-2">Caregiver Alerts</h2>
          <p className="text-gray-600">Monitor medication adherence and send alerts to caregivers</p>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            Auto-refresh (5 min)
          </label>
          <button
            onClick={checkAdherence}
            disabled={loading}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            {loading ? 'Checking...' : 'Check Now'}
          </button>
        </div>
      </div>

      {alertData && (
        <>
          {/* Alert status summary */}
          <div
            className={`rounded-lg shadow-md p-6 mb-6 ${
              alertData.should_alert ? 'bg-red-50 border-2 border-red-500' : 'bg-green-50 border-2 border-green-500'
            }`}
          >
            <div className="flex items-center gap-4">
              <div className="text-6xl">
                {alertData.should_alert ? '🚨' : '✅'}
              </div>
              <div className="flex-1">
                <h3
                  className={`text-2xl font-bold mb-2 ${
                    alertData.should_alert ? 'text-red-800' : 'text-green-800'
                  }`}
                >
                  {alertData.should_alert
                    ? 'Adherence Alert Detected'
                    : 'All Medications On Track'}
                </h3>
                <p
                  className={`text-sm ${
                    alertData.should_alert ? 'text-red-700' : 'text-green-700'
                  }`}
                >
                  {alertData.should_alert
                    ? `${alertData.low_adherence_medications.length} medication${
                        alertData.low_adherence_medications.length !== 1 ? 's' : ''
                      } with low adherence detected`
                    : 'All medications are being taken as prescribed'}
                </p>
                <p className="text-xs text-gray-600 mt-2">
                  Last checked: {formatDateTime(alertData.checked_at)}
                </p>
              </div>
            </div>
          </div>

          {/* Low adherence medications */}
          {alertData.should_alert && alertData.low_adherence_medications.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Medications Requiring Attention
              </h3>
              <div className="space-y-4">
                <AnimatePresence>
                  {alertData.low_adherence_medications.map((alert) => (
                    <motion.div
                      key={alert.medication_id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className={`border-l-4 rounded-lg p-4 ${getAlertColorClass(alert.alert_level)}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          <span className="text-3xl">{getAlertIcon(alert.alert_level)}</span>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-semibold text-lg">{alert.medication_name}</h4>
                              <span className="px-2 py-1 rounded text-xs font-bold uppercase">
                                {alert.alert_level}
                              </span>
                            </div>
                            <div className="space-y-2">
                              <div>
                                <p className="text-sm font-medium">Adherence Rate:</p>
                                <div className="flex items-center gap-2 mt-1">
                                  <div className="flex-1 bg-white rounded-full h-4 overflow-hidden">
                                    <div
                                      className={`h-full transition-all ${
                                        alert.adherence_rate >= 80
                                          ? 'bg-green-500'
                                          : alert.adherence_rate >= 50
                                          ? 'bg-yellow-500'
                                          : 'bg-red-500'
                                      }`}
                                      style={{ width: `${alert.adherence_rate}%` }}
                                    />
                                  </div>
                                  <span className="text-sm font-bold">
                                    {alert.adherence_rate.toFixed(1)}%
                                  </span>
                                </div>
                              </div>
                              <div className="bg-white bg-opacity-50 rounded p-3">
                                <p className="text-sm">
                                  <strong>Recommendation:</strong>{' '}
                                  {alert.alert_level === 'critical'
                                    ? 'Immediate caregiver intervention recommended. Adherence is critically low.'
                                    : 'Caregiver should check in with patient about medication routine.'}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => sendCaregiverNotification(alert)}
                          className="ml-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium whitespace-nowrap"
                        >
                          Send Alert
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          )}

          {/* Alert criteria information */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">Alert Criteria</h3>
            <div className="space-y-2 text-sm text-blue-800">
              <p>
                Caregiver alerts are triggered when medication adherence falls below certain
                thresholds over the past 7 days:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>
                  <strong>Critical Alert:</strong> Adherence below 50% - Immediate attention needed
                </li>
                <li>
                  <strong>Warning Alert:</strong> Adherence between 50-80% - Monitoring recommended
                </li>
                <li>
                  <strong>Good Adherence:</strong> Adherence 80% or above - No alert needed
                </li>
              </ul>
              <p className="mt-3">
                <strong>Note:</strong> Alerts can be sent to designated caregivers via email or SMS
                (when configured). Regular monitoring helps ensure patients receive their
                medications as prescribed.
              </p>
            </div>
          </div>

          {/* Caregiver contact information (placeholder) */}
          <div className="bg-white rounded-lg shadow-md p-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Caregiver Contact Information
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Configure caregiver contacts to receive automatic alerts when adherence issues are
              detected.
            </p>
            <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
              Manage Caregivers
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default CaregiverAlerts;
