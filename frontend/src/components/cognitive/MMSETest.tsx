/**
 * MMSE (Mini-Mental State Examination) Test Component
 * Interactive 3D interface for cognitive assessment
 * Requirements: 12.1, 12.2
 */

import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Center } from '@react-three/drei';
import AudioControls from './AudioControls';
import { useTextToSpeech } from '../../hooks/useTextToSpeech';

interface MMSETestProps {
  assessmentId?: string;
  onComplete: (responses: Record<string, any>) => void;
  onSaveProgress: (responses: Record<string, any>) => void;
}

interface MMSESection {
  id: string;
  title: string;
  instructions: string;
  questions: MMSEQuestion[];
}

interface MMSEQuestion {
  id: string;
  text: string;
  type: 'multiple-choice' | 'text-input' | 'drawing' | 'task';
  options?: string[];
  correctAnswer?: string;
}

const MMSETest: React.FC<MMSETestProps> = ({ assessmentId, onComplete, onSaveProgress }) => {
  const [currentSection, setCurrentSection] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [responses, setResponses] = useState<Record<string, any>>({});
  const [textInput, setTextInput] = useState('');
  
  // Text-to-speech hook
  const { speak, stop, pause, resume, isSpeaking, isPaused, isSupported } = useTextToSpeech({
    rate: 0.9,
    pitch: 1.0,
    volume: 1.0
  });

  // MMSE Test Structure
  const sections: MMSESection[] = [
    {
      id: 'orientation_time',
      title: 'Orientation to Time',
      instructions: 'Please answer the following questions about the current date and time.',
      questions: [
        { id: 'orientation_year', text: 'What year is it?', type: 'text-input', correctAnswer: new Date().getFullYear().toString() },
        { id: 'orientation_season', text: 'What season is it?', type: 'multiple-choice', options: ['Spring', 'Summer', 'Fall', 'Winter'] },
        { id: 'orientation_date', text: 'What is the date?', type: 'text-input' },
        { id: 'orientation_day', text: 'What day of the week is it?', type: 'multiple-choice', options: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] },
        { id: 'orientation_month', text: 'What month is it?', type: 'text-input' }
      ]
    },
    {
      id: 'orientation_place',
      title: 'Orientation to Place',
      instructions: 'Please answer the following questions about your current location.',
      questions: [
        { id: 'orientation_state', text: 'What state are we in?', type: 'text-input' },
        { id: 'orientation_county', text: 'What county are we in?', type: 'text-input' },
        { id: 'orientation_town', text: 'What town/city are we in?', type: 'text-input' },
        { id: 'orientation_hospital', text: 'What is the name of this place?', type: 'text-input' },
        { id: 'orientation_floor', text: 'What floor are we on?', type: 'text-input' }
      ]
    },
    {
      id: 'registration',
      title: 'Registration',
      instructions: 'I will say three words. Please repeat them after me and try to remember them.',
      questions: [
        { id: 'registration_word1', text: 'Repeat: APPLE', type: 'task' },
        { id: 'registration_word2', text: 'Repeat: TABLE', type: 'task' },
        { id: 'registration_word3', text: 'Repeat: PENNY', type: 'task' }
      ]
    },
    {
      id: 'attention',
      title: 'Attention and Calculation',
      instructions: 'Please count backwards from 100 by 7s. Stop after 5 subtractions.',
      questions: [
        { id: 'attention_score', text: 'Serial 7s: 100 - 7 = ? (Continue 5 times)', type: 'text-input' }
      ]
    },
    {
      id: 'recall',
      title: 'Recall',
      instructions: 'Please recall the three words I asked you to remember earlier.',
      questions: [
        { id: 'recall_word1', text: 'First word?', type: 'text-input', correctAnswer: 'apple' },
        { id: 'recall_word2', text: 'Second word?', type: 'text-input', correctAnswer: 'table' },
        { id: 'recall_word3', text: 'Third word?', type: 'text-input', correctAnswer: 'penny' }
      ]
    },
    {
      id: 'language',
      title: 'Language',
      instructions: 'Please complete the following language tasks.',
      questions: [
        { id: 'naming_object1', text: 'What is this object? (Show pencil)', type: 'task' },
        { id: 'naming_object2', text: 'What is this object? (Show watch)', type: 'task' },
        { id: 'repetition', text: 'Repeat: "No ifs, ands, or buts"', type: 'task' },
        { id: 'command_step1', text: 'Take this paper in your right hand', type: 'task' },
        { id: 'command_step2', text: 'Fold it in half', type: 'task' },
        { id: 'command_step3', text: 'Put it on the floor', type: 'task' },
        { id: 'reading', text: 'Read and follow: "Close your eyes"', type: 'task' },
        { id: 'writing', text: 'Write a complete sentence', type: 'text-input' },
        { id: 'drawing', text: 'Copy this design (two intersecting pentagons)', type: 'drawing' }
      ]
    }
  ];

  const currentSectionData = sections[currentSection];
  const currentQuestionData = currentSectionData?.questions[currentQuestion];
  const totalSections = sections.length;
  const totalQuestionsInSection = currentSectionData?.questions.length || 0;

  useEffect(() => {
    // Auto-save progress every 30 seconds
    const interval = setInterval(() => {
      if (Object.keys(responses).length > 0) {
        onSaveProgress(responses);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [responses, onSaveProgress]);

  const handleAnswer = (questionId: string, answer: any) => {
    const newResponses = { ...responses, [questionId]: answer };
    setResponses(newResponses);
    setTextInput('');
  };

  const handleNext = () => {
    if (currentQuestion < totalQuestionsInSection - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else if (currentSection < totalSections - 1) {
      setCurrentSection(currentSection + 1);
      setCurrentQuestion(0);
    } else {
      // Test complete
      onComplete(responses);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    } else if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
      setCurrentQuestion(sections[currentSection - 1].questions.length - 1);
    }
  };

  const handleCorrect = () => {
    handleAnswer(currentQuestionData.id, 'correct');
    setTimeout(handleNext, 500);
  };

  const handleIncorrect = () => {
    handleAnswer(currentQuestionData.id, 'incorrect');
    setTimeout(handleNext, 500);
  };

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      // Check if answer is correct (case-insensitive)
      const isCorrect = currentQuestionData.correctAnswer
        ? textInput.toLowerCase().trim() === currentQuestionData.correctAnswer.toLowerCase()
        : null;
      
      handleAnswer(currentQuestionData.id, isCorrect !== null ? (isCorrect ? 'correct' : 'incorrect') : textInput);
      setTimeout(handleNext, 500);
    }
  };

  const progress = ((currentSection * 100 / totalSections) + (currentQuestion * 100 / totalQuestionsInSection / totalSections));

  if (!currentSectionData || !currentQuestionData) {
    return <div className="text-white">Loading...</div>;
  }

  return (
    <div className="w-full h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 w-full h-2 bg-gray-800 z-50">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 pt-16">
        {/* Section Header */}
        <div className="mb-8 text-center">
          <h2 className="text-3xl font-bold mb-2">{currentSectionData.title}</h2>
          <p className="text-gray-400">{currentSectionData.instructions}</p>
          <p className="text-sm text-gray-500 mt-2">
            Section {currentSection + 1} of {totalSections} • Question {currentQuestion + 1} of {totalQuestionsInSection}
          </p>
          
          {/* Audio Controls */}
          <div className="mt-4 flex justify-center">
            <AudioControls
              onSpeak={() => speak(`${currentSectionData.instructions}. ${currentQuestionData.text}`)}
              onStop={stop}
              onPause={pause}
              onResume={resume}
              isSpeaking={isSpeaking}
              isPaused={isPaused}
              isSupported={isSupported}
            />
          </div>
        </div>

        {/* Question Display */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-gray-800 rounded-lg p-8 mb-8 shadow-2xl">
            <h3 className="text-2xl mb-6">{currentQuestionData.text}</h3>

            {/* Multiple Choice Options */}
            {currentQuestionData.type === 'multiple-choice' && currentQuestionData.options && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {currentQuestionData.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      handleAnswer(currentQuestionData.id, option.toLowerCase() === currentQuestionData.correctAnswer?.toLowerCase() ? 'correct' : 'incorrect');
                      setTimeout(handleNext, 500);
                    }}
                    className="bg-gray-700 hover:bg-blue-600 text-white py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-105"
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}

            {/* Text Input */}
            {currentQuestionData.type === 'text-input' && (
              <div>
                <input
                  type="text"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Type your answer here..."
                  autoFocus
                />
                <button
                  onClick={handleTextSubmit}
                  disabled={!textInput.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 rounded-lg transition-all duration-200"
                >
                  Submit Answer
                </button>
              </div>
            )}

            {/* Task Type (Examiner scores) */}
            {currentQuestionData.type === 'task' && (
              <div className="flex gap-4">
                <button
                  onClick={handleCorrect}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-4 rounded-lg transition-all duration-200 transform hover:scale-105"
                >
                  ✓ Correct
                </button>
                <button
                  onClick={handleIncorrect}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white py-4 rounded-lg transition-all duration-200 transform hover:scale-105"
                >
                  ✗ Incorrect
                </button>
              </div>
            )}

            {/* Drawing Type */}
            {currentQuestionData.type === 'drawing' && (
              <div>
                <div className="bg-white rounded-lg p-4 mb-4 h-64 flex items-center justify-center">
                  <p className="text-gray-800">Drawing canvas would go here</p>
                </div>
                <div className="flex gap-4">
                  <button
                    onClick={handleCorrect}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg transition-all duration-200"
                  >
                    ✓ Correct
                  </button>
                  <button
                    onClick={handleIncorrect}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg transition-all duration-200"
                  >
                    ✗ Incorrect
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentSection === 0 && currentQuestion === 0}
              className="bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white px-6 py-3 rounded-lg transition-all duration-200"
            >
              ← Previous
            </button>
            <button
              onClick={handleNext}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-all duration-200"
            >
              {currentSection === totalSections - 1 && currentQuestion === totalQuestionsInSection - 1
                ? 'Complete Test'
                : 'Next →'}
            </button>
          </div>
        </div>
      </div>

      {/* 3D Background Animation */}
      <div className="fixed inset-0 -z-10 opacity-20">
        <Canvas camera={{ position: [0, 0, 5] }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
          <Center>
            <mesh>
              <sphereGeometry args={[1, 32, 32]} />
              <meshStandardMaterial color="#4F46E5" wireframe />
            </mesh>
          </Center>
        </Canvas>
      </div>
    </div>
  );
};

export default MMSETest;
