import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import * as THREE from 'three';
import { useDeviceCapabilities } from '../../hooks/useDeviceCapabilities';

interface BrainModelProps {
  deterioration?: number; // 0 to 1, where 1 is fully deteriorated
  position?: [number, number, number];
  quality?: 'low' | 'medium' | 'high' | 'auto';
}

/**
 * Animated brain model with particle system for neural connections
 * Shows fade/deterioration animation to represent memory loss
 * Optimized for mobile and low-end devices
 * Requirements: 10.2, 7.5
 */
export default function BrainModel({ 
  deterioration = 0, 
  position = [0, 0, 0],
  quality = 'auto'
}: BrainModelProps) {
  const brainRef = useRef<THREE.Group>(null);
  const particlesRef = useRef<THREE.Points>(null);
  const capabilities = useDeviceCapabilities();
  
  // Determine quality settings
  const effectiveQuality = quality === 'auto' ? capabilities.preferredQuality : quality;
  
  // Adjust particle count based on device capability
  const particleCount = useMemo(() => {
    switch (effectiveQuality) {
      case 'low': return 300;
      case 'medium': return 600;
      case 'high': return 1000;
      default: return 600;
    }
  }, [effectiveQuality]);
  
  // Adjust sphere detail based on quality
  const sphereDetail = useMemo(() => {
    switch (effectiveQuality) {
      case 'low': return [1.5, 16, 16] as [number, number, number];
      case 'medium': return [1.5, 24, 24] as [number, number, number];
      case 'high': return [1.5, 32, 32] as [number, number, number];
      default: return [1.5, 24, 24] as [number, number, number];
    }
  }, [effectiveQuality]);

  // Create particle system for neural connections
  const particles = useMemo(() => {
    const count = particleCount;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const sizes = new Float32Array(count);

    // Create particles in a brain-like shape (sphere with some irregularity)
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      
      // Spherical distribution with some randomness
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const radius = 1.5 + Math.random() * 0.5;
      
      positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = radius * Math.cos(phi);

      // Color gradient from blue to purple
      colors[i3] = 0.4 + Math.random() * 0.3; // R
      colors[i3 + 1] = 0.2 + Math.random() * 0.3; // G
      colors[i3 + 2] = 0.8 + Math.random() * 0.2; // B

      sizes[i] = Math.random() * 2 + 1;
    }

    return { positions, colors, sizes, count };
  }, []);

  // Animate brain rotation and particle fade
  useFrame(({ clock }) => {
    if (brainRef.current) {
      // Slow rotation
      brainRef.current.rotation.y = clock.getElapsedTime() * 0.1;
      brainRef.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.05) * 0.1;
    }

    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array as Float32Array;
      const time = clock.getElapsedTime();

      // Animate particles with wave effect
      for (let i = 0; i < particles.count; i++) {
        const i3 = i * 3;
        const y = positions[i3 + 1];

        // Add subtle floating motion
        positions[i3 + 1] = y + Math.sin(time + i * 0.1) * 0.01;
      }

      particlesRef.current.geometry.attributes.position.needsUpdate = true;

      // Fade particles based on deterioration
      const material = particlesRef.current.material as THREE.PointsMaterial;
      material.opacity = 1 - deterioration * 0.7;
    }
  });

  return (
    <group ref={brainRef} position={position}>
      {/* Main brain sphere with transparency */}
      <Sphere args={sphereDetail}>
        <meshStandardMaterial
          color="#6366f1"
          transparent
          opacity={0.3 - deterioration * 0.2}
          roughness={0.5}
          metalness={0.2}
        />
      </Sphere>

      {/* Inner glow sphere - skip on low quality */}
      {effectiveQuality !== 'low' && (
        <Sphere args={[1.3, sphereDetail[1], sphereDetail[2]]}>
          <meshBasicMaterial
            color="#8b5cf6"
            transparent
            opacity={0.1 - deterioration * 0.05}
          />
        </Sphere>
      )}

      {/* Neural connection particles */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particles.count}
            array={particles.positions}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-color"
            count={particles.count}
            array={particles.colors}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-size"
            count={particles.count}
            array={particles.sizes}
            itemSize={1}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.05}
          vertexColors
          transparent
          opacity={0.8}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>

      {/* Connecting lines between particles (neural pathways) - skip on low quality */}
      {effectiveQuality !== 'low' && (
        <NeuralConnections 
          particlePositions={particles.positions} 
          deterioration={deterioration}
          quality={effectiveQuality}
        />
      )}
    </group>
  );
}

/**
 * Neural connection lines between particles
 */
function NeuralConnections({ 
  particlePositions, 
  deterioration,
  quality = 'medium'
}: { 
  particlePositions: Float32Array; 
  deterioration: number;
  quality?: 'low' | 'medium' | 'high';
}) {
  const linesRef = useRef<THREE.LineSegments>(null);

  const lineGeometry = useMemo(() => {
    const positions: number[] = [];
    const colors: number[] = [];
    const particleCount = particlePositions.length / 3;
    // Adjust connection count based on quality
    const maxConnections = quality === 'high' ? 200 : 100;

    // Create connections between nearby particles
    for (let i = 0; i < maxConnections; i++) {
      const idx1 = Math.floor(Math.random() * particleCount) * 3;
      const idx2 = Math.floor(Math.random() * particleCount) * 3;

      positions.push(
        particlePositions[idx1],
        particlePositions[idx1 + 1],
        particlePositions[idx1 + 2],
        particlePositions[idx2],
        particlePositions[idx2 + 1],
        particlePositions[idx2 + 2]
      );

      // Purple-blue gradient for connections
      const color = new THREE.Color(0x8b5cf6);
      colors.push(color.r, color.g, color.b);
      colors.push(color.r, color.g, color.b);
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, [particlePositions]);

  useFrame(({ clock }) => {
    if (linesRef.current) {
      const material = linesRef.current.material as THREE.LineBasicMaterial;
      // Fade connections as deterioration increases
      material.opacity = (0.3 - deterioration * 0.25) * (0.5 + Math.sin(clock.getElapsedTime() * 2) * 0.2);
    }
  });

  return (
    <lineSegments ref={linesRef} geometry={lineGeometry}>
      <lineBasicMaterial
        vertexColors
        transparent
        opacity={0.3}
        blending={THREE.AdditiveBlending}
      />
    </lineSegments>
  );
}
