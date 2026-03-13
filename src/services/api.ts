import axios, { type AxiosInstance, type AxiosError } from 'axios';
import { useAuthStore } from 'src/stores/auth-store';

/**
 * Base API client configuration
 * This will be used when backend is ready
 */
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore();
        const url = config.url || '';
        console.log('🔐 [API Request] URL:', url);
        console.log('🔐 [API Request] Token from store:', authStore.token ? 'EXISTS' : 'MISSING');

        // Skip adding token for public auth endpoints
        const isPublicAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/register');
        
        if (authStore.token && !isPublicAuthEndpoint) {
          config.headers.Authorization = `Bearer ${authStore.token}`;
          console.log('✅ [API Request] Authorization header added');
        } else if (isPublicAuthEndpoint) {
          console.log('ℹ️ [API Request] Skipping auth header for public endpoint');
        } else {
          console.warn('⚠️ [API Request] NO TOKEN IN STORE!');
        }

        return config;
      },
      (error) => {
        console.error('❌ [API Request] Error:', error);
        return Promise.reject(error);
      },
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => {
        console.log('✅ [API Response] Success:', response.config.url, 'Status:', response.status);
        return response;
      },
      (error: AxiosError) => {
        console.error(
          '❌ [API Response] Error:',
          error.config?.url,
          'Status:',
          error.response?.status,
        );

        // Handle 401 Unauthorized
        if (error.response?.status === 401) {
          const url = error.config?.url || '';

          // Don't clear auth for login/register requests (they might fail for valid reasons)
          if (!url.includes('/auth/login') && !url.includes('/auth/register')) {
            console.error('❌ 401 Unauthorized - Clearing auth and redirecting to login');
            const authStore = useAuthStore();
            authStore.clearAuth();

            // Only redirect if not already on login page
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
          } else {
            console.error('❌ 401 Unauthorized on auth endpoint (wrong credentials)');
          }
        }

        // Handle 403 Forbidden
        if (error.response?.status === 403) {
          console.error('❌ 403 Forbidden - Access denied');
        }

        // Handle 500 Server Error
        if (error.response?.status === 500) {
          console.error('❌ 500 Server Error');
        }

        return Promise.reject(error);
      },
    );
  }

  /**
   * GET request
   */
  async get<T>(url: string, config = {}): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  /**
   * POST request
   */
  async post<T>(url: string, data = {}, config = {}): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  /**
   * PUT request
   */
  async put<T>(url: string, data = {}, config = {}): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  /**
   * PATCH request
   */
  async patch<T>(url: string, data = {}, config = {}): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  /**
   * DELETE request
   */
  async delete<T>(url: string, config = {}): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiClient();

// Export for testing purposes
export default api;

/**
 * RACI Weights Configuration API
 */
export interface RaciWeightsConfig {
  id: number;
  workload: {
    responsible: number;
    accountable: number;
    consulted: number;
    informed: number;
  };
  duration: {
    responsible: number;
    accountable: number;
    consulted: number;
    informed: number;
  };
  createdAt: string;
  updatedAt: string;
}

export const raciWeightsApi = {
  /**
   * Get RACI weights configuration
   */
  async getRaciWeights(): Promise<RaciWeightsConfig> {
    return api.get<RaciWeightsConfig>('/raci-weights');
  },

  /**
   * Update RACI weights configuration
   */
  async updateRaciWeights(
    weights: Partial<Pick<RaciWeightsConfig, 'workload' | 'duration'>>,
  ): Promise<RaciWeightsConfig> {
    return api.put<RaciWeightsConfig>('/raci-weights', weights);
  },
};
