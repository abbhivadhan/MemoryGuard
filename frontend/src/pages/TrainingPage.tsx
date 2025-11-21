import React, { useState } from 'react';
import { Exercise } from '../services/exerciseService';
import ExerciseLibrary from '../components/cognitive/ExerciseLibrary';
import ExerciseProgress from '../components/cognitive/ExerciseProgress';
import ExercisePlayer from '../components/cognitive/ExercisePlayer';
import ExerciseMLInsights from '../components/cognitive/ExerciseMLInsights';

const TrainingPage: React.FC = () => {
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [activeTab, setActiveTab] = useState<'library' | 'progress' | 'insights'>('library');

  const handleSelectExercise = (exercise: Exercise) => {
    setSelectedExercise(exercise);
  };

  const handleExerciseComplete = () => {
    setSelectedExercise(null);
    setActiveTab('progress');
  };

  const handleExitExercise = () => {
    setSelectedExercise(null);
  };

  if (selectedExercise) {
    return (
      <ExercisePlayer
        exercise={selectedExercise}
        onComplete={handleExerciseComplete}
        onExit={handleExitExercise}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Cognitive Training
          </h1>
          <p className="text-gray-400 text-lg">
            Engage in exercises designed to maintain and improve cognitive function
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-gray-700">
          <button
            onClick={() => setActiveTab('library')}
            className={`px-6 py-3 font-semibold transition-colors ${
              activeTab === 'library'
                ? 'text-purple-400 border-b-2 border-purple-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            Exercise Library
          </button>
          <button
            onClick={() => setActiveTab('progress')}
            className={`px-6 py-3 font-semibold transition-colors ${
              activeTab === 'progress'
                ? 'text-purple-400 border-b-2 border-purple-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            My Progress
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-6 py-3 font-semibold transition-colors ${
              activeTab === 'insights'
                ? 'text-purple-400 border-b-2 border-purple-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            ML Insights
          </button>
        </div>

        {/* Content */}
        <div>
          {activeTab === 'library' && (
            <ExerciseLibrary onSelectExercise={handleSelectExercise} />
          )}
          {activeTab === 'progress' && <ExerciseProgress />}
          {activeTab === 'insights' && <ExerciseMLInsights />}
        </div>
      </div>
    </div>
  );
};

export default TrainingPage;
