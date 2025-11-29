import React, { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, MeshDistortMaterial, Sphere, Float, Sparkles } from '@react-three/drei';
import * as THREE from 'three';
import { HealthMetric } from '../../services/healthService';
import ErrorBoundary from '../ui/ErrorBoundary';
import { Brain } from 'lucide-react';

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
      <div className="h-[500px] relative bg-gradient-to-b from-gray-900 to-black">
        <ErrorBoundary fallback={
          <div className="h-full flex items-center justify-center text-gray-400">
            <div className="text-center">
              <Brain className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>3D visualization unavailable</p>
              <p className="text-sm mt-2">Viewing metrics in list format</p>
            </div>
          </div>
        }>
          <Canvas camera={{ position: [0, 0, 6], fov: 45 }} gl={{ antialias: true, alpha: true }}>
            <color attach="background" args={['#000000']} />
            <fog attach="fog" args={['#000000', 5, 15]} />
            
            {/* Enhanced Lighting */}
            <ambientLight intensity={0.3} />
            <pointLight position={[10, 10, 10]} intensity={1.5} color="#a78bfa" />
            <pointLight position={[-10, -10, -10]} intensity={0.8} color="#ec4899" />
            <spotLight position={[0, 10, 0]} angle={0.3} penumbra={1} intensity={2} color="#8b5cf6" />
            
            {/* Sparkles for ambient effect */}
            <Sparkles count={100} scale={10} size={2} speed={0.3} opacity={0.4} color="#a78bfa" />
            
            <BrainSphere metrics={metrics} />
            <OrbitControls 
              enableZoom={true} 
              enablePan={false} 
              autoRotate 
              autoRotateSpeed={0.5}
              minDistance={4}
              maxDistance={10}
            />
          </Canvas>
        </ErrorBoundary>
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
      {/* Outer glow sphere */}
      <Sphere args={[2.2, 64, 64]}>
        <meshBasicMaterial
          color="#8b5cf6"
          transparent
          opacity={0.05}
          side={THREE.BackSide}
        />
      </Sphere>

      {/* Central brain sphere with distortion */}
      <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.3}>
        <Sphere args={[1.5, 64, 64]}>
          <MeshDistortMaterial
            color="#1a1a2e"
            transparent
            opacity={0.6}
            distort={0.3}
            speed={2}
            roughness={0.4}
            metalness={0.8}
            emissive="#4c1d95"
            emissiveIntensity={0.3}
          />
        </Sphere>
      </Float>

      {/* Inner core with pulsing effect */}
      <PulsingCore />

      {/* Wireframe overlay */}
      <mesh>
        <sphereGeometry args={[1.52, 32, 32]} />
        <meshBasicMaterial
          color="#8b5cf6"
          wireframe
          transparent
          opacity={0.15}
        />
      </mesh>

      {/* Brain regions as enhanced markers */}
      {brainRegions.map((region, index) => (
        <BrainRegionMarker
          key={index}
          region={region}
          onHover={setHoveredRegion}
          isHovered={hoveredRegion?.name === region.name}
        />
      ))}

      {/* Connection lines between regions */}
      <RegionConnections regions={brainRegions} />
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
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    if (meshRef.current) {
      if (isHovered) {
        meshRef.current.scale.setScalar(1.3 + Math.sin(time * 3) * 0.15);
      } else {
        // Gentle breathing animation
        meshRef.current.scale.setScalar(1 + Math.sin(time * 2) * 0.05);
      }
    }

    if (glowRef.current) {
      glowRef.current.scale.setScalar(1.5 + Math.sin(time * 2) * 0.2);
      glowRef.current.rotation.x = time * 0.5;
      glowRef.current.rotation.y = time * 0.3;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <group position={region.position}>
        {/* Outer glow */}
        <mesh ref={glowRef}>
          <sphereGeometry args={[0.35, 16, 16]} />
          <meshBasicMaterial
            color={region.color}
            transparent
            opacity={isHovered ? 0.3 : 0.15}
            side={THREE.BackSide}
          />
        </mesh>

        {/* Main marker sphere */}
        <mesh
          ref={meshRef}
          onPointerOver={() => onHover(region)}
          onPointerOut={() => onHover(null)}
        >
          <sphereGeometry args={[0.25, 32, 32]} />
          <meshPhysicalMaterial
            color={region.color}
            emissive={region.color}
            emissiveIntensity={isHovered ? 1.2 : 0.6}
            metalness={0.9}
            roughness={0.1}
            clearcoat={1}
            clearcoatRoughness={0.1}
            transmission={0.1}
            thickness={0.5}
          />
        </mesh>

        {/* Ring indicator */}
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.3, 0.02, 16, 32]} />
          <meshBasicMaterial
            color={region.color}
            transparent
            opacity={isHovered ? 0.8 : 0.3}
          />
        </mesh>

        {isHovered && (
          <Html distanceFactor={8} position={[0, 0.5, 0]}>
            <div className="bg-gradient-to-br from-gray-900 via-purple-900/50 to-gray-900 text-white px-4 py-3 rounded-xl shadow-2xl border border-purple-500/50 backdrop-blur-sm whitespace-nowrap">
              <div className="font-bold text-lg mb-1" style={{ color: region.color }}>
                {region.name}
              </div>
              <div className="text-sm text-gray-200 mb-2">{region.metricName}</div>
              <div className="flex items-center gap-2">
                <div className="h-2 flex-1 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${region.health * 100}%`,
                      backgroundColor: region.color,
                    }}
                  />
                </div>
                <span className="text-xs font-semibold">
                  {(region.health * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </Html>
        )}
      </group>
    </Float>
  );
};

// Pulsing core component
const PulsingCore: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      const scale = 0.5 + Math.sin(state.clock.getElapsedTime() * 2) * 0.1;
      meshRef.current.scale.setScalar(scale);
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshBasicMaterial
        color="#a78bfa"
        transparent
        opacity={0.6}
      />
    </mesh>
  );
};

// Connection lines between regions
interface RegionConnectionsProps {
  regions: BrainRegion[];
}

const RegionConnections: React.FC<RegionConnectionsProps> = ({ regions }) => {
  if (regions.length < 2) return null;

  return (
    <group>
      {regions.map((region, i) => {
        if (i === 0) return null;
        const prevRegion = regions[i - 1];
        const points = [
          new THREE.Vector3(...region.position),
          new THREE.Vector3(...prevRegion.position),
        ];

        return (
          <mesh key={i}>
            <tubeGeometry args={[new THREE.CatmullRomCurve3(points), 20, 0.02, 8, false]} />
            <meshBasicMaterial
              color="#8b5cf6"
              transparent
              opacity={0.15}
            />
          </mesh>
        );
      })}
    </group>
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
