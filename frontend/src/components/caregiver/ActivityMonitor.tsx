/**
 * Activity Monitor - Real-time activity monitoring for caregivers
 * 
 * Requirements: 6.2
 */
import React, { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';


interface Activity {
  id: string;
  name: string;
  description: string;
  time_of_day?: string;
  type?: string;
  scheduled_time: string;
}

interface ActivityStatus {
  patient_id: string;
  patient_name: string;
  current_activities: Activity[];
  missed_activities: Activity[];
  completed_today: number;
  total_today: number;
  last_activity_time?: string;
}

interface ActivityMonitorProps {
  patientId: string;
}

// 3D Activity Timeline Component
const ActivityTimeline: React.FC<{ activities: Activity[]; missed: Activity[] }> = ({ 
  activities, 
  missed 
}) => {
  const allActivities = [...activities, ...missed].sort((a, b) => 
    new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime()
  );

  return (
    <>
      {allActivities.map((activity, index) => {
        const isMissed = missed.some(m => m.id === activity.id);
        const x = (index - allActivities.length / 2) * 2;
        const color = isMissed ? '#ef4444' : '#10b981';
        
        return (
          <group key={activity.id} position={[x, 0, 0]}>
            <mesh>
              <cylinderGeometry args={[0.2, 0.2, 1, 32]} />
              <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} />
            </mesh>
            <Text
              position={[0, -1, 0]}
              fontSize={0.2}
              color="white"
              anchorX="center"
              anchorY="middle"
            >
              {new Date(activity.scheduled_time).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </Text>
          </group>
        );
      })}
      
      {/* Timeline base */}
      <mesh position={[0, -0.5, 0]}>
        <boxGeometry args={[allActivities.length * 2, 0.1, 0.1]} />
        <meshStandardMaterial color="#4b5563" />
      </mesh>
    </>
  );
};

const ActivityMonitor: React.FC<ActivityMonitorProps> = ({ patientId }) => {
  const [status, setStatus] = useState<ActivityStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadActivityStatus();
    
    // Auto-refresh every 30 seconds
    let interval: ReturnType<typeof setInterval>;
    if (autoRefresh) {
      interval = setInterval(loadActivityStatus, 30000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [patientId, autoRefresh]);

  const loadActivityStatus = async () => {
    try {
      setError(null);
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/caregivers/patients/${patientId}/activity-status`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to load activity status');
      }
      
      const data = await response.json();
      setStatus(data);
    } catch (err: any) {
      console.error('Error loading activity status:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="text-white text-center">Loading activity status...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-red-700">
        <div className="text-red-500 text-center">{error}</div>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  const completionRate = status.total_today > 0 
    ? (status.completed_today / status.total_today * 100).toFixed(0)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-white">Activity Monitor</h2>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 text-sm text-gray-400">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded"
              />
              <span>Auto-refresh</span>
            </label>
            <button
              onClick={loadActivityStatus}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Completed Today</div>
            <div className="text-2xl font-bold text-green-500">
              {status.completed_today}/{status.total_today}
            </div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Completion Rate</div>
            <div className="text-2xl font-bold text-blue-500">{completionRate}%</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Missed Activities</div>
            <div className="text-2xl font-bold text-red-500">
              {status.missed_activities.length}
            </div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Last Activity</div>
            <div className="text-sm font-bold text-white">
              {status.last_activity_time 
                ? new Date(status.last_activity_time).toLocaleTimeString()
                : 'No activity'}
            </div>
          </div>
        </div>
      </div>

      {/* 3D Timeline Visualization */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Activity Timeline</h3>
        <div className="h-64 bg-gray-900 rounded-lg overflow-hidden">
          <Canvas camera={{ position: [0, 2, 8], fov: 50 }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} />
            <OrbitControls enableZoom={false} />
            <ActivityTimeline 
              activities={status.current_activities} 
              missed={status.missed_activities}
            />
          </Canvas>
        </div>
        <div className="mt-4 flex items-center justify-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-400">Upcoming</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-gray-400">Missed</span>
          </div>
        </div>
      </div>

      {/* Missed Activities Alert */}
      {status.missed_activities.length > 0 && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <svg className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 className="text-xl font-bold text-red-500">Missed Activities</h3>
          </div>
          <div className="space-y-3">
            {status.missed_activities.map((activity) => (
              <div key={activity.id} className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-white">{activity.name}</div>
                    <div className="text-sm text-gray-400">{activity.description}</div>
                  </div>
                  <div className="text-sm text-red-400">
                    Scheduled: {new Date(activity.scheduled_time).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Current/Upcoming Activities */}
      {status.current_activities.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Upcoming Activities</h3>
          <div className="space-y-3">
            {status.current_activities.map((activity) => (
              <div key={activity.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-white">{activity.name}</div>
                    <div className="text-sm text-gray-400">{activity.description}</div>
                  </div>
                  <div className="text-sm text-green-400">
                    {new Date(activity.scheduled_time).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Activities Message */}
      {status.current_activities.length === 0 && status.missed_activities.length === 0 && (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <div className="text-gray-400 text-lg">
            No activities scheduled for today
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityMonitor;
