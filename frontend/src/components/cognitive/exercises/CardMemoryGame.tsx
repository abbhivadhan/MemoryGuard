import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Box, Text } from '@react-three/drei';
import * as THREE from 'three';

interface Card {
  id: number;
  value: string;
  isFlipped: boolean;
  isMatched: boolean;
}

interface CardMemoryGameProps {
  pairs: number;
  timeLimit: number;
  showTime: number;
  onComplete: (score: number, timeTaken: number) => void;
}

const Card3D: React.FC<{
  card: Card;
  position: [number, number, number];
  onClick: () => void;
}> = ({ card, position, onClick }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame(() => {
    if (meshRef.current) {
      // Smooth rotation animation
      const targetRotation = card.isFlipped || card.isMatched ? Math.PI : 0;
      meshRef.current.rotation.y = THREE.MathUtils.lerp(
        meshRef.current.rotation.y,
        targetRotation,
        0.1
      );

      // Hover effect
      const targetScale = hovered && !card.isMatched ? 1.1 : 1;
      meshRef.current.scale.setScalar(
        THREE.MathUtils.lerp(meshRef.current.scale.x, targetScale, 0.1)
      );
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[1, 1.4, 0.1]} />
        <meshStandardMaterial
          color={card.isMatched ? '#10b981' : hovered ? '#a855f7' : '#6366f1'}
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>
      
      {/* Front face (value) */}
      {(card.isFlipped || card.isMatched) && (
        <Text
          position={[0, 0, 0.06]}
          fontSize={0.5}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          {card.value}
        </Text>
      )}
      
      {/* Back face (pattern) */}
      {!card.isFlipped && !card.isMatched && (
        <Text
          position={[0, 0, -0.06]}
          rotation={[0, Math.PI, 0]}
          fontSize={0.3}
          color="#4f46e5"
          anchorX="center"
          anchorY="middle"
        >
          ?
        </Text>
      )}
    </group>
  );
};

const CardMemoryGame: React.FC<CardMemoryGameProps> = ({
  pairs,
  timeLimit,
  showTime,
  onComplete
}) => {
  const [cards, setCards] = useState<Card[]>([]);
  const [flippedCards, setFlippedCards] = useState<number[]>([]);
  const [timeLeft, setTimeLeft] = useState(timeLimit);
  const [startTime] = useState(Date.now());
  const [gameStarted, setGameStarted] = useState(false);
  const [gameOver, setGameOver] = useState(false);

  useEffect(() => {
    initializeGame();
  }, [pairs]);

  useEffect(() => {
    if (!gameStarted || gameOver) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          setGameOver(true);
          const timeTaken = Math.floor((Date.now() - startTime) / 1000);
          const matchedCount = cards.filter(c => c.isMatched).length / 2;
          const score = (matchedCount / pairs) * 100;
          onComplete(score, timeTaken);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [gameStarted, gameOver, cards, pairs, startTime, onComplete]);

  useEffect(() => {
    if (flippedCards.length === 2) {
      const [first, second] = flippedCards;
      const firstCard = cards.find(c => c.id === first);
      const secondCard = cards.find(c => c.id === second);

      if (firstCard && secondCard && firstCard.value === secondCard.value) {
        // Match found
        setTimeout(() => {
          setCards(prev =>
            prev.map(card =>
              card.id === first || card.id === second
                ? { ...card, isMatched: true, isFlipped: false }
                : card
            )
          );
          setFlippedCards([]);
          
          // Check if game is complete
          const allMatched = cards.every(c => 
            c.isMatched || c.id === first || c.id === second
          );
          if (allMatched) {
            setGameOver(true);
            const timeTaken = Math.floor((Date.now() - startTime) / 1000);
            onComplete(100, timeTaken);
          }
        }, showTime);
      } else {
        // No match
        setTimeout(() => {
          setCards(prev =>
            prev.map(card =>
              card.id === first || card.id === second
                ? { ...card, isFlipped: false }
                : card
            )
          );
          setFlippedCards([]);
        }, showTime);
      }
    }
  }, [flippedCards, cards, showTime, startTime, onComplete]);

  const initializeGame = () => {
    const symbols = ['🌟', '🎨', '🎭', '🎪', '🎯', '🎲', '🎸', '🎹', '🎺', '🎻', '🏆', '🏅', '⚡', '🔥', '💎'];
    const selectedSymbols = symbols.slice(0, pairs);
    const cardPairs = [...selectedSymbols, ...selectedSymbols];
    
    // Shuffle cards
    const shuffled = cardPairs
      .map((value, index) => ({
        id: index,
        value,
        isFlipped: false,
        isMatched: false
      }))
      .sort(() => Math.random() - 0.5);

    setCards(shuffled);
    setFlippedCards([]);
    setTimeLeft(timeLimit);
    setGameOver(false);
  };

  const handleCardClick = (cardId: number) => {
    if (gameOver || flippedCards.length >= 2) return;
    
    const card = cards.find(c => c.id === cardId);
    if (!card || card.isFlipped || card.isMatched) return;

    if (!gameStarted) {
      setGameStarted(true);
    }

    setCards(prev =>
      prev.map(c => (c.id === cardId ? { ...c, isFlipped: true } : c))
    );
    setFlippedCards(prev => [...prev, cardId]);
  };

  const getGridLayout = () => {
    const totalCards = pairs * 2;
    const cols = Math.ceil(Math.sqrt(totalCards));
    const rows = Math.ceil(totalCards / cols);
    return { cols, rows };
  };

  const { cols, rows } = getGridLayout();
  const spacing = 1.6;

  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-gray-900 to-black">
      {/* HUD */}
      <div className="absolute top-4 left-0 right-0 z-10 flex justify-between px-8">
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-400 text-sm">Time Left</div>
          <div className="text-white text-2xl font-bold">
            {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
          </div>
        </div>
        
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-400 text-sm">Matches</div>
          <div className="text-white text-2xl font-bold">
            {cards.filter(c => c.isMatched).length / 2} / {pairs}
          </div>
        </div>
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />

        {cards.map((card, index) => {
          const col = index % cols;
          const row = Math.floor(index / cols);
          const x = (col - (cols - 1) / 2) * spacing;
          const y = ((rows - 1) / 2 - row) * spacing;

          return (
            <Card3D
              key={card.id}
              card={card}
              position={[x, y, 0]}
              onClick={() => handleCardClick(card.id)}
            />
          );
        })}
      </Canvas>

      {/* Game Over Overlay */}
      {gameOver && (
        <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-20">
          <div className="bg-gray-800 rounded-2xl p-8 text-center max-w-md">
            <h2 className="text-3xl font-bold text-white mb-4">
              {cards.every(c => c.isMatched) ? '🎉 Complete!' : '⏰ Time\'s Up!'}
            </h2>
            <p className="text-gray-300 mb-6">
              You matched {cards.filter(c => c.isMatched).length / 2} out of {pairs} pairs
            </p>
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

export default CardMemoryGame;
