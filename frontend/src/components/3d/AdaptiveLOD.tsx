/**
 * Adaptive Level of Detail Component
 * Automatically adjusts 3D model complexity based on device capabilities
 * Requirements: 10.2, 7.5
 */

import React, { useMemo } from 'react';
import { useDeviceCapabilities } from '../../hooks/useDeviceCapabilities';

interface AdaptiveLODProps {
  children: {
    high?: React.ReactNode;
    medium?: React.ReactNode;
    low: React.ReactNode;
  };
  forceQuality?: 'low' | 'medium' | 'high';
}

const AdaptiveLOD: React.FC<AdaptiveLODProps> = ({ children, forceQuality }) => {
  const capabilities = useDeviceCapabilities();
  
  const quality = useMemo(() => {
    if (forceQuality) return forceQuality;
    return capabilities.preferredQuality;
  }, [forceQuality, capabilities.preferredQuality]);
  
  // Render appropriate LOD based on quality
  if (quality === 'high' && children.high) {
    return <>{children.high}</>;
  }
  
  if (quality === 'medium' && children.medium) {
    return <>{children.medium}</>;
  }
  
  return <>{children.low}</>;
};

export default AdaptiveLOD;
