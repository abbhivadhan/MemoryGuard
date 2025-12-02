/**
 * MMSE (Mini-Mental State Examination) Test Component - REDESIGNED
 * Proper clinical assessment with full AI integration
 * Requirements: 12.1, 12.2, 12.3
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AudioControls from './AudioControls';
import { useTextToSpeech } from '../../hooks/useTextToSpeech';

interface MMSETestProps {
  assessmentId?: string;
  onComplete: (responses: Record<string, any>) => void;
  onSaveProgress: (responses: Record<string, any>) => void;
}

interface Question {
  id: string;
  category: string;
  instruction: string;
  question: string;
  type: 'text' | 'choice' | 'task-observation' | 'drawing';
  options?: string[];
  points: number;
  aiEvaluate?: boolean;
  expectedAnswer?: string | string[];
  helpText?: string;
  imageUrl?: string;
  imageAlt?: string;
}

const MMSETestNew: React.FC<MMSETestProps> = ({ onComplete, onSaveProgress }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, any>>({});
  const [userInput, setUserInput] = useState('');
  const [evaluating, setEvaluating] = useState(false);
  const [showInstructions, setShowInstructions] = useState(true);
  
  const { speak, stop, pause, resume, isSpeaking, isPaused, isSupported } = useTextToSpeech({
    rate: 0.9,
    pitch: 1.0,
    volume: 1.0
  });

  // Real MMSE Questions (30 points total)
  const questions: Question[] = [
    // ORIENTATION TO TIME (5 points)
    {
      id: 'orientation_year',
      category: 'Orientation to Time',
      instruction: 'I am going to ask you some questions about today\'s date.',
      question: 'What year is it?',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      expectedAnswer: new Date().getFullYear().toString(),
      helpText: 'Type the current year (e.g., 2024)'
    },
    {
      id: 'orientation_season',
      category: 'Orientation to Time',
      instruction: '',
      question: 'What season is it?',
      type: 'choice',
      options: ['Spring', 'Summer', 'Fall/Autumn', 'Winter'],
      points: 1,
      aiEvaluate: true,
      expectedAnswer: getCurrentSeason()
    },
    {
      id: 'orientation_date',
      category: 'Orientation to Time',
      instruction: '',
      question: 'What is today\'s date?',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      expectedAnswer: new Date().getDate().toString(),
      helpText: 'Type the day of the month (1-31)'
    },
    {
      id: 'orientation_day',
      category: 'Orientation to Time',
      instruction: '',
      question: 'What day of the week is it?',
      type: 'choice',
      options: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      points: 1,
      aiEvaluate: true,
      expectedAnswer: new Date().toLocaleDateString('en-US', { weekday: 'long' })
    },
    {
      id: 'orientation_month',
      category: 'Orientation to Time',
      instruction: '',
      question: 'What month is it?',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      expectedAnswer: new Date().toLocaleDateString('en-US', { month: 'long' }),
      helpText: 'Type the current month'
    },

    // ORIENTATION TO PLACE (5 points)
    {
      id: 'orientation_state',
      category: 'Orientation to Place',
      instruction: 'Now I will ask you about where we are.',
      question: 'What state are we in?',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      helpText: 'Type the name of your state'
    },
    {
      id: 'orientation_county',
      category: 'Orientation to Place',
      instruction: '',
      question: 'What county are we in?',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      helpText: 'Type the name of your county'
    },
    {
      id: 'orientation_city',
      category: 'Orientation to Place',
      instruction: '',
      question: 'What city or town are we in?',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      helpText: 'Type the name of your city'
    },
    {
      id: 'orientation_building',
      category: 'Orientation to Place',
      instruction: '',
      question: 'What building are we in? (or what is the name of this place?)',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      helpText: 'Type where you are (e.g., "home", "hospital", "clinic")'
    },
    {
      id: 'orientation_floor',
      category: 'Orientation to Place',
      instruction: '',
      question: 'What floor are we on?',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      helpText: 'Type the floor number or "ground floor"'
    },

    // REGISTRATION (3 points)
    {
      id: 'registration_instruction',
      category: 'Registration',
      instruction: 'I am going to name three objects. After I say them, I want you to repeat them. Remember what they are because I am going to ask you to name them again in a few minutes.',
      question: 'Please repeat these three words: APPLE, TABLE, PENNY',
      type: 'text',
      points: 3,
      aiEvaluate: true,
      expectedAnswer: ['apple', 'table', 'penny'],
      helpText: 'Type all three words separated by commas or spaces'
    },

    // ATTENTION AND CALCULATION (5 points)
    {
      id: 'serial_sevens',
      category: 'Attention and Calculation',
      instruction: 'Now I would like you to subtract 7 from 100, then keep subtracting 7 from each answer until I tell you to stop.',
      question: 'Start with 100 and subtract 7. What do you get? (Continue 5 times: 100-7, then subtract 7 from that answer, etc.)',
      type: 'text',
      points: 5,
      aiEvaluate: true,
      expectedAnswer: ['93', '86', '79', '72', '65'],
      helpText: 'Type your answers separated by commas (e.g., 93, 86, 79, 72, 65)'
    },

    // RECALL (3 points)
    {
      id: 'recall_words',
      category: 'Recall',
      instruction: 'Now, what were the three objects I asked you to remember earlier?',
      question: 'Please tell me the three words I asked you to remember.',
      type: 'text',
      points: 3,
      aiEvaluate: true,
      expectedAnswer: ['apple', 'table', 'penny'],
      helpText: 'Type the three words you were asked to remember'
    },

    // NAMING (2 points)
    {
      id: 'naming_objects',
      category: 'Language - Naming',
      instruction: 'I am going to show you some objects and I want you to tell me what they are.',
      question: 'What do you call this object you write with? (Hint: It\'s a common writing instrument)',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      expectedAnswer: ['pencil', 'pen'],
      helpText: 'Type the name of a writing instrument'
    },
    {
      id: 'naming_watch',
      category: 'Language - Naming',
      instruction: '',
      question: 'What do you call this object you wear on your wrist to tell time?',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      expectedAnswer: ['watch', 'wristwatch'],
      helpText: 'Type the name of a time-telling device worn on the wrist'
    },

    // REPETITION (1 point)
    {
      id: 'repetition',
      category: 'Language - Repetition',
      instruction: 'I am going to say a phrase. After I say it, I want you to repeat it exactly as I said it.',
      question: 'Please repeat this phrase exactly: "No ifs, ands, or buts"',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      expectedAnswer: 'no ifs ands or buts',
      helpText: 'Type the phrase exactly as shown'
    },

    // THREE-STAGE COMMAND (3 points)
    {
      id: 'three_stage_command',
      category: 'Language - Following Commands',
      instruction: 'I am going to give you a piece of paper. When I do, take the paper in your right hand, fold it in half with both hands, and put it on the floor.',
      question: 'Did you complete all three steps? (1) Take paper in right hand, (2) Fold it in half, (3) Put it on the floor',
      type: 'choice',
      options: ['Yes, I completed all 3 steps', 'I completed 2 steps', 'I completed 1 step', 'I did not complete any steps'],
      points: 3,
      helpText: 'This tests your ability to follow multi-step instructions'
    },

    // READING (1 point)
    {
      id: 'reading_command',
      category: 'Language - Reading',
      instruction: 'Please read the following instruction and do what it says.',
      question: 'Read this and do it: "CLOSE YOUR EYES"',
      type: 'choice',
      options: ['Yes, I closed my eyes', 'No, I did not close my eyes'],
      points: 1,
      helpText: 'Read the instruction and follow it'
    },

    // WRITING (1 point)
    {
      id: 'writing_sentence',
      category: 'Language - Writing',
      instruction: 'Please write a complete sentence. It can be about anything, but it must be a complete sentence with a subject and a verb.',
      question: 'Write any complete sentence:',
      type: 'text',
      points: 1,
      aiEvaluate: true,
      helpText: 'Type a complete sentence (e.g., "The sun is shining today.")'
    },

    // COPYING (1 point)
    {
      id: 'copying_design',
      category: 'Visuospatial - Copying',
      instruction: 'Please copy this design of two intersecting pentagons.',
      question: 'Were you able to draw two five-sided figures that intersect?',
      type: 'choice',
      options: ['Yes, I drew it correctly', 'I tried but it was not quite right', 'No, I could not do it'],
      points: 1,
      helpText: 'This tests your ability to copy a geometric design',
      imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Intersecting_pentagons.svg/320px-Intersecting_pentagons.svg.png',
      imageAlt: 'Two intersecting pentagons'
    }
  ];

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;

  useEffect(() => {
    const interval = setInterval(() => {
      if (Object.keys(responses).length > 0) {
        onSaveProgress(responses);
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [responses, onSaveProgress]);

  const evaluateWithAI = async (question: Question, answer: string): Promise<boolean> => {
    if (!question.aiEvaluate || !question.expectedAnswer) {
      return true;
    }

    try {
      const response = await fetch('/api/v1/assessments/evaluate-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          question: question.question,
          user_answer: answer,
          expected_answer: Array.isArray(question.expectedAnswer) 
            ? question.expectedAnswer.join(', ') 
            : question.expectedAnswer,
          context: `MMSE ${question.category} - ${question.points} point(s)`
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data.is_correct;
      }
    } catch (error) {
      console.error('AI evaluation error:', error);
    }

    // Fallback: simple matching
    const userLower = answer.toLowerCase().trim();
    if (Array.isArray(question.expectedAnswer)) {
      return question.expectedAnswer.some(exp => 
        userLower.includes(exp.toLowerCase()) || exp.toLowerCase().includes(userLower)
      );
    }
    return userLower === question.expectedAnswer?.toLowerCase();
  };

  const handleSubmit = async () => {
    if (!userInput.trim() && currentQuestion.type === 'text') return;

    setEvaluating(true);

    try {
      let score = 0;
      let isCorrect = false;

      if (currentQuestion.type === 'text' && currentQuestion.aiEvaluate) {
        isCorrect = await evaluateWithAI(currentQuestion, userInput);
        score = isCorrect ? currentQuestion.points : 0;
      } else if (currentQuestion.type === 'choice') {
        // For choice questions, calculate score based on selection
        const selectedIndex = currentQuestion.options?.indexOf(userInput) ?? -1;
        if (currentQuestion.id === 'three_stage_command') {
          score = selectedIndex === 0 ? 3 : selectedIndex === 1 ? 2 : selectedIndex === 2 ? 1 : 0;
          isCorrect = score > 0;
        } else if (currentQuestion.id === 'reading_command' || currentQuestion.id === 'copying_design') {
          score = selectedIndex === 0 ? 1 : 0;
          isCorrect = score > 0;
        } else {
          // Regular choice with AI evaluation
          isCorrect = await evaluateWithAI(currentQuestion, userInput);
          score = isCorrect ? currentQuestion.points : 0;
        }
      }

      const newResponses = {
        ...responses,
        [currentQuestion.id]: isCorrect || score > 0 ? "correct" : "incorrect",
        [`${currentQuestion.id}_answer`]: userInput,
        [`${currentQuestion.id}_score`]: score
      };

      setResponses(newResponses);
      setUserInput('');

      // Move to next question or complete
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setShowInstructions(true);
      } else {
        onComplete(newResponses);
      }
    } finally {
      setEvaluating(false);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setUserInput(responses[questions[currentIndex - 1].id] || '');
      setShowInstructions(true);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-blue-900 to-black text-white p-4">
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 w-full h-1 bg-gray-800 z-50">
        <motion.div
          className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>

      <div className="max-w-4xl mx-auto pt-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">MMSE Assessment</h1>
          <p className="text-gray-400">
            Question {currentIndex + 1} of {questions.length} • {currentQuestion.category}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            Points for this question: {currentQuestion.points}
          </p>
        </div>

        {/* Question Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-8 shadow-2xl"
          >
            {/* Instructions */}
            {currentQuestion.instruction && showInstructions && (
              <div className="mb-6 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
                <p className="text-blue-200 text-sm font-medium mb-2">EXAMINER INSTRUCTIONS:</p>
                <p className="text-white">{currentQuestion.instruction}</p>
                <button
                  onClick={() => setShowInstructions(false)}
                  className="mt-2 text-sm text-blue-300 hover:text-blue-100"
                >
                  Hide instructions
                </button>
              </div>
            )}

            {/* Audio Controls */}
            <div className="flex justify-center mb-6">
              <AudioControls
                onSpeak={() => speak(currentQuestion.question)}
                onStop={stop}
                onPause={pause}
                onResume={resume}
                isSpeaking={isSpeaking}
                isPaused={isPaused}
                isSupported={isSupported}
              />
            </div>

            {/* Question */}
            <h2 className="text-2xl font-semibold mb-6 text-center">
              {currentQuestion.question}
            </h2>

            {/* Image Display */}
            {currentQuestion.imageUrl && (
              <div className="flex justify-center mb-6">
                <img 
                  src={currentQuestion.imageUrl} 
                  alt={currentQuestion.imageAlt || 'Assessment image'}
                  className="max-w-md w-full rounded-lg border-2 border-white/20 shadow-lg"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            )}

            {/* Help Text */}
            {currentQuestion.helpText && (
              <p className="text-sm text-gray-400 mb-4 text-center italic">
                {currentQuestion.helpText}
              </p>
            )}

            {/* Input Area */}
            <div className="space-y-4">
              {currentQuestion.type === 'text' && (
                <div>
                  <textarea
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                      }
                    }}
                    className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[100px]"
                    placeholder="Type your answer here..."
                    autoFocus
                  />
                </div>
              )}

              {currentQuestion.type === 'choice' && currentQuestion.options && (
                <div className="grid grid-cols-1 gap-3">
                  {currentQuestion.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setUserInput(option);
                        setTimeout(handleSubmit, 100);
                      }}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        userInput === option
                          ? 'bg-blue-500 border-blue-400 text-white'
                          : 'bg-white/5 border-white/20 hover:bg-white/10 hover:border-white/30'
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 mt-8">
              <button
                onClick={handlePrevious}
                disabled={currentIndex === 0}
                className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 disabled:bg-white/5 disabled:text-gray-600 border border-white/20 rounded-lg transition-all"
              >
                ← Previous
              </button>
              
              {currentQuestion.type === 'text' && (
                <button
                  onClick={handleSubmit}
                  disabled={!userInput.trim() || evaluating}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 disabled:from-gray-600 disabled:to-gray-700 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  {evaluating ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                      Evaluating with AI...
                    </>
                  ) : currentIndex === questions.length - 1 ? (
                    'Complete Assessment'
                  ) : (
                    'Next →'
                  )}
                </button>
              )}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Progress Indicator */}
        <div className="mt-6 text-center text-sm text-gray-400">
          <p>Your responses are automatically saved every 30 seconds</p>
        </div>
      </div>
    </div>
  );
};

// Helper function
function getCurrentSeason(): string {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return 'Spring';
  if (month >= 5 && month <= 7) return 'Summer';
  if (month >= 8 && month <= 10) return 'Fall/Autumn';
  return 'Winter';
}

export default MMSETestNew;
