import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  medicationService,
  Medication,
  AdherenceStats,
  MedicationLogRequest,
} from '../../services/medicationService';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface MedicationWithStats extends Medication {
  stats?: AdherenceStats;
}

const AdherenceTracker: React.FC = () => {
  const [medications, setMedications] = useState<MedicationWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(7);
  const [showLogModal, setShowLogModal] = useState(false);
  const [selectedMed, setSelectedMed] = useState<Medication | null>(null);
  const [logData, setLogData] = useState<MedicationLogRequest>({
    scheduled_time: new Date().toISOString(),
    taken_time: undefined,
    skipped: false,
    notes: '',
  });

  useEffect(() => {
    loadMedicationsWithStats();
  }, [selectedPeriod]);

  const loadMedicationsWithStats = async () => {
    try {
      setLoading(true);
      const data = await medicationService.getMedications(true);
      
      // Load adherence stats for each medication
      const medsWithStats = await Promise.all(
        data.medications.map(async (med) => {
          try {
            const stats = await medicationService.getAdherenceStats(med.id, selectedPeriod);
            return { ...med, stats };
          } catch (error) {
            console.error(`Failed to load stats for ${med.name}:`, error);
            return med;
          }
        })
      );

      setMedications(medsWithStats);
    } catch (error) {
      console.error('Failed to load medications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogMedication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMed) return;

    try {
      await medicationService.logMedication(selectedMed.id, logData);
      setShowLogModal(false);
      setSelectedMed(null);
      setLogData({
        scheduled_time: new Date().toISOString(),
        taken_time: undefined,
        skipped: false,
        notes: '',
      });
      loadMedicationsWithStats();
    } catch (error) {
      console.error('Failed to log medication:', error);
      alert('Failed to log medication. Please try again.');
    }
  };

  const openLogModal = (med: Medication) => {
    setSelectedMed(med);
    setLogData({
      scheduled_time: new Date().toISOString(),
      taken_time: new Date().toISOString(),
      skipped: false,
      notes: '',
    });
    setShowLogModal(true);
  };

  const getAdherenceColor = (rate: number) => {
    if (rate >= 90) return 'text-green-600 bg-green-100';
    if (rate >= 80) return 'text-yellow-600 bg-yellow-100';
    if (rate >= 70) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getAdherenceLabel = (rate: number) => {
    if (rate >= 90) return 'Excellent';
    if (rate >= 80) return 'Good';
    if (rate >= 70) return 'Fair';
    return 'Needs Attention';
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

  const calculateOverallAdherence = () => {
    const medsWithStats = medications.filter((m) => m.stats);
    if (medsWithStats.length === 0) return 0;

    const totalRate = medsWithStats.reduce((sum, m) => sum + (m.stats?.adherence_rate || 0), 0);
    return totalRate / medsWithStats.length;
  };

  const getAdherenceTrendData = () => {
    // Generate trend data for the last N days
    const days = [];
    const rates = [];

    for (let i = selectedPeriod - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

      // Calculate adherence for this day (simplified)
      const dayRate = Math.random() * 20 + 75; // Placeholder - should calculate from actual data
      rates.push(dayRate);
    }

    return {
      labels: days,
      datasets: [
        {
          label: 'Adherence Rate (%)',
          data: rates,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: `Adherence Trend (Last ${selectedPeriod} Days)`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value: any) => `${value}%`,
        },
      },
    },
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const overallAdherence = calculateOverallAdherence();

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Medication Adherence</h2>
        <select
          value={selectedPeriod}
          onChange={(e) => setSelectedPeriod(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value={7}>Last 7 Days</option>
          <option value={14}>Last 14 Days</option>
          <option value={30}>Last 30 Days</option>
          <option value={90}>Last 90 Days</option>
        </select>
      </div>

      {/* Overall adherence summary */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Overall Adherence</h3>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-5xl font-bold text-gray-800 mb-2">
              {overallAdherence.toFixed(1)}%
            </div>
            <div
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getAdherenceColor(
                overallAdherence
              )}`}
            >
              {getAdherenceLabel(overallAdherence)}
            </div>
          </div>
          <div className="text-right text-sm text-gray-600">
            <p>
              {medications.filter((m) => m.stats && m.stats.adherence_rate >= 80).length} of{' '}
              {medications.length} medications
            </p>
            <p>meeting adherence goal (≥80%)</p>
          </div>
        </div>
      </div>

      {/* Adherence trend chart */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <Line data={getAdherenceTrendData()} options={chartOptions} />
      </div>

      {/* Individual medication adherence */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-800">Medication Details</h3>
        <AnimatePresence>
          {medications.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12 text-gray-500 bg-white rounded-lg shadow-md"
            >
              <p className="text-xl mb-2">No active medications</p>
              <p className="text-sm">Add medications to track adherence</p>
            </motion.div>
          ) : (
            medications.map((med) => (
              <motion.div
                key={med.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-lg shadow-md p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-lg font-semibold text-gray-800">{med.name}</h4>
                      {med.stats && (
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${getAdherenceColor(
                            med.stats.adherence_rate
                          )}`}
                        >
                          {med.stats.adherence_rate.toFixed(1)}%
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 text-sm">
                      {med.dosage} • {med.frequency}
                    </p>
                  </div>
                  <button
                    onClick={() => openLogModal(med)}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Log Dose
                  </button>
                </div>

                {med.stats && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200">
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Scheduled</p>
                      <p className="text-lg font-semibold text-gray-800">
                        {med.stats.total_scheduled}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Taken</p>
                      <p className="text-lg font-semibold text-green-600">
                        {med.stats.total_taken}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Skipped</p>
                      <p className="text-lg font-semibold text-red-600">
                        {med.stats.total_skipped}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Status</p>
                      <p className="text-sm font-medium text-gray-800">
                        {getAdherenceLabel(med.stats.adherence_rate)}
                      </p>
                    </div>
                  </div>
                )}

                {med.stats && (med.stats.last_taken || med.stats.next_scheduled) && (
                  <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600">
                    {med.stats.last_taken && (
                      <p>Last taken: {formatDateTime(med.stats.last_taken)}</p>
                    )}
                    {med.stats.next_scheduled && (
                      <p>Next scheduled: {formatDateTime(med.stats.next_scheduled)}</p>
                    )}
                  </div>
                )}

                {/* Recent adherence log */}
                {med.adherence_log && med.adherence_log.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Recent Activity</p>
                    <div className="space-y-2">
                      {med.adherence_log.slice(-5).reverse().map((log, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between text-sm py-2 px-3 bg-gray-50 rounded"
                        >
                          <span className="text-gray-600">
                            {formatDateTime(log.scheduled_time)}
                          </span>
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              log.skipped
                                ? 'bg-red-100 text-red-700'
                                : 'bg-green-100 text-green-700'
                            }`}
                          >
                            {log.skipped ? 'Skipped' : 'Taken'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Log medication modal */}
      <AnimatePresence>
        {showLogModal && selectedMed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowLogModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                Log Medication: {selectedMed.name}
              </h3>

              <form onSubmit={handleLogMedication} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scheduled Time
                  </label>
                  <input
                    type="datetime-local"
                    required
                    value={logData.scheduled_time.slice(0, 16)}
                    onChange={(e) =>
                      setLogData({ ...logData, scheduled_time: new Date(e.target.value).toISOString() })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="skipped"
                    checked={logData.skipped}
                    onChange={(e) =>
                      setLogData({
                        ...logData,
                        skipped: e.target.checked,
                        taken_time: e.target.checked ? undefined : new Date().toISOString(),
                      })
                    }
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="skipped" className="text-sm font-medium text-gray-700">
                    Mark as skipped
                  </label>
                </div>

                {!logData.skipped && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Taken Time
                    </label>
                    <input
                      type="datetime-local"
                      value={logData.taken_time?.slice(0, 16) || ''}
                      onChange={(e) =>
                        setLogData({ ...logData, taken_time: new Date(e.target.value).toISOString() })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes (optional)
                  </label>
                  <textarea
                    value={logData.notes}
                    onChange={(e) => setLogData({ ...logData, notes: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={2}
                    placeholder="Any notes about this dose..."
                  />
                </div>

                <div className="flex justify-end gap-2 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowLogModal(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Log Medication
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdherenceTracker;
