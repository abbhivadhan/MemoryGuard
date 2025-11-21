/**
 * Caregiver service for managing caregiver relationships and dashboard data.
 * 
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
 */
import api from './api';

export interface CaregiverPermissions {
  can_view_health_data: boolean;
  can_view_assessments: boolean;
  can_view_medications: boolean;
  can_manage_reminders: boolean;
  can_receive_alerts: boolean;
}

export interface CaregiverRelationship {
  id: string;
  patient_id: string;
  caregiver_id: string;
  caregiver_name: string;
  caregiver_email: string;
  relationship_type: string;
  relationship_description?: string;
  permissions: CaregiverPermissions;
  active: boolean;
  approved: boolean;
  created_at: string;
  updated_at: string;
}

export interface PatientSummary {
  patient_id: string;
  patient_name: string;
  last_active: string;
  cognitive_status?: {
    type: string;
    score: number;
    max_score: number;
    completed_at: string;
  };
  medication_adherence?: {
    adherence_rate: number;
    taken: number;
    total: number;
    period_days: number;
  };
  daily_activities?: {
    completed: number;
    total: number;
    completion_rate: number;
  };
  recent_alerts: Array<{
    id: string;
    type: string;
    message: string;
    severity: string;
    created_at: string;
  }>;
}

export interface InviteCaregiverRequest {
  caregiver_email: string;
  relationship_type: string;
  relationship_description?: string;
  can_view_health_data?: boolean;
  can_view_assessments?: boolean;
  can_view_medications?: boolean;
  can_manage_reminders?: boolean;
  can_receive_alerts?: boolean;
}

export interface UpdatePermissionsRequest {
  can_view_health_data?: boolean;
  can_view_assessments?: boolean;
  can_view_medications?: boolean;
  can_manage_reminders?: boolean;
  can_receive_alerts?: boolean;
}

export interface ActivityLog {
  id: string;
  patient_id: string;
  activity_type: string;
  activity_name: string;
  description: string;
  timestamp: string;
  status: string;
  metadata?: Record<string, any>;
}

export interface CaregiverAlert {
  id: string;
  patient_id: string;
  patient_name: string;
  alert_type: string;
  message: string;
  severity: string;
  created_at: string;
  acknowledged: boolean;
}

/**
 * Invite a caregiver to access patient data
 */
export const inviteCaregiver = async (
  request: InviteCaregiverRequest
): Promise<CaregiverRelationship> => {
  const response = await api.post('/caregivers/invite', request);
  return response.data;
};

/**
 * Get all caregivers for the current user (patient)
 */
export const getMyCaregivers = async (): Promise<CaregiverRelationship[]> => {
  const response = await api.get('/caregivers/my-caregivers');
  return response.data;
};

/**
 * Get all patients that the current user is a caregiver for
 */
export const getMyPatients = async (): Promise<PatientSummary[]> => {
  const response = await api.get('/caregivers/my-patients');
  return response.data;
};

/**
 * Update caregiver permissions
 */
export const updateCaregiverPermissions = async (
  relationshipId: string,
  permissions: UpdatePermissionsRequest
): Promise<CaregiverRelationship> => {
  const response = await api.put(
    `/caregivers/${relationshipId}/permissions`,
    permissions
  );
  return response.data;
};

/**
 * Revoke caregiver access
 */
export const revokeCaregiverAccess = async (
  relationshipId: string
): Promise<void> => {
  await api.delete(`/caregivers/${relationshipId}`);
};

/**
 * Get detailed patient information for caregiver dashboard
 */
export const getPatientDetails = async (
  patientId: string
): Promise<PatientSummary> => {
  const response = await api.get(`/caregivers/patients/${patientId}`);
  return response.data;
};

/**
 * Get activity log for a patient
 */
export const getPatientActivityLog = async (
  patientId: string,
  startDate?: string,
  endDate?: string,
  activityType?: string
): Promise<ActivityLog[]> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (activityType) params.append('activity_type', activityType);
  
  const response = await api.get(
    `/caregivers/patients/${patientId}/activity-log?${params.toString()}`
  );
  return response.data;
};

/**
 * Get alerts for all patients the caregiver monitors
 */
export const getCaregiverAlerts = async (
  acknowledged?: boolean
): Promise<CaregiverAlert[]> => {
  const params = new URLSearchParams();
  if (acknowledged !== undefined) {
    params.append('acknowledged', acknowledged.toString());
  }
  
  const response = await api.get(`/caregivers/alerts?${params.toString()}`);
  return response.data;
};

/**
 * Acknowledge an alert
 */
export const acknowledgeAlert = async (alertId: string): Promise<void> => {
  await api.post(`/caregivers/alerts/${alertId}/acknowledge`);
};

export default {
  inviteCaregiver,
  getMyCaregivers,
  getMyPatients,
  updateCaregiverPermissions,
  revokeCaregiverAccess,
  getPatientDetails,
  getPatientActivityLog,
  getCaregiverAlerts,
  acknowledgeAlert,
};
