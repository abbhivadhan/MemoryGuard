import React, { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html } from '@react-three/drei';
import * as THREE from 'three';
import { HealthMetric } from '../../services/healthService';

interface BiomarkerChart3DProps {
  metrics: HealthMetric[];
}

interface BiomarkerData {
  name: string;
  value: number;
  unit: string;
  normalRange: [number, number];
  color: string;
  timestamp: string;
}

const BiomarkerChart3D: React.FC<BiomarkerChart3DProps> = ({ metrics }) => {
  const biomarkerMetrics = useMemo(() => {
    return metrics.filter((m) => m.type === 'biomarker');
  }, [metrics]);

  const biomarkerData = useMemo<BiomarkerData[]>(() => {
    const data: BiomarkerData[] = [];

    biomarkerMetrics.forEach((metric) => {
      const name = metric.name.toLowerCase();
      let normalRange: [number, number] = [0, 100];
      let color = '#8b5cf6';

      // Define normal ranges for common biomarkers
      if (name.includes('amyloid') || name.includes('aβ42') || name.includes('abeta')) {
        normalRange = [500, 1000]; // pg/mL - higher is better
        color = metric.value >= 500 ? '#10b981' : '#ef4444';
      } else if (name.includes('tau') && !name.includes('p-tau')) {
        normalRange = [100, 300]; // pg/mL - lower is better
        color = metric.value <= 300 ? '#10b981' : '#ef4444';
      } else if (name.includes('p-tau') || name.includes('phosphorylated')) {
        normalRange = [20, 60]; // pg/mL - lower is better
        color = metric.value <= 60 ? '#10b981' : '#ef4444';
      }

      data.push({
        name: metric.name,
        value: metric.value,
        unit: metric.unit,
        normalRange,
        color,
        timestamp: metric.timestamp,
      });
    });

    return data;
  }, [biomarkerMetrics]);

  if (biomarkerData.length === 0) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center">
        <div className="text-4xl mb-3">🔬</div>
        <h3 className="text-lg font-semibold mb-2">No Biomarker Data</h3>
        <p className="text-gray-400 text-sm">
          Add biomarker measurements to see 3D visualization
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
      <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-4">
        <h3 className="text-xl font-bold text-white">3D Biomarker Levels</h3>
        <p className="text-white/80 text-sm">Interactive 3D bar chart with physics</p>
      </div>
      <div className="h-[400px] relative">
        <Canvas camera={{ position: [5, 5, 5], fov: 50 }}>
          <ambientLight intensity={0.6} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <spotLight position={[0, 10, 0]} angle={0.3} intensity={0.5} />
          <BiomarkerBars data={biomarkerData} />
          <OrbitControls enableZoom={true} enablePan={false} />
          <gridHelper args={[10, 10, '#444444', '#222222']} />
        </Canvas>
      </div>
    </div>
  );
};

interface BiomarkerBarsProps {
  data: BiomarkerData[];
}

const BiomarkerBars: React.FC<BiomarkerBarsProps> = ({ data }) => {
  const spacing = 2;
  const maxValue = useMemo(() => {
    return Math.max(...data.map((d) => d.normalRange[1]));
  }, [data]);

  return (
    <group>
      {data.map((biomarker, index) => {
        const xPos = (index - data.length / 2) * spacing;
        const normalizedHeight = (biomarker.value / maxValue) * 4;
        const normalRangeHeight = (biomarker.normalRange[1] / maxValue) * 4;

        return (
          <BiomarkerBar
            key={index}
            biomarker={biomarker}
            position={[xPos, 0, 0]}
            height={normalizedHeight}
            normalRangeHeight={normalRangeHeight}
          />
        );
      })}
    </group>
  );
};

interface BiomarkerBarProps {
  biomarker: BiomarkerData;
  position: [number, number, number];
  height: number;
  normalRangeHeight: number;
}

const BiomarkerBar: React.FC<BiomarkerBarProps> = ({
  biomarker,
  position,
  height,
  normalRangeHeight,
}) => {
  const barRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const [animatedHeight, setAnimatedHeight] = useState(0);

  // Animate bar height on mount
  useFrame(() => {
    if (animatedHeight < height) {
      setAnimatedHeight((prev) => Math.min(prev + 0.05, height));
    }
    
    // Pulse effect when hovered
    if (barRef.current && hovered) {
      const scale = 1 + Math.sin(Date.now() * 0.005) * 0.05;
      barRef.current.scale.set(scale, 1, scale);
    } else if (barRef.current) {
      barRef.current.scale.set(1, 1, 1);
    }
  });

  const isInNormalRange =
    biomarker.value >= biomarker.normalRange[0] &&
    biomarker.value <= biomarker.normalRange[1];

  return (
    <group position={position}>
      {/* Bar */}
      <mesh
        ref={barRef}
        position={[0, animatedHeight / 2, 0]}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[0.8, animatedHeight, 0.8]} />
        <meshStandardMaterial
          color={biomarker.color}
          emissive={biomarker.color}
          emissiveIntensity={hovered ? 0.3 : 0.1}
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>

      {/* Normal range indicator (transparent box) */}
      <mesh position={[0, normalRangeHeight / 2, 0]}>
        <boxGeometry args={[1, normalRangeHeight, 1]} />
        <meshStandardMaterial
          color="#ffffff"
          transparent
          opacity={0.1}
          wireframe={true}
        />
      </mesh>

      {/* Label */}
      <Text
        position={[0, -0.3, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {biomarker.name.split(' ')[0]}
      </Text>

      {/* Tooltip on hover */}
      {hovered && (
        <Html distanceFactor={10} position={[0, animatedHeight + 0.5, 0]}>
          <div className="bg-gray-900 text-white px-4 py-3 rounded-lg shadow-lg border border-gray-700 whitespace-nowrap">
            <div className="font-semibold text-lg">{biomarker.name}</div>
            <div className="text-2xl font-bold my-1" style={{ color: biomarker.color }}>
              {biomarker.value.toFixed(1)} {biomarker.unit}
            </div>
            <div className="text-sm text-gray-300">
              Normal: {biomarker.normalRange[0]}-{biomarker.normalRange[1]} {biomarker.unit}
            </div>
            <div className="text-xs mt-2">
              <span
                className={`px-2 py-1 rounded ${
                  isInNormalRange
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-red-500/20 text-red-400'
                }`}
              >
                {isInNormalRange ? '✓ Normal Range' : '⚠ Outside Range'}
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-2">
              {new Date(biomarker.timestamp).toLocaleDateString()}
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

export default BiomarkerChart3D;
