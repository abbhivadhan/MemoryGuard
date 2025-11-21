import { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Vector3 } from 'three';
import * as THREE from 'three';

/**
 * Hook for mouse-based physics interactions
 * Tracks mouse position in 3D space for particle interactions
 */
export function useMousePosition3D() {
  const mousePosition = useRef(new Vector3(0, 0, 0));
  const mouseVelocity = useRef(new Vector3(0, 0, 0));
  const prevPosition = useRef(new Vector3(0, 0, 0));

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      // Convert screen coordinates to normalized device coordinates (-1 to +1)
      const x = (event.clientX / window.innerWidth) * 2 - 1;
      const y = -(event.clientY / window.innerHeight) * 2 + 1;
      
      prevPosition.current.copy(mousePosition.current);
      mousePosition.current.set(x * 5, y * 5, 0);
      
      // Calculate velocity
      mouseVelocity.current.subVectors(mousePosition.current, prevPosition.current);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return { mousePosition: mousePosition.current, mouseVelocity: mouseVelocity.current };
}

/**
 * Hook for smooth camera animations
 */
export function useSmoothCamera(targetPosition: Vector3, smoothness = 0.1) {
  useFrame(({ camera }) => {
    camera.position.lerp(targetPosition, smoothness);
    camera.lookAt(0, 0, 0);
  });
}

/**
 * Hook for rotation animations
 */
export function useRotation(speed: Vector3 = new Vector3(0, 0.01, 0)) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.x += speed.x;
      meshRef.current.rotation.y += speed.y;
      meshRef.current.rotation.z += speed.z;
    }
  });

  return meshRef;
}

/**
 * Hook for floating animation
 */
export function useFloating(amplitude = 0.5, frequency = 1) {
  const meshRef = useRef<THREE.Mesh>(null);
  const initialY = useRef<number>(0);

  useEffect(() => {
    if (meshRef.current) {
      initialY.current = meshRef.current.position.y;
    }
  }, []);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.position.y = initialY.current + Math.sin(clock.getElapsedTime() * frequency) * amplitude;
    }
  });

  return meshRef;
}
