/**
 * Medical imaging service for uploading and analyzing brain scans.
 */
import api from './api';

export interface ImagingUploadResponse {
  id: string;
  user_id: string;
  modality: string;
  file_size: number;
  status: string;
  created_at: string;
  message: string;
}

export interface VolumetricMeasurements {
  hippocampal_volume_left?: number;
  hippocampal_volume_right?: number;
  hippocampal_volume_total?: number;
  entorhinal_cortex_volume_left?: number;
  entorhinal_cortex_volume_right?: number;
  cortical_thickness_mean?: number;
  cortical_thickness_std?: number;
  total_brain_volume?: number;
  total_gray_matter_volume?: number;
  total_white_matter_volume?: number;
  ventricle_volume?: number;
}

export interface AtrophyDetection {
  detected: boolean;
  regions: string[];
  severity?: string;
}

export interface ImagingAnalysis {
  id: string;
  user_id: string;
  modality: string;
  study_date?: string;
  study_description?: string;
  series_description?: string;
  status: string;
  processing_error?: string;
  volumetric_measurements?: VolumetricMeasurements;
  atrophy_detection?: AtrophyDetection;
  analysis_results?: any;
  ml_features?: any;
  created_at: string;
  updated_at: string;
}

export interface ImagingProcessingStatus {
  id: string;
  status: string;
  progress?: number;
  message?: string;
  error?: string;
}

/**
 * Upload a DICOM imaging file
 */
export const uploadImagingFile = async (file: File): Promise<ImagingUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/imaging/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Get imaging analysis results
 */
export const getImagingAnalysis = async (imagingId: string): Promise<ImagingAnalysis> => {
  const response = await api.get(`/imaging/${imagingId}/analysis`);
  return response.data;
};

/**
 * Check processing status
 */
export const getImagingStatus = async (imagingId: string): Promise<ImagingProcessingStatus> => {
  const response = await api.get(`/imaging/${imagingId}/status`);
  return response.data;
};

/**
 * Get all imaging studies for a user
 */
export const getUserImagingStudies = async (userId: string): Promise<ImagingAnalysis[]> => {
  const response = await api.get(`/imaging/user/${userId}`);
  return response.data.studies;
};

/**
 * Poll for imaging processing completion
 */
export const pollImagingStatus = async (
  imagingId: string,
  onProgress?: (status: ImagingProcessingStatus) => void,
  maxAttempts: number = 60,
  intervalMs: number = 2000
): Promise<ImagingAnalysis> => {
  let attempts = 0;

  while (attempts < maxAttempts) {
    const status = await getImagingStatus(imagingId);
    
    if (onProgress) {
      onProgress(status);
    }

    if (status.status === 'completed') {
      return await getImagingAnalysis(imagingId);
    }

    if (status.status === 'failed') {
      throw new Error(status.error || 'Imaging processing failed');
    }

    await new Promise(resolve => setTimeout(resolve, intervalMs));
    attempts++;
  }

  throw new Error('Imaging processing timeout');
};
