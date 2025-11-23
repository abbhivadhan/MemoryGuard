import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface MedicalDisclaimerProps {
  type?: 'prediction' | 'assessment' | 'general';
  className?: string;
  compact?: boolean;
}

/**
 * Medical Disclaimer Component
 * Displays important medical disclaimers for predictions and assessments
 * Requirements: 21.6
 */
const MedicalDisclaimer: React.FC<MedicalDisclaimerProps> = ({
  type = 'general',
  className = '',
  compact = false,
}) => {
  const getDisclaimerText = () => {
    switch (type) {
      case 'prediction':
        return {
          title: 'Medical Disclaimer',
          content: compact
            ? 'This analysis is for informational purposes only and does not constitute medical advice. Always consult with qualified healthcare professionals for diagnosis and treatment.'
            : 'This risk assessment is generated using machine learning models and is intended for informational purposes only. It does not constitute medical advice, diagnosis, or treatment. The predictions are based on patterns in data and should not be used as the sole basis for medical decisions. Always consult with qualified healthcare professionals, including neurologists and specialists, for proper diagnosis, treatment planning, and medical guidance. Individual results may vary, and this tool should be used as a supplement to, not a replacement for, professional medical care.',
        };
      case 'assessment':
        return {
          title: 'Assessment Notice',
          content: compact
            ? 'These cognitive assessments are screening tools only. Results should be reviewed by healthcare professionals for proper interpretation and diagnosis.'
            : 'These cognitive assessments are screening tools designed to help track cognitive function over time. They are not diagnostic tools and should not be used to self-diagnose any medical condition. Assessment results should be reviewed and interpreted by qualified healthcare professionals. Cognitive test scores can be affected by many factors including education, language, cultural background, mood, fatigue, and test-taking conditions. For accurate diagnosis and treatment of cognitive concerns, please consult with a neurologist, psychiatrist, or other qualified medical professional.',
        };
      case 'general':
      default:
        return {
          title: 'Important Notice',
          content: compact
            ? 'This platform provides health tracking and analysis tools for informational purposes. Always consult healthcare professionals for medical decisions.'
            : 'MemoryGuard is a health tracking and analysis platform designed to support individuals and caregivers in monitoring cognitive health. All features, predictions, and assessments provided by this platform are for informational and educational purposes only. They do not constitute medical advice, diagnosis, or treatment recommendations. Users should always consult with qualified healthcare professionals before making any medical decisions or changes to their care plan. This platform is not a substitute for professional medical care, and users should seek immediate medical attention for any urgent health concerns.',
        };
    }
  };

  const disclaimer = getDisclaimerText();

  if (compact) {
    return (
      <div className={`flex items-start gap-3 p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg ${className}`}>
        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-sm text-amber-200/90 leading-relaxed">
            {disclaimer.content}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-6 bg-amber-500/10 border-2 border-amber-500/30 rounded-xl ${className}`}>
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-amber-400" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-amber-300 mb-3">
            {disclaimer.title}
          </h3>
          <p className="text-amber-200/90 leading-relaxed">
            {disclaimer.content}
          </p>
          <div className="mt-4 pt-4 border-t border-amber-500/20">
            <p className="text-sm text-amber-300/70">
              <strong>Emergency:</strong> If you or someone you know is experiencing a medical emergency, 
              call emergency services immediately or go to the nearest emergency room.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Compact inline disclaimer for use in smaller spaces
export const InlineDisclaimer: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`flex items-center gap-2 text-xs text-gray-400 ${className}`}>
    <AlertTriangle className="w-3 h-3" />
    <span>Not medical advice. Consult healthcare professionals.</span>
  </div>
);

export default MedicalDisclaimer;
