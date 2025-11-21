/**
 * Medical Imaging Page
 * Upload and analyze brain MRI scans
 */
import React, { useState, useEffect } from 'react';
import { Brain, Upload, Activity, AlertTriangle } from 'lucide-react';
import ImagingUpload from '../components/imaging/ImagingUpload';
import BrainVisualization3D from '../components/imaging/BrainVisualization3D';
import {
  ImagingAnalysis,
  getUserImagingStudies
} from '../services/imagingService';
import { useAuthStore } from '../store/authStore';

const ImagingPage: React.FC = () => {
  const { user } = useAuthStore();
  const [selectedAnalysis, setSelectedAnalysis] = useState<ImagingAnalysis | null>(null);
  const [imagingStudies, setImagingStudies] = useState<ImagingAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    loadImagingStudies();
  }, [user]);

  const loadImagingStudies = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const studies = await getUserImagingStudies(user.id);
      setImagingStudies(studies);
      
      // Select the most recent completed study
      const completedStudy = studies.find(s => s.status === 'completed');
      if (completedStudy) {
        setSelectedAnalysis(completedStudy);
      }
    } catch (error) {
      console.error('Failed to load imaging studies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = (analysis: ImagingAnalysis) => {
    setSelectedAnalysis(analysis);
    setImagingStudies([analysis, ...imagingStudies]);
    setShowUpload(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="w-10 h-10 text-purple-400" />
            <h1 className="text-4xl font-bold">Medical Imaging Analysis</h1>
          </div>
          <p className="text-gray-300 text-lg">
            Upload and analyze brain MRI scans for volumetric measurements and atrophy detection
          </p>
        </div>

        {/* Upload Section */}
        {showUpload ? (
          <div className="mb-8 bg-gray-800/50 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-semibold">Upload New Scan</h2>
              <button
                onClick={() => setShowUpload(false)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
            <ImagingUpload
              onUploadComplete={handleUploadComplete}
              onError={(error) => console.error(error)}
            />
          </div>
        ) : (
          <div className="mb-8">
            <button
              onClick={() => setShowUpload(true)}
              className="flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors font-semibold"
            >
              <Upload className="w-5 h-5" />
              Upload New MRI Scan
            </button>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Studies List */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4">Your Imaging Studies</h2>
              
              {loading ? (
                <div className="text-center py-8">
                  <Activity className="w-8 h-8 mx-auto mb-2 animate-spin text-purple-400" />
                  <p className="text-gray-400">Loading studies...</p>
                </div>
              ) : imagingStudies.length === 0 ? (
                <div className="text-center py-8">
                  <Brain className="w-12 h-12 mx-auto mb-3 text-gray-600" />
                  <p className="text-gray-400 mb-4">No imaging studies yet</p>
                  <button
                    onClick={() => setShowUpload(true)}
                    className="text-purple-400 hover:text-purple-300 underline"
                  >
                    Upload your first scan
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {imagingStudies.map((study) => (
                    <button
                      key={study.id}
                      onClick={() => setSelectedAnalysis(study)}
                      className={`w-full text-left p-4 rounded-lg transition-colors ${
                        selectedAnalysis?.id === study.id
                          ? 'bg-purple-600'
                          : 'bg-gray-700/50 hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold">{study.modality}</span>
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            study.status === 'completed'
                              ? 'bg-green-600'
                              : study.status === 'processing'
                              ? 'bg-yellow-600'
                              : study.status === 'failed'
                              ? 'bg-red-600'
                              : 'bg-gray-600'
                          }`}
                        >
                          {study.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-300">
                        {new Date(study.created_at).toLocaleDateString()}
                      </p>
                      {study.atrophy_detection?.detected && (
                        <div className="flex items-center gap-1 mt-2 text-red-400 text-xs">
                          <AlertTriangle className="w-3 h-3" />
                          Atrophy detected
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Visualization and Details */}
          <div className="lg:col-span-2">
            {selectedAnalysis ? (
              <div className="space-y-6">
                {/* 3D Visualization */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6">
                  <h2 className="text-xl font-semibold mb-4">3D Brain Visualization</h2>
                  <div className="relative h-[500px] rounded-lg overflow-hidden">
                    <BrainVisualization3D
                      volumetricMeasurements={selectedAnalysis.volumetric_measurements}
                      atrophyDetection={selectedAnalysis.atrophy_detection}
                    />
                  </div>
                </div>

                {/* Measurements */}
                {selectedAnalysis.volumetric_measurements && (
                  <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6">
                    <h2 className="text-xl font-semibold mb-4">Volumetric Measurements</h2>
                    <div className="grid grid-cols-2 gap-4">
                      {selectedAnalysis.volumetric_measurements.hippocampal_volume_total && (
                        <div className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="text-sm text-gray-400 mb-1">Hippocampal Volume</p>
                          <p className="text-2xl font-bold">
                            {selectedAnalysis.volumetric_measurements.hippocampal_volume_total.toFixed(0)} mm³
                          </p>
                        </div>
                      )}
                      {selectedAnalysis.volumetric_measurements.cortical_thickness_mean && (
                        <div className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="text-sm text-gray-400 mb-1">Cortical Thickness</p>
                          <p className="text-2xl font-bold">
                            {selectedAnalysis.volumetric_measurements.cortical_thickness_mean.toFixed(2)} mm
                          </p>
                        </div>
                      )}
                      {selectedAnalysis.volumetric_measurements.total_brain_volume && (
                        <div className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="text-sm text-gray-400 mb-1">Total Brain Volume</p>
                          <p className="text-2xl font-bold">
                            {(selectedAnalysis.volumetric_measurements.total_brain_volume / 1000).toFixed(1)} cm³
                          </p>
                        </div>
                      )}
                      {selectedAnalysis.volumetric_measurements.ventricle_volume && (
                        <div className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="text-sm text-gray-400 mb-1">Ventricle Volume</p>
                          <p className="text-2xl font-bold">
                            {selectedAnalysis.volumetric_measurements.ventricle_volume.toFixed(0)} mm³
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Clinical Notes */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6">
                  <h2 className="text-xl font-semibold mb-4">Clinical Information</h2>
                  <div className="space-y-3 text-sm">
                    {selectedAnalysis.study_description && (
                      <div>
                        <span className="text-gray-400">Study: </span>
                        <span>{selectedAnalysis.study_description}</span>
                      </div>
                    )}
                    {selectedAnalysis.study_date && (
                      <div>
                        <span className="text-gray-400">Date: </span>
                        <span>{selectedAnalysis.study_date}</span>
                      </div>
                    )}
                    <div className="mt-4 p-4 bg-yellow-900/30 border border-yellow-600/50 rounded-lg">
                      <p className="text-yellow-200 text-xs">
                        <strong>Medical Disclaimer:</strong> These measurements are for informational purposes only.
                        Always consult with a qualified healthcare professional for medical diagnosis and treatment decisions.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-12 text-center">
                <Brain className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <h3 className="text-xl font-semibold mb-2">No Study Selected</h3>
                <p className="text-gray-400">
                  Select a study from the list or upload a new MRI scan to begin analysis
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImagingPage;
