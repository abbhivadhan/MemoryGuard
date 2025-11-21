/**
 * 3D Tutorial component for demonstrating recommendation activities
 * Requirements: 15.6
 */

import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Box, Sphere, Torus } from '@react-three/drei';
import { Vector3 } from 'three';

interface TutorialStep {
  title: string;
  description: string;
  animation: 'exercise' | 'meditation' | 'diet' | 'cognitive' | 'social';
}

interface RecommendationTutorial3DProps {
  category: 'diet' | 'exercise' | 'sleep' | 'cognitive' | 'social';
  onComplete?: () => void;
}

// Animated exercise figure
const ExerciseFigure: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);
  const [phase, setPhase] = useState(0);

  useFrame((state) => {
    if (groupRef.current) {
      // Simulate walking/running motion
      const time = state.clock.getElapsedTime();
      groupRef.current.position.y = Math.sin(time * 2) * 0.1;
      groupRef.current.rotation.z = Math.sin(time * 2) * 0.1;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Head */}
      <Sphere args={[0.3, 16, 16]} position={[0, 1.5, 0]}>
        <meshStandardMaterial color="#ffcc99" />
      </Sphere>
      
      {/* Body */}
      <Box args={[0.5, 0.8, 0.3]} position={[0, 0.8, 0]}>
        <meshStandardMaterial color="#4a90e2" />
      </Box>
      
      {/* Arms */}
      <Box args={[0.15, 0.6, 0.15]} position={[-0.4, 0.8, 0]} rotation={[0, 0, Math.PI / 6]}>
        <meshStandardMaterial color="#ffcc99" />
      </Box>
      <Box args={[0.15, 0.6, 0.15]} position={[0.4, 0.8, 0]} rotation={[0, 0, -Math.PI / 6]}>
        <meshStandardMaterial color="#ffcc99" />
      </Box>
      
      {/* Legs */}
      <Box args={[0.2, 0.7, 0.2]} position={[-0.15, 0.05, 0]}>
        <meshStandardMaterial color="#2c3e50" />
      </Box>
      <Box args={[0.2, 0.7, 0.2]} position={[0.15, 0.05, 0]}>
        <meshStandardMaterial color="#2c3e50" />
      </Box>
    </group>
  );
};


// Meditation/breathing animation
const MeditationFigure: React.FC = () => {
  const sphereRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (sphereRef.current) {
      const time = state.clock.getElapsedTime();
      // Breathing effect
      const scale = 1 + Math.sin(time * 0.5) * 0.2;
      sphereRef.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <group>
      {/* Sitting figure */}
      <Sphere args={[0.3, 16, 16]} position={[0, 0.8, 0]}>
        <meshStandardMaterial color="#ffcc99" />
      </Sphere>
      <Box args={[0.5, 0.6, 0.3]} position={[0, 0.3, 0]}>
        <meshStandardMaterial color="#9b59b6" />
      </Box>
      
      {/* Breathing aura */}
      <Sphere ref={sphereRef} args={[1, 32, 32]} position={[0, 0.5, 0]}>
        <meshStandardMaterial 
          color="#3498db" 
          transparent 
          opacity={0.2}
          wireframe
        />
      </Sphere>
    </group>
  );
};

// Diet/nutrition visualization
const DietVisualization: React.FC = () => {
  const items = [
    { pos: new Vector3(-1, 0.5, 0), color: '#e74c3c', label: 'Fruits' },
    { pos: new Vector3(0, 0.5, 0), color: '#2ecc71', label: 'Vegetables' },
    { pos: new Vector3(1, 0.5, 0), color: '#f39c12', label: 'Grains' },
    { pos: new Vector3(-0.5, -0.5, 0), color: '#3498db', label: 'Fish' },
    { pos: new Vector3(0.5, -0.5, 0), color: '#9b59b6', label: 'Nuts' },
  ];

  return (
    <group>
      {items.map((item, index) => (
        <group key={index} position={item.pos}>
          <Sphere args={[0.3, 16, 16]}>
            <meshStandardMaterial color={item.color} />
          </Sphere>
          <Text
            position={[0, -0.5, 0]}
            fontSize={0.15}
            color="white"
            anchorX="center"
            anchorY="middle"
          >
            {item.label}
          </Text>
        </group>
      ))}
    </group>
  );
};

// Cognitive training visualization
const CognitiveVisualization: React.FC = () => {
  const torusRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (torusRef.current) {
      torusRef.current.rotation.x = state.clock.getElapsedTime() * 0.5;
      torusRef.current.rotation.y = state.clock.getElapsedTime() * 0.3;
    }
  });

  return (
    <group>
      <Torus ref={torusRef} args={[1, 0.3, 16, 32]}>
        <meshStandardMaterial color="#e74c3c" wireframe />
      </Torus>
      <Sphere args={[0.5, 32, 32]}>
        <meshStandardMaterial color="#3498db" />
      </Sphere>
    </group>
  );
};

// Social interaction visualization
const SocialVisualization: React.FC = () => {
  const figures = [
    { pos: new Vector3(0, 0, 0), color: '#3498db' },
    { pos: new Vector3(-1.5, 0, 0), color: '#e74c3c' },
    { pos: new Vector3(1.5, 0, 0), color: '#2ecc71' },
    { pos: new Vector3(0, 0, 1.5), color: '#f39c12' },
  ];

  return (
    <group>
      {figures.map((fig, index) => (
        <Sphere key={index} args={[0.4, 16, 16]} position={fig.pos}>
          <meshStandardMaterial color={fig.color} />
        </Sphere>
      ))}
      {/* Connection lines */}
      {figures.map((fig, index) => (
        <React.Fragment key={`line-${index}`}>
          {figures.slice(index + 1).map((otherFig, otherIndex) => (
            <line key={`${index}-${otherIndex}`}>
              <bufferGeometry>
                <bufferAttribute
                  attach="attributes-position"
                  count={2}
                  array={new Float32Array([
                    fig.pos.x, fig.pos.y, fig.pos.z,
                    otherFig.pos.x, otherFig.pos.y, otherFig.pos.z
                  ])}
                  itemSize={3}
                />
              </bufferGeometry>
              <lineBasicMaterial color="#ffffff" opacity={0.3} transparent />
            </line>
          ))}
        </React.Fragment>
      ))}
    </group>
  );
};


const RecommendationTutorial3D: React.FC<RecommendationTutorial3DProps> = ({
  category,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);

  const tutorials: Record<string, TutorialStep[]> = {
    exercise: [
      {
        title: 'Aerobic Exercise',
        description: 'Walk briskly for 30 minutes, 5 days a week',
        animation: 'exercise'
      },
      {
        title: 'Strength Training',
        description: 'Include resistance exercises 2-3 times per week',
        animation: 'exercise'
      }
    ],
    sleep: [
      {
        title: 'Sleep Routine',
        description: 'Maintain consistent sleep schedule: 7-8 hours nightly',
        animation: 'meditation'
      },
      {
        title: 'Relaxation',
        description: 'Practice deep breathing before bed',
        animation: 'meditation'
      }
    ],
    diet: [
      {
        title: 'Mediterranean Diet',
        description: 'Focus on fruits, vegetables, fish, and olive oil',
        animation: 'diet'
      }
    ],
    cognitive: [
      {
        title: 'Brain Training',
        description: 'Engage in puzzles, reading, and learning new skills',
        animation: 'cognitive'
      }
    ],
    social: [
      {
        title: 'Social Engagement',
        description: 'Connect with friends and family regularly',
        animation: 'social'
      }
    ]
  };

  const steps = tutorials[category] || [];
  const currentTutorial = steps[currentStep];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete?.();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderAnimation = () => {
    switch (currentTutorial?.animation) {
      case 'exercise':
        return <ExerciseFigure />;
      case 'meditation':
        return <MeditationFigure />;
      case 'diet':
        return <DietVisualization />;
      case 'cognitive':
        return <CognitiveVisualization />;
      case 'social':
        return <SocialVisualization />;
      default:
        return null;
    }
  };

  if (!currentTutorial) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-400">No tutorial available for this category</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      {/* 3D Canvas */}
      <div className="flex-1 bg-gradient-to-b from-gray-900 to-gray-800 rounded-lg overflow-hidden">
        <Canvas camera={{ position: [0, 2, 5], fov: 50 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} />
          
          {renderAnimation()}
          
          <OrbitControls 
            enableZoom={true}
            enablePan={false}
            minDistance={3}
            maxDistance={10}
          />
        </Canvas>
      </div>

      {/* Tutorial Info */}
      <div className="bg-gray-800 p-6 rounded-b-lg">
        <div className="mb-4">
          <h3 className="text-2xl font-bold text-white mb-2">
            {currentTutorial.title}
          </h3>
          <p className="text-gray-300">
            {currentTutorial.description}
          </p>
        </div>

        {/* Progress indicator */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex space-x-2">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`h-2 w-12 rounded-full ${
                  index === currentStep
                    ? 'bg-blue-500'
                    : index < currentStep
                    ? 'bg-blue-700'
                    : 'bg-gray-600'
                }`}
              />
            ))}
          </div>
          <span className="text-gray-400 text-sm">
            {currentStep + 1} / {steps.length}
          </span>
        </div>

        {/* Navigation buttons */}
        <div className="flex justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>
          <button
            onClick={handleNext}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {currentStep === steps.length - 1 ? 'Complete' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecommendationTutorial3D;
