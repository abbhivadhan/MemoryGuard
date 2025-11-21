import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  medicationService,
  Medication,
  SideEffectCreate,
} from '../../services/medicationService';

const SideEffectsLogger: React.FC = () => {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedMed, setSelectedMed] = useState<Medication | null>(null);
  const [sideEffectData, setSideEffectData] = useState<SideEffectCreate>({
    side_effect: '',
    severity: undefined,
    occurred_at: undefined,
  });

  useEffect(() => {
    loadMedications();
  }, []);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMed) return;

    try {
      await medicationService.addSideEffect(selectedMed.id, sideEffectData);
      
      setSideEffectData({
        side_effect: '',
        severity: undefined,
        occurred_at: undefined,
      });
      setShowAddForm(false);
      setSelectedMed(null);
      loadMedications();
    } catch (error) {
      console.error('Failed to add side effect:', error);
      alert('Failed to add side effect. Please try again.');
    }
  };

  const openAddForm = (med: Medication) => {
    setSelectedMed(med);
    setSideEffectData({
      side_effect: '',
      severity: undefined,
      occurred_at: new Date().toISOString(),
    });
    setShowAddForm(true);
  };

  const parseSideEffect = (effect: string) => {
    // Parse the formatted side effect string
    // Format: "2024-01-15T10:30:00Z: Nausea (Severity: moderate)"
    const parts = effect.split(': ');
    if (parts.length < 2) return { date: '', description: effect, severity: '' };

    const date = new Date(parts[0]).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

    const descParts = parts[1].split(' (Severity: ');
    const description = descParts[0];
    const severity = descParts[1] ? descParts[1].replace(')', '') : '';

    return { date, description, severity };
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'mild':
        return 'bg-yellow-100 text-yellow-800';
      case 'moderate':
        return 'bg-orange-100 text-orange-800';
      case 'severe':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
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
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Side Effects Tracker</h2>
      </div>

      {/* Medications with side effects */}
      <div className="space-y-4">
        <AnimatePresence>
          {medications.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12 text-gray-500 bg-white rounded-lg shadow-md"
            >
              <p className="text-xl mb-2">No active medications</p>
              <p className="text-sm">Add medications to track side effects</p>
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
                      <span className="text-2xl">💊</span>
                      <h3 className="text-lg font-semibold text-gray-800">{med.name}</h3>
                      {med.side_effects && med.side_effects.length > 0 && (
                        <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-medium">
                          {med.side_effects.length} side effect{med.side_effects.length !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 text-sm">
                      {med.dosage} • {med.frequency}
                    </p>
                  </div>
                  <button
                    onClick={() => openAddForm(med)}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    + Add Side Effect
                  </button>
                </div>

                {/* Side effects list */}
                {med.side_effects && med.side_effects.length > 0 ? (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Reported Side Effects</h4>
                    <div className="space-y-2">
                      {med.side_effects.map((effect, idx) => {
                        const parsed = parseSideEffect(effect);
                        return (
                          <div
                            key={idx}
                            className="flex items-start justify-between p-3 bg-gray-50 rounded-lg"
                          >
                            <div className="flex-1">
                              <p className="text-gray-800 font-medium">{parsed.description}</p>
                              <p className="text-xs text-gray-500 mt-1">{parsed.date}</p>
                            </div>
                            {parsed.severity && (
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(
                                  parsed.severity
                                )}`}
                              >
                                {parsed.severity}
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="mt-4 pt-4 border-t border-gray-200 text-center text-gray-500 text-sm">
                    No side effects reported for this medication
                  </div>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Add side effect modal */}
      <AnimatePresence>
        {showAddForm && selectedMed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowAddForm(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                Report Side Effect: {selectedMed.name}
              </h3>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Side Effect Description *
                  </label>
                  <textarea
                    required
                    value={sideEffectData.side_effect}
                    onChange={(e) =>
                      setSideEffectData({ ...sideEffectData, side_effect: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Describe the side effect you experienced..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Severity
                  </label>
                  <select
                    value={sideEffectData.severity || ''}
                    onChange={(e) =>
                      setSideEffectData({
                        ...sideEffectData,
                        severity: e.target.value as 'mild' | 'moderate' | 'severe' | undefined,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select severity</option>
                    <option value="mild">Mild</option>
                    <option value="moderate">Moderate</option>
                    <option value="severe">Severe</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    When did it occur?
                  </label>
                  <input
                    type="datetime-local"
                    value={sideEffectData.occurred_at?.slice(0, 16) || ''}
                    onChange={(e) =>
                      setSideEffectData({
                        ...sideEffectData,
                        occurred_at: new Date(e.target.value).toISOString(),
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-4">
                  <p className="text-sm text-yellow-800">
                    <strong>Important:</strong> If you're experiencing severe side effects, contact
                    your healthcare provider immediately.
                  </p>
                </div>

                <div className="flex justify-end gap-2 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Report Side Effect
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Summary statistics */}
      <div className="mt-6 bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Side Effects Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-gray-800">
              {medications.reduce((sum, med) => sum + (med.side_effects?.length || 0), 0)}
            </p>
            <p className="text-sm text-gray-600 mt-1">Total Side Effects</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-gray-800">
              {medications.filter((med) => med.side_effects && med.side_effects.length > 0).length}
            </p>
            <p className="text-sm text-gray-600 mt-1">Medications with Side Effects</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-gray-800">
              {medications.filter((med) => !med.side_effects || med.side_effects.length === 0).length}
            </p>
            <p className="text-sm text-gray-600 mt-1">Medications without Side Effects</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SideEffectsLogger;
