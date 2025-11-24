import apiClient from './api';

export interface User {
  id: string;
  email: string;
  name: string;
  dateOfBirth?: string;
  apoeGenotype?: string;
  createdAt: string;
  lastActive: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
  is_new_user?: boolean;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
}

export interface LogoutResponse {
  message: string;
}

class AuthService {
  /**
   * Register a new user with email and password
   */
  async register(email: string, password: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', {
      email,
      password,
    });
    return response.data;
  }

  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    return response.data;
  }

  /**
   * Authenticate with Google OAuth token
   */
  async googleAuth(googleToken: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/google', {
      token: googleToken,
    });
    return response.data;
  }

  /**
   * Refresh access token using refresh token from cookie
   */
  async refreshToken(): Promise<RefreshResponse> {
    const response = await apiClient.post<RefreshResponse>('/auth/refresh');
    return response.data;
  }

  /**
   * Logout user and clear tokens
   */
  async logout(): Promise<LogoutResponse> {
    const response = await apiClient.post<LogoutResponse>('/auth/logout');
    return response.data;
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  }

  /**
   * Store access token in localStorage
   */
  setAccessToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  /**
   * Get access token from localStorage
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Remove access token from localStorage
   */
  clearAccessToken(): void {
    localStorage.removeItem('access_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}

const authService = new AuthService();
export { authService };
export default authService;
