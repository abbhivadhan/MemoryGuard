import React, { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line, Text, Html } from '@react-three/drei';
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
        <div className="text-4xl mb-3">📈</div>
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
      <div className="h-[400px] relative">
        <Canvas camera={{ position: [0, 3, 8], fov: 50 }}>
          <ambientLight intensity={0.6} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <TimelineCurve data={timelineData} />
          <OrbitControls enableZoom={true} enablePan={false} />
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
      {/* Historical line */}
      {historicalPoints.length > 1 && (
        <Line
          points={historicalPoints}
          color="#8b5cf6"
          lineWidth={3}
          dashed={false}
        />
      )}

      {/* Forecast line (dashed) */}
      {forecastPoints.length > 1 && (
        <Line
          points={forecastPoints}
          color="#fbbf24"
          lineWidth={3}
          dashed={true}
          dashScale={0.5}
          dashSize={0.2}
          gapSize={0.1}
        />
      )}

      {/* Data points */}
      {normalizedData.map((point, index) => (
        <TimelineDataPoint key={index} point={point} />
      ))}

      {/* Axis labels */}
      <Text
        position={[-5, -0.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
      >
        Past
      </Text>
      <Text
        position={[5, -0.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
      >
        Future
      </Text>
    </group>
  );
};

interface TimelineDataPointProps {
  point: TimelinePoint & { position: THREE.Vector3; index: number };
}

const TimelineDataPoint: React.FC<TimelineDataPointProps> = ({ point }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame(() => {
    if (meshRef.current) {
      if (hovered) {
        meshRef.current.scale.setScalar(1.5 + Math.sin(Date.now() * 0.005) * 0.2);
      } else {
        meshRef.current.scale.setScalar(1);
      }
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={point.position}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <sphereGeometry args={[0.15, 16, 16]} />
      <meshStandardMaterial
        color={point.color}
        emissive={point.color}
        emissiveIntensity={hovered ? 0.5 : 0.2}
      />
      {hovered && (
        <Html distanceFactor={10}>
          <div className="bg-gray-900 text-white px-4 py-3 rounded-lg shadow-lg border border-gray-700 whitespace-nowrap">
            <div className="font-semibold">{point.label}</div>
            <div className="text-sm text-gray-300 mt-1">
              {point.date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </div>
            {point.isForecast && (
              <div className="text-xs text-yellow-400 mt-1">
                ⚠ Forecasted Value
              </div>
            )}
          </div>
        </Html>
      )}
    </mesh>
  );
};

export default ProgressionTimeline3D;
