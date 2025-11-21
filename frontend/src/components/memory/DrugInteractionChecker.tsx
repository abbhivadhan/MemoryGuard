import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  medicationService,
  Medication,
  InteractionWarning,
} from '../../services/medicationService';

const DrugInteractionChecker: React.FC = () => {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [warnings, setWarnings] = useState<InteractionWarning[]>([]);
  const [selectedMeds, setSelectedMeds] = useState<string[]>([]);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  useEffect(() => {
    loadMedications();
  }, []);

  useEffect(() => {
    // Auto-select all active medications
    if (medications.length > 0) {
      setSelectedMeds(medications.map((med) => med.name));
    }
  }, [medications]);

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

  const checkInteractions = async () => {
    if (selectedMeds.length < 2) {
      alert('Please select at least 2 medications to check for interactions.');
      return;
    }

    try {
      setChecking(true);
      const result = await medicationService.checkInteractions(selectedMeds);
      setWarnings(result);
      setLastChecked(new Date());
    } catch (error) {
      console.error('Failed to check interactions:', error);
      alert('Failed to check drug interactions. Please try again.');
    } finally {
      setChecking(false);
    }
  };

  const toggleMedication = (medName: string) => {
    if (selectedMeds.includes(medName)) {
      setSelectedMeds(selectedMeds.filter((name) => name !== medName));
    } else {
      setSelectedMeds([...selectedMeds, medName]);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 border-red-500 text-red-800';
      case 'high':
        return 'bg-orange-100 border-orange-500 text-orange-800';
      case 'moderate':
        return 'bg-yellow-100 border-yellow-500 text-yellow-800';
      case 'low':
        return 'bg-blue-100 border-blue-500 text-blue-800';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'moderate':
        return '⚡';
      case 'low':
        return 'ℹ️';
      default:
        return '📋';
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
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Drug Interaction Checker</h2>
        <p className="text-gray-600">
          Check for potential interactions between your medications
        </p>
      </div>

      {medications.length === 0 ? (
        <div className="text-center py-12 text-gray-500 bg-white rounded-lg shadow-md">
          <p className="text-xl mb-2">No active medications</p>
          <p className="text-sm">Add medications to check for interactions</p>
        </div>
      ) : (
        <>
          {/* Medication selection */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Select Medications to Check
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
              {medications.map((med) => (
                <label
                  key={med.id}
                  className={`flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                    selectedMeds.includes(med.name)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedMeds.includes(med.name)}
                    onChange={() => toggleMedication(med.name)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <div className="ml-3 flex-1">
                    <p className="font-medium text-gray-800">{med.name}</p>
                    <p className="text-sm text-gray-600">{med.dosage}</p>
                  </div>
                </label>
              ))}
            </div>

            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                {selectedMeds.length} medication{selectedMeds.length !== 1 ? 's' : ''} selected
              </p>
              <button
                onClick={checkInteractions}
                disabled={checking || selectedMeds.length < 2}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  checking || selectedMeds.length < 2
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
              >
                {checking ? 'Checking...' : 'Check Interactions'}
              </button>
            </div>

            {lastChecked && (
              <p className="text-xs text-gray-500 mt-2">
                Last checked: {lastChecked.toLocaleString()}
              </p>
            )}
          </div>

          {/* Interaction warnings */}
          {lastChecked && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Interaction Results</h3>

              {warnings.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">✅</div>
                  <p className="text-xl font-semibold text-green-600 mb-2">
                    No Known Interactions
                  </p>
                  <p className="text-gray-600">
                    No significant interactions were found between the selected medications.
                  </p>
                  <p className="text-sm text-gray-500 mt-4">
                    Note: This is a basic check. Always consult your healthcare provider or
                    pharmacist for comprehensive drug interaction information.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <AnimatePresence>
                    {warnings.map((warning, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className={`border-l-4 rounded-lg p-4 ${getSeverityColor(
                          warning.severity
                        )}`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-3xl">{getSeverityIcon(warning.severity)}</span>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="px-2 py-1 rounded text-xs font-bold uppercase">
                                {warning.severity} Severity
                              </span>
                            </div>
                            <h4 className="font-semibold text-lg mb-2">{warning.description}</h4>
                            <div className="mb-3">
                              <p className="text-sm font-medium mb-1">Affected Medications:</p>
                              <div className="flex flex-wrap gap-2">
                                {warning.medications.map((med, medIdx) => (
                                  <span
                                    key={medIdx}
                                    className="px-2 py-1 bg-white rounded text-sm font-medium"
                                  >
                                    {med}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <div className="bg-white bg-opacity-50 rounded p-3">
                              <p className="text-sm font-medium mb-1">Recommendation:</p>
                              <p className="text-sm">{warning.recommendation}</p>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>

                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-6">
                    <p className="text-sm text-red-800">
                      <strong>Important:</strong> These are potential interactions based on known
                      drug interactions. This tool does not replace professional medical advice.
                      Always consult your healthcare provider or pharmacist before making any
                      changes to your medications.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Information panel */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              About Drug Interaction Checking
            </h3>
            <div className="space-y-2 text-sm text-blue-800">
              <p>
                <strong>What are drug interactions?</strong> Drug interactions occur when two or
                more medications affect each other's effectiveness or increase the risk of side
                effects.
              </p>
              <p>
                <strong>Severity levels:</strong>
              </p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>
                  <strong>Critical:</strong> Potentially life-threatening. Avoid combination.
                </li>
                <li>
                  <strong>High:</strong> Serious interaction. Requires medical supervision.
                </li>
                <li>
                  <strong>Moderate:</strong> May require dosage adjustment or monitoring.
                </li>
                <li>
                  <strong>Low:</strong> Minor interaction. Usually manageable.
                </li>
              </ul>
              <p className="mt-3">
                <strong>Note:</strong> This is a basic interaction checker. For comprehensive
                interaction information, consult with your healthcare provider or pharmacist. They
                have access to more detailed pharmaceutical databases and can provide personalized
                advice based on your complete medical history.
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DrugInteractionChecker;
