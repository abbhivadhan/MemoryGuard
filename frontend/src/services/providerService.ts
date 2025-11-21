/**
 * Provider portal service for healthcare provider access
 */
import api from './api';

export interface ProviderAccess {
  id: string;
  patient_id: string;
  provider_id: string;
  status: 'pending' | 'active' | 'revoked' | 'expired';
  granted_at: string | null;
  expires_at: string | null;
  revoked_at: string | null;
  can_view_assessments: boolean;
  can_view_health_metrics: boolean;
  can_view_medications: boolean;
  can_view_imaging: boolean;
  can_add_notes: boolean;
  access_reason: string | null;
  created_at: string;
}

export interface Provider {
  id: string;
  email: string;
  name: string;
  picture: string | null;
  provider_type: string;
  institution: string | null;
  specialty: string | null;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  last_active: string;
}

export interface ProviderAccessWithProvider extends ProviderAccess {
  provider: Provider;
}

export interface ProviderAccessGrant {
  provider_email: string;
  can_view_assessments?: boolean;
  can_view_health_metrics?: boolean;
  can_view_medications?: boolean;
  can_view_imaging?: boolean;
  can_add_notes?: boolean;
  access_reason?: string;
  expires_at?: string;
}

export interface AccessLog {
  id: string;
  provider_access_id: string;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  ip_address: string | null;
  details: string | null;
  created_at: string;
}

export interface ClinicalNote {
  id: string;
  patient_id: string;
  provider_id: string;
  title: string;
  content: string;
  note_type: string | null;
  is_private: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClinicalNoteWithProvider extends ClinicalNote {
  provider: Provider;
}

export interface PatientSummary {
  id: string;
  name: string;
  email: string;
  date_of_birth: string | null;
  apoe_genotype: string | null;
  last_active: string;
}

export interface PatientHealthOverview {
  latest_mmse_score: number | null;
  latest_moca_score: number | null;
  latest_risk_score: number | null;
  medication_adherence_rate: number | null;
  last_assessment_date: string | null;
  last_prediction_date: string | null;
}

export interface PatientDashboardData {
  patient: PatientSummary;
  health_overview: PatientHealthOverview;
  recent_assessments: any[];
  recent_health_metrics: any[];
  active_medications: any[];
  recent_predictions: any[];
  clinical_notes: ClinicalNote[];
}

// Patient endpoints for managing provider access
export const grantProviderAccess = async (
  accessGrant: ProviderAccessGrant
): Promise<ProviderAccess> => {
  const response = await api.post('/providers/access/grant', accessGrant);
  return response.data;
};

export const getMyProviders = async (): Promise<ProviderAccessWithProvider[]> => {
  const response = await api.get('/providers/access/my-providers');
  return response.data;
};

export const updateProviderAccess = async (
  accessId: string,
  updates: Partial<ProviderAccess>
): Promise<ProviderAccess> => {
  const response = await api.put(`/providers/access/${accessId}`, updates);
  return response.data;
};

export const revokeProviderAccess = async (accessId: string): Promise<void> => {
  await api.delete(`/providers/access/${accessId}`);
};

export const getAccessLogs = async (accessId: string): Promise<AccessLog[]> => {
  const response = await api.get(`/providers/access/${accessId}/logs`);
  return response.data;
};

// Provider endpoints for accessing patient data
export const getMyPatients = async (): Promise<PatientSummary[]> => {
  const response = await api.get('/providers/patients');
  return response.data;
};

export const getPatientDashboard = async (
  patientId: string
): Promise<PatientDashboardData> => {
  const response = await api.get(`/providers/patients/${patientId}/dashboard`);
  return response.data;
};

// Clinical notes endpoints
export const createClinicalNote = async (note: {
  patient_id: string;
  title: string;
  content: string;
  note_type?: string;
  is_private?: boolean;
}): Promise<ClinicalNote> => {
  const response = await api.post('/providers/notes', note);
  return response.data;
};

export const getPatientNotes = async (
  patientId: string
): Promise<ClinicalNoteWithProvider[]> => {
  const response = await api.get(`/providers/notes/${patientId}`);
  return response.data;
};

export const updateClinicalNote = async (
  noteId: string,
  updates: Partial<ClinicalNote>
): Promise<ClinicalNote> => {
  const response = await api.put(`/providers/notes/${noteId}`, updates);
  return response.data;
};

export const deleteClinicalNote = async (noteId: string): Promise<void> => {
  await api.delete(`/providers/notes/${noteId}`);
};
