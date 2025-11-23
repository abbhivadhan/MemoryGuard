import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface StarfieldProps {
  count?: number;
}

/**
 * 3D Starfield with physics-based movement
 * Creates a space-like atmosphere with twinkling stars
 */
export default function Starfield({ count = 200 }: StarfieldProps) {
  const pointsRef = useRef<THREE.Points>(null);

  // Generate star positions and properties
  const { positions, colors, sizes, velocities } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    const velocities = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;

      // Random position in a large sphere
      const radius = 15 + Math.random() * 20;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = radius * Math.cos(phi) - 10;

      // White to light blue colors
      const colorVariation = Math.random();
      if (colorVariation < 0.7) {
        // White stars
        colors[i3] = 1;
        colors[i3 + 1] = 1;
        colors[i3 + 2] = 1;
      } else if (colorVariation < 0.85) {
        // Light blue stars
        colors[i3] = 0.8;
        colors[i3 + 1] = 0.9;
        colors[i3 + 2] = 1;
      } else {
        // Slight yellow tint
        colors[i3] = 1;
        colors[i3 + 1] = 0.95;
        colors[i3 + 2] = 0.8;
      }

      // Random size
      sizes[i] = Math.random() * 2 + 0.5;

      // Slow drift velocity
      velocities[i3] = (Math.random() - 0.5) * 0.002;
      velocities[i3 + 1] = (Math.random() - 0.5) * 0.002;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.002;
    }

    return { positions, colors, sizes, velocities };
  }, [count]);

  // Animate stars with physics
  useFrame(({ clock }) => {
    if (!pointsRef.current) return;

    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;
    const time = clock.getElapsedTime();

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;

      // Apply velocity for drift
      positions[i3] += velocities[i3];
      positions[i3 + 1] += velocities[i3 + 1];
      positions[i3 + 2] += velocities[i3 + 2];

      // Wrap around if star goes too far
      const distance = Math.sqrt(
        positions[i3] ** 2 +
        positions[i3 + 1] ** 2 +
        positions[i3 + 2] ** 2
      );

      if (distance > 35) {
        // Reset to opposite side
        const factor = 15 / distance;
        positions[i3] *= -factor;
        positions[i3 + 1] *= -factor;
        positions[i3 + 2] *= -factor;
      }
    }

    pointsRef.current.geometry.attributes.position.needsUpdate = true;

    // Rotate entire starfield slowly
    pointsRef.current.rotation.y = time * 0.01;
    pointsRef.current.rotation.x = time * 0.005;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={count}
          array={colors}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-size"
          count={count}
          array={sizes}
          itemSize={1}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.15}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}
