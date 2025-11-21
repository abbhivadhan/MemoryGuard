import { useRef, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { useSphere } from '@react-three/cannon';
import * as THREE from 'three';

interface ParticleProps {
  position: [number, number, number];
  velocity: [number, number, number];
  color: THREE.Color;
  size: number;
}

function Particle({ position, velocity, color, size }: ParticleProps) {
  const [ref, api] = useSphere(() => ({
    mass: 0.1 + Math.random() * 0.2,
    position,
    velocity,
    args: [size],
    linearDamping: 0.3,
    angularDamping: 0.3,
  }));

  const { mouse, viewport } = useThree();
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (ref.current) {
      const mouseX = (mouse.x * viewport.width) / 2;
      const mouseY = (mouse.y * viewport.height) / 2;

      const pos = ref.current.position;
      const dx = pos.x - mouseX;
      const dy = pos.y - mouseY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      // Repulsion force from mouse
      if (distance < 4) {
        const force = (4 - distance) * 0.3;
        const dirX = (dx / distance) * force;
        const dirY = (dy / distance) * force;
        api.applyForce([dirX, dirY, 0], [0, 0, 0]);
      }

      // Attraction to center
      const centerDist = Math.sqrt(pos.x * pos.x + pos.y * pos.y + pos.z * pos.z);
      if (centerDist > 6) {
        const pullForce = (centerDist - 6) * 0.05;
        api.applyForce(
          [(-pos.x / centerDist) * pullForce, (-pos.y / centerDist) * pullForce, (-pos.z / centerDist) * pullForce],
          [0, 0, 0]
        );
      }

      // Sync mesh with physics
      if (meshRef.current && ref.current) {
        meshRef.current.position.copy(ref.current.position);
        meshRef.current.rotation.x += 0.01;
        meshRef.current.rotation.y += 0.01;
      }
    }
  });

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[size, 1]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.5}
        metalness={0.9}
        roughness={0.1}
        transparent
        opacity={0.9}
      />
    </mesh>
  );
}

interface AdvancedParticlesProps {
  count?: number;
}

export default function AdvancedParticles({ count = 40 }: AdvancedParticlesProps) {
  const particles = useMemo(() => {
    return Array.from({ length: count }, () => {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const radius = 3 + Math.random() * 3;

      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);

      const hue = 0.55 + Math.random() * 0.15; // Blue to purple range
      const color = new THREE.Color().setHSL(hue, 0.8, 0.6);

      return {
        position: [x, y, z] as [number, number, number],
        velocity: [
          (Math.random() - 0.5) * 0.5,
          (Math.random() - 0.5) * 0.5,
          (Math.random() - 0.5) * 0.5,
        ] as [number, number, number],
        color,
        size: 0.1 + Math.random() * 0.15,
      };
    });
  }, [count]);

  return (
    <>
      {particles.map((particle, i) => (
        <Particle key={i} {...particle} />
      ))}
    </>
  );
}
