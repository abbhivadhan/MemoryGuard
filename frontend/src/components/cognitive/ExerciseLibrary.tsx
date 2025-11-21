import React, { useState, useEffect } from 'react';
import { exerciseService, Exercise } from '../../services/exerciseService';

interface ExerciseLibraryProps {
  onSelectExercise: (exercise: Exercise) => void;
}

const ExerciseLibrary: React.FC<ExerciseLibraryProps> = ({ onSelectExercise }) => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');

  useEffect(() => {
    loadExercises();
  }, [selectedType, selectedDifficulty]);

  const loadExercises = async () => {
    try {
      setLoading(true);
      const data = await exerciseService.getExerciseLibrary(
        selectedType || undefined,
        selectedDifficulty || undefined
      );
      setExercises(data);
    } catch (error) {
      console.error('Failed to load exercises:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'memory_game':
        return '🧠';
      case 'pattern_recognition':
        return '🔍';
      case 'problem_solving':
        return '🧩';
      default:
        return '📝';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'hard':
        return 'bg-orange-500';
      case 'expert':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Exercise Type
          </label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">All Types</option>
            <option value="memory_game">Memory Games</option>
            <option value="pattern_recognition">Pattern Recognition</option>
            <option value="problem_solving">Problem Solving</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Difficulty
          </label>
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">All Levels</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
            <option value="expert">Expert</option>
          </select>
        </div>
      </div>

      {/* Exercise Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {exercises.map((exercise) => (
          <div
            key={exercise.id}
            className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-purple-500 transition-all cursor-pointer transform hover:scale-105"
            onClick={() => onSelectExercise(exercise)}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="text-4xl">{getTypeIcon(exercise.type)}</div>
              <span className={`${getDifficultyColor(exercise.difficulty)} text-white text-xs px-3 py-1 rounded-full font-semibold uppercase`}>
                {exercise.difficulty}
              </span>
            </div>

            <h3 className="text-xl font-bold text-white mb-2">
              {exercise.name}
            </h3>

            <p className="text-gray-400 text-sm mb-4">
              {exercise.description}
            </p>

            <div className="flex items-center justify-between">
              <span className="text-purple-400 text-sm font-medium">
                {formatType(exercise.type)}
              </span>
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                Start
              </button>
            </div>
          </div>
        ))}
      </div>

      {exercises.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">
            No exercises found matching your filters.
          </p>
        </div>
      )}
    </div>
  );
};

export default ExerciseLibrary;
