import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Float, Sphere, MeshDistortMaterial, Torus, Icosahedron } from '@react-three/drei';
import * as THREE from 'three';

interface DashboardSceneProps {
  activeTab: string;
  hoveredCard: string | null;
}

/**
 * Dynamic 3D scene for dashboard with physics-based animations
 * Responds to user interactions and tab changes
 */
export default function DashboardScene({ activeTab, hoveredCard }: DashboardSceneProps) {
  const groupRef = useRef<THREE.Group>(null);

  // Animate scene based on active tab
  useFrame(({ clock }) => {
    if (groupRef.current) {
      const time = clock.getElapsedTime();
      groupRef.current.rotation.y = time * 0.05;
      groupRef.current.rotation.x = Math.sin(time * 0.1) * 0.05;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Ambient particles */}
      <AmbientParticles count={100} />

      {/* Central orb that changes based on tab */}
      <CentralOrb activeTab={activeTab} hoveredCard={hoveredCard} />

      {/* Floating geometric shapes */}
      <FloatingGeometry />

      {/* Energy rings */}
      <EnergyRings />
    </group>
  );
}

/**
 * Central orb that reacts to interactions
 */
function CentralOrb({ activeTab, hoveredCard }: { activeTab: string; hoveredCard: string | null }) {
  const orbRef = useRef<THREE.Mesh>(null);

  const color = useMemo(() => {
    switch (activeTab) {
      case 'risk': return '#a855f7';
      case 'health': return '#06b6d4';
      case 'memory': return '#10b981';
      default: return '#6366f1';
    }
  }, [activeTab]);

  useFrame(({ clock }) => {
    if (orbRef.current) {
      const time = clock.getElapsedTime();
      const scale = hoveredCard ? 1.2 : 1.0;
      orbRef.current.scale.lerp(new THREE.Vector3(scale, scale, scale), 0.1);
      
      // Pulse effect
      const pulse = 1 + Math.sin(time * 2) * 0.05;
      orbRef.current.scale.multiplyScalar(pulse);
    }
  });

  return (
    <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
      <Sphere ref={orbRef} args={[1.5, 64, 64]} position={[0, 0, -5]}>
        <MeshDistortMaterial
          color={color}
          attach="material"
          distort={0.3}
          speed={2}
          roughness={0.2}
          metalness={0.8}
          transparent
          opacity={0.6}
        />
      </Sphere>
    </Float>
  );
}

/**
 * Ambient particle system
 */
function AmbientParticles({ count }: { count: number }) {
  const particlesRef = useRef<THREE.Points>(null);

  const particles = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const sizes = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      
      // Random position in a large sphere
      const radius = 10 + Math.random() * 10;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      
      positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = radius * Math.cos(phi);

      // Color gradient
      const colorChoice = Math.random();
      if (colorChoice < 0.33) {
        colors[i3] = 0.4; colors[i3 + 1] = 0.7; colors[i3 + 2] = 0.9; // Cyan
      } else if (colorChoice < 0.66) {
        colors[i3] = 0.6; colors[i3 + 1] = 0.4; colors[i3 + 2] = 0.9; // Purple
      } else {
        colors[i3] = 0.9; colors[i3 + 1] = 0.4; colors[i3 + 2] = 0.7; // Pink
      }

      sizes[i] = Math.random() * 2 + 0.5;
    }

    return { positions, colors, sizes };
  }, [count]);

  useFrame(({ clock }) => {
    if (particlesRef.current) {
      const time = clock.getElapsedTime();
      particlesRef.current.rotation.y = time * 0.02;
      particlesRef.current.rotation.x = time * 0.01;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={particles.positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={count}
          array={particles.colors}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-size"
          count={count}
          array={particles.sizes}
          itemSize={1}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.1}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

/**
 * Floating geometric shapes
 */
function FloatingGeometry() {
  return (
    <>
      <Float speed={2} rotationIntensity={1} floatIntensity={2}>
        <Icosahedron args={[0.5, 0]} position={[-4, 2, -3]}>
          <meshStandardMaterial
            color="#06b6d4"
            wireframe
            transparent
            opacity={0.3}
          />
        </Icosahedron>
      </Float>

      <Float speed={1.5} rotationIntensity={1.5} floatIntensity={1.5}>
        <Torus args={[0.6, 0.2, 16, 32]} position={[4, -2, -4]}>
          <meshStandardMaterial
            color="#a855f7"
            wireframe
            transparent
            opacity={0.3}
          />
        </Torus>
      </Float>

      <Float speed={1.8} rotationIntensity={0.8} floatIntensity={1.8}>
        <Icosahedron args={[0.4, 0]} position={[3, 3, -5]}>
          <meshStandardMaterial
            color="#ec4899"
            wireframe
            transparent
            opacity={0.3}
          />
        </Icosahedron>
      </Float>

      <Float speed={2.2} rotationIntensity={1.2} floatIntensity={2.2}>
        <Torus args={[0.5, 0.15, 16, 32]} position={[-3, -3, -3]}>
          <meshStandardMaterial
            color="#10b981"
            wireframe
            transparent
            opacity={0.3}
          />
        </Torus>
      </Float>
    </>
  );
}

/**
 * Energy rings that pulse
 */
function EnergyRings() {
  const ring1Ref = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);
  const ring3Ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();

    if (ring1Ref.current) {
      ring1Ref.current.rotation.z = time * 0.5;
      const scale = 1 + Math.sin(time * 2) * 0.1;
      ring1Ref.current.scale.set(scale, scale, 1);
    }

    if (ring2Ref.current) {
      ring2Ref.current.rotation.z = -time * 0.3;
      const scale = 1 + Math.sin(time * 2 + Math.PI / 3) * 0.1;
      ring2Ref.current.scale.set(scale, scale, 1);
    }

    if (ring3Ref.current) {
      ring3Ref.current.rotation.z = time * 0.4;
      const scale = 1 + Math.sin(time * 2 + (Math.PI * 2) / 3) * 0.1;
      ring3Ref.current.scale.set(scale, scale, 1);
    }
  });

  return (
    <group position={[0, 0, -5]}>
      <Torus ref={ring1Ref} args={[2, 0.02, 16, 100]}>
        <meshBasicMaterial
          color="#06b6d4"
          transparent
          opacity={0.4}
          blending={THREE.AdditiveBlending}
        />
      </Torus>

      <Torus ref={ring2Ref} args={[2.5, 0.02, 16, 100]}>
        <meshBasicMaterial
          color="#a855f7"
          transparent
          opacity={0.3}
          blending={THREE.AdditiveBlending}
        />
      </Torus>

      <Torus ref={ring3Ref} args={[3, 0.02, 16, 100]}>
        <meshBasicMaterial
          color="#ec4899"
          transparent
          opacity={0.2}
          blending={THREE.AdditiveBlending}
        />
      </Torus>
    </group>
  );
}
