import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Cylinder } from '@react-three/drei';
import * as THREE from 'three';

interface TowerOfHanoiProps {
  disks: number;
  onComplete: (score: number, timeTaken: number) => void;
}

interface Disk {
  id: number;
  size: number;
  peg: number;
}

const Disk3D: React.FC<{
  disk: Disk;
  position: [number, number, number];
  onClick: () => void;
  isSelected: boolean;
}> = ({ disk, position, onClick, isSelected }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame(() => {
    if (meshRef.current) {
      // Hover and selection effects
      const targetY = position[1] + (isSelected ? 0.5 : 0) + (hovered ? 0.2 : 0);
      meshRef.current.position.y = THREE.MathUtils.lerp(
        meshRef.current.position.y,
        targetY,
        0.1
      );
    }
  });

  const colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];
  const color = colors[disk.id % colors.length];

  return (
    <mesh
      ref={meshRef}
      position={position}
      onClick={onClick}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <cylinderGeometry args={[disk.size, disk.size, 0.3, 32]} />
      <meshStandardMaterial
        color={isSelected ? '#ffffff' : color}
        metalness={0.5}
        roughness={0.3}
        emissive={isSelected ? color : '#000000'}
        emissiveIntensity={isSelected ? 0.5 : 0}
      />
    </mesh>
  );
};

const Peg3D: React.FC<{ position: [number, number, number] }> = ({ position }) => {
  return (
    <group position={position}>
      {/* Base */}
      <mesh position={[0, -0.1, 0]}>
        <cylinderGeometry args={[1.5, 1.5, 0.2, 32]} />
        <meshStandardMaterial color="#374151" metalness={0.3} roughness={0.7} />
      </mesh>
      
      {/* Pole */}
      <mesh position={[0, 1.5, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 3, 32]} />
        <meshStandardMaterial color="#6b7280" metalness={0.5} roughness={0.5} />
      </mesh>
    </group>
  );
};

const TowerOfHanoi: React.FC<TowerOfHanoiProps> = ({ disks, onComplete }) => {
  const [diskState, setDiskState] = useState<Disk[]>([]);
  const [selectedDisk, setSelectedDisk] = useState<number | null>(null);
  const [moves, setMoves] = useState(0);
  const [startTime] = useState(Date.now());
  const [gameComplete, setGameComplete] = useState(false);

  const minMoves = Math.pow(2, disks) - 1;

  useEffect(() => {
    initializeGame();
  }, [disks]);

  const initializeGame = () => {
    const initialDisks: Disk[] = [];
    for (let i = 0; i < disks; i++) {
      initialDisks.push({
        id: i,
        size: 1 - (i * 0.15),
        peg: 0
      });
    }
    setDiskState(initialDisks);
    setSelectedDisk(null);
    setMoves(0);
    setGameComplete(false);
  };

  const getDisksOnPeg = (peg: number) => {
    return diskState
      .filter(d => d.peg === peg)
      .sort((a, b) => b.size - a.size);
  };

  const getTopDisk = (peg: number) => {
    const disksOnPeg = getDisksOnPeg(peg);
    return disksOnPeg.length > 0 ? disksOnPeg[disksOnPeg.length - 1] : null;
  };

  const canPlaceDisk = (diskId: number, targetPeg: number) => {
    const disk = diskState.find(d => d.id === diskId);
    if (!disk) return false;

    const topDisk = getTopDisk(targetPeg);
    
    // Can place if peg is empty or disk is smaller than top disk
    return !topDisk || disk.size < topDisk.size;
  };

  const handleDiskClick = (diskId: number) => {
    const disk = diskState.find(d => d.id === diskId);
    if (!disk) return;

    // Check if this is the top disk on its peg
    const topDisk = getTopDisk(disk.peg);
    if (topDisk?.id !== diskId) return;

    if (selectedDisk === null) {
      // Select disk
      setSelectedDisk(diskId);
    } else if (selectedDisk === diskId) {
      // Deselect disk
      setSelectedDisk(null);
    }
  };

  const handlePegClick = (pegIndex: number) => {
    if (selectedDisk === null) return;

    const disk = diskState.find(d => d.id === selectedDisk);
    if (!disk || disk.peg === pegIndex) {
      setSelectedDisk(null);
      return;
    }

    if (canPlaceDisk(selectedDisk, pegIndex)) {
      // Move disk
      setDiskState(prev =>
        prev.map(d =>
          d.id === selectedDisk ? { ...d, peg: pegIndex } : d
        )
      );
      setMoves(prev => prev + 1);
      setSelectedDisk(null);

      // Check if game is complete
      setTimeout(() => {
        const allOnLastPeg = diskState.every(d => 
          d.id === selectedDisk ? pegIndex === 2 : d.peg === 2
        );
        
        if (allOnLastPeg) {
          setGameComplete(true);
          const timeTaken = Math.floor((Date.now() - startTime) / 1000);
          const efficiency = Math.min((minMoves / (moves + 1)) * 100, 100);
          onComplete(efficiency, timeTaken);
        }
      }, 100);
    } else {
      setSelectedDisk(null);
    }
  };

  const getDiskPosition = (disk: Disk): [number, number, number] => {
    const pegX = (disk.peg - 1) * 4;
    const disksOnPeg = getDisksOnPeg(disk.peg);
    const diskIndex = disksOnPeg.findIndex(d => d.id === disk.id);
    const y = 0.2 + (diskIndex * 0.35);
    
    return [pegX, y, 0];
  };

  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-gray-900 to-black">
      {/* HUD */}
      <div className="absolute top-4 left-0 right-0 z-10 flex justify-between px-8">
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-400 text-sm">Moves</div>
          <div className="text-white text-2xl font-bold">{moves}</div>
        </div>
        
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-400 text-sm">Optimal</div>
          <div className="text-white text-2xl font-bold">{minMoves}</div>
        </div>
      </div>

      {/* Instructions */}
      <div className="absolute top-24 left-0 right-0 z-10 text-center">
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg px-6 py-3 inline-block max-w-2xl">
          <p className="text-white">
            Move all disks to the rightmost peg. Click a disk to select it, then click a peg to move it.
            <br />
            <span className="text-gray-400 text-sm">
              Larger disks cannot be placed on smaller ones.
            </span>
          </p>
        </div>
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 4, 10], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, 10, 10]} intensity={0.5} />
        <spotLight position={[0, 10, 0]} intensity={0.8} angle={0.6} />

        {/* Pegs */}
        {[0, 1, 2].map((pegIndex) => (
          <group
            key={`peg-${pegIndex}`}
            onClick={() => handlePegClick(pegIndex)}
          >
            <Peg3D position={[(pegIndex - 1) * 4, 0, 0]} />
          </group>
        ))}

        {/* Disks */}
        {diskState.map((disk) => (
          <Disk3D
            key={disk.id}
            disk={disk}
            position={getDiskPosition(disk)}
            onClick={() => handleDiskClick(disk.id)}
            isSelected={selectedDisk === disk.id}
          />
        ))}
      </Canvas>

      {/* Game Complete Overlay */}
      {gameComplete && (
        <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-20">
          <div className="bg-gray-800 rounded-2xl p-8 text-center max-w-md">
            <h2 className="text-3xl font-bold text-white mb-4">
              🎉 Puzzle Solved!
            </h2>
            <div className="space-y-2 mb-6">
              <p className="text-gray-300">
                Moves: <span className="text-white font-bold">{moves}</span>
              </p>
              <p className="text-gray-300">
                Optimal: <span className="text-white font-bold">{minMoves}</span>
              </p>
              <p className="text-gray-300">
                Efficiency: <span className="text-white font-bold">
                  {Math.min((minMoves / moves) * 100, 100).toFixed(1)}%
                </span>
              </p>
            </div>
            <button
              onClick={initializeGame}
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              Play Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TowerOfHanoi;
