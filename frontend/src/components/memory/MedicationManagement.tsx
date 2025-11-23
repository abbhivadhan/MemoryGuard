import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { medicationService, Medication, MedicationCreate } from '../../services/medicationService';
import EmptyState, { EmptyStateIcons } from '../ui/EmptyState';

interface MedicationFormData {
  name: string;
  dosage: string;
  frequency: string;
  schedule: Date[];
  instructions: string;
  prescriber: string;
  pharmacy: string;
  start_date: Date;
  end_date: Date | null;
}

const MedicationManagement: React.FC = () => {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingMed, setEditingMed] = useState<Medication | null>(null);
  const [selectedMed, setSelectedMed] = useState<Medication | null>(null);

  const [formData, setFormData] = useState<MedicationFormData>({
    name: '',
    dosage: '',
    frequency: 'once daily',
    schedule: [],
    instructions: '',
    prescriber: '',
    pharmacy: '',
    start_date: new Date(),
    end_date: null,
  });

  const [scheduleTime, setScheduleTime] = useState('08:00');

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

    try {
      const medicationData: MedicationCreate = {
        name: formData.name,
        dosage: formData.dosage,
        frequency: formData.frequency,
        schedule: formData.schedule.map(d => d.toISOString()),
        instructions: formData.instructions || undefined,
        prescriber: formData.prescriber || undefined,
        pharmacy: formData.pharmacy || undefined,
        start_date: formData.start_date.toISOString(),
        end_date: formData.end_date?.toISOString() || undefined,
      };

      if (editingMed) {
        await medicationService.updateMedication(editingMed.id, medicationData);
      } else {
        await medicationService.createMedication(medicationData);
      }

      resetForm();
      loadMedications();
    } catch (error) {
      console.error('Failed to save medication:', error);
      alert('Failed to save medication. Please try again.');
    }
  };

  const handleEdit = (med: Medication) => {
    setEditingMed(med);
    setFormData({
      name: med.name,
      dosage: med.dosage,
      frequency: med.frequency,
      schedule: med.schedule.map(s => new Date(s)),
      instructions: med.instructions || '',
      prescriber: med.prescriber || '',
      pharmacy: med.pharmacy || '',
      start_date: new Date(med.start_date),
      end_date: med.end_date ? new Date(med.end_date) : null,
    });
    setShowAddForm(true);
  };

  const handleDelete = async (medId: string) => {
    if (window.confirm('Are you sure you want to delete this medication?')) {
      try {
        await medicationService.deleteMedication(medId);
        loadMedications();
      } catch (error) {
        console.error('Failed to delete medication:', error);
      }
    }
  };

  const handleToggleActive = async (med: Medication) => {
    try {
      await medicationService.updateMedication(med.id, { active: !med.active });
      loadMedications();
    } catch (error) {
      console.error('Failed to update medication:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      dosage: '',
      frequency: 'once daily',
      schedule: [],
      instructions: '',
      prescriber: '',
      pharmacy: '',
      start_date: new Date(),
      end_date: null,
    });
    setScheduleTime('08:00');
    setShowAddForm(false);
    setEditingMed(null);
  };

  const addScheduleTime = () => {
    const [hours, minutes] = scheduleTime.split(':').map(Number);
    const newTime = new Date();
    newTime.setHours(hours, minutes, 0, 0);
    
    setFormData({
      ...formData,
      schedule: [...formData.schedule, newTime],
    });
  };

  const removeScheduleTime = (index: number) => {
    setFormData({
      ...formData,
      schedule: formData.schedule.filter((_, i) => i !== index),
    });
  };

  const formatTime = (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-blue-50">Medication Management</h2>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-gradient-to-r from-teal-500 to-cyan-500 text-white rounded-lg hover:from-teal-600 hover:to-cyan-600 transition-all shadow-lg"
        >
          {showAddForm ? 'Cancel' : '+ Add Medication'}
        </motion.button>
      </div>

      {/* Add/Edit medication form */}
      <AnimatePresence>
        {showAddForm && (
          <motion.form
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            onSubmit={handleSubmit}
            className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4 text-blue-50">
              {editingMed ? 'Edit Medication' : 'Add New Medication'}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Medication Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-white placeholder-gray-500"
                  placeholder="e.g., Donepezil"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Dosage *</label>
                <input
                  type="text"
                  required
                  value={formData.dosage}
                  onChange={(e) => setFormData({ ...formData, dosage: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-white placeholder-gray-500"
                  placeholder="e.g., 10mg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Frequency *</label>
                <select
                  required
                  value={formData.frequency}
                  onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-white"
                >
                  <option value="once daily">Once daily</option>
                  <option value="twice daily">Twice daily</option>
                  <option value="three times daily">Three times daily</option>
                  <option value="every 4 hours">Every 4 hours</option>
                  <option value="every 6 hours">Every 6 hours</option>
                  <option value="every 8 hours">Every 8 hours</option>
                  <option value="every 12 hours">Every 12 hours</option>
                  <option value="as needed">As needed</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Prescriber</label>
                <input
                  type="text"
                  value={formData.prescriber}
                  onChange={(e) => setFormData({ ...formData, prescriber: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Dr. Smith"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Pharmacy</label>
                <input
                  type="text"
                  value={formData.pharmacy}
                  onChange={(e) => setFormData({ ...formData, pharmacy: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="CVS Pharmacy"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Start Date</label>
                <input
                  type="date"
                  value={formData.start_date.toISOString().split('T')[0]}
                  onChange={(e) => setFormData({ ...formData, start_date: new Date(e.target.value) })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">Instructions</label>
                <textarea
                  value={formData.instructions}
                  onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={2}
                  placeholder="Take with food"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Schedule Times
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="time"
                    value={scheduleTime}
                    onChange={(e) => setScheduleTime(e.target.value)}
                    className="flex-1 px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={addScheduleTime}
                    className="px-4 py-2 bg-gray-200 text-gray-300 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    + Add Time
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.schedule.map((time, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full"
                    >
                      <span>{formatTime(time)}</span>
                      <button
                        type="button"
                        onClick={() => removeScheduleTime(index)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 bg-gray-200 text-gray-300 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                {editingMed ? 'Update' : 'Add'} Medication
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>

      {/* Medications list */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AnimatePresence>
          {medications.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="col-span-2 backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg"
            >
              <EmptyState
                icon={EmptyStateIcons.NoMedications}
                title="No Medications Added"
                description="Add your medications to track adherence, set reminders, and monitor side effects. Enter real prescription information from your healthcare provider."
                action={{
                  label: 'Add Medication',
                  onClick: () => setShowAddForm(true),
                }}
              />
            </motion.div>
          ) : (
            medications.map((med) => (
              <motion.div
                key={med.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-4 border-l-4 ${
                  med.active ? 'border-blue-500' : 'border-gray-300 opacity-60'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">💊</span>
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          med.active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-400'
                        }`}
                      >
                        {med.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-blue-50">{med.name}</h3>
                    <p className="text-gray-400 text-sm">{med.dosage}</p>
                    <p className="text-gray-500 text-sm">{med.frequency}</p>
                  </div>
                  <div className="flex flex-col gap-1">
                    <button
                      onClick={() => handleEdit(med)}
                      className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleToggleActive(med)}
                      className="px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600 transition-colors"
                    >
                      {med.active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => handleDelete(med.id)}
                      className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {med.schedule && med.schedule.length > 0 && (
                  <div className="mb-2">
                    <p className="text-xs font-medium text-gray-400 mb-1">Schedule:</p>
                    <div className="flex flex-wrap gap-1">
                      {med.schedule.map((time, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                        >
                          {formatTime(time)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {med.instructions && (
                  <p className="text-xs text-gray-400 mb-2">
                    <span className="font-medium">Instructions:</span> {med.instructions}
                  </p>
                )}

                {med.prescriber && (
                  <p className="text-xs text-gray-400">
                    <span className="font-medium">Prescriber:</span> {med.prescriber}
                  </p>
                )}

                <div className="mt-3 pt-3 border-t border-gray-200">
                  <button
                    onClick={() => setSelectedMed(med)}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    View Details →
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Medication details modal */}
      <AnimatePresence>
        {selectedMed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedMed(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-2xl font-bold text-blue-50">{selectedMed.name}</h3>
                <button
                  onClick={() => setSelectedMed(null)}
                  className="text-gray-500 hover:text-gray-300 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-400">Dosage</p>
                  <p className="text-blue-50">{selectedMed.dosage}</p>
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-400">Frequency</p>
                  <p className="text-blue-50">{selectedMed.frequency}</p>
                </div>

                {selectedMed.instructions && (
                  <div>
                    <p className="text-sm font-medium text-gray-400">Instructions</p>
                    <p className="text-blue-50">{selectedMed.instructions}</p>
                  </div>
                )}

                {selectedMed.prescriber && (
                  <div>
                    <p className="text-sm font-medium text-gray-400">Prescriber</p>
                    <p className="text-blue-50">{selectedMed.prescriber}</p>
                  </div>
                )}

                {selectedMed.pharmacy && (
                  <div>
                    <p className="text-sm font-medium text-gray-400">Pharmacy</p>
                    <p className="text-blue-50">{selectedMed.pharmacy}</p>
                  </div>
                )}

                <div>
                  <p className="text-sm font-medium text-gray-400">Start Date</p>
                  <p className="text-blue-50">{formatDate(selectedMed.start_date)}</p>
                </div>

                {selectedMed.end_date && (
                  <div>
                    <p className="text-sm font-medium text-gray-400">End Date</p>
                    <p className="text-blue-50">{formatDate(selectedMed.end_date)}</p>
                  </div>
                )}

                {selectedMed.side_effects && selectedMed.side_effects.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-400 mb-2">Side Effects</p>
                    <ul className="list-disc list-inside space-y-1">
                      {selectedMed.side_effects.map((effect, idx) => (
                        <li key={idx} className="text-blue-50 text-sm">
                          {effect}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MedicationManagement;
