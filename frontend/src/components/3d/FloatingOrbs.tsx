import { useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import { useSphere } from '@react-three/cannon';
import * as THREE from 'three';

interface OrbProps {
  position: [number, number, number];
  color: string;
  size: number;
}

function FloatingOrb({ position, color, size }: OrbProps) {
  const [ref, api] = useSphere(() => ({
    mass: 0.3,
    position,
    args: [size],
    linearDamping: 0.8,
    angularDamping: 0.8,
  }));

  useFrame(({ clock }) => {
    if (ref.current) {
      // Apply gentle upward force to keep orbs floating
      const time = clock.getElapsedTime();
      const floatForce = Math.sin(time * 0.5) * 0.02;
      api.applyForce([0, floatForce, 0], [0, 0, 0]);

      // Add gentle rotation
      ref.current.rotation.x += 0.005;
      ref.current.rotation.y += 0.008;
    }
  });

  return (
    // @ts-ignore - cannon ref type mismatch
    <Sphere ref={ref} args={[size, 32, 32]}>
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.4}
        metalness={0.9}
        roughness={0.1}
        transparent
        opacity={0.8}
      />
      {/* Inner glow */}
      <Sphere args={[size * 0.8, 32, 32]}>
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.3}
          blending={THREE.AdditiveBlending}
        />
      </Sphere>
    </Sphere>
  );
}

interface FloatingOrbsProps {
  count?: number;
}

/**
 * Physics-based floating orbs with glow effects
 */
export default function FloatingOrbs({ count = 15 }: FloatingOrbsProps) {
  const orbs = useMemo(() => {
    const colors = [
      '#60a5fa', // blue
      '#a78bfa', // purple
      '#f472b6', // pink
      '#fb923c', // orange
      '#34d399', // green
      '#fbbf24', // yellow
    ];

    return Array.from({ length: count }, (_, i) => ({
      position: [
        (Math.random() - 0.5) * 12,
        (Math.random() - 0.5) * 8,
        (Math.random() - 0.5) * 6,
      ] as [number, number, number],
      color: colors[i % colors.length],
      size: 0.3 + Math.random() * 0.4,
    }));
  }, [count]);

  return (
    <>
      {orbs.map((orb, i) => (
        <FloatingOrb key={i} {...orb} />
      ))}
    </>
  );
}
