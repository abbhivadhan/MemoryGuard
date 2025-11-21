/**
 * Adaptive 3D Container
 * Automatically switches between 3D and 2D based on WebGL support
 * Requirements: 10.4, 7.6
 */

import React, { Suspense } from 'react';
import { useDeviceCapabilities } from '../../hooks/useDeviceCapabilities';

interface Adaptive3DContainerProps {
  children3D: React.ReactNode;
  children2D: React.ReactNode;
  fallbackMessage?: string;
  className?: string;
}

const LoadingFallback: React.FC<{ message?: string }> = ({ message }) => (
  <div className="flex items-center justify-center h-full">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4" />
      <p className="text-gray-300">{message || 'Loading 3D content...'}</p>
    </div>
  </div>
);

const Adaptive3DContainer: React.FC<Adaptive3DContainerProps> = ({
  children3D,
  children2D,
  fallbackMessage,
  className = '',
}) => {
  const capabilities = useDeviceCapabilities();

  if (!capabilities.supportsWebGL) {
    return (
      <div className={className}>
        {fallbackMessage && (
          <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <p className="text-sm text-yellow-200 text-center">
              {fallbackMessage}
            </p>
          </div>
        )}
        {children2D}
      </div>
    );
  }

  return (
    <div className={className}>
      <Suspense fallback={<LoadingFallback />}>
        {children3D}
      </Suspense>
    </div>
  );
};

export default Adaptive3DContainer;
