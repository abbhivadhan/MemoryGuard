import api from './api';
import { LocationData } from './locationService';

export interface MedicalInfo {
  medications?: string[];
  allergies?: string[];
  conditions?: string[];
  blood_type?: string;
  emergency_notes?: string;
}

export interface EmergencyAlert {
  id: string;
  user_id: string;
  location?: {
    latitude: number;
    longitude: number;
    accuracy: number;
    address?: string;
  };
  medical_info?: MedicalInfo;
  is_active: boolean;
  resolved_at?: string;
  resolution_notes?: string;
  contacts_notified?: string[];
  notification_sent_at?: string;
  trigger_type: 'manual' | 'automatic';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface EmergencyContact {
  id: string;
  user_id: string;
  name: string;
  phone: string;
  email?: string;
  relationship_type: string;
  relationship_description?: string;
  priority: string;
  active: boolean;
  address?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface EmergencyAlertCreate {
  location?: LocationData;
  medical_info?: MedicalInfo;
  trigger_type?: 'manual' | 'automatic';
  notes?: string;
}

class EmergencyService {
  /**
   * Activate an emergency alert
   */
  async activateEmergencyAlert(data: EmergencyAlertCreate): Promise<EmergencyAlert> {
    const response = await api.post('/emergency/activate', data);
    return response.data;
  }

  /**
   * Get all emergency alerts
   */
  async getEmergencyAlerts(activeOnly: boolean = false): Promise<EmergencyAlert[]> {
    const response = await api.get('/emergency/alerts', {
      params: { active_only: activeOnly },
    });
    return response.data;
  }

  /**
   * Get a specific emergency alert
   */
  async getEmergencyAlert(alertId: string): Promise<EmergencyAlert> {
    const response = await api.get(`/emergency/alerts/${alertId}`);
    return response.data;
  }

  /**
   * Resolve an emergency alert
   */
  async resolveEmergencyAlert(
    alertId: string,
    resolutionNotes?: string
  ): Promise<EmergencyAlert> {
    const response = await api.post(`/emergency/alerts/${alertId}/resolve`, {
      resolution_notes: resolutionNotes,
    });
    return response.data;
  }

  /**
   * Get all emergency contacts
   */
  async getEmergencyContacts(): Promise<EmergencyContact[]> {
    const response = await api.get('/emergency/contacts');
    return response.data;
  }

  /**
   * Create a new emergency contact
   */
  async createEmergencyContact(
    contactData: Partial<EmergencyContact>
  ): Promise<EmergencyContact> {
    const response = await api.post('/emergency/contacts', contactData);
    return response.data;
  }

  /**
   * Update an emergency contact
   */
  async updateEmergencyContact(
    contactId: string,
    contactData: Partial<EmergencyContact>
  ): Promise<EmergencyContact> {
    const response = await api.put(`/emergency/contacts/${contactId}`, contactData);
    return response.data;
  }

  /**
   * Delete an emergency contact
   */
  async deleteEmergencyContact(contactId: string): Promise<void> {
    await api.delete(`/emergency/contacts/${contactId}`);
  }

  /**
   * Get medical information for emergency
   */
  async getMedicalInfo(): Promise<MedicalInfo> {
    // This would fetch from user profile or health records
    // For now, return empty object
    return {};
  }

  /**
   * Update medical information
   */
  async updateMedicalInfo(medicalInfo: MedicalInfo): Promise<MedicalInfo> {
    // This would update user profile or health records
    // For now, just return the input
    return medicalInfo;
  }
}

export const emergencyService = new EmergencyService();
