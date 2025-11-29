import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface NumberSequenceProps {
  sequenceLength: number;
  displayTime: number;
  maxNumber: number;
  onComplete: (score: number, timeTaken: number) => void;
}

const NumberSequence: React.FC<NumberSequenceProps> = ({
  sequenceLength,
  displayTime,
  maxNumber,
  onComplete
}) => {
  const [sequence, setSequence] = useState<number[]>([]);
  const [userInput, setUserInput] = useState<number[]>([]);
  const [phase, setPhase] = useState<'ready' | 'showing' | 'input' | 'result'>('ready');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [round, setRound] = useState(1);
  const [startTime] = useState(Date.now());
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);

  const maxRounds = 5;

  const generateSequence = () => {
    const newSequence: number[] = [];
    for (let i = 0; i < sequenceLength; i++) {
      newSequence.push(Math.floor(Math.random() * (maxNumber + 1)));
    }
    return newSequence;
  };

  const startRound = () => {
    const newSequence = generateSequence();
    setSequence(newSequence);
    setUserInput([]);
    setCurrentIndex(0);
    setIsCorrect(null);
    setPhase('showing');
  };

  useEffect(() => {
    if (phase === 'showing' && currentIndex < sequence.length) {
      const timer = setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
      }, displayTime);
      return () => clearTimeout(timer);
    } else if (phase === 'showing' && currentIndex >= sequence.length) {
      setTimeout(() => setPhase('input'), 500);
    }
  }, [phase, currentIndex, sequence.length, displayTime]);

  const handleNumberClick = (num: number) => {
    if (phase !== 'input') return;

    const newInput = [...userInput, num];
    setUserInput(newInput);

    if (newInput.length === sequence.length) {
      checkAnswer(newInput);
    }
  };

  const checkAnswer = (input: number[]) => {
    const correct = input.every((num, idx) => num === sequence[idx]);
    setIsCorrect(correct);
    
    if (correct) {
      setScore(prev => prev + 100);
    }

    setPhase('result');

    setTimeout(() => {
      if (round < maxRounds) {
        setRound(prev => prev + 1);
        startRound();
      } else {
        const timeTaken = Math.floor((Date.now() - startTime) / 1000);
        const finalScore = Math.round((score + (correct ? 100 : 0)) / maxRounds);
        onComplete(finalScore, timeTaken);
      }
    }, 2000);
  };

  return (
    <div className="w-full h-screen bg-gradient-to-b from-indigo-900 via-purple-900 to-black flex flex-col items-center justify-center p-8">
      {/* Header */}
      <div className="absolute top-8 left-0 right-0 flex justify-between px-8">
        <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-300 text-sm">Round</div>
          <div className="text-white text-2xl font-bold">{round} / {maxRounds}</div>
        </div>
        <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3">
          <div className="text-gray-300 text-sm">Score</div>
          <div className="text-white text-2xl font-bold">{score}</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center">
        <AnimatePresence mode="wait">
          {phase === 'ready' && (
            <motion.div
              key="ready"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="text-center"
            >
              <h2 className="text-4xl font-bold text-white mb-6">Number Sequence</h2>
              <p className="text-xl text-gray-300 mb-8">
                Remember the sequence of {sequenceLength} numbers
              </p>
              <button
                onClick={startRound}
                className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-lg text-xl font-semibold transition-colors"
              >
                Start
              </button>
            </motion.div>
          )}

          {phase === 'showing' && (
            <motion.div
              key="showing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center"
            >
              <p className="text-gray-300 text-xl mb-8">Watch carefully...</p>
              <div className="flex gap-4 justify-center">
                {sequence.map((num, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{
                      scale: idx < currentIndex ? 1 : 0,
                      opacity: idx < currentIndex ? 1 : 0
                    }}
                    className="w-24 h-24 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center"
                  >
                    <span className="text-5xl font-bold text-white">{num}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {phase === 'input' && (
            <motion.div
              key="input"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center"
            >
              <p className="text-gray-300 text-xl mb-8">Enter the sequence</p>
              
              {/* User Input Display */}
              <div className="flex gap-4 justify-center mb-12">
                {Array.from({ length: sequenceLength }).map((_, idx) => (
                  <div
                    key={idx}
                    className="w-24 h-24 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border-2 border-white/20"
                  >
                    {userInput[idx] !== undefined && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="text-5xl font-bold text-white"
                      >
                        {userInput[idx]}
                      </motion.span>
                    )}
                  </div>
                ))}
              </div>

              {/* Number Pad */}
              <div className="grid grid-cols-5 gap-4 max-w-md mx-auto">
                {Array.from({ length: maxNumber + 1 }).map((_, num) => (
                  <motion.button
                    key={num}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleNumberClick(num)}
                    className="w-16 h-16 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-2xl font-bold transition-colors"
                  >
                    {num}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {phase === 'result' && (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="text-center"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200 }}
                className={`text-8xl mb-6 ${isCorrect ? 'text-green-400' : 'text-red-400'}`}
              >
                {isCorrect ? '✓' : '✗'}
              </motion.div>
              <h3 className="text-3xl font-bold text-white mb-4">
                {isCorrect ? 'Correct!' : 'Incorrect'}
              </h3>
              <p className="text-xl text-gray-300">
                {round < maxRounds ? 'Next round starting...' : 'Exercise complete!'}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default NumberSequence;
