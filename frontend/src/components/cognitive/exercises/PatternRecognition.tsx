import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, Box, Cone, Torus } from '@react-three/drei';
import * as THREE from 'three';

interface PatternRecognitionProps {
  patternLength: number;
  options: number;
  onComplete: (score: number, timeTaken: number) => void;
}

const Shape3D: React.FC<{
  type: string;
  color: string;
  position: [number, number, number];
  scale?: number;
  onClick?: () => void;
  isAnswer?: boolean;
}> = ({ type, color, position, scale = 1, onClick, isAnswer }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      // Gentle rotation
      meshRef.current.rotation.y += 0.01;
      
      // Hover effect
      const targetScale = hovered ? scale * 1.2 : scale;
      meshRef.current.scale.setScalar(
        THREE.MathUtils.lerp(meshRef.current.scale.x, targetScale, 0.1)
      );

      // Floating animation
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime + position[0]) * 0.1;
    }
  });

  const renderShape = () => {
    const props = {
      ref: meshRef,
      onClick,
      onPointerOver: () => setHovered(true),
      onPointerOut: () => setHovered(false)
    };

    switch (type) {
      case 'sphere':
        return (
          <Sphere {...props} args={[0.5, 32, 32]}>
            <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
          </Sphere>
        );
      case 'cube':
        return (
          <Box {...props} args={[0.8, 0.8, 0.8]}>
            <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
          </Box>
        );
      case 'cone':
        return (
          <Cone {...props} args={[0.5, 1, 32]}>
            <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
          </Cone>
        );
      case 'torus':
        return (
          <Torus {...props} args={[0.4, 0.15, 16, 32]}>
            <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
          </Torus>
        );
      default:
        return null;
    }
  };

  return <group position={position}>{renderShape()}</group>;
};

const PatternRecognition: React.FC<PatternRecognitionProps> = ({
  patternLength,
  options,
  onComplete
}) => {
  const [pattern, setPattern] = useState<Array<{ type: string; color: string }>>([]);
  const [answerOptions, setAnswerOptions] = useState<Array<{ type: string; color: string }>>([]);
  const [correctAnswer, setCorrectAnswer] = useState(0);
  const [score, setScore] = useState(0);
  const [round, setRound] = useState(1);
  const [totalRounds] = useState(5);
  const [startTime] = useState(Date.now());
  const [feedback, setFeedback] = useState<'correct' | 'incorrect' | null>(null);

  const shapes = ['sphere', 'cube', 'cone', 'torus'];
  const colors = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

  useEffect(() => {
    generatePattern();
  }, [round]);

  const generatePattern = () => {
    // Generate a pattern sequence
    const newPattern: Array<{ type: string; color: string }> = [];
    
    // Create a simple pattern (alternating or repeating)
    const patternType = Math.random() > 0.5 ? 'alternating' : 'repeating';
    
    if (patternType === 'alternating') {
      const shape1 = shapes[Math.floor(Math.random() * shapes.length)];
      const shape2 = shapes[Math.floor(Math.random() * shapes.length)];
      const color1 = colors[Math.floor(Math.random() * colors.length)];
      const color2 = colors[Math.floor(Math.random() * colors.length)];
      
      for (let i = 0; i < patternLength; i++) {
        newPattern.push({
          type: i % 2 === 0 ? shape1 : shape2,
          color: i % 2 === 0 ? color1 : color2
        });
      }
    } else {
      // Repeating pattern
      const shape = shapes[Math.floor(Math.random() * shapes.length)];
      const color = colors[Math.floor(Math.random() * colors.length)];
      
      for (let i = 0; i < patternLength; i++) {
        newPattern.push({ type: shape, color });
      }
    }

    setPattern(newPattern);

    // Generate answer options
    const correctNext = { ...newPattern[newPattern.length % 2] };
    const newOptions = [correctNext];
    
    // Add incorrect options
    while (newOptions.length < options) {
      const randomOption = {
        type: shapes[Math.floor(Math.random() * shapes.length)],
        color: colors[Math.floor(Math.random() * colors.length)]
      };
      
      // Ensure it's different from correct answer
      if (randomOption.type !== correctNext.type || randomOption.color !== correctNext.color) {
        newOptions.push(randomOption);
      }
    }

    // Shuffle options
    const shuffled = newOptions.sort(() => Math.random() - 0.5);
    setAnswerOptions(shuffled);
    setCorrectAnswer(shuffled.findIndex(opt => 
      opt.type === correctNext.type && opt.color === correctNext.color
    ));
    setFeedback(null);
  };

  const handleAnswer = (index: number) => {
    if (feedback) return; // Prevent multiple clicks

    const isCorrect = index === correctAnswer;
    setFeedback(isCorrect ? 'correct' : 'incorrect');

    if (isCorrect) {
      setScore(prev => prev + 1);
    }

    setTimeout(() => {
      if (round < totalRounds) {
        setRound(prev => prev + 1);
      } else {
        // Game complete
        const timeTaken = Math.floor((Date.now() - startTime) / 1000);
        const finalScore = ((score + (isCorrect ? 1 : 0)) / totalRounds) * 100;
        onComplete(finalScore, timeTaken);
      }
    }, 1500);
  };

  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-gray-900 to-black">
      {/* HUD */}
      <div className="absolute top-4 left-0 right-0 z-10 flex justify-between px-8">
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-400 text-sm">Round</div>
          <div className="text-white text-2xl font-bold">
            {round} / {totalRounds}
          </div>
        </div>
        
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-400 text-sm">Score</div>
          <div className="text-white text-2xl font-bold">{score}</div>
        </div>
      </div>

      {/* Instructions */}
      <div className="absolute top-24 left-0 right-0 z-10 text-center">
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg px-6 py-3 inline-block">
          <p className="text-white text-lg">
            What comes next in the pattern?
          </p>
        </div>
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 12], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />
        <spotLight position={[0, 10, 0]} intensity={0.5} />

        {/* Pattern Display */}
        {pattern.map((item, index) => (
          <Shape3D
            key={`pattern-${index}`}
            type={item.type}
            color={item.color}
            position={[
              (index - (patternLength - 1) / 2) * 2,
              2,
              0
            ]}
            scale={0.8}
          />
        ))}

        {/* Question Mark */}
        <Shape3D
          type="sphere"
          color="#6366f1"
          position={[
            (patternLength - (patternLength - 1) / 2) * 2,
            2,
            0
          ]}
          scale={0.8}
        />

        {/* Answer Options */}
        {answerOptions.map((option, index) => (
          <Shape3D
            key={`option-${index}`}
            type={option.type}
            color={option.color}
            position={[
              (index - (answerOptions.length - 1) / 2) * 2.5,
              -2,
              0
            ]}
            onClick={() => handleAnswer(index)}
            isAnswer={true}
          />
        ))}
      </Canvas>

      {/* Feedback */}
      {feedback && (
        <div className="absolute inset-0 flex items-center justify-center z-20 pointer-events-none">
          <div className={`text-6xl font-bold ${
            feedback === 'correct' ? 'text-green-400' : 'text-red-400'
          } animate-bounce`}>
            {feedback === 'correct' ? '✓ Correct!' : '✗ Try Again'}
          </div>
        </div>
      )}
    </div>
  );
};

export default PatternRecognition;
