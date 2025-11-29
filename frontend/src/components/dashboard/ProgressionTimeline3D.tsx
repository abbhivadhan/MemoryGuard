import React, { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line, Text, Html, Float, Sparkles } from '@react-three/drei';
import * as THREE from 'three';
import { HealthMetric } from '../../services/healthService';

interface ProgressionTimeline3DProps {
  metrics: HealthMetric[];
  predictions?: {
    sixMonth: number;
    twelveMonth: number;
    twentyFourMonth: number;
  };
}

interface TimelinePoint {
  date: Date;
  value: number;
  label: string;
  isForecast: boolean;
  color: string;
}

const ProgressionTimeline3D: React.FC<ProgressionTimeline3DProps> = ({
  metrics,
  predictions,
}) => {
  // Focus on cognitive metrics for progression
  const cognitiveMetrics = useMemo(() => {
    return metrics
      .filter((m) => m.type === 'cognitive')
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }, [metrics]);

  const timelineData = useMemo<TimelinePoint[]>(() => {
    const points: TimelinePoint[] = [];

    // Add historical data points
    cognitiveMetrics.forEach((metric) => {
      points.push({
        date: new Date(metric.timestamp),
        value: metric.value,
        label: `${metric.name}: ${metric.value}`,
        isForecast: false,
        color: '#8b5cf6',
      });
    });

    // Add forecast points if predictions exist
    if (predictions && cognitiveMetrics.length > 0) {
      const lastMetric = cognitiveMetrics[cognitiveMetrics.length - 1];
      const lastDate = new Date(lastMetric.timestamp);

      // 6-month forecast
      const sixMonthDate = new Date(lastDate);
      sixMonthDate.setMonth(sixMonthDate.getMonth() + 6);
      points.push({
        date: sixMonthDate,
        value: predictions.sixMonth,
        label: `6-month forecast: ${predictions.sixMonth.toFixed(1)}`,
        isForecast: true,
        color: '#fbbf24',
      });

      // 12-month forecast
      const twelveMonthDate = new Date(lastDate);
      twelveMonthDate.setMonth(twelveMonthDate.getMonth() + 12);
      points.push({
        date: twelveMonthDate,
        value: predictions.twelveMonth,
        label: `12-month forecast: ${predictions.twelveMonth.toFixed(1)}`,
        isForecast: true,
        color: '#f97316',
      });

      // 24-month forecast
      const twentyFourMonthDate = new Date(lastDate);
      twentyFourMonthDate.setMonth(twentyFourMonthDate.getMonth() + 24);
      points.push({
        date: twentyFourMonthDate,
        value: predictions.twentyFourMonth,
        label: `24-month forecast: ${predictions.twentyFourMonth.toFixed(1)}`,
        isForecast: true,
        color: '#ef4444',
      });
    }

    return points;
  }, [cognitiveMetrics, predictions]);

  if (timelineData.length === 0) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center">
        <h3 className="text-lg font-semibold mb-2">No Timeline Data</h3>
        <p className="text-gray-400 text-sm">
          Add cognitive assessments to track progression over time
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
      <div className="bg-gradient-to-r from-green-500 to-emerald-500 p-4">
        <h3 className="text-xl font-bold text-white">Progression Timeline</h3>
        <p className="text-white/80 text-sm">
          Historical data and forecasted progression
        </p>
      </div>
      <div className="h-[400px] relative bg-gradient-to-b from-gray-900 to-black">
        <Canvas 
          camera={{ position: [0, 4, 10], fov: 45 }} 
          gl={{ antialias: true, alpha: true }}
        >
          <color attach="background" args={['#000000']} />
          <fog attach="fog" args={['#000000', 8, 20]} />
          
          {/* Enhanced Lighting */}
          <ambientLight intensity={0.3} />
          <pointLight position={[10, 10, 10]} intensity={2} color="#10b981" />
          <pointLight position={[-10, 5, -10]} intensity={1.5} color="#6366f1" />
          <spotLight 
            position={[0, 10, 5]} 
            angle={0.5} 
            penumbra={1} 
            intensity={2} 
            color="#34d399" 
          />
          
          {/* Ambient sparkles */}
          <Sparkles count={80} scale={20} size={2} speed={0.2} opacity={0.3} color="#10b981" />
          
          <TimelineCurve data={timelineData} />
          
          <OrbitControls 
            enableZoom={true} 
            enablePan={false}
            minDistance={6}
            maxDistance={15}
            maxPolarAngle={Math.PI / 2.2}
          />
        </Canvas>
        <div className="absolute bottom-4 right-4 bg-gray-900/90 rounded-lg p-3 text-xs">
          <div className="text-white font-semibold mb-2">Legend</div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span className="text-gray-300">Historical Data</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span className="text-gray-300">Forecasted</span>
          </div>
        </div>
      </div>
    </div>
  );
};

interface TimelineCurveProps {
  data: TimelinePoint[];
}

const TimelineCurve: React.FC<TimelineCurveProps> = ({ data }) => {
  // Normalize data for 3D space
  const normalizedData = useMemo(() => {
    if (data.length === 0) return [];

    const minDate = data[0].date.getTime();
    const maxDate = data[data.length - 1].date.getTime();
    const dateRange = maxDate - minDate || 1;

    const values = data.map((d) => d.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const valueRange = maxValue - minValue || 1;

    return data.map((point, index) => {
      const x = ((point.date.getTime() - minDate) / dateRange) * 8 - 4; // Spread across 8 units
      const y = ((point.value - minValue) / valueRange) * 4; // Height up to 4 units
      const z = 0;

      return {
        ...point,
        position: new THREE.Vector3(x, y, z),
        index,
      };
    });
  }, [data]);

  // Create curve points for the line
  const curvePoints = useMemo(() => {
    return normalizedData.map((d) => d.position);
  }, [normalizedData]);

  // Split into historical and forecast segments
  const historicalPoints = useMemo(() => {
    return curvePoints.filter((_, i) => !normalizedData[i].isForecast);
  }, [curvePoints, normalizedData]);

  const forecastPoints = useMemo(() => {
    const lastHistorical = normalizedData.findIndex((d) => d.isForecast);
    if (lastHistorical === -1) return [];
    return curvePoints.slice(lastHistorical - 1); // Include last historical point
  }, [curvePoints, normalizedData]);

  return (
    <group>
      {/* Historical line with glow */}
      {historicalPoints.length > 1 && (
        <>
          <Line
            points={historicalPoints}
            color="#8b5cf6"
            lineWidth={5}
          />
        </>
      )}

      {/* Forecast line (dashed) */}
      {forecastPoints.length > 1 && (
        <>
          <Line
            points={forecastPoints}
            color="#fbbf24"
            lineWidth={5}
            dashed={true}
            dashScale={0.5}
            dashSize={0.3}
            gapSize={0.15}
          />
        </>
      )}

      {/* Surface under the curve */}
      <TimelineSurface points={curvePoints} />

      {/* Data points */}
      {normalizedData.map((point, index) => (
        <TimelineDataPoint key={index} point={point} />
      ))}

      {/* Enhanced axis labels with glow */}
      <Text
        position={[-5, -0.8, 0]}
        fontSize={0.4}
        color="#8b5cf6"
        anchorX="center"
        outlineWidth={0.03}
        outlineColor="#000000"
      >
        PAST
      </Text>
      <Text
        position={[5, -0.8, 0]}
        fontSize={0.4}
        color="#fbbf24"
        anchorX="center"
        outlineWidth={0.03}
        outlineColor="#000000"
      >
        FUTURE
      </Text>

      {/* Grid lines */}
      <TimelineGrid />
    </group>
  );
};

interface TimelineDataPointProps {
  point: TimelinePoint & { position: THREE.Vector3; index: number };
}

const TimelineDataPoint: React.FC<TimelineDataPointProps> = ({ point }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    if (meshRef.current) {
      if (hovered) {
        meshRef.current.scale.setScalar(1.8 + Math.sin(time * 5) * 0.3);
      } else {
        meshRef.current.scale.setScalar(1 + Math.sin(time * 2 + point.index) * 0.1);
      }
    }

    if (glowRef.current) {
      glowRef.current.scale.setScalar(2 + Math.sin(time * 3) * 0.3);
      glowRef.current.rotation.z = time;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.3} floatIntensity={0.2}>
      <group position={point.position}>
        {/* Outer glow ring */}
        <mesh ref={glowRef}>
          <torusGeometry args={[0.3, 0.05, 16, 32]} />
          <meshBasicMaterial
            color={point.color}
            transparent
            opacity={hovered ? 0.6 : 0.3}
          />
        </mesh>

        {/* Glow sphere */}
        <mesh>
          <sphereGeometry args={[0.35, 32, 32]} />
          <meshBasicMaterial
            color={point.color}
            transparent
            opacity={0.2}
            side={THREE.BackSide}
          />
        </mesh>

        {/* Main data point */}
        <mesh
          ref={meshRef}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
        >
          <sphereGeometry args={[0.2, 32, 32]} />
          <meshPhysicalMaterial
            color={point.color}
            emissive={point.color}
            emissiveIntensity={hovered ? 1.5 : 0.8}
            metalness={0.9}
            roughness={0.1}
            clearcoat={1}
            clearcoatRoughness={0.1}
            transmission={0.2}
          />
        </mesh>

        {/* Sparkles for forecast points */}
        {point.isForecast && (
          <Sparkles
            count={15}
            scale={1}
            size={2}
            speed={0.5}
            opacity={0.6}
            color={point.color}
          />
        )}

        {/* Vertical indicator line */}
        {point.position.y > 0 && (
          <Line
            points={[
              new THREE.Vector3(0, 0, 0),
              new THREE.Vector3(0, -point.position.y, 0),
            ]}
            color={point.color}
            lineWidth={1}
            dashed
            dashScale={0.5}
          />
        )}

        {hovered && (
          <Html distanceFactor={8} position={[0, 0.8, 0]}>
            <div className="bg-gradient-to-br from-gray-900 via-green-900/50 to-gray-900 text-white px-5 py-4 rounded-xl shadow-2xl border border-green-500/50 backdrop-blur-md whitespace-nowrap">
              <div className="font-bold text-lg mb-2" style={{ color: point.color }}>
                {point.label}
              </div>
              <div className="text-sm text-gray-300 mb-2">
                {point.date.toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </div>
              {point.isForecast && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-yellow-500/20 border border-yellow-500/50">
                  <span className="text-yellow-300 text-lg">⚠</span>
                  <span className="text-xs text-yellow-300 font-semibold">
                    Forecasted Value
                  </span>
                </div>
              )}
            </div>
          </Html>
        )}
      </group>
    </Float>
  );
};

// Surface under the curve
interface TimelineSurfaceProps {
  points: THREE.Vector3[];
}

const TimelineSurface: React.FC<TimelineSurfaceProps> = ({ points }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  const geometry = useMemo(() => {
    if (points.length < 2) return null;

    const vertices: number[] = [];
    const indices: number[] = [];

    points.forEach((point, i) => {
      // Top point
      vertices.push(point.x, point.y, point.z);
      // Bottom point
      vertices.push(point.x, 0, point.z);

      if (i < points.length - 1) {
        const base = i * 2;
        // Create two triangles for each segment
        indices.push(base, base + 1, base + 2);
        indices.push(base + 1, base + 3, base + 2);
      }
    });

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geo.setIndex(indices);
    geo.computeVertexNormals();

    return geo;
  }, [points]);

  useFrame((state) => {
    if (meshRef.current) {
      const material = meshRef.current.material as THREE.MeshBasicMaterial;
      material.opacity = 0.1 + Math.sin(state.clock.getElapsedTime() * 2) * 0.05;
    }
  });

  if (!geometry) return null;

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshBasicMaterial
        color="#10b981"
        transparent
        opacity={0.1}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
};

// Grid lines for reference
const TimelineGrid: React.FC = () => {
  const gridRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (gridRef.current) {
      gridRef.current.children.forEach((child, i) => {
        const material = (child as THREE.Line).material as THREE.LineBasicMaterial;
        material.opacity = 0.05 + Math.sin(state.clock.getElapsedTime() + i * 0.5) * 0.02;
      });
    }
  });

  const gridLines = useMemo(() => {
    const lines = [];
    // Horizontal lines
    for (let i = 0; i <= 4; i++) {
      const y = i;
      lines.push({
        points: [
          [-5, y, 0],
          [5, y, 0],
        ],
        key: `h-${i}`,
      });
    }
    // Vertical lines
    for (let i = -4; i <= 4; i += 2) {
      const x = i;
      lines.push({
        points: [
          [x, 0, 0],
          [x, 4, 0],
        ],
        key: `v-${i}`,
      });
    }
    return lines;
  }, []);

  return (
    <group ref={gridRef}>
      {gridLines.map((line) => (
        <Line
          key={line.key}
          points={line.points.map(p => new THREE.Vector3(p[0], p[1], p[2]))}
          color="#10b981"
          lineWidth={0.5}
        />
      ))}
    </group>
  );
};

export default ProgressionTimeline3D;
