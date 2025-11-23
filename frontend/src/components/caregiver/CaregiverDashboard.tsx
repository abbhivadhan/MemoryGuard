/**
 * Caregiver Dashboard - Main dashboard for caregivers to monitor patients
 * 
 * Requirements: 6.2, 6.3
 */
import React, { useEffect, useState } from 'react';
import { getMyPatients, PatientSummary } from '../../services/caregiverService';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

interface PatientCardProps {
  patient: PatientSummary;
  onViewDetails: (patientId: string) => void;
}

const PatientCard: React.FC<PatientCardProps> = ({ patient, onViewDetails }) => {
  const lastActiveDate = new Date(patient.last_active);
  const hoursAgo = Math.floor((Date.now() - lastActiveDate.getTime()) / (1000 * 60 * 60));
  
  // Determine status color based on last active time
  const getStatusColor = () => {
    if (hoursAgo < 24) return 'bg-green-500';
    if (hoursAgo < 48) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  // Get cognitive status color
  const getCognitiveColor = () => {
    if (!patient.cognitive_status) return 'text-gray-400';
    const percentage = (patient.cognitive_status.score / patient.cognitive_status.max_score) * 100;
    if (percentage >= 80) return 'text-green-500';
    if (percentage >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };
  
  // Get adherence color
  const getAdherenceColor = () => {
    if (!patient.medication_adherence) return 'text-gray-400';
    const rate = patient.medication_adherence.adherence_rate;
    if (rate >= 80) return 'text-green-500';
    if (rate >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700 hover:border-purple-500 transition-all">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
          <h3 className="text-xl font-bold text-white">{patient.patient_name}</h3>
        </div>
        <button
          onClick={() => onViewDetails(patient.patient_id)}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors"
        >
          View Details
        </button>
      </div>

      {/* Last Active */}
      <div className="mb-4 text-sm text-gray-400">
        Last active: {hoursAgo < 1 ? 'Just now' : `${hoursAgo} hours ago`}
      </div>

      {/* Cognitive Status */}
      {patient.cognitive_status && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Cognitive Status</span>
            <span className={`text-sm font-bold ${getCognitiveColor()}`}>
              {patient.cognitive_status.score}/{patient.cognitive_status.max_score}
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getCognitiveColor().replace('text-', 'bg-')}`}
              style={{
                width: `${(patient.cognitive_status.score / patient.cognitive_status.max_score) * 100}%`
              }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {patient.cognitive_status.type} - {new Date(patient.cognitive_status.completed_at).toLocaleDateString()}
          </div>
        </div>
      )}

      {/* Medication Adherence */}
      {patient.medication_adherence && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Medication Adherence</span>
            <span className={`text-sm font-bold ${getAdherenceColor()}`}>
              {patient.medication_adherence.adherence_rate}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getAdherenceColor().replace('text-', 'bg-')}`}
              style={{ width: `${patient.medication_adherence.adherence_rate}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {patient.medication_adherence.taken}/{patient.medication_adherence.total} doses (last 7 days)
          </div>
        </div>
      )}

      {/* Daily Activities */}
      {patient.daily_activities && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Daily Activities</span>
            <span className="text-sm font-bold text-blue-400">
              {patient.daily_activities.completed}/{patient.daily_activities.total}
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-blue-500"
              style={{ width: `${patient.daily_activities.completion_rate}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {patient.daily_activities.completion_rate}% completed today
          </div>
        </div>
      )}

      {/* Recent Alerts */}
      {patient.recent_alerts && patient.recent_alerts.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="text-sm text-gray-400 mb-2">Recent Alerts</div>
          <div className="space-y-2">
            {patient.recent_alerts.slice(0, 3).map((alert) => (
              <div
                key={alert.id}
                className={`text-xs p-2 rounded ${
                  alert.severity === 'high'
                    ? 'bg-red-900/30 text-red-300'
                    : alert.severity === 'medium'
                    ? 'bg-yellow-900/30 text-yellow-300'
                    : 'bg-blue-900/30 text-blue-300'
                }`}
              >
                <div className="font-semibold">{alert.type}</div>
                <div className="text-gray-400">{alert.message}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// 3D Status Visualization Component
const StatusVisualization: React.FC<{ patients: PatientSummary[] }> = ({ patients }) => {
  return (
    <div className="h-64 bg-gray-800 rounded-lg overflow-hidden">
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <OrbitControls enableZoom={false} />
        
        {patients.map((patient, index) => {
          const angle = (index / patients.length) * Math.PI * 2;
          const radius = 2;
          const x = Math.cos(angle) * radius;
          const z = Math.sin(angle) * radius;
          
          // Determine color based on overall status
          let color = '#10b981'; // green
          if (patient.medication_adherence && patient.medication_adherence.adherence_rate < 60) {
            color = '#ef4444'; // red
          } else if (patient.medication_adherence && patient.medication_adherence.adherence_rate < 80) {
            color = '#f59e0b'; // yellow
          }
          
          return (
            <mesh key={patient.patient_id} position={[x, 0, z]}>
              <sphereGeometry args={[0.3, 32, 32]} />
              <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
            </mesh>
          );
        })}
      </Canvas>
    </div>
  );
};

const CaregiverDashboard: React.FC = () => {
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMyPatients();
      setPatients(data);
    } catch (err: any) {
      console.error('Error loading patients:', err);
      setError(err.response?.data?.detail || 'Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (patientId: string) => {
    setSelectedPatient(patientId);
    // Navigate to detailed patient view
    window.location.href = `/caregiver/patient/${patientId}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading patients...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-500 text-xl">{error}</div>
      </div>
    );
  }

  if (patients.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-8">Caregiver Dashboard</h1>
          <div className="bg-gray-800 rounded-lg p-12 text-center">
            <div className="text-gray-400 text-lg mb-4">
              You are not currently monitoring any patients.
            </div>
            <div className="text-gray-500 text-sm">
              Patients can grant you caregiver access from their account settings.
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Calculate summary statistics
  const totalPatients = patients.length;
  const activePatients = patients.filter(p => {
    const hoursAgo = Math.floor((Date.now() - new Date(p.last_active).getTime()) / (1000 * 60 * 60));
    return hoursAgo < 24;
  }).length;
  
  const avgAdherence = patients
    .filter(p => p.medication_adherence)
    .reduce((sum, p) => sum + (p.medication_adherence?.adherence_rate || 0), 0) / 
    patients.filter(p => p.medication_adherence).length || 0;
  
  const totalAlerts = patients.reduce((sum, p) => sum + p.recent_alerts.length, 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Caregiver Portal</h2>
        <p className="text-gray-400">Monitor and support your patients</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="backdrop-blur-xl bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="text-gray-400 text-sm mb-2">Total Patients</div>
          <div className="text-3xl font-bold text-white">{totalPatients}</div>
        </div>
        <div className="backdrop-blur-xl bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="text-gray-400 text-sm mb-2">Active Today</div>
          <div className="text-3xl font-bold text-green-400">{activePatients}</div>
        </div>
        <div className="backdrop-blur-xl bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="text-gray-400 text-sm mb-2">Avg Adherence</div>
          <div className="text-3xl font-bold text-blue-400">{avgAdherence.toFixed(0)}%</div>
        </div>
        <div className="backdrop-blur-xl bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="text-gray-400 text-sm mb-2">Recent Alerts</div>
          <div className="text-3xl font-bold text-yellow-400">{totalAlerts}</div>
        </div>
      </div>

      {/* 3D Visualization */}
      <div>
        <h3 className="text-2xl font-bold text-white mb-4">Patient Status Overview</h3>
        <StatusVisualization patients={patients} />
      </div>

      {/* Patient Cards */}
      <div>
        <h3 className="text-2xl font-bold text-white mb-4">Your Patients</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {patients.map((patient) => (
            <PatientCard
              key={patient.patient_id}
              patient={patient}
              onViewDetails={handleViewDetails}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default CaregiverDashboard;
