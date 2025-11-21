import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MedicalInfo, emergencyService } from '../../services/emergencyService';

const MedicalInfoCard: React.FC = () => {
  const [medicalInfo, setMedicalInfo] = useState<MedicalInfo>({
    medications: [],
    allergies: [],
    conditions: [],
    blood_type: '',
    emergency_notes: '',
  });

  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load medical info on mount
  useEffect(() => {
    loadMedicalInfo();
  }, []);

  const loadMedicalInfo = async () => {
    try {
      const info = await emergencyService.getMedicalInfo();
      if (info) {
        setMedicalInfo(info);
      }
    } catch (error) {
      console.error('Failed to load medical info:', error);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await emergencyService.updateMedicalInfo(medicalInfo);
      setSaveSuccess(true);
      setIsEditing(false);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to save medical info:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddItem = (field: 'medications' | 'allergies' | 'conditions') => {
    const value = prompt(`Add ${field.slice(0, -1)}:`);
    if (value && value.trim()) {
      setMedicalInfo({
        ...medicalInfo,
        [field]: [...(medicalInfo[field] || []), value.trim()],
      });
    }
  };

  const handleRemoveItem = (
    field: 'medications' | 'allergies' | 'conditions',
    index: number
  ) => {
    const items = medicalInfo[field] || [];
    setMedicalInfo({
      ...medicalInfo,
      [field]: items.filter((_, i) => i !== index),
    });
  };

  const handleGenerateQRCode = () => {
    // Generate a shareable link with medical info
    const data = encodeURIComponent(JSON.stringify(medicalInfo));
    const url = `${window.location.origin}/emergency-info?data=${data}`;
    
    // In a real implementation, this would generate a QR code
    alert(`QR Code URL: ${url}\n\nThis would display a QR code that first responders can scan.`);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <svg
            className="h-8 w-8 text-red-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-xl font-bold text-white">Emergency Medical Information</h3>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-cyan-400 hover:text-cyan-300 text-sm underline"
          >
            Edit
          </button>
        )}
      </div>

      <p className="text-gray-400 text-sm mb-6">
        This information will be shared with emergency contacts and first responders during
        emergencies.
      </p>

      {/* Blood Type */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Blood Type
        </label>
        {isEditing ? (
          <select
            value={medicalInfo.blood_type || ''}
            onChange={(e) =>
              setMedicalInfo({ ...medicalInfo, blood_type: e.target.value })
            }
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option value="">Select blood type</option>
            <option value="A+">A+</option>
            <option value="A-">A-</option>
            <option value="B+">B+</option>
            <option value="B-">B-</option>
            <option value="AB+">AB+</option>
            <option value="AB-">AB-</option>
            <option value="O+">O+</option>
            <option value="O-">O-</option>
          </select>
        ) : (
          <p className="text-white">
            {medicalInfo.blood_type || 'Not specified'}
          </p>
        )}
      </div>

      {/* Medications */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-300">
            Current Medications
          </label>
          {isEditing && (
            <button
              onClick={() => handleAddItem('medications')}
              className="text-cyan-400 hover:text-cyan-300 text-sm"
            >
              + Add
            </button>
          )}
        </div>
        {medicalInfo.medications && medicalInfo.medications.length > 0 ? (
          <ul className="space-y-2">
            {medicalInfo.medications.map((med, index) => (
              <li
                key={index}
                className="flex items-center justify-between bg-gray-700 rounded px-3 py-2"
              >
                <span className="text-white text-sm">{med}</span>
                {isEditing && (
                  <button
                    onClick={() => handleRemoveItem('medications', index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    ×
                  </button>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 text-sm">No medications listed</p>
        )}
      </div>

      {/* Allergies */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-300">Allergies</label>
          {isEditing && (
            <button
              onClick={() => handleAddItem('allergies')}
              className="text-cyan-400 hover:text-cyan-300 text-sm"
            >
              + Add
            </button>
          )}
        </div>
        {medicalInfo.allergies && medicalInfo.allergies.length > 0 ? (
          <ul className="space-y-2">
            {medicalInfo.allergies.map((allergy, index) => (
              <li
                key={index}
                className="flex items-center justify-between bg-red-900 bg-opacity-30 border border-red-700 rounded px-3 py-2"
              >
                <span className="text-red-200 text-sm">{allergy}</span>
                {isEditing && (
                  <button
                    onClick={() => handleRemoveItem('allergies', index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    ×
                  </button>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 text-sm">No allergies listed</p>
        )}
      </div>

      {/* Medical Conditions */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-300">
            Medical Conditions
          </label>
          {isEditing && (
            <button
              onClick={() => handleAddItem('conditions')}
              className="text-cyan-400 hover:text-cyan-300 text-sm"
            >
              + Add
            </button>
          )}
        </div>
        {medicalInfo.conditions && medicalInfo.conditions.length > 0 ? (
          <ul className="space-y-2">
            {medicalInfo.conditions.map((condition, index) => (
              <li
                key={index}
                className="flex items-center justify-between bg-gray-700 rounded px-3 py-2"
              >
                <span className="text-white text-sm">{condition}</span>
                {isEditing && (
                  <button
                    onClick={() => handleRemoveItem('conditions', index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    ×
                  </button>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 text-sm">No conditions listed</p>
        )}
      </div>

      {/* Emergency Notes */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Emergency Notes
        </label>
        {isEditing ? (
          <textarea
            value={medicalInfo.emergency_notes || ''}
            onChange={(e) =>
              setMedicalInfo({ ...medicalInfo, emergency_notes: e.target.value })
            }
            rows={3}
            placeholder="Any additional information first responders should know..."
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        ) : (
          <p className="text-white text-sm">
            {medicalInfo.emergency_notes || 'No additional notes'}
          </p>
        )}
      </div>

      {/* Action Buttons */}
      {isEditing ? (
        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex-1 px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            onClick={() => {
              setIsEditing(false);
              loadMedicalInfo();
            }}
            className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          onClick={handleGenerateQRCode}
          className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"
            />
          </svg>
          Generate QR Code
        </button>
      )}

      {saveSuccess && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 bg-green-900 bg-opacity-30 border border-green-700 rounded-lg p-3 text-center"
        >
          <p className="text-green-200 text-sm">Medical information saved successfully!</p>
        </motion.div>
      )}

      {/* Info Box */}
      <div className="mt-6 bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <h4 className="text-blue-300 font-semibold text-sm mb-1">
              Accessible Without Login
            </h4>
            <p className="text-blue-200 text-xs">
              The QR code provides access to your emergency medical information without
              requiring login. Keep it on your phone's lock screen or print it to carry
              with you. First responders can scan it to quickly access critical
              information.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedicalInfoCard;
