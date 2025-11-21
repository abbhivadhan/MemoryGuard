/**
 * Caregiver Page - Main page for caregiver features
 * 
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
 */
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CaregiverDashboard from '../components/caregiver/CaregiverDashboard';
import ActivityMonitor from '../components/caregiver/ActivityMonitor';
import AlertSystem from '../components/caregiver/AlertSystem';
import ActivityLogViewer from '../components/caregiver/ActivityLogViewer';

type TabType = 'dashboard' | 'activity' | 'alerts' | 'log';

const CaregiverPage: React.FC = () => {
  const { patientId } = useParams<{ patientId?: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>(patientId ? 'activity' : 'dashboard');
  const [patientName] = useState('Patient');

  const tabs = [
    { id: 'dashboard' as TabType, label: 'Dashboard' },
    { id: 'activity' as TabType, label: 'Activity Monitor', requiresPatient: true },
    { id: 'alerts' as TabType, label: 'Alerts' },
    { id: 'log' as TabType, label: 'Activity Log', requiresPatient: true },
  ];

  const renderContent = () => {
    if (activeTab === 'dashboard') {
      return <CaregiverDashboard />;
    }

    if (!patientId && (activeTab === 'activity' || activeTab === 'log')) {
      return (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <div className="text-gray-400 text-lg mb-4">
            Please select a patient from the dashboard to view their activity
          </div>
          <button
            onClick={() => setActiveTab('dashboard')}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
      );
    }

    switch (activeTab) {
      case 'activity':
        return patientId ? <ActivityMonitor patientId={patientId} /> : null;
      case 'alerts':
        return <AlertSystem />;
      case 'log':
        return patientId ? (
          <ActivityLogViewer patientId={patientId} patientName={patientName} />
        ) : null;
      default:
        return <CaregiverDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Caregiver Portal</h1>
              {patientId && (
                <p className="text-gray-400">
                  Monitoring: {patientName}
                </p>
              )}
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              Back to My Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex space-x-1">
            {tabs.map((tab) => {
              const isDisabled = tab.requiresPatient && !patientId;
              return (
                <button
                  key={tab.id}
                  onClick={() => !isDisabled && setActiveTab(tab.id)}
                  disabled={isDisabled}
                  className={`px-6 py-4 font-semibold transition-colors ${
                    activeTab === tab.id
                      ? 'text-white border-b-2 border-purple-500'
                      : isDisabled
                      ? 'text-gray-600 cursor-not-allowed'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        {renderContent()}
      </div>
    </div>
  );
};

export default CaregiverPage;
