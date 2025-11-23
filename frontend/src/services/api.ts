import axios, { AxiosInstance, AxiosError } from 'axios';

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Lazy load logger to avoid circular dependencies
let logAPICall: any = null;
let logError: any = null;

// Load logger asynchronously
import('./logger').then((module) => {
  logAPICall = module.logAPICall;
  logError = module.logError;
}).catch(() => {
  // Fallback to console if logger fails
  logAPICall = console.log;
  logError = console.error;
});

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies
});

// Request interceptor to add auth token and timing
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request start time for performance logging
    (config as any).metadata = { startTime: Date.now() };
    
    return config;
  },
  (error) => {
    if (logError) {
      logError('API request error', error);
    } else {
      console.error('API request error:', error);
    }
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and logging
apiClient.interceptors.response.use(
  (response) => {
    // Log successful API calls
    const config = response.config as any;
    const duration = Date.now() - (config.metadata?.startTime || Date.now());
    
    if (logAPICall) {
      logAPICall(
        config.method?.toUpperCase() || 'GET',
        config.url || '',
        response.status,
        duration
      );
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    // Log failed API calls
    if (originalRequest?.metadata?.startTime && logAPICall) {
      const duration = Date.now() - originalRequest.metadata.startTime;
      logAPICall(
        originalRequest.method?.toUpperCase() || 'GET',
        originalRequest.url || '',
        error.response?.status || 0,
        duration,
        { error: error.message }
      );
    }

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh the token
        const response = await axios.post(
          `${API_BASE_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        );

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        if (logError) {
          logError('Token refresh failed', refreshError as Error);
        } else {
          console.error('Token refresh failed:', refreshError);
        }
        localStorage.removeItem('access_token');
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
