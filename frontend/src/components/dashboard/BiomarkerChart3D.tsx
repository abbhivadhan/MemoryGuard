import React, { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html, Float, Sparkles, RoundedBox } from '@react-three/drei';
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
      <div className="h-[400px] relative bg-gradient-to-b from-gray-900 to-black">
        <Canvas 
          camera={{ position: [6, 6, 6], fov: 45 }} 
          gl={{ antialias: true, alpha: true }}
          shadows
        >
          <color attach="background" args={['#000000']} />
          <fog attach="fog" args={['#000000', 8, 20]} />
          
          {/* Enhanced Lighting */}
          <ambientLight intensity={0.3} />
          <pointLight position={[10, 10, 10]} intensity={2} color="#60a5fa" castShadow />
          <pointLight position={[-10, 5, -10]} intensity={1} color="#06b6d4" />
          <spotLight 
            position={[0, 15, 0]} 
            angle={0.5} 
            penumbra={1} 
            intensity={3} 
            color="#3b82f6" 
            castShadow 
          />
          
          {/* Sparkles for ambient effect */}
          <Sparkles count={50} scale={15} size={3} speed={0.2} opacity={0.3} color="#60a5fa" />
          
          <BiomarkerBars data={biomarkerData} />
          
          {/* Simple floor */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
            <planeGeometry args={[20, 20]} />
            <meshStandardMaterial
              color="#050505"
              metalness={0.9}
              roughness={0.1}
            />
          </mesh>
          
          <OrbitControls 
            enableZoom={true} 
            enablePan={false}
            minDistance={5}
            maxDistance={15}
            maxPolarAngle={Math.PI / 2.2}
          />
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
  const barRef = useRef<THREE.Group>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const [animatedHeight, setAnimatedHeight] = useState(0);

  // Animate bar height on mount and effects
  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    if (animatedHeight < height) {
      setAnimatedHeight((prev) => Math.min(prev + 0.08, height));
    }
    
    if (barRef.current) {
      if (hovered) {
        const scale = 1.1 + Math.sin(time * 4) * 0.08;
        barRef.current.scale.set(scale, 1, scale);
      } else {
        barRef.current.scale.set(1, 1, 1);
      }
    }

    if (glowRef.current) {
      glowRef.current.rotation.y = time * 2;
      glowRef.current.scale.setScalar(1 + Math.sin(time * 3) * 0.1);
    }
  });

  const isInNormalRange =
    biomarker.value >= biomarker.normalRange[0] &&
    biomarker.value <= biomarker.normalRange[1];

  return (
    <group position={position}>
      <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.1}>
        <group ref={barRef}>
          {/* Base platform */}
          <RoundedBox
            args={[1.2, 0.1, 1.2]}
            radius={0.05}
            position={[0, 0.05, 0]}
            castShadow
          >
            <meshPhysicalMaterial
              color={biomarker.color}
              metalness={0.9}
              roughness={0.2}
              clearcoat={1}
              clearcoatRoughness={0.1}
            />
          </RoundedBox>

          {/* Main bar with rounded edges */}
          <RoundedBox
            args={[0.9, animatedHeight, 0.9]}
            radius={0.1}
            position={[0, animatedHeight / 2 + 0.1, 0]}
            onPointerOver={() => setHovered(true)}
            onPointerOut={() => setHovered(false)}
            castShadow
          >
            <meshPhysicalMaterial
              color={biomarker.color}
              emissive={biomarker.color}
              emissiveIntensity={hovered ? 0.8 : 0.3}
              metalness={0.8}
              roughness={0.2}
              clearcoat={1}
              clearcoatRoughness={0.1}
              transmission={0.1}
              thickness={0.5}
            />
          </RoundedBox>

          {/* Glowing top cap */}
          <mesh 
            ref={glowRef}
            position={[0, animatedHeight + 0.1, 0]}
          >
            <cylinderGeometry args={[0.5, 0.5, 0.05, 32]} />
            <meshBasicMaterial
              color={biomarker.color}
              transparent
              opacity={hovered ? 0.8 : 0.5}
            />
          </mesh>

          {/* Energy particles rising */}
          {hovered && (
            <Sparkles
              count={20}
              scale={[1, animatedHeight + 2, 1]}
              size={2}
              speed={1}
              opacity={0.6}
              color={biomarker.color}
              position={[0, animatedHeight / 2, 0]}
            />
          )}
        </group>
      </Float>

      {/* Normal range indicator with glow */}
      <mesh position={[0, normalRangeHeight / 2, 0]}>
        <boxGeometry args={[1.3, normalRangeHeight, 1.3]} />
        <meshBasicMaterial
          color="#ffffff"
          transparent
          opacity={0.08}
          wireframe={true}
        />
      </mesh>

      {/* Holographic label */}
      <Text
        position={[0, -0.4, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        fontSize={0.35}
        color={biomarker.color}
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.02}
        outlineColor="#000000"
      >
        {biomarker.name.split(' ')[0]}
      </Text>

      {/* Tooltip on hover */}
      {hovered && (
        <Html distanceFactor={8} position={[0, animatedHeight + 1, 0]}>
          <div className="bg-gradient-to-br from-gray-900 via-blue-900/50 to-gray-900 text-white px-5 py-4 rounded-xl shadow-2xl border border-blue-500/50 backdrop-blur-md whitespace-nowrap">
            <div className="font-bold text-xl mb-2" style={{ color: biomarker.color }}>
              {biomarker.name}
            </div>
            <div className="text-3xl font-bold my-2 flex items-baseline gap-2">
              <span style={{ color: biomarker.color }}>{biomarker.value.toFixed(1)}</span>
              <span className="text-lg text-gray-400">{biomarker.unit}</span>
            </div>
            <div className="text-sm text-gray-300 mb-3">
              Normal Range: {biomarker.normalRange[0]}-{biomarker.normalRange[1]} {biomarker.unit}
            </div>
            <div className="flex items-center justify-between gap-4">
              <span
                className={`px-3 py-1.5 rounded-lg font-semibold text-sm ${
                  isInNormalRange
                    ? 'bg-green-500/30 text-green-300 border border-green-500/50'
                    : 'bg-red-500/30 text-red-300 border border-red-500/50'
                }`}
              >
                {isInNormalRange ? '✓ Normal' : '⚠ Abnormal'}
              </span>
              <span className="text-xs text-gray-400">
                {new Date(biomarker.timestamp).toLocaleDateString()}
              </span>
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

export default BiomarkerChart3D;
