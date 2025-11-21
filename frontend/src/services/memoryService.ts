/**
 * Memory Assistant API service
 */
import api from './api';

// Reminder types
export interface Reminder {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  reminder_type: 'medication' | 'appointment' | 'routine' | 'custom';
  scheduled_time: string;
  frequency: 'once' | 'daily' | 'weekly' | 'monthly' | 'custom';
  is_active: boolean;
  is_completed: boolean;
  completed_at?: string;
  send_notification: boolean;
  notification_sent: boolean;
  related_entity_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ReminderCreate {
  title: string;
  description?: string;
  reminder_type: 'medication' | 'appointment' | 'routine' | 'custom';
  scheduled_time: string;
  frequency: 'once' | 'daily' | 'weekly' | 'monthly' | 'custom';
  send_notification?: boolean;
  related_entity_id?: string;
}

export interface ReminderUpdate {
  title?: string;
  description?: string;
  scheduled_time?: string;
  frequency?: 'once' | 'daily' | 'weekly' | 'monthly' | 'custom';
  is_active?: boolean;
  is_completed?: boolean;
  send_notification?: boolean;
}

// Routine types
export interface DailyRoutine {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  scheduled_time?: string;
  time_of_day?: 'morning' | 'afternoon' | 'evening';
  days_of_week: number[];
  is_active: boolean;
  order_index: number;
  reminder_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoutineCompletion {
  id: string;
  user_id: string;
  routine_id: string;
  completion_date: string;
  completed: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DailyRoutineWithCompletion {
  routine: DailyRoutine;
  completion?: RoutineCompletion;
}

export interface DailyRoutineCreate {
  title: string;
  description?: string;
  scheduled_time?: string;
  time_of_day?: 'morning' | 'afternoon' | 'evening';
  days_of_week?: number[];
  reminder_enabled?: boolean;
  order_index?: number;
}

export interface RoutineCompletionCreate {
  routine_id: string;
  completion_date: string;
  completed: boolean;
  notes?: string;
}

// Face recognition types
export interface FaceProfile {
  id: string;
  user_id: string;
  name: string;
  relationship?: string;
  notes?: string;
  photo_url?: string;
  created_at: string;
  updated_at: string;
}

export interface FaceProfileCreate {
  name: string;
  relationship?: string;
  notes?: string;
  face_embedding: number[];
  photo_url?: string;
}

export interface FaceRecognitionMatch {
  profile: FaceProfile;
  similarity: number;
  confidence: 'high' | 'medium' | 'low';
}

export interface FaceRecognitionResponse {
  matches: FaceRecognitionMatch[];
  best_match?: FaceRecognitionMatch;
}

// Reminder API
export const reminderService = {
  async createReminder(data: ReminderCreate): Promise<Reminder> {
    const response = await api.post('/reminders/', data);
    return response.data;
  },

  async getReminders(filters?: {
    reminder_type?: string;
    is_active?: boolean;
    is_completed?: boolean;
    start_date?: string;
    end_date?: string;
  }): Promise<{ reminders: Reminder[]; total: number }> {
    const response = await api.get('/reminders/', { params: filters });
    return response.data;
  },

  async getUpcomingReminders(hours: number = 24): Promise<{ reminders: Reminder[]; total: number }> {
    const response = await api.get('/reminders/upcoming', { params: { hours } });
    return response.data;
  },

  async getReminder(id: string): Promise<Reminder> {
    const response = await api.get(`/reminders/${id}`);
    return response.data;
  },

  async updateReminder(id: string, data: ReminderUpdate): Promise<Reminder> {
    const response = await api.put(`/reminders/${id}`, data);
    return response.data;
  },

  async completeReminder(id: string): Promise<Reminder> {
    const response = await api.post(`/reminders/${id}/complete`);
    return response.data;
  },

  async deleteReminder(id: string): Promise<void> {
    await api.delete(`/reminders/${id}`);
  },
};

// Routine API
export const routineService = {
  async createRoutine(data: DailyRoutineCreate): Promise<DailyRoutine> {
    const response = await api.post('/routines/', data);
    return response.data;
  },

  async getRoutines(filters?: {
    is_active?: boolean;
    time_of_day?: string;
    include_today?: boolean;
  }): Promise<{ routines: DailyRoutineWithCompletion[]; total: number }> {
    const response = await api.get('/routines/', { params: filters });
    return response.data;
  },

  async getTodayRoutines(): Promise<{ routines: DailyRoutineWithCompletion[]; total: number }> {
    const response = await api.get('/routines/today');
    return response.data;
  },

  async getRoutine(id: string): Promise<DailyRoutine> {
    const response = await api.get(`/routines/${id}`);
    return response.data;
  },

  async updateRoutine(id: string, data: Partial<DailyRoutineCreate>): Promise<DailyRoutine> {
    const response = await api.put(`/routines/${id}`, data);
    return response.data;
  },

  async deleteRoutine(id: string): Promise<void> {
    await api.delete(`/routines/${id}`);
  },

  async createCompletion(data: RoutineCompletionCreate): Promise<RoutineCompletion> {
    const response = await api.post('/routines/completions', data);
    return response.data;
  },

  async getCompletionStats(days: number = 7): Promise<{
    total_completions: number;
    completed_count: number;
    skipped_count: number;
    completion_rate: number;
    days: number;
  }> {
    const response = await api.get('/routines/completions/stats', { params: { days } });
    return response.data;
  },
};

// Face recognition API
export const faceService = {
  async createProfile(data: FaceProfileCreate): Promise<FaceProfile> {
    const response = await api.post('/faces/', data);
    return response.data;
  },

  async getProfiles(): Promise<{ profiles: FaceProfile[]; total: number }> {
    const response = await api.get('/faces/');
    return response.data;
  },

  async getProfile(id: string): Promise<FaceProfile> {
    const response = await api.get(`/faces/${id}`);
    return response.data;
  },

  async updateProfile(id: string, data: Partial<FaceProfileCreate>): Promise<FaceProfile> {
    const response = await api.put(`/faces/${id}`, data);
    return response.data;
  },

  async deleteProfile(id: string): Promise<void> {
    await api.delete(`/faces/${id}`);
  },

  async recognizeFace(
    face_embedding: number[],
    threshold: number = 0.6
  ): Promise<FaceRecognitionResponse> {
    const response = await api.post('/faces/recognize', {
      face_embedding,
      threshold,
    });
    return response.data;
  },
};
