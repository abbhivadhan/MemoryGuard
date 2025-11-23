import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface CaregiverAccess {
  email: string;
  name: string;
  permissions: {
    view_reminders: boolean;
    manage_reminders: boolean;
    view_routines: boolean;
    manage_routines: boolean;
    view_medications: boolean;
    receive_alerts: boolean;
  };
}

const CaregiverConfig: React.FC = () => {
  const [caregivers, setCaregivers] = useState<CaregiverAccess[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [alertSettings, setAlertSettings] = useState({
    missed_medication: true,
    low_adherence: true,
    missed_routines: true,
    emergency_alerts: true,
  });

  const [newCaregiver, setNewCaregiver] = useState<CaregiverAccess>({
    email: '',
    name: '',
    permissions: {
      view_reminders: true,
      manage_reminders: false,
      view_routines: true,
      manage_routines: false,
      view_medications: true,
      receive_alerts: true,
    },
  });

  useEffect(() => {
    loadCaregivers();
  }, []);

  const loadCaregivers = () => {
    // In a real implementation, this would fetch from the API
    // For now, we'll use localStorage as a demo
    const stored = localStorage.getItem('caregivers');
    if (stored) {
      setCaregivers(JSON.parse(stored));
    }
  };

  const saveCaregivers = (updatedCaregivers: CaregiverAccess[]) => {
    localStorage.setItem('caregivers', JSON.stringify(updatedCaregivers));
    setCaregivers(updatedCaregivers);
  };

  const handleAddCaregiver = (e: React.FormEvent) => {
    e.preventDefault();
    const updated = [...caregivers, newCaregiver];
    saveCaregivers(updated);
    setShowAddForm(false);
    setNewCaregiver({
      email: '',
      name: '',
      permissions: {
        view_reminders: true,
        manage_reminders: false,
        view_routines: true,
        manage_routines: false,
        view_medications: true,
        receive_alerts: true,
      },
    });
  };

  const handleRemoveCaregiver = (email: string) => {
    if (window.confirm('Are you sure you want to remove this caregiver?')) {
      const updated = caregivers.filter((c) => c.email !== email);
      saveCaregivers(updated);
    }
  };

  const handleUpdatePermissions = (email: string, permission: string, value: boolean) => {
    const updated = caregivers.map((c) => {
      if (c.email === email) {
        return {
          ...c,
          permissions: {
            ...c.permissions,
            [permission]: value,
          },
        };
      }
      return c;
    });
    saveCaregivers(updated);
  };

  const handleSaveAlertSettings = () => {
    localStorage.setItem('alert_settings', JSON.stringify(alertSettings));
    alert('Alert settings saved successfully!');
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-3xl font-bold text-blue-50 mb-6">Caregiver Configuration</h2>

      {/* Alert Settings */}
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Alert Settings</h3>
        <p className="text-gray-400 mb-4">
          Configure when caregivers should receive alerts about your activities
        </p>

        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={alertSettings.missed_medication}
              onChange={(e) =>
                setAlertSettings({ ...alertSettings, missed_medication: e.target.checked })
              }
              className="w-5 h-5 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div>
              <div className="font-medium text-blue-50">Missed Medication</div>
              <div className="text-sm text-gray-400">
                Alert when a medication reminder is not completed
              </div>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={alertSettings.low_adherence}
              onChange={(e) =>
                setAlertSettings({ ...alertSettings, low_adherence: e.target.checked })
              }
              className="w-5 h-5 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div>
              <div className="font-medium text-blue-50">Low Adherence</div>
              <div className="text-sm text-gray-400">
                Alert when medication adherence falls below 80% over 7 days
              </div>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={alertSettings.missed_routines}
              onChange={(e) =>
                setAlertSettings({ ...alertSettings, missed_routines: e.target.checked })
              }
              className="w-5 h-5 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div>
              <div className="font-medium text-blue-50">Missed Routines</div>
              <div className="text-sm text-gray-400">
                Alert when 3 or more daily routine items are not completed
              </div>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={alertSettings.emergency_alerts}
              onChange={(e) =>
                setAlertSettings({ ...alertSettings, emergency_alerts: e.target.checked })
              }
              className="w-5 h-5 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div>
              <div className="font-medium text-blue-50">Emergency Alerts</div>
              <div className="text-sm text-gray-400">
                Alert for emergency button activations and concerning patterns
              </div>
            </div>
          </label>
        </div>

        <button
          onClick={handleSaveAlertSettings}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Save Alert Settings
        </button>
      </div>

      {/* Caregiver Management */}
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Authorized Caregivers</h3>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            {showAddForm ? 'Cancel' : '+ Add Caregiver'}
          </button>
        </div>

        {/* Add caregiver form */}
        {showAddForm && (
          <motion.form
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            onSubmit={handleAddCaregiver}
            className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-lg p-4 mb-6"
          >
            <h4 className="font-semibold mb-3 text-blue-50">Add New Caregiver</h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Name *</label>
                <input
                  type="text"
                  required
                  value={newCaregiver.name}
                  onChange={(e) => setNewCaregiver({ ...newCaregiver, name: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Sarah Johnson"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Email *</label>
                <input
                  type="email"
                  required
                  value={newCaregiver.email}
                  onChange={(e) => setNewCaregiver({ ...newCaregiver, email: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="caregiver@example.com"
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">Permissions</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {Object.entries(newCaregiver.permissions).map(([key, value]) => (
                  <label key={key} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) =>
                        setNewCaregiver({
                          ...newCaregiver,
                          permissions: {
                            ...newCaregiver.permissions,
                            [key]: e.target.checked,
                          },
                        })
                      }
                      className="w-4 h-4 text-blue-500 rounded"
                    />
                    <span className="text-sm text-gray-300">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 bg-white/10 text-gray-300 border border-white/20 rounded-lg hover:bg-white/20 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Add Caregiver
              </button>
            </div>
          </motion.form>
        )}

        {/* Caregivers list */}
        {caregivers.length === 0 ? (
          <p className="text-center text-gray-400 py-8">
            No caregivers added yet. Add a caregiver to enable remote monitoring and support.
          </p>
        ) : (
          <div className="space-y-4">
            {caregivers.map((caregiver) => (
              <div key={caregiver.email} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-lg font-semibold text-blue-50">{caregiver.name}</h4>
                    <p className="text-sm text-gray-400">{caregiver.email}</p>
                  </div>
                  <button
                    onClick={() => handleRemoveCaregiver(caregiver.email)}
                    className="px-3 py-1 text-sm text-red-400 border border-red-500/50 rounded hover:bg-red-500/20 transition-colors"
                  >
                    Remove
                  </button>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {Object.entries(caregiver.permissions).map(([key, value]) => (
                    <label key={key} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) =>
                          handleUpdatePermissions(caregiver.email, key, e.target.checked)
                        }
                        className="w-4 h-4 text-blue-500 rounded"
                      />
                      <span className="text-sm text-gray-300">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Information box */}
      <div className="mt-6 backdrop-blur-xl bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <h4 className="font-semibold text-blue-300 mb-2">About Caregiver Access</h4>
        <ul className="text-sm text-blue-200 space-y-1">
          <li>• Caregivers will receive an email invitation to access your information</li>
          <li>• You can modify or revoke permissions at any time</li>
          <li>• All caregiver access is logged for your security</li>
          <li>• Caregivers can only see information you explicitly grant access to</li>
        </ul>
      </div>
    </div>
  );
};

export default CaregiverConfig;
