import React, { useState, useEffect, useRef } from 'react';
import { FaceProfile, faceService, FaceRecognitionMatch } from '../../services/memoryService';
import { motion, AnimatePresence } from 'framer-motion';
import * as faceapi from '@vladmandic/face-api';

const FaceRecognition: React.FC = () => {
  const [profiles, setProfiles] = useState<FaceProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [recognizing, setRecognizing] = useState(false);
  const [recognitionResult, setRecognitionResult] = useState<FaceRecognitionMatch | null>(null);
  const [modelsLoaded, setModelsLoaded] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [newProfile, setNewProfile] = useState({
    name: '',
    relationship: '',
    notes: '',
  });

  useEffect(() => {
    loadProfiles();
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      // Load face-api.js models from CDN
      const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model';
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
        faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
        faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
      ]);
      setModelsLoaded(true);
    } catch (error) {
      console.error('Failed to load face recognition models:', error);
    }
  };

  const loadProfiles = async () => {
    try {
      setLoading(true);
      const data = await faceService.getProfiles();
      setProfiles(data.profiles);
    } catch (error) {
      console.error('Failed to load profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Failed to start camera:', error);
      alert('Failed to access camera. Please check permissions.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const extractFaceEmbedding = async (
    imageElement: HTMLImageElement | HTMLVideoElement
  ): Promise<number[] | null> => {
    if (!modelsLoaded) {
      alert('Face recognition models are still loading. Please wait.');
      return null;
    }

    try {
      const detection = await faceapi
        .detectSingleFace(imageElement, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceDescriptor();

      if (!detection) {
        alert('No face detected. Please try again with a clear face photo.');
        return null;
      }

      return Array.from(detection.descriptor);
    } catch (error) {
      console.error('Failed to extract face embedding:', error);
      return null;
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const img = new Image();
    img.src = URL.createObjectURL(file);

    img.onload = async () => {
      const embedding = await extractFaceEmbedding(img);
      if (embedding) {
        try {
          // In a real app, you'd upload the photo to storage and get a URL
          const photoUrl = URL.createObjectURL(file);

          await faceService.createProfile({
            name: newProfile.name,
            relationship: newProfile.relationship,
            notes: newProfile.notes,
            face_embedding: embedding,
            photo_url: photoUrl,
          });

          setShowAddForm(false);
          setNewProfile({ name: '', relationship: '', notes: '' });
          loadProfiles();
        } catch (error) {
          console.error('Failed to create profile:', error);
          alert('Failed to create profile. Please try again.');
        }
      }
      URL.revokeObjectURL(img.src);
    };
  };

  const recognizeFace = async () => {
    if (!videoRef.current || !modelsLoaded) return;

    setRecognizing(true);
    setRecognitionResult(null);

    try {
      const embedding = await extractFaceEmbedding(videoRef.current);
      if (embedding) {
        const result = await faceService.recognizeFace(embedding, 0.6);
        if (result.best_match) {
          setRecognitionResult(result.best_match);
        } else {
          alert('No matching face found in your profiles.');
        }
      }
    } catch (error) {
      console.error('Failed to recognize face:', error);
      alert('Failed to recognize face. Please try again.');
    } finally {
      setRecognizing(false);
    }
  };

  const handleDeleteProfile = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this profile?')) {
      try {
        await faceService.deleteProfile(id);
        loadProfiles();
      } catch (error) {
        console.error('Failed to delete profile:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Face Recognition</h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          {showAddForm ? 'Cancel' : '+ Add Person'}
        </button>
      </div>

      {!modelsLoaded && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-yellow-800">Loading face recognition models...</p>
        </div>
      )}

      {/* Add profile form */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white rounded-lg shadow-md p-6 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4">Add New Person</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  required
                  value={newProfile.name}
                  onChange={(e) => setNewProfile({ ...newProfile, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Sarah Johnson"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Relationship
                </label>
                <input
                  type="text"
                  value={newProfile.relationship}
                  onChange={(e) => setNewProfile({ ...newProfile, relationship: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Daughter, Friend, Doctor"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={newProfile.notes}
                  onChange={(e) => setNewProfile({ ...newProfile, notes: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={2}
                  placeholder="Memory prompts or additional context..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Photo *</label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Upload a clear photo showing the person's face
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Camera recognition */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Recognize Face</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full rounded-lg bg-gray-900"
            />
            <canvas ref={canvasRef} className="hidden" />

            <div className="flex gap-2 mt-4">
              <button
                onClick={startCamera}
                disabled={!modelsLoaded}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
              >
                Start Camera
              </button>
              <button
                onClick={stopCamera}
                className="flex-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                Stop Camera
              </button>
            </div>

            <button
              onClick={recognizeFace}
              disabled={recognizing || !modelsLoaded}
              className="w-full mt-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
            >
              {recognizing ? 'Recognizing...' : 'Recognize Face'}
            </button>
          </div>

          <div>
            {recognitionResult ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-green-50 border border-green-200 rounded-lg p-6"
              >
                <h4 className="text-2xl font-bold text-green-800 mb-2">
                  {recognitionResult.profile.name}
                </h4>
                {recognitionResult.profile.relationship && (
                  <p className="text-green-700 mb-2">
                    {recognitionResult.profile.relationship}
                  </p>
                )}
                {recognitionResult.profile.notes && (
                  <p className="text-gray-700 mb-4">{recognitionResult.profile.notes}</p>
                )}
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Confidence:</span>
                  <span
                    className={`px-2 py-1 rounded text-sm ${
                      recognitionResult.confidence === 'high'
                        ? 'bg-green-500 text-white'
                        : recognitionResult.confidence === 'medium'
                        ? 'bg-yellow-500 text-white'
                        : 'bg-orange-500 text-white'
                    }`}
                  >
                    {recognitionResult.confidence} ({(recognitionResult.similarity * 100).toFixed(1)}
                    %)
                  </span>
                </div>
              </motion.div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 h-full flex items-center justify-center">
                <p className="text-gray-500 text-center">
                  Recognition result will appear here
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Profiles list */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4">Saved Profiles ({profiles.length})</h3>

        {profiles.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            No profiles yet. Add your first person to get started.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {profiles.map((profile) => (
              <motion.div
                key={profile.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="border border-gray-200 rounded-lg p-4"
              >
                {profile.photo_url && (
                  <img
                    src={profile.photo_url}
                    alt={profile.name}
                    className="w-full h-48 object-cover rounded-lg mb-3"
                  />
                )}
                <h4 className="text-lg font-semibold text-gray-800">{profile.name}</h4>
                {profile.relationship && (
                  <p className="text-sm text-gray-600">{profile.relationship}</p>
                )}
                {profile.notes && <p className="text-sm text-gray-500 mt-2">{profile.notes}</p>}
                <button
                  onClick={() => handleDeleteProfile(profile.id)}
                  className="mt-3 w-full px-3 py-1 text-sm text-red-600 border border-red-600 rounded hover:bg-red-50 transition-colors"
                >
                  Delete
                </button>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FaceRecognition;
