import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { medicationService, Medication, AdherenceLogEntry } from '../../services/medicationService';

interface MedicationLogEditorProps {
  patientId?: string;
}

const MedicationLogEditor: React.FC<MedicationLogEditorProps> = ({ patientId }) => {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [selectedMed, setSelectedMed] = useState<Medication | null>(null);
  const [editingLog, setEditingLog] = useState<{ index: number; log: AdherenceLogEntry } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMedications();
  }, [patientId]);

  const loadMedications = async () => {
    try {
      setLoading(true);
      const data = await medicationService.getMedications(true);
      setMedications(data.medications);
    } catch (error) {
      console.error('Failed to load medications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditLog = (med: Medication, index: number) => {
    setSelectedMed(med);
    setEditingLog({
      index,
      log: { ...med.adherence_log[index] },
    });
  };

  const handleSaveLog = async () => {
    if (!selectedMed || editingLog === null) return;

    try {
      // Update the adherence log
      const updatedLogs = [...selectedMed.adherence_log];
      updatedLogs[editingLog.index] = editingLog.log;

      // Update medication with new logs
      await medicationService.updateMedication(selectedMed.id, {
        // We need to send the entire adherence_log array
        // This requires a backend endpoint that accepts adherence_log updates
      });

      // For now, we'll re-log the medication with corrected data
      await medicationService.logMedication(selectedMed.id, {
        scheduled_time: editingLog.log.scheduled_time,
        taken_time: editingLog.log.taken_time,
        skipped: editingLog.log.skipped,
        notes: editingLog.log.notes || 'Edited by caregiver',
      });

      setEditingLog(null);
      setSelectedMed(null);
      loadMedications();
    } catch (error) {
      console.error('Failed to update log:', error);
      alert('Failed to update medication log. Please try again.');
    }
  };

  const handleDeleteLog = async (_med: Medication, _index: number) => {
    if (!window.confirm('Are you sure you want to delete this log entry?')) return;

    try {
      // This would require a backend endpoint to delete specific log entries
      // For now, we'll show an alert
      alert('Log deletion requires backend support. Please contact system administrator.');
    } catch (error) {
      console.error('Failed to delete log:', error);
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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Medication Log Editor</h2>
        <p className="text-gray-400">Review and edit patient medication adherence logs</p>
      </div>

      <div className="space-y-4">
        {medications.length === 0 ? (
          <div className="text-center py-12 backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg">
            <p className="text-xl mb-2 text-white">No medications found</p>
            <p className="text-sm text-gray-400">Patient has no active medications</p>
          </div>
        ) : (
          medications.map((med) => (
            <div
              key={med.id}
              className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white">{med.name}</h3>
                  <p className="text-gray-400 text-sm">
                    {med.dosage} • {med.frequency}
                  </p>
                </div>
                <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-sm">
                  {med.adherence_log?.length || 0} logs
                </span>
              </div>

              {med.adherence_log && med.adherence_log.length > 0 ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-white mb-2">Adherence Logs</p>
                  {med.adherence_log.slice().reverse().map((log, idx) => {
                    const actualIndex = med.adherence_log.length - 1 - idx;
                    return (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-white/5 border border-white/10 rounded-lg"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="text-gray-300 text-sm">
                              Scheduled: {formatDateTime(log.scheduled_time)}
                            </span>
                            {log.taken_time && (
                              <span className="text-gray-400 text-xs">
                                Taken: {formatDateTime(log.taken_time)}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-1 rounded text-xs font-medium ${
                                log.skipped
                                  ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                                  : 'bg-green-500/20 text-green-300 border border-green-500/30'
                              }`}
                            >
                              {log.skipped ? 'Skipped' : 'Taken'}
                            </span>
                            {log.notes && (
                              <span className="text-xs text-gray-400">Note: {log.notes}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEditLog(med, actualIndex)}
                            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-sm"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteLog(med, actualIndex)}
                            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-gray-400 text-sm">No adherence logs yet</p>
              )}
            </div>
          ))
        )}
      </div>

      {/* Edit Log Modal */}
      <AnimatePresence>
        {editingLog && selectedMed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setEditingLog(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="backdrop-blur-xl bg-gray-900 border border-white/20 rounded-lg shadow-xl p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold text-white mb-4">
                Edit Log: {selectedMed.name}
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Scheduled Time
                  </label>
                  <input
                    type="datetime-local"
                    value={editingLog.log.scheduled_time.slice(0, 16)}
                    onChange={(e) =>
                      setEditingLog({
                        ...editingLog,
                        log: {
                          ...editingLog.log,
                          scheduled_time: new Date(e.target.value).toISOString(),
                        },
                      })
                    }
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="edit-skipped"
                    checked={editingLog.log.skipped}
                    onChange={(e) =>
                      setEditingLog({
                        ...editingLog,
                        log: {
                          ...editingLog.log,
                          skipped: e.target.checked,
                          taken_time: e.target.checked ? undefined : editingLog.log.taken_time,
                        },
                      })
                    }
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="edit-skipped" className="text-sm font-medium text-gray-300">
                    Mark as skipped
                  </label>
                </div>

                {!editingLog.log.skipped && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Taken Time
                    </label>
                    <input
                      type="datetime-local"
                      value={editingLog.log.taken_time?.slice(0, 16) || ''}
                      onChange={(e) =>
                        setEditingLog({
                          ...editingLog,
                          log: {
                            ...editingLog.log,
                            taken_time: new Date(e.target.value).toISOString(),
                          },
                        })
                      }
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Notes
                  </label>
                  <textarea
                    value={editingLog.log.notes || ''}
                    onChange={(e) =>
                      setEditingLog({
                        ...editingLog,
                        log: {
                          ...editingLog.log,
                          notes: e.target.value,
                        },
                      })
                    }
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Add notes about this log entry..."
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <button
                  onClick={() => setEditingLog(null)}
                  className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveLog}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MedicationLogEditor;
