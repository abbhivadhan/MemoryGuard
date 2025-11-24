import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Target, Puzzle, Search, TrendingUp, Clock, Award, ChevronRight } from 'lucide-react';
import { exerciseService, Exercise, ExerciseStats } from '../../services/exerciseService';

interface ExerciseLibraryProps {
  onSelectExercise: (exercise: Exercise) => void;
}

const ExerciseLibrary: React.FC<ExerciseLibraryProps> = ({ onSelectExercise }) => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [exerciseStats, setExerciseStats] = useState<Record<string, ExerciseStats>>({});
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

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
      
      // Load stats for each exercise
      const stats: Record<string, ExerciseStats> = {};
      await Promise.all(
        data.map(async (exercise) => {
          try {
            const stat = await exerciseService.getExerciseStats(exercise.id);
            stats[exercise.id] = stat;
          } catch (error) {
            // Stats not available for this exercise
          }
        })
      );
      setExerciseStats(stats);
    } catch (error) {
      console.error('Failed to load exercises:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'memory_game':
        return Brain;
      case 'pattern_recognition':
        return Search;
      case 'problem_solving':
        return Puzzle;
      default:
        return Target;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'from-green-500 to-emerald-600';
      case 'medium':
        return 'from-yellow-500 to-amber-600';
      case 'hard':
        return 'from-orange-500 to-red-600';
      case 'expert':
        return 'from-red-500 to-rose-700';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const formatType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const filteredExercises = exercises.filter(exercise => 
    exercise.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    exercise.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters and Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="md:col-span-1">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Search Exercises
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name..."
                className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-10 pr-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          {/* Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Exercise Type
            </label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            >
              <option value="">All Types</option>
              <option value="memory_game">Memory Games</option>
              <option value="pattern_recognition">Pattern Recognition</option>
              <option value="problem_solving">Problem Solving</option>
            </select>
          </div>

          {/* Difficulty Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Difficulty Level
            </label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            >
              <option value="">All Levels</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
              <option value="expert">Expert</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Exercise Grid */}
      <AnimatePresence mode="popLayout">
        <motion.div
          layout
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredExercises.map((exercise, index) => {
            const Icon = getTypeIcon(exercise.type);
            const stats = exerciseStats[exercise.id];
            
            return (
              <motion.div
                key={exercise.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.02, y: -5 }}
                onClick={() => onSelectExercise(exercise)}
                className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6 cursor-pointer hover:border-purple-500/50 transition-all group"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <motion.div
                    whileHover={{ rotate: 5, scale: 1.1 }}
                    className="p-3 bg-gradient-to-br from-purple-500/20 to-violet-500/20 rounded-xl border border-purple-500/30"
                  >
                    <Icon className="w-6 h-6 text-purple-400" />
                  </motion.div>
                  <span className={`bg-gradient-to-r ${getDifficultyColor(exercise.difficulty)} text-white text-xs px-3 py-1.5 rounded-full font-semibold uppercase shadow-lg`}>
                    {exercise.difficulty}
                  </span>
                </div>

                {/* Title and Description */}
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
                  {exercise.name}
                </h3>

                <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                  {exercise.description}
                </p>

                {/* Stats */}
                {stats && stats.total_attempts > 0 && (
                  <div className="grid grid-cols-3 gap-2 mb-4 p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-gray-400 text-xs mb-1">
                        <TrendingUp className="w-3 h-3" />
                        <span>Attempts</span>
                      </div>
                      <div className="text-white font-bold text-sm">{stats.total_attempts}</div>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-gray-400 text-xs mb-1">
                        <Award className="w-3 h-3" />
                        <span>Best</span>
                      </div>
                      <div className="text-white font-bold text-sm">{stats.best_score.toFixed(0)}</div>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-gray-400 text-xs mb-1">
                        <Clock className="w-3 h-3" />
                        <span>Avg</span>
                      </div>
                      <div className="text-white font-bold text-sm">{stats.average_score.toFixed(0)}</div>
                    </div>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between">
                  <span className="text-purple-400 text-sm font-medium">
                    {formatType(exercise.type)}
                  </span>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-lg flex items-center gap-2"
                  >
                    Start
                    <ChevronRight className="w-4 h-4" />
                  </motion.button>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </AnimatePresence>

      {/* Empty State */}
      {filteredExercises.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16 backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10"
        >
          <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400 text-lg mb-2">
            No exercises found matching your criteria
          </p>
          <p className="text-gray-500 text-sm">
            Try adjusting your filters or search query
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default ExerciseLibrary;
