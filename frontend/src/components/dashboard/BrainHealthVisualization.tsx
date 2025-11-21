import React, { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { HealthMetric } from '../../services/healthService';

interface BrainHealthVisualizationProps {
  metrics: HealthMetric[];
}

interface BrainRegion {
  name: string;
  position: [number, number, number];
  color: string;
  health: number; // 0-1 scale
  metricName: string;
}

const BrainHealthVisualization: React.FC<BrainHealthVisualizationProps> = ({ metrics }) => {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-4">
        <h3 className="text-xl font-bold text-white">3D Brain Health Map</h3>
        <p className="text-white/80 text-sm">Interactive visualization of brain regions</p>
      </div>
      <div className="h-[500px] relative">
        <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} />
          <BrainSphere metrics={metrics} />
          <OrbitControls enableZoom={true} enablePan={false} />
        </Canvas>
        <div className="absolute bottom-4 left-4 bg-gray-900/90 rounded-lg p-3 text-xs">
          <div className="text-white font-semibold mb-2">Health Scale</div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-4 h-4 rounded bg-green-500"></div>
            <span className="text-gray-300">Excellent (80-100%)</span>
          </div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-4 h-4 rounded bg-yellow-500"></div>
            <span className="text-gray-300">Good (60-80%)</span>
          </div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-4 h-4 rounded bg-orange-500"></div>
            <span className="text-gray-300">Fair (40-60%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-500"></div>
            <span className="text-gray-300">Poor (&lt;40%)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

interface BrainSphereProps {
  metrics: HealthMetric[];
}

const BrainSphere: React.FC<BrainSphereProps> = ({ metrics }) => {
  const groupRef = useRef<THREE.Group>(null);
  const [hoveredRegion, setHoveredRegion] = useState<BrainRegion | null>(null);

  // Map metrics to brain regions
  const brainRegions = useMemo<BrainRegion[]>(() => {
    const regions: BrainRegion[] = [];

    // Find cognitive metrics
    const cognitiveMetrics = metrics.filter((m) => m.type === 'cognitive');
    const biomarkerMetrics = metrics.filter((m) => m.type === 'biomarker');
    const imagingMetrics = metrics.filter((m) => m.type === 'imaging');

    // Map MMSE score to frontal lobe (normalize to 0-1, MMSE is 0-30)
    const mmse = cognitiveMetrics.find((m) => m.name.toLowerCase().includes('mmse'));
    if (mmse) {
      regions.push({
        name: 'Frontal Lobe',
        position: [0, 1.2, 0.8],
        color: getHealthColor(mmse.value / 30),
        health: mmse.value / 30,
        metricName: `MMSE: ${mmse.value}/30`,
      });
    }

    // Map MoCA score to temporal lobe (normalize to 0-1, MoCA is 0-30)
    const moca = cognitiveMetrics.find((m) => m.name.toLowerCase().includes('moca'));
    if (moca) {
      regions.push({
        name: 'Temporal Lobe',
        position: [-1.2, 0, 0],
        color: getHealthColor(moca.value / 30),
        health: moca.value / 30,
        metricName: `MoCA: ${moca.value}/30`,
      });
      regions.push({
        name: 'Temporal Lobe (R)',
        position: [1.2, 0, 0],
        color: getHealthColor(moca.value / 30),
        health: moca.value / 30,
        metricName: `MoCA: ${moca.value}/30`,
      });
    }

    // Map hippocampal volume to hippocampus
    const hippocampus = imagingMetrics.find((m) => m.name.toLowerCase().includes('hippocampal'));
    if (hippocampus) {
      // Normalize hippocampal volume (typical range 3000-4000 mm³)
      const normalizedHealth = Math.min(1, Math.max(0, (hippocampus.value - 2500) / 1500));
      regions.push({
        name: 'Hippocampus (L)',
        position: [-0.8, -0.5, 0],
        color: getHealthColor(normalizedHealth),
        health: normalizedHealth,
        metricName: `Volume: ${hippocampus.value.toFixed(0)} ${hippocampus.unit}`,
      });
      regions.push({
        name: 'Hippocampus (R)',
        position: [0.8, -0.5, 0],
        color: getHealthColor(normalizedHealth),
        health: normalizedHealth,
        metricName: `Volume: ${hippocampus.value.toFixed(0)} ${hippocampus.unit}`,
      });
    }

    // Map amyloid beta to parietal lobe
    const amyloid = biomarkerMetrics.find((m) => m.name.toLowerCase().includes('amyloid'));
    if (amyloid) {
      // Lower amyloid is better, so invert (typical range 200-1000 pg/mL, <500 is good)
      const normalizedHealth = Math.min(1, Math.max(0, 1 - (amyloid.value - 200) / 800));
      regions.push({
        name: 'Parietal Lobe',
        position: [0, 0.5, -1.2],
        color: getHealthColor(normalizedHealth),
        health: normalizedHealth,
        metricName: `Aβ42: ${amyloid.value.toFixed(0)} ${amyloid.unit}`,
      });
    }

    // Map tau to occipital lobe
    const tau = biomarkerMetrics.find((m) => m.name.toLowerCase().includes('tau'));
    if (tau) {
      // Lower tau is better (typical range 100-600 pg/mL, <300 is good)
      const normalizedHealth = Math.min(1, Math.max(0, 1 - (tau.value - 100) / 500));
      regions.push({
        name: 'Occipital Lobe',
        position: [0, -0.2, -1.5],
        color: getHealthColor(normalizedHealth),
        health: normalizedHealth,
        metricName: `Tau: ${tau.value.toFixed(0)} ${tau.unit}`,
      });
    }

    // If no regions, add default regions
    if (regions.length === 0) {
      regions.push(
        {
          name: 'Frontal Lobe',
          position: [0, 1.2, 0.8],
          color: '#888888',
          health: 0.5,
          metricName: 'No data',
        },
        {
          name: 'Temporal Lobe (L)',
          position: [-1.2, 0, 0],
          color: '#888888',
          health: 0.5,
          metricName: 'No data',
        },
        {
          name: 'Temporal Lobe (R)',
          position: [1.2, 0, 0],
          color: '#888888',
          health: 0.5,
          metricName: 'No data',
        },
        {
          name: 'Parietal Lobe',
          position: [0, 0.5, -1.2],
          color: '#888888',
          health: 0.5,
          metricName: 'No data',
        },
        {
          name: 'Occipital Lobe',
          position: [0, -0.2, -1.5],
          color: '#888888',
          health: 0.5,
          metricName: 'No data',
        }
      );
    }

    return regions;
  }, [metrics]);

  // Rotate the brain slowly
  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.002;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Central brain sphere */}
      <mesh>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshStandardMaterial
          color="#1a1a2e"
          transparent
          opacity={0.3}
          wireframe={false}
        />
      </mesh>

      {/* Brain regions as colored spheres */}
      {brainRegions.map((region, index) => (
        <BrainRegionMarker
          key={index}
          region={region}
          onHover={setHoveredRegion}
          isHovered={hoveredRegion?.name === region.name}
        />
      ))}
    </group>
  );
};

interface BrainRegionMarkerProps {
  region: BrainRegion;
  onHover: (region: BrainRegion | null) => void;
  isHovered: boolean;
}

const BrainRegionMarker: React.FC<BrainRegionMarkerProps> = ({
  region,
  onHover,
  isHovered,
}) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (meshRef.current && isHovered) {
      meshRef.current.scale.setScalar(1 + Math.sin(Date.now() * 0.005) * 0.1);
    } else if (meshRef.current) {
      meshRef.current.scale.setScalar(1);
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={region.position}
      onPointerOver={() => onHover(region)}
      onPointerOut={() => onHover(null)}
    >
      <sphereGeometry args={[0.2, 16, 16]} />
      <meshStandardMaterial
        color={region.color}
        emissive={region.color}
        emissiveIntensity={isHovered ? 0.5 : 0.2}
      />
      {isHovered && (
        <Html distanceFactor={10}>
          <div className="bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg border border-gray-700 whitespace-nowrap">
            <div className="font-semibold">{region.name}</div>
            <div className="text-sm text-gray-300">{region.metricName}</div>
            <div className="text-xs text-gray-400 mt-1">
              Health: {(region.health * 100).toFixed(0)}%
            </div>
          </div>
        </Html>
      )}
    </mesh>
  );
};

// Helper function to get color based on health score
function getHealthColor(health: number): string {
  if (health >= 0.8) return '#10b981'; // green
  if (health >= 0.6) return '#eab308'; // yellow
  if (health >= 0.4) return '#f97316'; // orange
  return '#ef4444'; // red
}

export default BrainHealthVisualization;
