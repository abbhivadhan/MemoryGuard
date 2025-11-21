import { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text, Sphere, Ring } from '@react-three/drei';
import { motion } from 'framer-motion';
import { mlService, PredictionResponse } from '../../services/mlService';
import { useAuthStore } from '../../store/authStore';

interface RiskAssessmentProps {
  userId?: number | string;
  prediction?: PredictionResponse | null;
}

// 3D Risk Gauge Component
function RiskGauge({ riskScore, riskLevel }: { riskScore: number; riskLevel: string }) {
  const getColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return '#10b981'; // green
      case 'moderate':
        return '#f59e0b'; // amber
      case 'high':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  const color = getColor(riskLevel);

  return (
    <group>
      {/* Background ring */}
      <Ring args={[1.8, 2, 64]} rotation={[0, 0, 0]}>
        <meshBasicMaterial color="#1f2937" transparent opacity={0.3} />
      </Ring>

      {/* Risk level ring */}
      <Ring 
        args={[1.8, 2, 64, 1, 0, riskScore * Math.PI * 2]} 
        rotation={[0, 0, -Math.PI / 2]}
      >
        <meshBasicMaterial color={color} />
      </Ring>

      {/* Center sphere */}
      <Sphere args={[1.5, 32, 32]}>
        <meshStandardMaterial 
          color={color} 
          emissive={color}
          emissiveIntensity={0.3}
          metalness={0.8}
          roughness={0.2}
        />
      </Sphere>

      {/* Risk score text */}
      <Text
        position={[0, 0, 1.6]}
        fontSize={0.5}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        {(riskScore * 100).toFixed(0)}%
      </Text>

      {/* Risk level text */}
      <Text
        position={[0, -0.6, 1.6]}
        fontSize={0.25}
        color={color}
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-regular.woff"
      >
        {riskLevel.toUpperCase()}
      </Text>

      {/* Ambient light */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
    </group>
  );
}

export default function RiskAssessment({ userId, prediction: externalPrediction }: RiskAssessmentProps) {
  const { user } = useAuthStore();
  const [prediction, setPrediction] = useState<PredictionResponse | null>(externalPrediction || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const effectiveUserId = userId || user?.id;

  useEffect(() => {
    if (!externalPrediction && effectiveUserId) {
      loadLatestPrediction();
    }
  }, [effectiveUserId, externalPrediction]);

  const loadLatestPrediction = async () => {
    if (!effectiveUserId) return;

    setLoading(true);
    setError(null);

    try {
      const userIdNum = typeof effectiveUserId === 'string' ? parseInt(effectiveUserId) : effectiveUserId;
      const latestPrediction = await mlService.getLatestPrediction(userIdNum);
      setPrediction(latestPrediction);
    } catch (err) {
      console.error('Error loading prediction:', err);
      setError('Failed to load risk assessment');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-center h-64">
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
            onClick={loadLatestPrediction}
            className="mt-4 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="text-center text-gray-400">
          <p className="mb-4">No risk assessment available</p>
          <p className="text-sm">Complete health metrics and cognitive assessments to generate a risk assessment.</p>
        </div>
      </div>
    );
  }

  const riskScore = prediction.probability || 0;
  const riskLevel = prediction.risk_level || 'unknown';
  const confidenceLower = prediction.confidence_interval_lower || 0;
  const confidenceUpper = prediction.confidence_interval_upper || 0;
  const confidenceScore = prediction.confidence_score || 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-gray-800 rounded-lg p-6"
    >
      <h2 className="text-2xl font-bold text-white mb-6">Risk Assessment</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 3D Risk Gauge */}
        <div className="h-80 bg-gray-900 rounded-lg overflow-hidden">
          <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
            <RiskGauge riskScore={riskScore} riskLevel={riskLevel} />
            <OrbitControls 
              enableZoom={false} 
              enablePan={false}
              autoRotate
              autoRotateSpeed={0.5}
            />
          </Canvas>
        </div>

        {/* Risk Details */}
        <div className="space-y-4">
          {/* Risk Category */}
          <div className="bg-gray-900 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Risk Category</h3>
            <div className="flex items-center space-x-2">
              <div 
                className={`w-3 h-3 rounded-full ${
                  riskLevel.toLowerCase() === 'low' ? 'bg-green-500' :
                  riskLevel.toLowerCase() === 'moderate' ? 'bg-amber-500' :
                  riskLevel.toLowerCase() === 'high' ? 'bg-red-500' :
                  'bg-gray-500'
                }`}
              />
              <span className="text-xl font-bold text-white capitalize">{riskLevel}</span>
            </div>
          </div>

          {/* Confidence Interval */}
          <div className="bg-gray-900 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-3">Confidence Interval</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Lower Bound</span>
                <span className="text-white font-medium">{(confidenceLower * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${confidenceLower * 100}%` }}
                />
              </div>
              
              <div className="flex justify-between text-sm mt-3">
                <span className="text-gray-400">Upper Bound</span>
                <span className="text-white font-medium">{(confidenceUpper * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${confidenceUpper * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Confidence Score */}
          <div className="bg-gray-900 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Model Confidence</h3>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-white">{(confidenceScore * 100).toFixed(1)}%</span>
              <span className="text-sm text-gray-400">confidence</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
              <div 
                className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${confidenceScore * 100}%` }}
              />
            </div>
          </div>

          {/* Assessment Date */}
          <div className="bg-gray-900 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Assessment Date</h3>
            <p className="text-white">
              {new Date(prediction.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>

          {/* Model Version */}
          {prediction.model_version && (
            <div className="text-xs text-gray-500 text-center">
              Model: {prediction.model_version}
            </div>
          )}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-amber-900/20 border border-amber-700/50 rounded-lg">
        <p className="text-sm text-amber-200">
          <strong>Medical Disclaimer:</strong> This risk assessment is for informational purposes only 
          and should not be used as a substitute for professional medical advice, diagnosis, or treatment. 
          Always consult with a qualified healthcare professional.
        </p>
      </div>
    </motion.div>
  );
}
