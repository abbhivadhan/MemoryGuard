import React, { useState, useEffect } from 'react';
import { Exercise, exerciseService } from '../../services/exerciseService';
import CardMemoryGame from './exercises/CardMemoryGame';
import PatternRecognition from './exercises/PatternRecognition';
import TowerOfHanoi from './exercises/TowerOfHanoi';
import NumberSequence from './exercises/NumberSequence';
import PathFinding from './exercises/PathFinding';
import LogicPuzzle from './exercises/LogicPuzzle';

interface ExercisePlayerProps {
  exercise: Exercise;
  onComplete: () => void;
  onExit: () => void;
}

const ExercisePlayer: React.FC<ExercisePlayerProps> = ({
  exercise,
  onComplete,
  onExit
}) => {
  const [loading, setLoading] = useState(false);
  const [recommendedDifficulty, setRecommendedDifficulty] = useState<string | null>(null);

  useEffect(() => {
    loadRecommendedDifficulty();
  }, [exercise.id]);

  const loadRecommendedDifficulty = async () => {
    try {
      const data = await exerciseService.getRecommendedDifficulty(exercise.id);
      setRecommendedDifficulty(data.recommended_difficulty);
    } catch (error) {
      console.error('Failed to load recommended difficulty:', error);
    }
  };

  const handleExerciseComplete = async (score: number, timeTaken: number) => {
    console.log('Exercise completed!', { score, timeTaken, exercise: exercise.name });
    
    try {
      setLoading(true);
      
      const performanceData = {
        exercise_id: exercise.id,
        difficulty: exercise.difficulty,
        score,
        max_score: 100,
        time_taken: timeTaken,
        completed: true,
        performance_data: {
          exercise_type: exercise.type,
          exercise_name: exercise.name
        }
      };
      
      console.log('Recording performance:', performanceData);
      
      const result = await exerciseService.recordPerformance(performanceData);
      
      console.log('Performance recorded successfully:', result);

      // Show completion message briefly before calling onComplete
      setTimeout(() => {
        onComplete();
      }, 2000);
    } catch (error) {
      console.error('Failed to record performance:', error);
      alert('Failed to save your progress. Please try again.');
      onComplete();
    } finally {
      setLoading(false);
    }
  };

  const renderExercise = () => {
    const config = exercise.config || {};

    switch (exercise.type) {
      case 'memory_game':
        if (exercise.name.includes('Card Memory')) {
          return (
            <CardMemoryGame
              pairs={config.pairs || 6}
              timeLimit={config.time_limit || 120}
              showTime={config.show_time || 1000}
              onComplete={handleExerciseComplete}
            />
          );
        } else if (exercise.name.includes('Number Sequence')) {
          return (
            <NumberSequence
              sequenceLength={config.sequence_length || 4}
              displayTime={config.display_time || 1000}
              maxNumber={config.max_number || 9}
              onComplete={handleExerciseComplete}
            />
          );
        }
        return <div className="text-white">Memory game not implemented</div>;

      case 'pattern_recognition':
        return (
          <PatternRecognition
            patternLength={config.pattern_length || 4}
            options={config.options || 4}
            onComplete={handleExerciseComplete}
          />
        );

      case 'problem_solving':
        if (exercise.name.includes('Tower of Hanoi')) {
          return (
            <TowerOfHanoi
              disks={config.disks || 3}
              onComplete={handleExerciseComplete}
            />
          );
        } else if (exercise.name.includes('Path Finding')) {
          return (
            <PathFinding
              gridSize={config.grid_size || 5}
              obstacles={config.obstacles || 3}
              onComplete={handleExerciseComplete}
            />
          );
        } else if (exercise.name.includes('Logic Puzzle')) {
          return (
            <LogicPuzzle
              items={config.items || 4}
              clues={config.clues || 5}
              onComplete={handleExerciseComplete}
            />
          );
        }
        return <div className="text-white">Problem-solving game not implemented</div>;

      default:
        return <div className="text-white">Exercise type not supported</div>;
    }
  };

  if (loading) {
    return (
      <div className="w-full h-screen bg-gradient-to-b from-gray-900 to-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Saving your progress...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Exit Button */}
      <button
        onClick={onExit}
        className="absolute top-4 right-4 z-30 bg-gray-800/80 backdrop-blur-sm hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
      >
        Exit
      </button>

      {/* Difficulty Recommendation */}
      {recommendedDifficulty && recommendedDifficulty !== exercise.difficulty && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-30 bg-blue-600/80 backdrop-blur-sm text-white px-4 py-2 rounded-lg text-sm">
          💡 Recommended difficulty: {recommendedDifficulty}
        </div>
      )}

      {/* Exercise */}
      {renderExercise()}
    </div>
  );
};

export default ExercisePlayer;
