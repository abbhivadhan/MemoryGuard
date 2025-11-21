import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import * as THREE from 'three';

interface DNAHelixProps {
  position?: [number, number, number];
  scale?: number;
}

/**
 * Animated DNA helix representing genetic factors in Alzheimer's
 */
export default function DNAHelix({ position = [0, 0, 0], scale = 1 }: DNAHelixProps) {
  const groupRef = useRef<THREE.Group>(null);
  const helixCount = 40;
  const radius = 1.5 * scale;
  const height = 8 * scale;

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = clock.getElapsedTime() * 0.3;
    }
  });

  // Generate helix points
  const helixPoints = Array.from({ length: helixCount }, (_, i) => {
    const t = (i / helixCount) * Math.PI * 4;
    const y = (i / helixCount) * height - height / 2;
    
    return {
      pos1: [
        Math.cos(t) * radius,
        y,
        Math.sin(t) * radius,
      ] as [number, number, number],
      pos2: [
        Math.cos(t + Math.PI) * radius,
        y,
        Math.sin(t + Math.PI) * radius,
      ] as [number, number, number],
    };
  });

  return (
    <group ref={groupRef} position={position}>
      {helixPoints.map((point, i) => (
        <group key={i}>
          {/* Strand 1 */}
          <Sphere args={[0.15 * scale, 16, 16]} position={point.pos1}>
            <meshStandardMaterial
              color="#60a5fa"
              emissive="#60a5fa"
              emissiveIntensity={0.3}
              metalness={0.8}
              roughness={0.2}
            />
          </Sphere>
          
          {/* Strand 2 */}
          <Sphere args={[0.15 * scale, 16, 16]} position={point.pos2}>
            <meshStandardMaterial
              color="#a78bfa"
              emissive="#a78bfa"
              emissiveIntensity={0.3}
              metalness={0.8}
              roughness={0.2}
            />
          </Sphere>

          {/* Connecting bar */}
          <ConnectingBar start={point.pos1} end={point.pos2} scale={scale} />
        </group>
      ))}
    </group>
  );
}

function ConnectingBar({ 
  start, 
  end, 
  scale 
}: { 
  start: [number, number, number]; 
  end: [number, number, number];
  scale: number;
}) {
  const midpoint: [number, number, number] = [
    (start[0] + end[0]) / 2,
    (start[1] + end[1]) / 2,
    (start[2] + end[2]) / 2,
  ];

  const direction = new THREE.Vector3(
    end[0] - start[0],
    end[1] - start[1],
    end[2] - start[2]
  );
  const length = direction.length();
  const quaternion = new THREE.Quaternion();
  quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction.normalize()
  );

  return (
    <mesh position={midpoint} quaternion={quaternion}>
      <cylinderGeometry args={[0.05 * scale, 0.05 * scale, length, 8]} />
      <meshStandardMaterial
        color="#8b5cf6"
        emissive="#8b5cf6"
        emissiveIntensity={0.2}
        metalness={0.6}
        roughness={0.3}
      />
    </mesh>
  );
}
