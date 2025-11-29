import { Canvas } from '@react-three/fiber';
import { Physics } from '@react-three/cannon';
import { ReactNode } from 'react';
import { useDeviceCapabilities } from '../../hooks/useDeviceCapabilities';

interface SceneProps {
  children: ReactNode;
  camera?: {
    position?: [number, number, number];
    fov?: number;
  };
  enablePhysics?: boolean;
  quality?: 'low' | 'medium' | 'high' | 'auto';
}

/**
 * Base Scene component for 3D rendering with optional physics
 * Provides a configured Canvas with lighting and physics world
 * Automatically optimizes for mobile and low-end devices
 * Requirements: 10.2, 7.5
 */
export default function Scene({ 
  children, 
  camera = { position: [0, 0, 5], fov: 75 },
  enablePhysics = true,
  quality = 'auto'
}: SceneProps) {
  const capabilities = useDeviceCapabilities();
  
  // Determine quality settings
  const effectiveQuality = quality === 'auto' ? capabilities.preferredQuality : quality;
  
  // Quality-based settings
  const qualitySettings = {
    low: {
      antialias: false,
      dpr: [1, 1],
      shadows: false,
      physicsIterations: 5,
      lightIntensity: 0.7,
    },
    medium: {
      antialias: true,
      dpr: [1, 1.5],
      shadows: false,
      physicsIterations: 8,
      lightIntensity: 0.8,
    },
    high: {
      antialias: true,
      dpr: [1, 2],
      shadows: true,
      physicsIterations: 10,
      lightIntensity: 1,
    },
  };
  
  const settings = qualitySettings[effectiveQuality];
  
  return (
    <Canvas
      camera={camera}
      gl={{ 
        antialias: settings.antialias,
        alpha: true,
        powerPreference: capabilities.isMobile ? 'default' : 'high-performance',
        // Disable stencil buffer on mobile for better performance
        stencil: !capabilities.isMobile,
      }}
      dpr={settings.dpr as [number, number]}
      style={{ background: 'transparent' }}
      // Reduce frame rate on low-end devices
      frameloop={capabilities.isLowEnd ? 'demand' : 'always'}
    >
      {/* Ambient light for overall scene illumination */}
      <ambientLight intensity={0.5 * settings.lightIntensity} />
      
      {/* Directional light for shadows and depth */}
      <directionalLight 
        position={[10, 10, 5]} 
        intensity={1 * settings.lightIntensity}
        castShadow={settings.shadows}
      />
      
      {/* Point light for highlights - skip on low quality */}
      {effectiveQuality !== 'low' && (
        <pointLight position={[-10, -10, -5]} intensity={0.5 * settings.lightIntensity} />
      )}

      {enablePhysics ? (
        <Physics
          gravity={[0, -9.8, 0]}
          iterations={settings.physicsIterations}
          tolerance={effectiveQuality === 'low' ? 0.001 : 0.0001}
          allowSleep={true}
          broadphase="SAP" // Sweep and Prune for better performance
          // Reduce physics update rate on low-end devices
          stepSize={capabilities.isLowEnd ? 1/30 : 1/60}
        >
          {children}
        </Physics>
      ) : (
        children
      )}
    </Canvas>
  );
}
