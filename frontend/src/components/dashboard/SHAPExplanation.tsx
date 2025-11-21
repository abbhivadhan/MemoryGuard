import { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text, Box } from '@react-three/drei';
import { motion } from 'framer-motion';
import * as THREE from 'three';
import { mlService, ExplanationResponse } from '../../services/mlService';

interface SHAPExplanationProps {
  predictionId: number;
}

// 3D Feature Importance Bar
function FeatureBar({ 
  feature, 
  value, 
  position, 
  maxValue,
  isPositive 
}: { 
  feature: string; 
  value: number; 
  position: [number, number, number];
  maxValue: number;
  isPositive: boolean;
}) {
  const normalizedValue = Math.abs(value) / maxValue;
  const barLength = normalizedValue * 3; // Scale to max 3 units
  const color = isPositive ? '#ef4444' : '#10b981'; // Red for positive (increases risk), green for negative (decreases risk)

  return (
    <group position={position}>
      {/* Bar */}
      <Box 
        args={[barLength, 0.3, 0.3]} 
        position={[barLength / 2, 0, 0]}
      >
        <meshStandardMaterial 
          color={color}
          emissive={color}
          emissiveIntensity={0.3}
          metalness={0.6}
          roughness={0.4}
        />
      </Box>

      {/* Feature label */}
      <Text
        position={[-0.2, 0, 0]}
        fontSize={0.15}
        color="white"
        anchorX="right"
        anchorY="middle"
        maxWidth={2}
      >
        {feature}
      </Text>

      {/* Value label */}
      <Text
        position={[barLength + 0.2, 0, 0]}
        fontSize={0.12}
        color={color}
        anchorX="left"
        anchorY="middle"
      >
        {value.toFixed(3)}
      </Text>
    </group>
  );
}

// 3D SHAP Visualization
function SHAPVisualization({ explanation }: { explanation: ExplanationResponse }) {
  const topFeatures = explanation.top_features.slice(0, 10); // Show top 10
  const maxValue = Math.max(...topFeatures.map(f => Math.abs(f.shap_value)));

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
        Feature Importance
      </Text>

      {/* Feature bars */}
      {topFeatures.map((feature, index) => (
        <FeatureBar
          key={feature.feature}
          feature={feature.feature.replace(/_/g, ' ')}
          value={feature.shap_value}
          position={[0, 2 - index * 0.5, 0]}
          maxValue={maxValue}
          isPositive={feature.shap_value > 0}
        />
      ))}

      {/* Legend */}
      <group position={[0, -3.5, 0]}>
        <Box args={[0.3, 0.15, 0.15]} position={[-1, 0, 0]}>
          <meshStandardMaterial color="#ef4444" />
        </Box>
        <Text
          position={[-0.6, 0, 0]}
          fontSize={0.12}
          color="white"
          anchorX="left"
          anchorY="middle"
        >
          Increases Risk
        </Text>

        <Box args={[0.3, 0.15, 0.15]} position={[1, 0, 0]}>
          <meshStandardMaterial color="#10b981" />
        </Box>
        <Text
          position={[1.4, 0, 0]}
          fontSize={0.12}
          color="white"
          anchorX="left"
          anchorY="middle"
        >
          Decreases Risk
        </Text>
      </group>

      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
    </group>
  );
}

export default function SHAPExplanation({ predictionId }: SHAPExplanationProps) {
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadExplanation();
  }, [predictionId]);

  const loadExplanation = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await mlService.getExplanation(predictionId);
      setExplanation(data);
    } catch (err) {
      console.error('Error loading explanation:', err);
      setError('Failed to load explanation');
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

  if (error || !explanation) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="text-center text-red-400">
          <p>{error || 'No explanation available'}</p>
          <button
            onClick={loadExplanation}
            className="mt-4 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="bg-gray-800 rounded-lg p-6"
    >
      <h2 className="text-2xl font-bold text-white mb-6">Risk Factor Analysis</h2>

      {/* 3D Visualization */}
      <div className="h-[600px] bg-gray-900 rounded-lg overflow-hidden mb-6">
        <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
          <SHAPVisualization explanation={explanation} />
          <OrbitControls 
            enableZoom={true}
            enablePan={true}
            minDistance={5}
            maxDistance={15}
          />
        </Canvas>
      </div>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Positive Contributors (Increase Risk) */}
        <div className="bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-red-400 mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
            </svg>
            Risk-Increasing Factors
          </h3>
          <div className="space-y-3">
            {explanation.positive_contributors.slice(0, 5).map((contributor, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-gray-300 text-sm capitalize">
                  {contributor.feature.replace(/_/g, ' ')}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.abs(contributor.contribution) * 100}%` }}
                    />
                  </div>
                  <span className="text-red-400 text-sm font-medium w-12 text-right">
                    +{(contributor.contribution * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Negative Contributors (Decrease Risk) */}
        <div className="bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-400 mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
            </svg>
            Protective Factors
          </h3>
          <div className="space-y-3">
            {explanation.negative_contributors.slice(0, 5).map((contributor, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-gray-300 text-sm capitalize">
                  {contributor.feature.replace(/_/g, ' ')}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.abs(contributor.contribution) * 100}%` }}
                    />
                  </div>
                  <span className="text-green-400 text-sm font-medium w-12 text-right">
                    {(contributor.contribution * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 p-4 bg-blue-900/20 border border-blue-700/50 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-300 mb-2">Understanding SHAP Values</h4>
        <p className="text-sm text-blue-200">
          SHAP (SHapley Additive exPlanations) values show how much each factor contributes to your risk assessment. 
          Positive values (red) increase risk, while negative values (green) decrease risk. 
          The length of each bar represents the magnitude of the contribution.
        </p>
      </div>
    </motion.div>
  );
}
