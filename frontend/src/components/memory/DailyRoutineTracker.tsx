import React, { useState, useEffect } from 'react';
import {
  DailyRoutineWithCompletion,
  routineService,
  DailyRoutineCreate,
} from '../../services/memoryService';
import { motion, AnimatePresence } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

// 3D Progress Ring Component
const ProgressRing: React.FC<{ progress: number }> = ({ progress }) => {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]}>
      <torusGeometry args={[1, 0.2, 16, 100, (progress / 100) * Math.PI * 2]} />
      <meshStandardMaterial
        color={progress === 100 ? '#10b981' : '#3b82f6'}
        emissive={progress === 100 ? '#10b981' : '#3b82f6'}
        emissiveIntensity={0.5}
      />
    </mesh>
  );
};

const DailyRoutineTracker: React.FC = () => {
  const [routines, setRoutines] = useState<DailyRoutineWithCompletion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [stats, setStats] = useState<any>(null);

  const [newRoutine, setNewRoutine] = useState<DailyRoutineCreate>({
    title: '',
    description: '',
    time_of_day: 'morning',
    days_of_week: [0, 1, 2, 3, 4, 5, 6],
    reminder_enabled: true,
    order_index: 0,
  });

  useEffect(() => {
    loadRoutines();
    loadStats();
  }, []);

  const loadRoutines = async () => {
    try {
      setLoading(true);
      const data = await routineService.getTodayRoutines();
      setRoutines(data.routines);
    } catch (error) {
      console.error('Failed to load routines:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await routineService.getCompletionStats(7);
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleToggleCompletion = async (routine: DailyRoutineWithCompletion) => {
    try {
      const isCompleted = routine.completion?.completed || false;
      await routineService.createCompletion({
        routine_id: routine.routine.id,
        completion_date: new Date().toISOString(),
        completed: !isCompleted,
      });
      loadRoutines();
      loadStats();
    } catch (error) {
      console.error('Failed to toggle completion:', error);
    }
  };

  const handleCreateRoutine = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await routineService.createRoutine(newRoutine);
      setShowCreateForm(false);
      setNewRoutine({
        title: '',
        description: '',
        time_of_day: 'morning',
        days_of_week: [0, 1, 2, 3, 4, 5, 6],
        reminder_enabled: true,
        order_index: 0,
      });
      loadRoutines();
    } catch (error) {
      console.error('Failed to create routine:', error);
    }
  };

  const handleDeleteRoutine = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this routine?')) {
      try {
        await routineService.deleteRoutine(id);
        loadRoutines();
      } catch (error) {
        console.error('Failed to delete routine:', error);
      }
    }
  };

  const completedCount = routines.filter((r) => r.completion?.completed).length;
  const totalCount = routines.length;
  const completionPercentage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Daily Routine</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          {showCreateForm ? 'Cancel' : '+ New Routine'}
        </button>
      </div>

      {/* 3D Progress Visualization */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4 text-center">Today's Progress</h3>
        <div className="h-64 relative">
          <Canvas camera={{ position: [0, 2, 5], fov: 50 }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} />
            <ProgressRing progress={completionPercentage} />
            <OrbitControls enableZoom={false} />
          </Canvas>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center">
              <div className="text-4xl font-bold text-gray-800">
                {completedCount}/{totalCount}
              </div>
              <div className="text-sm text-gray-600">Tasks Completed</div>
            </div>
          </div>
        </div>

        {stats && (
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{stats.completion_rate}%</div>
              <div className="text-sm text-gray-600">7-Day Rate</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{stats.completed_count}</div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">{stats.skipped_count}</div>
              <div className="text-sm text-gray-600">Skipped</div>
            </div>
          </div>
        )}
      </div>

      {/* Create form */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.form
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            onSubmit={handleCreateRoutine}
            className="bg-white rounded-lg shadow-md p-6 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4">Create New Routine</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  required
                  value={newRoutine.title}
                  onChange={(e) => setNewRoutine({ ...newRoutine, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Morning exercise"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={newRoutine.description}
                  onChange={(e) => setNewRoutine({ ...newRoutine, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={2}
                  placeholder="Additional details..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Time of Day
                </label>
                <select
                  value={newRoutine.time_of_day}
                  onChange={(e) =>
                    setNewRoutine({ ...newRoutine, time_of_day: e.target.value as any })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="morning">Morning</option>
                  <option value="afternoon">Afternoon</option>
                  <option value="evening">Evening</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Days of Week
                </label>
                <div className="flex gap-2">
                  {dayNames.map((day, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => {
                        const days = newRoutine.days_of_week || [];
                        if (days.includes(index)) {
                          setNewRoutine({
                            ...newRoutine,
                            days_of_week: days.filter((d) => d !== index),
                          });
                        } else {
                          setNewRoutine({
                            ...newRoutine,
                            days_of_week: [...days, index].sort(),
                          });
                        }
                      }}
                      className={`px-3 py-2 rounded-lg transition-colors ${
                        newRoutine.days_of_week?.includes(index)
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {day}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-4">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Create Routine
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>

      {/* Routines list */}
      <div className="space-y-3">
        <AnimatePresence>
          {routines.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12 text-gray-500 bg-white rounded-lg shadow-md"
            >
              <p className="text-xl mb-2">No routines for today</p>
              <p className="text-sm">Create your first routine to get started</p>
            </motion.div>
          ) : (
            routines.map((item) => {
              const isCompleted = item.completion?.completed || false;
              return (
                <motion.div
                  key={item.routine.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className={`bg-white rounded-lg shadow-md p-4 border-l-4 transition-all ${
                    isCompleted ? 'border-green-500' : 'border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <button
                        onClick={() => handleToggleCompletion(item)}
                        className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${
                          isCompleted
                            ? 'bg-green-500 border-green-500'
                            : 'border-gray-300 hover:border-blue-500'
                        }`}
                      >
                        {isCompleted && <span className="text-white text-lg">✓</span>}
                      </button>

                      <div className="flex-1">
                        <h3
                          className={`text-lg font-semibold ${
                            isCompleted ? 'line-through text-gray-500' : 'text-gray-800'
                          }`}
                        >
                          {item.routine.title}
                        </h3>
                        {item.routine.description && (
                          <p className="text-sm text-gray-600">{item.routine.description}</p>
                        )}
                        <div className="flex items-center gap-2 mt-1">
                          {item.routine.time_of_day && (
                            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                              {item.routine.time_of_day}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => handleDeleteRoutine(item.routine.id)}
                      className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default DailyRoutineTracker;
