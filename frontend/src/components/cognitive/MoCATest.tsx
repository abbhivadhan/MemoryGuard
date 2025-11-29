/**
 * MoCA (Montreal Cognitive Assessment) Test Component
 * Interactive 3D interface for cognitive assessment
 * Requirements: 12.1, 12.2
 */

import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Center } from '@react-three/drei';
import AudioControls from './AudioControls';
import { useTextToSpeech } from '../../hooks/useTextToSpeech';

interface MoCATestProps {
  assessmentId?: string;
  onComplete: (responses: Record<string, any>) => void;
  onSaveProgress: (responses: Record<string, any>) => void;
}

interface MoCASection {
  id: string;
  title: string;
  instructions: string;
  questions: MoCAQuestion[];
}

interface MoCAQuestion {
  id: string;
  text: string;
  type: 'multiple-choice' | 'text-input' | 'drawing' | 'task' | 'score-input';
  options?: string[];
  correctAnswer?: string;
  maxScore?: number;
}

const MoCATest: React.FC<MoCATestProps> = ({ onComplete, onSaveProgress }) => {
  const [currentSection, setCurrentSection] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [responses, setResponses] = useState<Record<string, any>>({});
  const [textInput, setTextInput] = useState('');
  const [scoreInput, setScoreInput] = useState('');
  const [evaluating, setEvaluating] = useState(false);
  
  // Text-to-speech hook
  const { speak, stop, pause, resume, isSpeaking, isPaused, isSupported } = useTextToSpeech({
    rate: 0.9,
    pitch: 1.0,
    volume: 1.0
  });

  // MoCA Test Structure
  const sections: MoCASection[] = [
    {
      id: 'visuospatial',
      title: 'Visuospatial/Executive',
      instructions: 'Complete the following visuospatial and executive function tasks.',
      questions: [
        { id: 'trail_making', text: 'Trail Making: Connect numbers and letters in alternating order (1-A-2-B-3-C...)', type: 'task' },
        { id: 'cube_copy', text: 'Copy this cube drawing', type: 'drawing' },
        { id: 'clock_drawing_score', text: 'Clock Drawing: Draw a clock showing 10 past 11 (Score 0-3)', type: 'score-input', maxScore: 3 }
      ]
    },
    {
      id: 'naming',
      title: 'Naming',
      instructions: 'Name the following animals.',
      questions: [
        { id: 'naming_lion', text: 'What animal is this? (Show lion)', type: 'task' },
        { id: 'naming_rhino', text: 'What animal is this? (Show rhinoceros)', type: 'task' },
        { id: 'naming_camel', text: 'What animal is this? (Show camel)', type: 'task' }
      ]
    },
    {
      id: 'memory_registration',
      title: 'Memory - Registration',
      instructions: 'I will read a list of words. Listen carefully and try to remember them. I will ask you to recall them later.',
      questions: [
        { id: 'memory_registration', text: 'Words to remember: FACE, VELVET, CHURCH, DAISY, RED', type: 'task' }
      ]
    },
    {
      id: 'attention',
      title: 'Attention',
      instructions: 'Complete the following attention tasks.',
      questions: [
        { id: 'digit_span_forward', text: 'Repeat these numbers: 2-1-8-5-4', type: 'task' },
        { id: 'digit_span_backward', text: 'Repeat these numbers backward: 7-4-2', type: 'task' },
        { id: 'vigilance', text: 'Tap when you hear the letter A: F-B-A-C-M-N-A-A-J-K-L-B-A-F-A-K-D-E-A-A-A-J', type: 'task' },
        { id: 'serial7_score', text: 'Serial 7s: Start at 100 and subtract 7 (Score 0-3 for correct answers)', type: 'score-input', maxScore: 3 }
      ]
    },
    {
      id: 'language',
      title: 'Language',
      instructions: 'Complete the following language tasks.',
      questions: [
        { id: 'sentence_repetition1', text: 'Repeat: "I only know that John is the one to help today"', type: 'task' },
        { id: 'sentence_repetition2', text: 'Repeat: "The cat always hid under the couch when dogs were in the room"', type: 'task' },
        { id: 'fluency', text: 'Name as many words as you can that begin with the letter F in one minute (11+ words = correct)', type: 'task' }
      ]
    },
    {
      id: 'abstraction',
      title: 'Abstraction',
      instructions: 'Tell me how these items are alike.',
      questions: [
        { id: 'abstraction1', text: 'How are a train and a bicycle alike?', type: 'task' },
        { id: 'abstraction2', text: 'How are a watch and a ruler alike?', type: 'task' }
      ]
    },
    {
      id: 'delayed_recall',
      title: 'Delayed Recall',
      instructions: 'Now, please recall the words I asked you to remember earlier.',
      questions: [
        { id: 'recall_word1', text: 'First word?', type: 'text-input', correctAnswer: 'face' },
        { id: 'recall_word2', text: 'Second word?', type: 'text-input', correctAnswer: 'velvet' },
        { id: 'recall_word3', text: 'Third word?', type: 'text-input', correctAnswer: 'church' },
        { id: 'recall_word4', text: 'Fourth word?', type: 'text-input', correctAnswer: 'daisy' },
        { id: 'recall_word5', text: 'Fifth word?', type: 'text-input', correctAnswer: 'red' }
      ]
    },
    {
      id: 'orientation',
      title: 'Orientation',
      instructions: 'Please answer the following questions.',
      questions: [
        { id: 'orientation_date', text: 'What is the date today?', type: 'text-input' },
        { id: 'orientation_month', text: 'What month is it?', type: 'text-input' },
        { id: 'orientation_year', text: 'What year is it?', type: 'text-input', correctAnswer: new Date().getFullYear().toString() },
        { id: 'orientation_day', text: 'What day of the week is it?', type: 'multiple-choice', options: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], correctAnswer: new Date().toLocaleDateString('en-US', { weekday: 'long' }) },
        { id: 'orientation_place', text: 'What is the name of this place?', type: 'text-input' },
        { id: 'orientation_city', text: 'What city are we in?', type: 'text-input' }
      ]
    },
    {
      id: 'education',
      title: 'Education Level',
      instructions: 'Final question for scoring adjustment.',
      questions: [
        { id: 'education_years', text: 'How many years of formal education have you completed?', type: 'text-input' }
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
    setScoreInput('');
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

  const handleTextSubmit = async () => {
    if (textInput.trim()) {
      setEvaluating(true);
      
      // Use AI to evaluate answer if there's an expected answer
      if (currentQuestionData.correctAnswer) {
        try {
          const response = await fetch('/api/v1/assessments/evaluate-answer', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
              question: currentQuestionData.text,
              user_answer: textInput,
              expected_answer: currentQuestionData.correctAnswer,
              context: currentSectionData.title
            })
          });
          
          if (response.ok) {
            const data = await response.json();
            handleAnswer(currentQuestionData.id, data.is_correct ? 'correct' : 'incorrect');
          } else {
            // Fallback to simple matching
            const isCorrect = textInput.toLowerCase().trim() === currentQuestionData.correctAnswer.toLowerCase();
            handleAnswer(currentQuestionData.id, isCorrect ? 'correct' : 'incorrect');
          }
        } catch (error) {
          console.error('Error evaluating answer:', error);
          // Fallback to simple matching
          const isCorrect = textInput.toLowerCase().trim() === currentQuestionData.correctAnswer.toLowerCase();
          handleAnswer(currentQuestionData.id, isCorrect ? 'correct' : 'incorrect');
        }
      } else {
        // No expected answer, just store the response
        handleAnswer(currentQuestionData.id, textInput);
      }
      
      setEvaluating(false);
      setTimeout(handleNext, 500);
    }
  };

  const handleScoreSubmit = () => {
    const score = parseInt(scoreInput);
    if (!isNaN(score) && score >= 0 && score <= (currentQuestionData.maxScore || 10)) {
      handleAnswer(currentQuestionData.id, score);
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
          className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
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
                    className="bg-gray-700 hover:bg-purple-600 text-white py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-105"
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
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Type your answer here..."
                  autoFocus
                />
                <button
                  onClick={handleTextSubmit}
                  disabled={!textInput.trim() || evaluating}
                  className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
                >
                  {evaluating ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Evaluating with AI...
                    </>
                  ) : (
                    'Submit Answer'
                  )}
                </button>
              </div>
            )}

            {/* Score Input */}
            {currentQuestionData.type === 'score-input' && (
              <div>
                <input
                  type="number"
                  value={scoreInput}
                  onChange={(e) => setScoreInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleScoreSubmit()}
                  min="0"
                  max={currentQuestionData.maxScore || 10}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder={`Enter score (0-${currentQuestionData.maxScore || 10})`}
                  autoFocus
                />
                <button
                  onClick={handleScoreSubmit}
                  disabled={!scoreInput}
                  className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white py-3 rounded-lg transition-all duration-200"
                >
                  Submit Score
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
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg transition-all duration-200"
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
              <torusGeometry args={[1, 0.4, 16, 100]} />
              <meshStandardMaterial color="#A855F7" wireframe />
            </mesh>
          </Center>
        </Canvas>
      </div>
    </div>
  );
};

export default MoCATest;
