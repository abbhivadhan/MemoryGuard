import { useState, useEffect } from 'react';
import BrainModel from './BrainModel';
import DNAHelix from './DNAHelix';
import NeuralNetwork from './NeuralNetwork';

interface DynamicSceneProps {
  section: number;
  deterioration: number;
}

/**
 * Dynamic 3D scene that changes based on scroll position
 */
export default function DynamicScene({ section, deterioration }: DynamicSceneProps) {
  const [currentScene, setCurrentScene] = useState(0);

  useEffect(() => {
    setCurrentScene(section);
  }, [section]);

  return (
    <>
      {/* Scene 0: Hero - Brain only */}
      <group visible={currentScene === 0}>
        <BrainModel position={[0, 0, 0]} deterioration={deterioration} />
      </group>

      {/* Scene 1: Understanding - DNA Helix */}
      <group visible={currentScene === 1}>
        <DNAHelix position={[0, 0, 0]} scale={1} />
      </group>

      {/* Scene 2: Detection - Neural Network */}
      <group visible={currentScene === 2}>
        <NeuralNetwork position={[0, 0, 0]} nodeCount={70} />
      </group>

      {/* Scene 3: Progression - Combined visualization */}
      <group visible={currentScene === 3}>
        <BrainModel position={[0, 0, 0]} deterioration={0.5} />
        <NeuralNetwork position={[0, 0, 0]} nodeCount={50} />
      </group>

      {/* Scene 4: Solution - Full system */}
      <group visible={currentScene >= 4}>
        <BrainModel position={[0, 0, 0]} deterioration={0} />
        <DNAHelix position={[3, 0, 0]} scale={0.7} />
      </group>
    </>
  );
}
