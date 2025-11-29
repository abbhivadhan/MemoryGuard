import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { mlService, ExplanationResponse, PredictionResponse } from '../../services/mlService';

interface RiskExplanationProps {
  predictionId: number;
  prediction?: PredictionResponse;
}

// Helper function to format feature names
const formatFeatureName = (feature: string): string => {
  return feature
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Helper function to get feature description
const getFeatureDescription = (feature: string, value: number, isPositive: boolean): string => {
  const featureLower = feature.toLowerCase();
  const impact = isPositive ? 'increases' : 'decreases';

  
  // Common feature descriptions
  const descriptions: Record<string, string> = {
    'mmse_score': `Your MMSE cognitive test score ${impact} your risk. ${isPositive ? 'Lower scores indicate cognitive decline.' : 'Higher scores suggest better cognitive function.'}`,
    'moca_score': `Your MoCA cognitive assessment ${impact} your risk. ${isPositive ? 'Lower scores may indicate cognitive impairment.' : 'Higher scores reflect better cognitive health.'}`,
    'age': `Your age ${impact} your risk. ${isPositive ? 'Advanced age is a known risk factor for Alzheimer\'s disease.' : 'Younger age is associated with lower risk.'}`,
    'csf_abeta42': `Your CSF Amyloid-beta 42 levels ${impact} your risk. ${isPositive ? 'Lower levels may indicate amyloid plaque buildup.' : 'Normal levels suggest less amyloid pathology.'}`,
    'csf_tau': `Your CSF Tau protein levels ${impact} your risk. ${isPositive ? 'Elevated tau levels may indicate neuronal damage.' : 'Normal tau levels are protective.'}`,
    'csf_ptau': `Your CSF Phosphorylated Tau levels ${impact} your risk. ${isPositive ? 'Elevated p-tau is associated with Alzheimer\'s pathology.' : 'Normal p-tau levels are favorable.'}`,
    'hippocampal_volume': `Your hippocampal volume ${impact} your risk. ${isPositive ? 'Reduced volume may indicate brain atrophy.' : 'Preserved volume is a positive indicator.'}`,
    'apoe_e4': `Your APOE genotype ${impact} your risk. ${isPositive ? 'Carrying APOE-ε4 alleles increases genetic risk.' : 'Not carrying APOE-ε4 is protective.'}`,
    'education_years': `Your education level ${impact} your risk. ${isPositive ? 'Lower education may reduce cognitive reserve.' : 'Higher education builds cognitive reserve.'}`,
    'physical_activity': `Your physical activity level ${impact} your risk. ${isPositive ? 'Low activity is a modifiable risk factor.' : 'Regular exercise is protective.'}`,
    'sleep_quality': `Your sleep quality ${impact} your risk. ${isPositive ? 'Poor sleep may contribute to cognitive decline.' : 'Good sleep supports brain health.'}`,
    'social_engagement': `Your social engagement ${impact} your risk. ${isPositive ? 'Limited social interaction may increase risk.' : 'Active social life is protective.'}`,
    'diet_quality': `Your diet quality ${impact} your risk. ${isPositive ? 'Poor nutrition may contribute to risk.' : 'A healthy diet supports brain health.'}`,
    'blood_pressure': `Your blood pressure ${impact} your risk. ${isPositive ? 'High blood pressure may damage brain blood vessels.' : 'Controlled blood pressure is protective.'}`,
    'cholesterol': `Your cholesterol levels ${impact} your risk. ${isPositive ? 'High cholesterol may contribute to vascular risk.' : 'Healthy cholesterol levels are beneficial.'}`,
    'glucose': `Your glucose levels ${impact} your risk. ${isPositive ? 'Elevated glucose may indicate diabetes, a risk factor.' : 'Normal glucose control is protective.'}`,
  };

  // Find matching description
  for (const [key, desc] of Object.entries(descriptions)) {
    if (featureLower.includes(key)) {
      return desc;
    }
  }

  // Default description
  return `Your ${formatFeatureName(feature)} ${impact} your risk assessment by ${Math.abs(value * 100).toFixed(1)}%.`;
};

// Generate overall risk explanation
const generateOverallExplanation = (
  prediction: PredictionResponse,
  explanation: ExplanationResponse
): string => {
  const riskLevel = prediction.risk_level?.toLowerCase() || 'unknown';
  const probability = (prediction.probability || 0) * 100;
  const topFactors = explanation.top_features.slice(0, 3);

  let text = '';

  // Risk level introduction
  if (riskLevel === 'low') {
    text = `Based on your current health data, you have a ${probability.toFixed(0)}% estimated risk of developing Alzheimer's disease, which is considered LOW risk. `;
  } else if (riskLevel === 'moderate') {
    text = `Based on your current health data, you have a ${probability.toFixed(0)}% estimated risk of developing Alzheimer's disease, which is considered MODERATE risk. `;
  } else if (riskLevel === 'high') {
    text = `Based on your current health data, you have a ${probability.toFixed(0)}% estimated risk of developing Alzheimer's disease, which is considered HIGH risk. `;
  } else {
    text = `Based on your current health data, your risk assessment is ${probability.toFixed(0)}%. `;
  }

  // Key factors
  text += `The most significant factors influencing this assessment are: `;
  
  const factorNames = topFactors.map(f => formatFeatureName(f.feature));
  if (factorNames.length === 1) {
    text += `${factorNames[0]}. `;
  } else if (factorNames.length === 2) {
    text += `${factorNames[0]} and ${factorNames[1]}. `;
  } else {
    text += `${factorNames.slice(0, -1).join(', ')}, and ${factorNames[factorNames.length - 1]}. `;
  }

  // Actionable advice
  if (riskLevel === 'high' || riskLevel === 'moderate') {
    text += `We recommend discussing these results with your healthcare provider to develop a personalized prevention plan. `;
    text += `Many risk factors are modifiable through lifestyle changes, including regular exercise, a healthy diet, quality sleep, and staying socially engaged.`;
  } else {
    text += `Continue maintaining your healthy lifestyle habits to support long-term brain health. `;
    text += `Regular monitoring and preventive care remain important even with low risk.`;
  }

  return text;
};

export default function RiskExplanation({ predictionId, prediction }: RiskExplanationProps) {
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadExplanation();
  }, [predictionId]);

  const loadExplanation = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await mlService.getExplanation(predictionId);
      setExplanation(data);
    } catch (err) {
      console.error('Error loading explanation:', err);
      setError('Failed to load explanation');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
        </div>
      </div>
    );
  }

  if (error || !explanation) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="text-center text-red-400">
          <p>{error || 'No explanation available'}</p>
        </div>
      </div>
    );
  }

  const overallExplanation = prediction 
    ? generateOverallExplanation(prediction, explanation)
    : explanation.explanation_text;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="bg-gray-800 rounded-lg p-6"
    >
      <h2 className="text-2xl font-bold text-white mb-6">Understanding Your Risk</h2>

      {/* Overall Explanation */}
      <div className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 border border-cyan-700/50 rounded-lg p-6 mb-6">
        <div className="flex items-start space-x-3">
          <svg className="w-6 h-6 text-cyan-400 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-gray-200 leading-relaxed text-lg">
            {overallExplanation}
          </p>
        </div>
      </div>

      {/* Key Factors Breakdown */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-white mb-4">Key Factors Explained</h3>

        {/* Top positive contributors */}
        {explanation.positive_contributors.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-red-400 uppercase tracking-wide">
              Risk-Increasing Factors
            </h4>
            {explanation.positive_contributors.slice(0, 3).map((contributor, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="bg-gray-900 rounded-lg p-4 border-l-4 border-red-500"
              >
                <div className="flex items-start justify-between mb-2">
                  <h5 className="font-semibold text-white">
                    {formatFeatureName(contributor.feature)}
                  </h5>
                  <span className="text-red-400 text-sm font-medium">
                    +{(contributor.contribution * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {getFeatureDescription(contributor.feature, contributor.contribution, true)}
                </p>
              </motion.div>
            ))}
          </div>
        )}

        {/* Top negative contributors */}
        {explanation.negative_contributors.length > 0 && (
          <div className="space-y-3 mt-6">
            <h4 className="text-sm font-medium text-green-400 uppercase tracking-wide">
              Protective Factors
            </h4>
            {explanation.negative_contributors.slice(0, 3).map((contributor, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: (index + 3) * 0.1 }}
                className="bg-gray-900 rounded-lg p-4 border-l-4 border-green-500"
              >
                <div className="flex items-start justify-between mb-2">
                  <h5 className="font-semibold text-white">
                    {formatFeatureName(contributor.feature)}
                  </h5>
                  <span className="text-green-400 text-sm font-medium">
                    {(contributor.contribution * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {getFeatureDescription(contributor.feature, contributor.contribution, false)}
                </p>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="mt-6 p-4 bg-purple-900/20 border border-purple-700/50 rounded-lg">
        <h4 className="text-sm font-semibold text-purple-300 mb-3 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
          </svg>
          Next Steps
        </h4>
        <ul className="space-y-2 text-sm text-purple-200">
          <li className="flex items-start">
            <span className="text-purple-400 mr-2">•</span>
            <span>Discuss these results with your healthcare provider for personalized guidance</span>
          </li>
          <li className="flex items-start">
            <span className="text-purple-400 mr-2">•</span>
            <span>Focus on modifiable risk factors through lifestyle changes</span>
          </li>
          <li className="flex items-start">
            <span className="text-purple-400 mr-2">•</span>
            <span>Continue regular cognitive assessments to monitor changes over time</span>
          </li>
          <li className="flex items-start">
            <span className="text-purple-400 mr-2">•</span>
            <span>Explore our personalized recommendations for brain health optimization</span>
          </li>
        </ul>
      </div>

      {/* Scientific Note */}
      <div className="mt-4 p-3 bg-gray-900 rounded-lg">
        <p className="text-xs text-gray-400">
          <strong>Note:</strong> This explanation is generated using SHAP (SHapley Additive exPlanations), 
          a scientifically validated method for interpreting machine learning predictions. Each factor's 
          contribution is calculated based on its impact on the model's output compared to baseline values.
        </p>
      </div>
    </motion.div>
  );
}
