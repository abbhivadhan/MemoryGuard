/**
 * 3D Brain Visualization Component
 * Renders brain MRI data with highlighted regions of interest using realistic mesh and physics
 */
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { VolumetricMeasurements, AtrophyDetection } from '../../services/imagingService';

interface BrainVisualization3DProps {
  volumetricMeasurements?: VolumetricMeasurements;
  atrophyDetection?: AtrophyDetection;
  className?: string;
}

// Create realistic brain geometry with proper hemispheres
const createBrainGeometry = () => {
  // Start with ellipsoid for brain shape
  const geometry = new THREE.SphereGeometry(1, 128, 128);
  const positions = geometry.attributes.position;
  
  for (let i = 0; i < positions.count; i++) {
    let x = positions.getX(i);
    let y = positions.getY(i);
    let z = positions.getZ(i);
    
    // Normalize
    const length = Math.sqrt(x * x + y * y + z * z);
    x = x / length;
    y = y / length;
    z = z / length;
    
    // Create brain-like ellipsoid shape (wider, taller, less deep)
    const scaleX = 2.2; // Width
    const scaleY = 2.5; // Height
    const scaleZ = 2.0; // Depth
    
    // Apply ellipsoid scaling
    x *= scaleX;
    y *= scaleY;
    z *= scaleZ;
    
    // Add longitudinal fissure (split between hemispheres)
    const fissureDepth = Math.abs(x) < 0.15 ? Math.abs(x) * 2 : 0.3;
    if (y > 0.5) {
      z -= fissureDepth * (y - 0.5) * 0.8;
    }
    
    // Create realistic gyri and sulci (brain wrinkles)
    const gyri1 = Math.sin(x * 4 + y * 3) * Math.cos(z * 3.5) * 0.12;
    const gyri2 = Math.sin(x * 7 + z * 5) * Math.cos(y * 6) * 0.08;
    const gyri3 = Math.sin(y * 9 + z * 7) * Math.cos(x * 8) * 0.06;
    const gyri4 = Math.sin(x * 12) * Math.cos(y * 11) * Math.sin(z * 10) * 0.04;
    
    // Add sulci (grooves) - more pronounced on top
    const sulciDepth = y > 0 ? (y / scaleY) * 0.15 : 0.05;
    const sulci = (gyri1 + gyri2 + gyri3 + gyri4) * (1 + sulciDepth);
    
    // Flatten bottom slightly (where brain stem connects)
    if (y < -1.5) {
      y += (y + 1.5) * 0.3;
    }
    
    // Make frontal lobe more prominent (front)
    if (z > 1.0) {
      z += (z - 1.0) * 0.3;
    }
    
    // Make occipital lobe rounder (back)
    if (z < -1.0) {
      const factor = Math.abs(z + 1.0) * 0.2;
      x *= (1 - factor * 0.3);
      y *= (1 - factor * 0.2);
    }
    
    positions.setXYZ(i, x + sulci, y + sulci * 0.8, z + sulci * 0.9);
  }
  
  geometry.computeVertexNormals();
  return geometry;
};

// Create cerebellum (back lower part of brain)
const createCerebellumGeometry = () => {
  const geometry = new THREE.SphereGeometry(0.8, 64, 64);
  const positions = geometry.attributes.position;
  
  for (let i = 0; i < positions.count; i++) {
    let x = positions.getX(i);
    let y = positions.getY(i);
    let z = positions.getZ(i);
    
    // Flatten top where it connects to cerebrum
    if (y > 0.3) {
      y *= 0.6;
    }
    
    // Add fine wrinkles characteristic of cerebellum
    const wrinkles = Math.sin(x * 15) * Math.cos(z * 15) * 0.05;
    
    positions.setXYZ(i, x + wrinkles, y, z + wrinkles);
  }
  
  geometry.computeVertexNormals();
  return geometry;
};

// Create hippocampus geometry (seahorse-shaped curved structure)
const createHippocampusGeometry = () => {
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0.15, -0.25, 0.1),
    new THREE.Vector3(0.25, -0.5, 0.15),
    new THREE.Vector3(0.2, -0.75, 0.25),
    new THREE.Vector3(0.1, -0.95, 0.35),
    new THREE.Vector3(0, -1.0, 0.4),
  ]);
  
  const geometry = new THREE.TubeGeometry(curve, 24, 0.25, 16, false);
  return geometry;
};

// Create cortical region geometry (irregular blob)
const createCorticalGeometry = () => {
  const geometry = new THREE.SphereGeometry(1, 32, 32);
  const positions = geometry.attributes.position;
  
  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i);
    const y = positions.getY(i);
    const z = positions.getZ(i);
    
    const noise = Math.sin(x * 8) * Math.cos(y * 8) * Math.sin(z * 8) * 0.15;
    const length = Math.sqrt(x * x + y * y + z * z);
    const factor = 1 + noise;
    
    positions.setXYZ(
      i,
      (x / length) * length * factor,
      (y / length) * length * factor,
      (z / length) * length * factor
    );
  }
  
  geometry.computeVertexNormals();
  return geometry;
};

interface BrainRegionProps {
  position: [number, number, number];
  scale: number;
  color: string;
  label: string;
  isAtrophied: boolean;
  geometry?: THREE.BufferGeometry;
  onClick?: () => void;
}

const BrainRegion: React.FC<BrainRegionProps> = ({
  position,
  scale,
  color,
  label,
  isAtrophied,
  geometry,
  onClick
}) => {
  const [hovered, setHovered] = React.useState(false);
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current && isAtrophied) {
      // Gentle pulsing for atrophied regions
      const pulse = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.08;
      meshRef.current.scale.setScalar(scale * pulse);
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      scale={scale}
      onClick={onClick}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      geometry={geometry || new THREE.SphereGeometry(1, 32, 32)}
      castShadow
      receiveShadow
    >
      <meshPhysicalMaterial
        color={isAtrophied ? '#ff4444' : color}
        transparent
        opacity={hovered ? 0.95 : 0.85}
        roughness={0.3}
        metalness={0.1}
        clearcoat={0.5}
        clearcoatRoughness={0.2}
        emissive={isAtrophied ? '#ff0000' : color}
        emissiveIntensity={isAtrophied ? 0.4 : 0.1}
      />
      {hovered && (
        <Html distanceFactor={10} zIndexRange={[100, 0]}>
          <div className="bg-gray-900/95 backdrop-blur-sm text-white px-3 py-2 rounded-lg shadow-xl text-sm whitespace-nowrap pointer-events-none border border-white/20">
            {label}
            {isAtrophied && (
              <div className="text-red-400 text-xs mt-1 font-semibold">⚠ Atrophy Detected</div>
            )}
          </div>
        </Html>
      )}
    </mesh>
  );
};

// Static brain shell component
const BrainShell: React.FC<{ geometry: THREE.BufferGeometry }> = ({ geometry }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      // Gentle rotation
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.05;
    }
  });

  return (
    <mesh ref={meshRef} geometry={geometry} position={[0, 0, 0]} castShadow receiveShadow>
      <meshPhysicalMaterial
        color="#d4b5a0"
        transparent
        opacity={0.35}
        roughness={0.8}
        metalness={0.05}
        clearcoat={0.4}
        clearcoatRoughness={0.3}
      />
    </mesh>
  );
};

const BrainModel: React.FC<{
  volumetricMeasurements?: VolumetricMeasurements;
  atrophyDetection?: AtrophyDetection;
}> = ({ volumetricMeasurements, atrophyDetection }) => {
  // Create geometries
  const brainGeometry = useMemo(() => createBrainGeometry(), []);
  const cerebellumGeometry = useMemo(() => createCerebellumGeometry(), []);
  const hippocampusGeometry = useMemo(() => createHippocampusGeometry(), []);
  const corticalGeometry = useMemo(() => createCorticalGeometry(), []);

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
    return Math.max(0.5, Math.min(1.5, volumetricMeasurements.hippocampal_volume_total / 7500));
  }, [volumetricMeasurements]);

  const corticalScale = useMemo(() => {
    if (!volumetricMeasurements?.cortical_thickness_mean) return 1;
    return Math.max(0.7, Math.min(1.3, volumetricMeasurements.cortical_thickness_mean / 3.0));
  }, [volumetricMeasurements]);

  return (
    <>
      {/* Main cerebrum (brain) structure - static */}
      <BrainShell geometry={brainGeometry} />
      
      {/* Cerebellum - back lower part */}
      <mesh geometry={cerebellumGeometry} position={[0, -1.8, -1.5]} castShadow receiveShadow>
        <meshPhysicalMaterial
          color="#c4a590"
          transparent
          opacity={0.4}
          roughness={0.7}
          metalness={0.05}
          clearcoat={0.3}
        />
      </mesh>

      {/* Hippocampus - Left (deep inside temporal lobe) */}
      <BrainRegion
        position={[-1.5, -0.8, 0.2]}
        scale={hippocampalScale * 0.6}
        color="#4a90e2"
        label={`Left Hippocampus${volumetricMeasurements?.hippocampal_volume_left ? ` (${volumetricMeasurements.hippocampal_volume_left.toFixed(0)} mm³)` : ''}`}
        isAtrophied={hasAtrophy('hippocampal')}
        geometry={hippocampusGeometry}
      />

      {/* Hippocampus - Right (deep inside temporal lobe) */}
      <BrainRegion
        position={[1.5, -0.8, 0.2]}
        scale={hippocampalScale * 0.6}
        color="#4a90e2"
        label={`Right Hippocampus${volumetricMeasurements?.hippocampal_volume_right ? ` (${volumetricMeasurements.hippocampal_volume_right.toFixed(0)} mm³)` : ''}`}
        isAtrophied={hasAtrophy('hippocampal')}
        geometry={hippocampusGeometry}
      />

      {/* Entorhinal Cortex - Left (medial temporal lobe) */}
      <BrainRegion
        position={[-1.8, -1.0, 0.5]}
        scale={0.3}
        color="#7b68ee"
        label="Left Entorhinal Cortex"
        isAtrophied={hasAtrophy('entorhinal')}
        geometry={corticalGeometry}
      />

      {/* Entorhinal Cortex - Right (medial temporal lobe) */}
      <BrainRegion
        position={[1.8, -1.0, 0.5]}
        scale={0.3}
        color="#7b68ee"
        label="Right Entorhinal Cortex"
        isAtrophied={hasAtrophy('entorhinal')}
        geometry={corticalGeometry}
      />

      {/* Frontal Lobe regions (front top) */}
      <BrainRegion
        position={[-0.7, 1.2, 1.3]}
        scale={corticalScale * 0.4}
        color="#ff6b9d"
        label="Left Frontal Cortex"
        isAtrophied={hasAtrophy('frontal')}
        geometry={corticalGeometry}
      />
      
      <BrainRegion
        position={[0.7, 1.2, 1.3]}
        scale={corticalScale * 0.4}
        color="#ff6b9d"
        label="Right Frontal Cortex"
        isAtrophied={hasAtrophy('frontal')}
        geometry={corticalGeometry}
      />

      {/* Parietal regions (top back) */}
      <BrainRegion
        position={[-0.9, 1.6, -0.3]}
        scale={corticalScale * 0.38}
        color="#ff8c42"
        label="Left Parietal Cortex"
        isAtrophied={hasAtrophy('parietal')}
        geometry={corticalGeometry}
      />
      
      <BrainRegion
        position={[0.9, 1.6, -0.3]}
        scale={corticalScale * 0.38}
        color="#ff8c42"
        label="Right Parietal Cortex"
        isAtrophied={hasAtrophy('parietal')}
        geometry={corticalGeometry}
      />

      {/* Temporal regions (sides) */}
      <BrainRegion
        position={[-1.7, 0.0, 0.2]}
        scale={corticalScale * 0.4}
        color="#9b59b6"
        label="Left Temporal Cortex"
        isAtrophied={hasAtrophy('temporal')}
        geometry={corticalGeometry}
      />
      
      <BrainRegion
        position={[1.7, 0.0, 0.2]}
        scale={corticalScale * 0.4}
        color="#9b59b6"
        label="Right Temporal Cortex"
        isAtrophied={hasAtrophy('temporal')}
        geometry={corticalGeometry}
      />

      {/* Ventricles - internal structures (center) */}
      <BrainRegion
        position={[-0.35, 0.2, 0]}
        scale={0.4}
        color="#00bcd4"
        label={`Left Ventricle${volumetricMeasurements?.ventricle_volume ? ` (${(volumetricMeasurements.ventricle_volume / 2).toFixed(0)} mm³)` : ''}`}
        isAtrophied={false}
      />
      
      <BrainRegion
        position={[0.35, 0.2, 0]}
        scale={0.4}
        color="#00bcd4"
        label={`Right Ventricle${volumetricMeasurements?.ventricle_volume ? ` (${(volumetricMeasurements.ventricle_volume / 2).toFixed(0)} mm³)` : ''}`}
        isAtrophied={false}
      />

      {/* Enhanced Lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight 
        position={[10, 10, 10]} 
        intensity={1.5} 
        castShadow
      />
      <directionalLight position={[-10, -5, -10]} intensity={0.5} />
      <pointLight position={[0, 5, 5]} intensity={1} color="#ffffff" />
      <pointLight position={[5, 0, -5]} intensity={0.6} color="#4a90e2" />
      <pointLight position={[-5, 0, -5]} intensity={0.6} color="#ff6b9d" />
      <spotLight
        position={[5, 8, 5]}
        angle={0.4}
        penumbra={1}
        intensity={0.8}
        castShadow
      />
    </>
  );
};

const BrainVisualization3D: React.FC<BrainVisualization3DProps> = ({
  volumetricMeasurements,
  atrophyDetection,
  className = ''
}) => {
  return (
    <div className={`w-full h-full ${className}`}>
      <Canvas 
        camera={{ position: [0, 0, 8], fov: 60 }}
        shadows
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: 'high-performance'
        }}
      >
        <color attach="background" args={['#0a0a0a']} />
        <fog attach="fog" args={['#0a0a0a', 8, 20]} />
        
        <BrainModel
          volumetricMeasurements={volumetricMeasurements}
          atrophyDetection={atrophyDetection}
        />
        
        <OrbitControls
          enableZoom={true}
          enablePan={true}
          enableRotate={true}
          autoRotate={true}
          autoRotateSpeed={0.3}
          minDistance={5}
          maxDistance={15}
        />
      </Canvas>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-gray-900/90 backdrop-blur-sm p-4 rounded-lg text-white text-sm border border-white/10">
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
            <span>Frontal Cortex</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ff8c42]"></div>
            <span>Parietal Cortex</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#9b59b6]"></div>
            <span>Temporal Cortex</span>
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
        <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-400">
          <p>Drag to rotate • Scroll to zoom</p>
          <p>Hover over regions for details</p>
        </div>
      </div>

      {/* Atrophy Alert */}
      {atrophyDetection?.detected && (
        <div className="absolute top-4 right-4 bg-red-900/90 backdrop-blur-sm p-4 rounded-lg text-white max-w-xs border border-red-500/50">
          <h3 className="font-semibold text-red-300 mb-2">⚠ Atrophy Detected</h3>
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
