/**
 * Audio Controls Component for Assessment Instructions
 * Requirements: 12.6
 */

import React from 'react';

interface AudioControlsProps {
  onSpeak: () => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
  isSpeaking: boolean;
  isPaused: boolean;
  isSupported: boolean;
}

const AudioControls: React.FC<AudioControlsProps> = ({
  onSpeak,
  onStop,
  onPause,
  onResume,
  isSpeaking,
  isPaused,
  isSupported
}) => {
  if (!isSupported) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <span>🔇 Audio not supported in this browser</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {!isSpeaking && !isPaused && (
        <button
          onClick={onSpeak}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-all duration-200"
          title="Read instructions aloud"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
          <span>Listen</span>
        </button>
      )}

      {isSpeaking && !isPaused && (
        <>
          <button
            onClick={onPause}
            className="flex items-center gap-2 bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg transition-all duration-200"
            title="Pause audio"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Pause</span>
          </button>
          <button
            onClick={onStop}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-all duration-200"
            title="Stop audio"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
            </svg>
            <span>Stop</span>
          </button>
        </>
      )}

      {isPaused && (
        <>
          <button
            onClick={onResume}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-all duration-200"
            title="Resume audio"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Resume</span>
          </button>
          <button
            onClick={onStop}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-all duration-200"
            title="Stop audio"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
            </svg>
            <span>Stop</span>
          </button>
        </>
      )}

      {isSpeaking && (
        <div className="flex items-center gap-1 text-blue-400">
          <div className="w-1 h-3 bg-blue-400 animate-pulse" style={{ animationDelay: '0ms' }}></div>
          <div className="w-1 h-4 bg-blue-400 animate-pulse" style={{ animationDelay: '150ms' }}></div>
          <div className="w-1 h-3 bg-blue-400 animate-pulse" style={{ animationDelay: '300ms' }}></div>
        </div>
      )}
    </div>
  );
};

export default AudioControls;
