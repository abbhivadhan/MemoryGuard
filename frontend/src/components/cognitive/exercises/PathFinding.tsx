import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface PathFindingProps {
  gridSize: number;
  obstacles: number;
  onComplete: (score: number, timeTaken: number) => void;
}

interface Cell {
  row: number;
  col: number;
  isObstacle: boolean;
  isStart: boolean;
  isEnd: boolean;
  isPath: boolean;
  isVisited: boolean;
}

const PathFinding: React.FC<PathFindingProps> = ({
  gridSize,
  obstacles,
  onComplete
}) => {
  const [grid, setGrid] = useState<Cell[][]>([]);
  const [path, setPath] = useState<[number, number][]>([]);
  const [optimalPath, setOptimalPath] = useState<[number, number][]>([]);
  const [gameComplete, setGameComplete] = useState(false);
  const [startTime] = useState(Date.now());
  const [moves, setMoves] = useState(0);

  useEffect(() => {
    initializeGrid();
  }, [gridSize, obstacles]);

  const initializeGrid = () => {
    const newGrid: Cell[][] = [];
    
    // Create empty grid
    for (let row = 0; row < gridSize; row++) {
      newGrid[row] = [];
      for (let col = 0; col < gridSize; col++) {
        newGrid[row][col] = {
          row,
          col,
          isObstacle: false,
          isStart: row === 0 && col === 0,
          isEnd: row === gridSize - 1 && col === gridSize - 1,
          isPath: false,
          isVisited: false
        };
      }
    }

    // Add random obstacles
    let obstaclesPlaced = 0;
    while (obstaclesPlaced < obstacles) {
      const row = Math.floor(Math.random() * gridSize);
      const col = Math.floor(Math.random() * gridSize);
      
      // Don't place obstacles on start or end
      if ((row === 0 && col === 0) || (row === gridSize - 1 && col === gridSize - 1)) {
        continue;
      }
      
      if (!newGrid[row][col].isObstacle) {
        newGrid[row][col].isObstacle = true;
        obstaclesPlaced++;
      }
    }

    setGrid(newGrid);
    setPath([[0, 0]]);
    
    // Calculate optimal path using BFS
    const optimal = findOptimalPath(newGrid);
    setOptimalPath(optimal);
  };

  const findOptimalPath = (grid: Cell[][]): [number, number][] => {
    const queue: [[number, number], [number, number][]][] = [[[0, 0], [[0, 0]]]];
    const visited = new Set<string>();
    visited.add('0,0');

    const directions: [number, number][] = [[0, 1], [1, 0], [0, -1], [-1, 0]];

    while (queue.length > 0) {
      const [[row, col], path] = queue.shift()!;

      if (row === gridSize - 1 && col === gridSize - 1) {
        return path;
      }

      for (const [dr, dc] of directions) {
        const newRow = row + dr;
        const newCol = col + dc;
        const key = `${newRow},${newCol}`;

        if (
          newRow >= 0 && newRow < gridSize &&
          newCol >= 0 && newCol < gridSize &&
          !visited.has(key) &&
          !grid[newRow][newCol].isObstacle
        ) {
          visited.add(key);
          const newPath: [number, number][] = [...path, [newRow, newCol]];
          queue.push([[newRow, newCol], newPath]);
        }
      }
    }

    return [];
  };

  const handleCellClick = (row: number, col: number) => {
    if (gameComplete) return;

    const lastPos = path[path.length - 1];
    const [lastRow, lastCol] = lastPos;

    // Check if adjacent
    const isAdjacent = 
      (Math.abs(row - lastRow) === 1 && col === lastCol) ||
      (Math.abs(col - lastCol) === 1 && row === lastRow);

    if (!isAdjacent) return;

    // Check if obstacle
    if (grid[row][col].isObstacle) return;

    // Add to path
    const newPath: [number, number][] = [...path, [row, col]];
    setPath(newPath);
    setMoves(prev => prev + 1);

    // Update grid
    const newGrid = grid.map(r => r.map(c => ({ ...c, isPath: false, isVisited: false })));
    newPath.forEach(([r, c]) => {
      newGrid[r][c].isPath = true;
    });
    setGrid(newGrid);

    // Check if reached end
    if (row === gridSize - 1 && col === gridSize - 1) {
      setGameComplete(true);
      const timeTaken = Math.floor((Date.now() - startTime) / 1000);
      const efficiency = Math.min((optimalPath.length / newPath.length) * 100, 100);
      onComplete(Math.round(efficiency), timeTaken);
    }
  };

  const getCellColor = (cell: Cell) => {
    if (cell.isStart) return 'bg-green-500';
    if (cell.isEnd) return 'bg-red-500';
    if (cell.isObstacle) return 'bg-gray-700';
    if (cell.isPath) return 'bg-blue-400';
    return 'bg-gray-800/50';
  };

  const cellSize = Math.min(60, Math.floor(500 / gridSize));

  return (
    <div className="w-full h-screen bg-gradient-to-b from-gray-900 to-black flex flex-col items-center justify-center p-8">
      {/* Header */}
      <div className="absolute top-8 left-0 right-0 flex justify-between px-8">
        <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-300 text-sm">Moves</div>
          <div className="text-white text-2xl font-bold">{moves}</div>
        </div>
        <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-300 text-sm">Optimal</div>
          <div className="text-white text-2xl font-bold">{optimalPath.length - 1}</div>
        </div>
      </div>

      {/* Instructions */}
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold text-white mb-2">Path Finding</h2>
        <p className="text-gray-300">
          Click adjacent cells to move from <span className="text-green-400">start</span> to <span className="text-red-400">end</span>
        </p>
        <p className="text-gray-400 text-sm mt-2">
          Avoid obstacles and find the shortest path!
        </p>
      </div>

      {/* Grid */}
      <div 
        className="grid gap-1 bg-gray-900/50 p-4 rounded-xl backdrop-blur-sm"
        style={{
          gridTemplateColumns: `repeat(${gridSize}, ${cellSize}px)`,
        }}
      >
        {grid.map((row, rowIdx) =>
          row.map((cell, colIdx) => (
            <motion.button
              key={`${rowIdx}-${colIdx}`}
              whileHover={{ scale: cell.isObstacle ? 1 : 1.1 }}
              whileTap={{ scale: cell.isObstacle ? 1 : 0.95 }}
              onClick={() => handleCellClick(rowIdx, colIdx)}
              className={`${getCellColor(cell)} rounded transition-colors ${
                cell.isObstacle ? 'cursor-not-allowed' : 'cursor-pointer'
              }`}
              style={{
                width: `${cellSize}px`,
                height: `${cellSize}px`,
              }}
              disabled={cell.isObstacle}
            >
              {cell.isStart && <span className="text-white font-bold text-xs">S</span>}
              {cell.isEnd && <span className="text-white font-bold text-xs">E</span>}
            </motion.button>
          ))
        )}
      </div>

      {/* Legend */}
      <div className="mt-8 flex gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span className="text-gray-300">Start</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span className="text-gray-300">End</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-400 rounded"></div>
          <span className="text-gray-300">Your Path</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-700 rounded"></div>
          <span className="text-gray-300">Obstacle</span>
        </div>
      </div>

      {/* Complete Overlay */}
      {gameComplete && (
        <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-20">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-gray-800 rounded-2xl p-8 text-center max-w-md"
          >
            <h2 className="text-3xl font-bold text-white mb-4">
              🎉 Path Complete!
            </h2>
            <div className="space-y-2 mb-6">
              <p className="text-gray-300">
                Your moves: <span className="text-white font-bold">{moves}</span>
              </p>
              <p className="text-gray-300">
                Optimal: <span className="text-white font-bold">{optimalPath.length - 1}</span>
              </p>
              <p className="text-gray-300">
                Efficiency: <span className="text-white font-bold">
                  {Math.min((optimalPath.length / path.length) * 100, 100).toFixed(1)}%
                </span>
              </p>
            </div>
            <button
              onClick={initializeGrid}
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              Try Again
            </button>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default PathFinding;
