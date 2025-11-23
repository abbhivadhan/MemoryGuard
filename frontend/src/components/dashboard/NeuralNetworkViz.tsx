import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface NeuralNetworkVizProps {
  nodeCount?: number;
  layers?: number;
  color?: string;
  animated?: boolean;
}

/**
 * 3D Neural Network Visualization
 * Shows interconnected nodes with physics-based animations
 */
export default function NeuralNetworkViz({
  nodeCount = 50,
  layers = 3,
  color = '#06b6d4',
  animated = true
}: NeuralNetworkVizProps) {
  const groupRef = useRef<THREE.Group>(null);
  const linesRef = useRef<THREE.LineSegments>(null);

  // Generate node positions
  const nodes = useMemo(() => {
    const positions: THREE.Vector3[] = [];
    const nodesPerLayer = Math.ceil(nodeCount / layers);

    for (let layer = 0; layer < layers; layer++) {
      const layerNodes = layer === layers - 1 ? nodeCount - positions.length : nodesPerLayer;
      const layerZ = (layer - (layers - 1) / 2) * 2;

      for (let i = 0; i < layerNodes; i++) {
        const angle = (i / layerNodes) * Math.PI * 2;
        const radius = 1.5 + Math.random() * 0.5;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        positions.push(new THREE.Vector3(x, y, layerZ));
      }
    }

    return positions;
  }, [nodeCount, layers]);

  // Generate connections between nodes
  const connections = useMemo(() => {
    const lines: [THREE.Vector3, THREE.Vector3][] = [];
    const maxDistance = 3;

    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const distance = nodes[i].distanceTo(nodes[j]);
        if (distance < maxDistance) {
          lines.push([nodes[i], nodes[j]]);
        }
      }
    }

    return lines;
  }, [nodes]);

  // Create line geometry
  const lineGeometry = useMemo(() => {
    const positions: number[] = [];
    const colors: number[] = [];

    connections.forEach(([start, end]) => {
      positions.push(start.x, start.y, start.z);
      positions.push(end.x, end.y, end.z);

      const c = new THREE.Color(color);
      colors.push(c.r, c.g, c.b);
      colors.push(c.r, c.g, c.b);
    });

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, [connections, color]);

  // Animation
  useFrame(({ clock }) => {
    if (!animated) return;

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
    <group ref={groupRef}>
      {/* Nodes */}
      {nodes.map((position, index) => (
        <Node
          key={index}
          position={position}
          color={color}
          index={index}
          animated={animated}
        />
      ))}

      {/* Connections */}
      <lineSegments ref={linesRef} geometry={lineGeometry}>
        <lineBasicMaterial
          vertexColors
          transparent
          opacity={0.3}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>
    </group>
  );
}

interface NodeProps {
  position: THREE.Vector3;
  color: string;
  index: number;
  animated: boolean;
}

function Node({ position, color, index, animated }: NodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!animated || !meshRef.current) return;

    const time = clock.getElapsedTime();
    const scale = 1 + Math.sin(time * 2 + index * 0.1) * 0.2;
    meshRef.current.scale.setScalar(scale);
  });

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.05, 16, 16]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.5}
        transparent
        opacity={0.8}
      />
      {/* Glow effect */}
      <pointLight color={color} intensity={0.5} distance={1} />
    </mesh>
  );
}
