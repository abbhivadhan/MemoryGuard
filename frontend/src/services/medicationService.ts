import api from './api';

export interface Medication {
  id: string;
  user_id: string;
  name: string;
  dosage: string;
  frequency: string;
  schedule: string[];
  adherence_log: AdherenceLogEntry[];
  side_effects: string[];
  active: boolean;
  instructions?: string;
  prescriber?: string;
  pharmacy?: string;
  start_date: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export interface AdherenceLogEntry {
  scheduled_time: string;
  taken_time?: string;
  skipped: boolean;
  notes?: string;
  logged_at: string;
}

export interface MedicationCreate {
  name: string;
  dosage: string;
  frequency: string;
  schedule?: string[];
  instructions?: string;
  prescriber?: string;
  pharmacy?: string;
  start_date?: string;
  end_date?: string;
}

export interface MedicationUpdate {
  name?: string;
  dosage?: string;
  frequency?: string;
  schedule?: string[];
  instructions?: string;
  prescriber?: string;
  pharmacy?: string;
  active?: boolean;
  end_date?: string;
}

export interface MedicationLogRequest {
  scheduled_time: string;
  taken_time?: string;
  skipped: boolean;
  notes?: string;
}

export interface AdherenceStats {
  medication_id: string;
  medication_name: string;
  total_scheduled: number;
  total_taken: number;
  total_skipped: number;
  adherence_rate: number;
  period_days: number;
  last_taken?: string;
  next_scheduled?: string;
}

export interface SideEffectCreate {
  side_effect: string;
  severity?: 'mild' | 'moderate' | 'severe';
  occurred_at?: string;
}

export interface InteractionWarning {
  severity: string;
  description: string;
  medications: string[];
  recommendation: string;
}

export interface MedicationListResponse {
  medications: Medication[];
  total: number;
}

class MedicationService {
  async createMedication(data: MedicationCreate): Promise<Medication> {
    const response = await api.post('/medications/', data);
    return response.data;
  }

  async getMedications(activeOnly: boolean = true): Promise<MedicationListResponse> {
    const response = await api.get('/medications/', {
      params: { active_only: activeOnly },
    });
    return response.data;
  }

  async getMedication(medicationId: string): Promise<Medication> {
    const response = await api.get(`/medications/${medicationId}`);
    return response.data;
  }

  async updateMedication(medicationId: string, data: MedicationUpdate): Promise<Medication> {
    const response = await api.put(`/medications/${medicationId}`, data);
    return response.data;
  }

  async deleteMedication(medicationId: string): Promise<void> {
    await api.delete(`/medications/${medicationId}`);
  }

  async logMedication(medicationId: string, data: MedicationLogRequest): Promise<Medication> {
    const response = await api.post(`/medications/${medicationId}/log`, data);
    return response.data;
  }

  async getAdherenceStats(medicationId: string, days: number = 7): Promise<AdherenceStats> {
    const response = await api.get(`/medications/${medicationId}/adherence`, {
      params: { days },
    });
    return response.data;
  }

  async addSideEffect(medicationId: string, data: SideEffectCreate): Promise<Medication> {
    const response = await api.post(`/medications/${medicationId}/side-effects`, data);
    return response.data;
  }

  async checkInteractions(medicationNames: string[]): Promise<InteractionWarning[]> {
    const response = await api.post('/medications/check-interactions', medicationNames);
    return response.data;
  }

  async checkAdherenceAlert(userId: string): Promise<any> {
    const response = await api.get(`/medications/users/${userId}/adherence-alert`);
    return response.data;
  }
}

export const medicationService = new MedicationService();
