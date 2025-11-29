import React, { useState } from 'react';
import EmergencyButton from './EmergencyButton';
import { emergencyService, MedicalInfo } from '../../services/emergencyService';
import { locationService, LocationData } from '../../services/locationService';
import { motion, AnimatePresence } from 'framer-motion';

const EmergencySystem: React.FC = () => {
  const [isActivating, setIsActivating] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEmergencyActivated = async () => {
    setIsActivating(true);
    setError(null);

    try {
      // Get current location
      let location: LocationData | undefined;
      try {
        location = await locationService.getCurrentLocation();
        // Try to get address
        if (location) {
          const address = await locationService.getAddressFromLocation(location);
          location.address = address;
        }
      } catch (locationError) {
        console.error('Failed to get location:', locationError);
        // Continue without location
      }

      // Get medical information
      let medicalInfo: MedicalInfo | undefined;
      try {
        medicalInfo = await emergencyService.getMedicalInfo();
      } catch (medicalError) {
        console.error('Failed to get medical info:', medicalError);
        // Continue without medical info
      }

      // Activate emergency alert
      await emergencyService.activateEmergencyAlert({
        location,
        medical_info: medicalInfo,
        trigger_type: 'manual',
      });

      // Show success message
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 5000);
    } catch (err) {
      console.error('Failed to activate emergency alert:', err);
      setError('Failed to send emergency alert. Please try again or call emergency services directly.');
    } finally {
      setIsActivating(false);
    }
  };

  return (
    <>
      <EmergencyButton onEmergencyActivated={handleEmergencyActivated} />

      {/* Loading Overlay */}
      <AnimatePresence>
        {isActivating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[70] flex items-center justify-center bg-black bg-opacity-75"
          >
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
              <div className="text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-red-600 mx-auto mb-4"></div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Activating Emergency Alert
                </h3>
                <p className="text-gray-600">
                  Getting your location and notifying emergency contacts...
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success Message */}
      <AnimatePresence>
        {showSuccess && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-24 right-6 z-[60] bg-green-600 text-white rounded-lg shadow-2xl p-6 max-w-md"
          >
            <div className="flex items-start gap-4">
              <svg
                className="h-6 w-6 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div>
                <h4 className="font-bold mb-1">Emergency Alert Sent!</h4>
                <p className="text-sm">
                  Your emergency contacts have been notified with your location and medical
                  information.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-24 right-6 z-[60] bg-red-600 text-white rounded-lg shadow-2xl p-6 max-w-md"
          >
            <div className="flex items-start gap-4">
              <svg
                className="h-6 w-6 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div>
                <h4 className="font-bold mb-1">Error</h4>
                <p className="text-sm">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="mt-2 text-sm underline hover:no-underline"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default EmergencySystem;
