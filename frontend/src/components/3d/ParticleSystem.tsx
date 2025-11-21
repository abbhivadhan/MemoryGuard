import { useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { useSphere } from '@react-three/cannon';

interface MemoryFragmentProps {
  position: [number, number, number];
  index: number;
}

/**
 * Individual memory fragment with physics
 */
function MemoryFragment({ position, index }: MemoryFragmentProps) {
  const [ref, api] = useSphere(() => ({
    mass: 0.5,
    position,
    args: [0.15], // radius
    linearDamping: 0.5,
    angularDamping: 0.5,
  }));

  const { mouse, viewport } = useThree();

  // Track mouse position for interaction
  useFrame(() => {
    if (ref.current) {
      // Convert mouse position to 3D space
      const mouseX = (mouse.x * viewport.width) / 2;
      const mouseY = (mouse.y * viewport.height) / 2;

      // Get current position
      const pos = ref.current.position;
      const distance = Math.sqrt(
        Math.pow(pos.x - mouseX, 2) + 
        Math.pow(pos.y - mouseY, 2)
      );

      // Apply force when mouse is near
      if (distance < 3) {
        const force = 2 / (distance + 0.5);
        const dirX = (pos.x - mouseX) * force;
        const dirY = (pos.y - mouseY) * force;
        
        api.applyForce([dirX * 0.5, dirY * 0.5, 0], [0, 0, 0]);
      }

      // Rotate mesh
      ref.current.rotation.x += 0.01;
      ref.current.rotation.y += 0.01;
    }
  });

  // Random color for each fragment
  const color = useMemo(() => {
    const colors = ['#60a5fa', '#a78bfa', '#f472b6', '#fb923c', '#34d399'];
    return colors[index % colors.length];
  }, [index]);

  return (
    // @ts-ignore - cannon ref type mismatch
    <mesh ref={ref} castShadow>
      <boxGeometry args={[0.2, 0.2, 0.2]} />
      <meshStandardMaterial
        color={color}
        transparent
        opacity={0.8}
        roughness={0.3}
        metalness={0.7}
        emissive={color}
        emissiveIntensity={0.2}
      />
    </mesh>
  );
}

interface ParticleSystemProps {
  count?: number;
}

/**
 * Physics-based particle system with floating memory fragments
 * Particles respond to mouse interaction with gravity and collision
 */
export default function ParticleSystem({ count = 30 }: ParticleSystemProps) {
  // Generate random positions for particles
  const positions = useMemo(() => {
    const pos: [number, number, number][] = [];
    for (let i = 0; i < count; i++) {
      pos.push([
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 5,
      ]);
    }
    return pos;
  }, [count]);

  // Invisible boundaries to keep particles in view
  const boundaries = useMemo(() => [
    { position: [0, 6, 0] as [number, number, number], rotation: [0, 0, 0] as [number, number, number] },
    { position: [0, -6, 0] as [number, number, number], rotation: [0, 0, 0] as [number, number, number] },
    { position: [-10, 0, 0] as [number, number, number], rotation: [0, 0, Math.PI / 2] as [number, number, number] },
    { position: [10, 0, 0] as [number, number, number], rotation: [0, 0, Math.PI / 2] as [number, number, number] },
    { position: [0, 0, -5] as [number, number, number], rotation: [Math.PI / 2, 0, 0] as [number, number, number] },
    { position: [0, 0, 5] as [number, number, number], rotation: [Math.PI / 2, 0, 0] as [number, number, number] },
  ], []);

  return (
    <>
      {/* Invisible boundary walls */}
      {boundaries.map((boundary, i) => (
        <InvisibleWall key={i} {...boundary} />
      ))}

      {/* Memory fragments */}
      {positions.map((pos, i) => (
        <MemoryFragment key={i} position={pos} index={i} />
      ))}
    </>
  );
}

/**
 * Invisible physics wall to contain particles
 */
function InvisibleWall({ 
  position, 
  rotation
}: { 
  position: [number, number, number];
  rotation: [number, number, number];
}) {
  const [ref] = useSphere(() => ({
    type: 'Static',
    position,
    rotation,
    args: [0.1],
  }));

  // @ts-ignore - cannon ref type mismatch
  return <mesh ref={ref} visible={false} />;
}
