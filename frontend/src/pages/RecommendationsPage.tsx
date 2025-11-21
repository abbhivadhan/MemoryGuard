/**
 * Recommendations Page
 * Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6
 */

import React from 'react';
import RecommendationsDashboard from '../components/recommendations/RecommendationsDashboard';

const RecommendationsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900">
      <RecommendationsDashboard />
    </div>
  );
};

export default RecommendationsPage;
