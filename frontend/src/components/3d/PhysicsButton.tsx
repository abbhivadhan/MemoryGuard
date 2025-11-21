import { useRef, useState } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Text, RoundedBox } from '@react-three/drei';
import { useSphere } from '@react-three/cannon';
import * as THREE from 'three';

interface PhysicsButtonProps {
  position: [number, number, number];
  text: string;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
}

/**
 * Modern 3D interactive button with physics-based hover effects
 * Sleek design with rounded corners and gradient effects
 */
export default function PhysicsButton({
  position,
  text,
  onClick,
  variant = 'primary',
}: PhysicsButtonProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const groupRef = useRef<THREE.Group>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const { mouse, viewport } = useThree();

  // Physics body for the button
  const [ref, api] = useSphere(() => ({
    mass: 1,
    position,
    args: [0.5],
    linearDamping: 0.9,
    angularDamping: 0.9,
  }));

  const colors = {
    primary: {
      base: '#6366f1',
      hover: '#818cf8',
      glow: '#a5b4fc',
    },
    secondary: {
      base: '#8b5cf6',
      hover: '#a78bfa',
      glow: '#c4b5fd',
    },
  };

  const currentColors = colors[variant];

  // Track mouse interaction
  useFrame(({ clock }) => {
    if (ref.current && groupRef.current) {
      // Convert mouse position to 3D space
      const mouseX = (mouse.x * viewport.width) / 2;
      const mouseY = (mouse.y * viewport.height) / 2;

      // Get current position
      const pos = ref.current.position;
      const distance = Math.sqrt(
        Math.pow(pos.x - mouseX, 2) + Math.pow(pos.y - mouseY, 2)
      );

      // Apply hover effect when mouse is near
      if (distance < 2) {
        setIsHovered(true);
        
        // Apply subtle repulsion force
        const force = 0.5 / (distance + 0.5);
        const dirX = (pos.x - mouseX) * force;
        const dirY = (pos.y - mouseY) * force;
        
        api.applyForce([dirX * 0.1, dirY * 0.1, 0], [0, 0, 0]);
      } else {
        setIsHovered(false);
      }

      // Sync group position with physics body
      groupRef.current.position.copy(pos);

      // Gentle floating animation
      groupRef.current.rotation.y = Math.sin(clock.getElapsedTime() * 0.5) * 0.05;
    }

    // Animate glow
    if (glowRef.current) {
      const material = glowRef.current.material as THREE.MeshBasicMaterial;
      material.opacity = isHovered 
        ? 0.3 + Math.sin(clock.getElapsedTime() * 3) * 0.1
        : 0.15;
    }
  });

  const handleClick = () => {
    setIsPressed(true);
    
    // Apply impulse on click
    api.applyImpulse([0, 0, -2], [0, 0, 0]);
    
    setTimeout(() => {
      setIsPressed(false);
      if (onClick) onClick();
    }, 200);
  };

  const currentColor = isPressed
    ? currentColors.base
    : isHovered
    ? currentColors.hover
    : currentColors.base;

  const scale = isPressed ? 0.95 : isHovered ? 1.08 : 1;

  return (
    <group ref={groupRef}>
      {/* Outer glow layer */}
      <RoundedBox
        ref={glowRef}
        args={[2.4, 0.8, 0.4]}
        radius={0.15}
        smoothness={4}
        scale={scale * 1.1}
      >
        <meshBasicMaterial
          color={currentColors.glow}
          transparent
          opacity={0.15}
          blending={THREE.AdditiveBlending}
        />
      </RoundedBox>

      {/* Main button body */}
      <RoundedBox
        // @ts-ignore - cannon ref type mismatch
        ref={ref}
        args={[2.2, 0.7, 0.35]}
        radius={0.12}
        smoothness={4}
        onClick={handleClick}
        scale={scale}
      >
        <meshStandardMaterial
          color={currentColor}
          roughness={0.2}
          metalness={0.9}
          emissive={currentColor}
          emissiveIntensity={isHovered ? 0.4 : 0.2}
        />
      </RoundedBox>

      {/* Inner highlight */}
      <RoundedBox
        args={[2.1, 0.6, 0.3]}
        radius={0.1}
        smoothness={4}
        scale={scale}
        position={[0, 0.05, 0]}
      >
        <meshBasicMaterial
          color="#ffffff"
          transparent
          opacity={isHovered ? 0.15 : 0.08}
          blending={THREE.AdditiveBlending}
        />
      </RoundedBox>

      {/* Button text */}
      <Text
        position={[0, 0, 0.2]}
        fontSize={0.22}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/Inter-Bold.woff"
        outlineWidth={0.015}
        outlineColor="#000000"
        letterSpacing={0.02}
      >
        {text}
      </Text>

      {/* Animated particles around button when hovered */}
      {isHovered && <ButtonParticles />}
    </group>
  );
}

/**
 * Small particles that orbit around the button when hovered
 */
function ButtonParticles() {
  const particlesRef = useRef<THREE.Points>(null);

  const particles = new Float32Array(20 * 3);
  for (let i = 0; i < 20; i++) {
    const angle = (i / 20) * Math.PI * 2;
    const radius = 1.3;
    particles[i * 3] = Math.cos(angle) * radius;
    particles[i * 3 + 1] = Math.sin(angle) * radius * 0.3;
    particles[i * 3 + 2] = 0;
  }

  useFrame(({ clock }) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.z = clock.getElapsedTime() * 0.5;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={20}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#ffffff"
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

/**
 * Simple 2D-style button for fallback or non-3D contexts
 */
export function SimpleButton({
  text,
  onClick,
  className = '',
}: {
  text: string;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg 
        transition-all duration-200 transform hover:scale-105 active:scale-95 
        shadow-lg hover:shadow-xl ${className}`}
    >
      {text}
    </button>
  );
}
