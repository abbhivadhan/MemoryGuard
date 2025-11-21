import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { offlineEmergencyService } from '../../services/offlineEmergencyService';
import { useAuthStore } from '../../store/authStore';
import { WifiOff } from 'lucide-react';

interface EmergencyButtonProps {
  onEmergencyActivated: () => void;
}

const EmergencyButton: React.FC<EmergencyButtonProps> = ({ onEmergencyActivated }) => {
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [countdown, setCountdown] = useState<number | null>(null);
  const { user } = useAuthStore();
  const isOffline = !navigator.onLine;

  const handleEmergencyClick = () => {
    setShowConfirmation(true);
  };

  const handleConfirm = async () => {
    // Start 3-second countdown
    setCountdown(3);
    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev === null || prev <= 1) {
          clearInterval(interval);
          setShowConfirmation(false);
          setCountdown(null);
          
          // Trigger offline emergency if no connection
          if (isOffline && user?.id) {
            offlineEmergencyService.triggerEmergencyAlert(user.id).catch(console.error);
          }
          
          onEmergencyActivated();
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleCancel = () => {
    setShowConfirmation(false);
    setCountdown(null);
  };

  return (
    <>
      {/* Floating Emergency Button */}
      <motion.button
        onClick={handleEmergencyClick}
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-red-600 hover:bg-red-700 rounded-full shadow-2xl flex items-center justify-center text-white font-bold text-2xl transition-all duration-300 hover:scale-110 focus:outline-none focus:ring-4 focus:ring-red-400"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        animate={{
          boxShadow: [
            '0 0 20px rgba(220, 38, 38, 0.5)',
            '0 0 40px rgba(220, 38, 38, 0.8)',
            '0 0 20px rgba(220, 38, 38, 0.5)',
          ],
        }}
        transition={{
          boxShadow: {
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          },
        }}
        aria-label="Emergency SOS Button"
      >
        SOS
      </motion.button>

      {/* Confirmation Dialog */}
      <AnimatePresence>
        {showConfirmation && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60] flex items-center justify-center bg-black bg-opacity-75 p-4"
            onClick={handleCancel}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-center">
                {/* Warning Icon */}
                <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-red-100 mb-6">
                  <svg
                    className="h-12 w-12 text-red-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                </div>

                {/* Title */}
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  Emergency Alert
                </h3>

                {/* Message */}
                <p className="text-gray-600 mb-6">
                  {countdown !== null ? (
                    <span className="text-3xl font-bold text-red-600">
                      Activating in {countdown}...
                    </span>
                  ) : (
                    <>
                      This will immediately alert your emergency contacts and share your
                      location. Are you sure you want to proceed?
                      {isOffline && (
                        <span className="flex items-center justify-center gap-2 mt-3 text-orange-600 font-semibold">
                          <WifiOff className="w-4 h-4" />
                          Offline mode - Using device capabilities
                        </span>
                      )}
                    </>
                  )}
                </p>

                {/* Action Buttons */}
                {countdown === null && (
                  <div className="flex gap-4">
                    <button
                      onClick={handleCancel}
                      className="flex-1 px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleConfirm}
                      className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-red-400"
                    >
                      Confirm Emergency
                    </button>
                  </div>
                )}

                {countdown !== null && (
                  <button
                    onClick={handleCancel}
                    className="w-full px-6 py-3 bg-gray-800 hover:bg-gray-900 text-white font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-600"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default EmergencyButton;
