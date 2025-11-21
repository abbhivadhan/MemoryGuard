import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import * as THREE from 'three';

interface NeuralNetworkProps {
  position?: [number, number, number];
  nodeCount?: number;
}

/**
 * Animated neural network visualization with pulsing connections
 */
export default function NeuralNetwork({ 
  position = [0, 0, 0], 
  nodeCount = 50 
}: NeuralNetworkProps) {
  const groupRef = useRef<THREE.Group>(null);
  const linesRef = useRef<THREE.LineSegments>(null);

  // Generate nodes in a spherical distribution
  const nodes = useMemo(() => {
    return Array.from({ length: nodeCount }, () => {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const radius = 2 + Math.random() * 1;

      return new THREE.Vector3(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.sin(phi) * Math.sin(theta),
        radius * Math.cos(phi)
      );
    });
  }, [nodeCount]);

  // Generate connections between nearby nodes
  const lineGeometry = useMemo(() => {
    const positions: number[] = [];
    const colors: number[] = [];

    nodes.forEach((node1, i) => {
      nodes.forEach((node2, j) => {
        if (i < j && node1.distanceTo(node2) < 1.5) {
          positions.push(node1.x, node1.y, node1.z);
          positions.push(node2.x, node2.y, node2.z);

          const color = new THREE.Color().setHSL(0.6 + Math.random() * 0.2, 0.8, 0.6);
          colors.push(color.r, color.g, color.b);
          colors.push(color.r, color.g, color.b);
        }
      });
    });

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, [nodes]);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = clock.getElapsedTime() * 0.1;
      groupRef.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.2) * 0.1;
    }

    if (linesRef.current) {
      const material = linesRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.3 + Math.sin(clock.getElapsedTime() * 2) * 0.2;
    }
  });

  return (
    <group ref={groupRef} position={position}>
      {/* Nodes */}
      {nodes.map((node, i) => (
        <Sphere key={i} args={[0.08, 16, 16]} position={[node.x, node.y, node.z]}>
          <meshStandardMaterial
            color="#60a5fa"
            emissive="#60a5fa"
            emissiveIntensity={0.5}
            metalness={0.8}
            roughness={0.2}
          />
        </Sphere>
      ))}

      {/* Connections */}
      <lineSegments ref={linesRef} geometry={lineGeometry}>
        <lineBasicMaterial
          vertexColors
          transparent
          opacity={0.3}
          blending={THREE.AdditiveBlending}
          linewidth={2}
        />
      </lineSegments>
    </group>
  );
}
