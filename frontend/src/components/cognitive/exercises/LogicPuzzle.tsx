import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface LogicPuzzleProps {
  items: number;
  clues: number;
  onComplete: (score: number, timeTaken: number) => void;
}

const LogicPuzzle: React.FC<LogicPuzzleProps> = ({
  items,
  clues: _clues,
  onComplete
}) => {
  const [solution, setSolution] = useState<string[]>([]);
  const [userAnswer, setUserAnswer] = useState<string[]>([]);
  const [gameComplete, setGameComplete] = useState(false);
  const [startTime] = useState(Date.now());
  const [hints, setHints] = useState<string[]>([]);

  const colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange'];
  const positions = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth'];

  useEffect(() => {
    generatePuzzle();
  }, [items]);

  const generatePuzzle = () => {
    // Generate a random solution
    const availableColors = colors.slice(0, items);
    const shuffled = [...availableColors].sort(() => Math.random() - 0.5);
    setSolution(shuffled);
    setUserAnswer(Array(items).fill(''));
    
    // Generate hints
    const newHints: string[]= [];
    
    // Hint 1: Position of one color
    const hintIdx1 = Math.floor(Math.random() * items);
    newHints.push(`${shuffled[hintIdx1]} is in the ${positions[hintIdx1].toLowerCase()} position`);
    
    // Hint 2: Relative position
    if (items > 2) {
      const idx1 = Math.floor(Math.random() * (items - 1));
      const idx2 = idx1 + 1;
      newHints.push(`${shuffled[idx1]} is directly before ${shuffled[idx2]}`);
    }
    
    // Hint 3: Not in position
    if (items > 2) {
      const colorIdx = Math.floor(Math.random() * items);
      let wrongPos = Math.floor(Math.random() * items);
      while (wrongPos === colorIdx) {
        wrongPos = Math.floor(Math.random() * items);
      }
      newHints.push(`${shuffled[colorIdx]} is not in the ${positions[wrongPos].toLowerCase()} position`);
    }
    
    setHints(newHints);
  };

  const handleColorSelect = (position: number, color: string) => {
    const newAnswer = [...userAnswer];
    newAnswer[position] = color;
    setUserAnswer(newAnswer);
  };

  const checkSolution = () => {
    const correct = userAnswer.every((color, idx) => color === solution[idx]);
    setGameComplete(true);
    
    const timeTaken = Math.floor((Date.now() - startTime) / 1000);
    const score = correct ? 100 : 0;
    
    setTimeout(() => {
      onComplete(score, timeTaken);
    }, 2000);
  };

  const isCorrect = userAnswer.every((color, idx) => color === solution[idx]);
  const allFilled = userAnswer.every(color => color !== '');

  return (
    <div className="w-full h-screen bg-gradient-to-b from-purple-900 via-indigo-900 to-black flex flex-col items-center justify-center p-8">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className="text-4xl font-bold text-white mb-4">Logic Puzzle</h2>
          <p className="text-xl text-gray-300">
            Use the clues to determine the correct order of colors
          </p>
        </div>

        {/* Clues */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-8">
          <h3 className="text-xl font-semibold text-white mb-4">Clues:</h3>
          <div className="space-y-2">
            {hints.map((hint, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.2 }}
                className="text-gray-200 flex items-start gap-2"
              >
                <span className="text-purple-400 font-bold">{idx + 1}.</span>
                <span>{hint}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Answer Grid */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-6">
          <h3 className="text-xl font-semibold text-white mb-4">Your Answer:</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Array.from({ length: items }).map((_, idx) => (
              <div key={idx} className="text-center">
                <div className="text-gray-300 text-sm mb-2">{positions[idx]}</div>
                <select
                  value={userAnswer[idx]}
                  onChange={(e) => handleColorSelect(idx, e.target.value)}
                  className="w-full bg-gray-800 text-white border-2 border-gray-600 rounded-lg px-3 py-2 focus:border-purple-500 focus:outline-none"
                  disabled={gameComplete}
                >
                  <option value="">Select...</option>
                  {colors.slice(0, items).map(color => (
                    <option key={color} value={color}>{color}</option>
                  ))}
                </select>
                {userAnswer[idx] && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className={`mt-2 w-full h-16 rounded-lg`}
                    style={{
                      backgroundColor: userAnswer[idx].toLowerCase()
                    }}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        {!gameComplete && (
          <div className="text-center">
            <button
              onClick={checkSolution}
              disabled={!allFilled}
              className={`px-8 py-3 rounded-lg font-semibold text-white transition-colors ${
                allFilled
                  ? 'bg-purple-600 hover:bg-purple-700'
                  : 'bg-gray-600 cursor-not-allowed'
              }`}
            >
              Check Solution
            </button>
          </div>
        )}

        {/* Result */}
        {gameComplete && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center"
          >
            <div className={`text-6xl mb-4 ${isCorrect ? 'text-green-400' : 'text-red-400'}`}>
              {isCorrect ? '✓' : '✗'}
            </div>
            <h3 className="text-3xl font-bold text-white mb-2">
              {isCorrect ? 'Correct!' : 'Incorrect'}
            </h3>
            {!isCorrect && (
              <div className="mt-4">
                <p className="text-gray-300 mb-2">Correct solution:</p>
                <div className="flex gap-2 justify-center">
                  {solution.map((color, idx) => (
                    <div key={idx} className="text-center">
                      <div className="text-gray-400 text-xs mb-1">{positions[idx]}</div>
                      <div
                        className="w-16 h-16 rounded-lg"
                        style={{ backgroundColor: color.toLowerCase() }}
                      />
                      <div className="text-white text-sm mt-1">{color}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default LogicPuzzle;
