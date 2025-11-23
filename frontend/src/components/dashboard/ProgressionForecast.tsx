import { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Line, Text, Sphere } from '@react-three/drei';
import { motion } from 'framer-motion';
import * as THREE from 'three';
import { mlService, ForecastResponse } from '../../services/mlService';
import { useAuthStore } from '../../store/authStore';
import { InlineDisclaimer } from '../ui/MedicalDisclaimer';

interface ProgressionForecastProps {
  userId?: number | string;
  currentMetrics?: Record<string, number>;
}

// 3D Forecast Timeline
function ForecastTimeline({ forecast }: { forecast: ForecastResponse }) {
  const timePoints = ['Current', '6 Months', '12 Months', '24 Months'];
  
  // Extract risk scores
  const riskScores = [
    0.5, // Placeholder for current (will be replaced with actual)
    forecast.forecasts['6_months']?.risk_score || 0,
    forecast.forecasts['12_months']?.risk_score || 0,
    forecast.forecasts['24_months']?.risk_score || 0,
  ];

  // Create curve points
  const curvePoints = riskScores.map((score, index) => {
    const x = (index - 1.5) * 2; // Spread along x-axis
    const y = score * 3 - 1.5; // Map risk score to y position
    return new THREE.Vector3(x, y, 0);
  });

  // Create smooth curve
  const curve = new THREE.CatmullRomCurve3(curvePoints);
  const points = curve.getPoints(50);

  // Get color based on risk score
  const getColor = (score: number) => {
    if (score < 0.33) return '#10b981'; // green
    if (score < 0.67) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  return (
    <group>
      {/* Title */}
      <Text
        position={[0, 3, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        Risk Progression Forecast
      </Text>

      {/* Curve line */}
      <Line
        points={points}
        color="#06b6d4"
        lineWidth={3}
      />

      {/* Data points */}
      {curvePoints.map((point, index) => (
        <group key={index} position={point}>
          {/* Sphere at data point */}
          <Sphere args={[0.15, 16, 16]}>
            <meshStandardMaterial 
              color={getColor(riskScores[index])}
              emissive={getColor(riskScores[index])}
              emissiveIntensity={0.5}
            />
          </Sphere>

          {/* Time label */}
          <Text
            position={[0, -0.5, 0]}
            fontSize={0.15}
            color="white"
            anchorX="center"
            anchorY="top"
          >
            {timePoints[index]}
          </Text>

          {/* Risk score label */}
          <Text
            position={[0, 0.4, 0]}
            fontSize={0.12}
            color={getColor(riskScores[index])}
            anchorX="center"
            anchorY="bottom"
          >
            {(riskScores[index] * 100).toFixed(0)}%
          </Text>

          {/* Uncertainty range (vertical line) */}
          {index > 0 && (
            <Line
              points={[
                new THREE.Vector3(0, -0.2, 0),
                new THREE.Vector3(0, 0.2, 0),
              ]}
              color="#6b7280"
              lineWidth={2}
              transparent
              opacity={0.5}
            />
          )}
        </group>
      ))}

      {/* Grid lines */}
      {[0, 0.33, 0.67, 1].map((value, index) => {
        const y = value * 3 - 1.5;
        return (
          <group key={index}>
            <Line
              points={[
                new THREE.Vector3(-3.5, y, -0.1),
                new THREE.Vector3(3.5, y, -0.1),
              ]}
              color="#374151"
              lineWidth={1}
              transparent
              opacity={0.3}
            />
            <Text
              position={[-3.8, y, 0]}
              fontSize={0.1}
              color="#9ca3af"
              anchorX="right"
              anchorY="middle"
            >
              {(value * 100).toFixed(0)}%
            </Text>
          </group>
        );
      })}

      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
    </group>
  );
}

export default function ProgressionForecast({ userId, currentMetrics }: ProgressionForecastProps) {
  const { user } = useAuthStore();
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const effectiveUserId = userId || user?.id;

  useEffect(() => {
    if (effectiveUserId && currentMetrics) {
      loadForecast();
    }
  }, [effectiveUserId, currentMetrics]);

  const loadForecast = async () => {
    if (!effectiveUserId || !currentMetrics) return;

    setLoading(true);
    setError(null);

    try {
      const userIdNum = typeof effectiveUserId === 'string' ? parseInt(effectiveUserId) : effectiveUserId;
      const data = await mlService.getForecast({
        user_id: userIdNum,
        current_metrics: currentMetrics,
        forecast_months: [6, 12, 24],
      });
      setForecast(data);
    } catch (err) {
      console.error('Error loading forecast:', err);
      setError('Failed to load progression forecast');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="text-center text-red-400">
          <p>{error}</p>
          <button
            onClick={loadForecast}
            className="mt-4 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!forecast) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="text-center text-gray-400">
          <p className="mb-4">No progression forecast available</p>
          <p className="text-sm">Complete health metrics to generate a progression forecast.</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="bg-gray-800 rounded-lg p-6"
    >
      <h2 className="text-2xl font-bold text-white mb-6">Progression Forecast</h2>

      {/* 3D Timeline Visualization */}
      <div className="h-96 bg-gray-900 rounded-lg overflow-hidden mb-6">
        <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
          <ForecastTimeline forecast={forecast} />
          <OrbitControls 
            enableZoom={true}
            enablePan={false}
            minDistance={5}
            maxDistance={12}
          />
        </Canvas>
      </div>

      {/* Detailed Forecast Data */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* 6 Month Forecast */}
        <div className="bg-gray-900 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-white">6 Months</h3>
            <span className={`text-2xl font-bold ${
              (forecast.forecasts['6_months']?.risk_score || 0) < 0.33 ? 'text-green-400' :
              (forecast.forecasts['6_months']?.risk_score || 0) < 0.67 ? 'text-amber-400' :
              'text-red-400'
            }`}>
              {((forecast.forecasts['6_months']?.risk_score || 0) * 100).toFixed(0)}%
            </span>
          </div>
          
          {forecast.forecasts['6_months']?.metrics && (
            <div className="space-y-2">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Predicted Metrics</p>
              {Object.entries(forecast.forecasts['6_months'].metrics).slice(0, 3).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-white font-medium">{typeof value === 'number' ? value.toFixed(1) : value}</span>
                </div>
              ))}
            </div>
          )}

          {/* Uncertainty indicator */}
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Confidence</span>
              <span className="text-cyan-400">{(forecast.confidence_level * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* 12 Month Forecast */}
        <div className="bg-gray-900 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-white">12 Months</h3>
            <span className={`text-2xl font-bold ${
              (forecast.forecasts['12_months']?.risk_score || 0) < 0.33 ? 'text-green-400' :
              (forecast.forecasts['12_months']?.risk_score || 0) < 0.67 ? 'text-amber-400' :
              'text-red-400'
            }`}>
              {((forecast.forecasts['12_months']?.risk_score || 0) * 100).toFixed(0)}%
            </span>
          </div>
          
          {forecast.forecasts['12_months']?.metrics && (
            <div className="space-y-2">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Predicted Metrics</p>
              {Object.entries(forecast.forecasts['12_months'].metrics).slice(0, 3).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-white font-medium">{typeof value === 'number' ? value.toFixed(1) : value}</span>
                </div>
              ))}
            </div>
          )}

          {/* Uncertainty indicator */}
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Confidence</span>
              <span className="text-cyan-400">{(forecast.confidence_level * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* 24 Month Forecast */}
        <div className="bg-gray-900 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-white">24 Months</h3>
            <span className={`text-2xl font-bold ${
              (forecast.forecasts['24_months']?.risk_score || 0) < 0.33 ? 'text-green-400' :
              (forecast.forecasts['24_months']?.risk_score || 0) < 0.67 ? 'text-amber-400' :
              'text-red-400'
            }`}>
              {((forecast.forecasts['24_months']?.risk_score || 0) * 100).toFixed(0)}%
            </span>
          </div>
          
          {forecast.forecasts['24_months']?.metrics && (
            <div className="space-y-2">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Predicted Metrics</p>
              {Object.entries(forecast.forecasts['24_months'].metrics).slice(0, 3).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-white font-medium">{typeof value === 'number' ? value.toFixed(1) : value}</span>
                </div>
              ))}
            </div>
          )}

          {/* Uncertainty indicator */}
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Confidence</span>
              <span className="text-cyan-400">{(forecast.confidence_level * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Progression Rates */}
      {Object.keys(forecast.progression_rates).length > 0 && (
        <div className="bg-gray-900 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">Estimated Progression Rates</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(forecast.progression_rates).map(([metric, rate]) => (
              <div key={metric} className="flex items-center justify-between">
                <span className="text-gray-400 text-sm capitalize">{metric.replace(/_/g, ' ')}</span>
                <span className={`font-medium ${rate < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  {rate > 0 ? '+' : ''}{rate.toFixed(2)}/year
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interpretation Guide */}
      <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-300 mb-2">Understanding Your Forecast</h4>
        <div className="space-y-2 text-sm text-blue-200">
          <p>
            This forecast predicts how your risk may change over the next 6, 12, and 24 months based on 
            current trends in your health metrics and cognitive assessments.
          </p>
          <p>
            <strong>Important:</strong> These are statistical projections, not certainties. Your actual 
            progression may differ based on lifestyle changes, treatments, and other factors. The shaded 
            areas represent uncertainty ranges in the predictions.
          </p>
          <p>
            Regular monitoring and proactive health management can help modify these trajectories. 
            Discuss these forecasts with your healthcare provider to develop an appropriate care plan.
          </p>
        </div>
      </div>

      {/* Forecast metadata */}
      <div className="mt-4 flex flex-col items-center gap-2">
        <div className="text-xs text-gray-500 text-center">
          Forecast generated on {new Date(forecast.generated_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
        <InlineDisclaimer />
      </div>
    </motion.div>
  );
}
