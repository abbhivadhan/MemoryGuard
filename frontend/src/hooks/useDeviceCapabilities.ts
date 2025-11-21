/**
 * useDeviceCapabilities Hook
 * Detects device capabilities for 3D rendering optimization
 * Requirements: 10.2, 7.5
 */

import { useState, useEffect } from 'react';

interface DeviceCapabilities {
  supportsWebGL: boolean;
  isMobile: boolean;
  isLowEnd: boolean;
  pixelRatio: number;
  maxTextureSize: number;
  gpuTier: 'low' | 'medium' | 'high';
  preferredQuality: 'low' | 'medium' | 'high';
}

const detectWebGLSupport = (): boolean => {
  try {
    const canvas = document.createElement('canvas');
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
    );
  } catch (e) {
    return false;
  }
};

const detectGPUTier = (gl: WebGLRenderingContext | null): 'low' | 'medium' | 'high' => {
  if (!gl) return 'low';
  
  const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
  if (debugInfo) {
    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
    const rendererLower = renderer.toLowerCase();
    
    // High-end GPUs
    if (
      rendererLower.includes('nvidia') ||
      rendererLower.includes('geforce') ||
      rendererLower.includes('radeon') ||
      rendererLower.includes('amd')
    ) {
      return 'high';
    }
    
    // Low-end or integrated GPUs
    if (
      rendererLower.includes('intel') ||
      rendererLower.includes('mali') ||
      rendererLower.includes('adreno') ||
      rendererLower.includes('powervr')
    ) {
      return 'low';
    }
  }
  
  return 'medium';
};

const isMobileDevice = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
};

const isLowEndDevice = (): boolean => {
  // Check for low memory
  const memory = (navigator as any).deviceMemory;
  if (memory && memory < 4) return true;
  
  // Check for low CPU cores
  const cores = navigator.hardwareConcurrency;
  if (cores && cores < 4) return true;
  
  return false;
};

export const useDeviceCapabilities = (): DeviceCapabilities => {
  const [capabilities, setCapabilities] = useState<DeviceCapabilities>(() => {
    const supportsWebGL = detectWebGLSupport();
    const mobile = isMobileDevice();
    const lowEnd = isLowEndDevice();
    
    let gpuTier: 'low' | 'medium' | 'high' = 'medium';
    let maxTextureSize = 2048;
    
    if (supportsWebGL) {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (gl) {
        gpuTier = detectGPUTier(gl as WebGLRenderingContext);
        maxTextureSize = (gl as WebGLRenderingContext).getParameter(
          (gl as WebGLRenderingContext).MAX_TEXTURE_SIZE
        );
      }
    }
    
    // Determine preferred quality based on device
    let preferredQuality: 'low' | 'medium' | 'high' = 'high';
    if (mobile || lowEnd || gpuTier === 'low') {
      preferredQuality = 'low';
    } else if (gpuTier === 'medium') {
      preferredQuality = 'medium';
    }
    
    return {
      supportsWebGL,
      isMobile: mobile,
      isLowEnd: lowEnd,
      pixelRatio: Math.min(window.devicePixelRatio || 1, 2),
      maxTextureSize,
      gpuTier,
      preferredQuality,
    };
  });

  useEffect(() => {
    // Re-check on visibility change (e.g., when device wakes up)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        const supportsWebGL = detectWebGLSupport();
        const mobile = isMobileDevice();
        const lowEnd = isLowEndDevice();
        
        let gpuTier: 'low' | 'medium' | 'high' = 'medium';
        let maxTextureSize = 2048;
        
        if (supportsWebGL) {
          const canvas = document.createElement('canvas');
          const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
          if (gl) {
            gpuTier = detectGPUTier(gl as WebGLRenderingContext);
            maxTextureSize = (gl as WebGLRenderingContext).getParameter(
              (gl as WebGLRenderingContext).MAX_TEXTURE_SIZE
            );
          }
        }
        
        let preferredQuality: 'low' | 'medium' | 'high' = 'high';
        if (mobile || lowEnd || gpuTier === 'low') {
          preferredQuality = 'low';
        } else if (gpuTier === 'medium') {
          preferredQuality = 'medium';
        }
        
        setCapabilities({
          supportsWebGL,
          isMobile: mobile,
          isLowEnd: lowEnd,
          pixelRatio: Math.min(window.devicePixelRatio || 1, 2),
          maxTextureSize,
          gpuTier,
          preferredQuality,
        });
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  return capabilities;
};
