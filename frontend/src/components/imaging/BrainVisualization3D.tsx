/**
 * 3D Brain Visualization Component
 * Renders brain MRI data with highlighted regions of interest
 */
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html } from '@react-three/drei';
import * as THREE from 'three';
import { VolumetricMeasurements, AtrophyDetection } from '../../services/imagingService';

interface BrainVisualization3DProps {
  volumetricMeasurements?: VolumetricMeasurements;
  atrophyDetection?: AtrophyDetection;
  className?: string;
}

interface BrainRegionProps {
  position: [number, number, number];
  scale: number;
  color: string;
  label: string;
  isAtrophied: boolean;
  onClick?: () => void;
}

const BrainRegion: React.FC<BrainRegionProps> = ({
  position,
  scale,
  color,
  label,
  isAtrophied,
  onClick
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = React.useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      // Gentle pulsing animation for atrophied regions
      if (isAtrophied) {
        meshRef.current.scale.setScalar(
          scale + Math.sin(state.clock.elapsedTime * 2) * 0.05
        );
      }
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        scale={scale}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial
          color={isAtrophied ? '#ff4444' : color}
          transparent
          opacity={hovered ? 0.9 : 0.7}
          emissive={isAtrophied ? '#ff0000' : '#000000'}
          emissiveIntensity={isAtrophied ? 0.3 : 0}
        />
      </mesh>
      {hovered && (
        <Html distanceFactor={10}>
          <div className="bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg text-sm whitespace-nowrap">
            {label}
            {isAtrophied && (
              <div className="text-red-400 text-xs mt-1">Atrophy Detected</div>
            )}
          </div>
        </Html>
      )}
    </group>
  );
};

const BrainModel: React.FC<{
  volumetricMeasurements?: VolumetricMeasurements;
  atrophyDetection?: AtrophyDetection;
}> = ({ volumetricMeasurements, atrophyDetection }) => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.2) * 0.1;
    }
  });

  // Check if regions have atrophy
  const hasAtrophy = (regionName: string): boolean => {
    if (!atrophyDetection?.regions) return false;
    return atrophyDetection.regions.some(r => 
      r.toLowerCase().includes(regionName.toLowerCase())
    );
  };

  // Calculate relative sizes based on measurements
  const hippocampalScale = useMemo(() => {
    if (!volumetricMeasurements?.hippocampal_volume_total) return 1;
    // Normalize to typical range (6000-9000 mm³)
    return Math.max(0.5, Math.min(1.5, volumetricMeasurements.hippocampal_volume_total / 7500));
  }, [volumetricMeasurements]);

  const corticalScale = useMemo(() => {
    if (!volumetricMeasurements?.cortical_thickness_mean) return 1;
    // Normalize to typical range (2.5-3.5 mm)
    return Math.max(0.7, Math.min(1.3, volumetricMeasurements.cortical_thickness_mean / 3.0));
  }, [volumetricMeasurements]);

  return (
    <group ref={groupRef}>
      {/* Main brain structure */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[3, 64, 64]} />
        <meshStandardMaterial
          color="#e8d5c4"
          transparent
          opacity={0.3}
          wireframe={false}
        />
      </mesh>

      {/* Hippocampus - Left */}
      <BrainRegion
        position={[-2, -0.5, 0]}
        scale={hippocampalScale * 0.4}
        color="#4a90e2"
        label={`Left Hippocampus${volumetricMeasurements?.hippocampal_volume_left ? ` (${volumetricMeasurements.hippocampal_volume_left.toFixed(0)} mm³)` : ''}`}
        isAtrophied={hasAtrophy('hippocampal')}
      />

      {/* Hippocampus - Right */}
      <BrainRegion
        position={[2, -0.5, 0]}
        scale={hippocampalScale * 0.4}
        color="#4a90e2"
        label={`Right Hippocampus${volumetricMeasurements?.hippocampal_volume_right ? ` (${volumetricMeasurements.hippocampal_volume_right.toFixed(0)} mm³)` : ''}`}
        isAtrophied={hasAtrophy('hippocampal')}
      />

      {/* Entorhinal Cortex - Left */}
      <BrainRegion
        position={[-2.5, -1, 0.5]}
        scale={0.3}
        color="#7b68ee"
        label="Left Entorhinal Cortex"
        isAtrophied={hasAtrophy('entorhinal')}
      />

      {/* Entorhinal Cortex - Right */}
      <BrainRegion
        position={[2.5, -1, 0.5]}
        scale={0.3}
        color="#7b68ee"
        label="Right Entorhinal Cortex"
        isAtrophied={hasAtrophy('entorhinal')}
      />

      {/* Cortical regions */}
      <BrainRegion
        position={[0, 2, 0]}
        scale={corticalScale * 0.5}
        color="#ff6b9d"
        label={`Cortex${volumetricMeasurements?.cortical_thickness_mean ? ` (${volumetricMeasurements.cortical_thickness_mean.toFixed(2)} mm)` : ''}`}
        isAtrophied={hasAtrophy('cortical')}
      />

      {/* Ventricles */}
      <BrainRegion
        position={[0, 0, 0]}
        scale={0.6}
        color="#00bcd4"
        label={`Ventricles${volumetricMeasurements?.ventricle_volume ? ` (${volumetricMeasurements.ventricle_volume.toFixed(0)} mm³)` : ''}`}
        isAtrophied={false}
      />

      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
    </group>
  );
};

const BrainVisualization3D: React.FC<BrainVisualization3DProps> = ({
  volumetricMeasurements,
  atrophyDetection,
  className = ''
}) => {
  return (
    <div className={`w-full h-full ${className}`}>
      <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
        <color attach="background" args={['#0a0a0a']} />
        <BrainModel
          volumetricMeasurements={volumetricMeasurements}
          atrophyDetection={atrophyDetection}
        />
        <OrbitControls
          enableZoom={true}
          enablePan={true}
          enableRotate={true}
          autoRotate={true}
          autoRotateSpeed={0.5}
        />
      </Canvas>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-gray-900/90 backdrop-blur-sm p-4 rounded-lg text-white text-sm">
        <h3 className="font-semibold mb-2">Brain Regions</h3>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#4a90e2]"></div>
            <span>Hippocampus</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#7b68ee]"></div>
            <span>Entorhinal Cortex</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ff6b9d]"></div>
            <span>Cortex</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#00bcd4]"></div>
            <span>Ventricles</span>
          </div>
          {atrophyDetection?.detected && (
            <div className="flex items-center gap-2 mt-2 pt-2 border-t border-gray-700">
              <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
              <span className="text-red-400">Atrophy Detected</span>
            </div>
          )}
        </div>
      </div>

      {/* Atrophy Alert */}
      {atrophyDetection?.detected && (
        <div className="absolute top-4 right-4 bg-red-900/90 backdrop-blur-sm p-4 rounded-lg text-white max-w-xs">
          <h3 className="font-semibold text-red-300 mb-2">Atrophy Detected</h3>
          <p className="text-sm mb-2">
            Severity: <span className="font-semibold capitalize">{atrophyDetection.severity}</span>
          </p>
          <p className="text-xs text-gray-300">
            Affected regions: {atrophyDetection.regions.join(', ')}
          </p>
        </div>
      )}
    </div>
  );
};

export default BrainVisualization3D;
