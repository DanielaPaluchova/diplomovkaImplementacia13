import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'src/services/api';

export interface User {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'developer' | 'viewer';
  avatar?: string;
  createdAt: Date;
}

interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
  role?: 'developer' | 'manager';
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const isAuthenticated = computed(() => !!user.value);
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isManager = computed(() => user.value?.role === 'manager' || user.value?.role === 'admin');
  const userName = computed(() => user.value?.name || 'Guest');
  const userInitials = computed(() => {
    if (!user.value) return 'G';
    return user.value.name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  });

  // Actions

  /**
   * Initialize auth state from localStorage
   */
  function initializeAuth() {
    console.log('🔄 [Auth Init] Starting...');
    console.log('🔍 [Auth Init] Checking localStorage...');

    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');

    console.log('🔍 [Auth Init] Token in localStorage:', storedToken ? 'EXISTS' : 'MISSING');
    console.log('🔍 [Auth Init] User in localStorage:', storedUser ? 'EXISTS' : 'MISSING');

    if (storedToken && storedUser) {
      try {
        token.value = storedToken;
        user.value = JSON.parse(storedUser);
        console.log('✅ [Auth Init] Success! User:', user.value?.email);
        console.log('🔐 [Auth Init] Token restored to store');
        console.log('🔐 [Auth Init] Current token in store:', token.value ? 'SET' : 'NOT SET');
      } catch (err) {
        console.error('❌ [Auth Init] Failed to parse:', err);
        clearAuth();
      }
    } else {
      console.log('⚠️ [Auth Init] No token found in localStorage');
      console.log('📊 [Auth Init] localStorage keys:', Object.keys(localStorage));
    }
  }

  /**
   * Login with email and password
   */
  async function login(credentials: LoginCredentials): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      // REAL API CALL
      const response = await api.post<{ user: User; token: string }>('/auth/login', {
        email: credentials.email,
        password: credentials.password,
      });

      user.value = response.user;
      token.value = response.token;

      console.log('✅ Login successful - Token received:', token.value ? 'YES' : 'NO');
      console.log('👤 User:', user.value);

      // Always save to localStorage (simpler and more reliable)
      if (token.value) {
        localStorage.setItem('auth_token', token.value);
        localStorage.setItem('auth_user', JSON.stringify(user.value));
        console.log('💾 Token saved to localStorage');

        // Verify it was actually saved
        const savedToken = localStorage.getItem('auth_token');
        if (savedToken === token.value) {
          console.log('✅ Token verified in localStorage!');
        } else {
          console.error('❌ Token NOT in localStorage after save!');
        }
      }

      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Register new user
   */
  async function register(data: RegisterData): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      // REAL API CALL
      const response = await api.post<{ user: User; token: string }>('/auth/register', {
        email: data.email,
        password: data.password,
        name: data.name,
        role: data.role || 'developer',
      });

      user.value = response.user;
      token.value = response.token;

      // Always save to localStorage
      if (token.value) {
        localStorage.setItem('auth_token', token.value);
        localStorage.setItem('auth_user', JSON.stringify(user.value));
        console.log('💾 [Register] Token saved to localStorage');
      }

      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Registration failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Logout user
   */
  async function logout() {
    isLoading.value = true;

    try {
      // REAL API CALL
      await api.post('/auth/logout');

      clearAuth();
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Clear auth state and storage
   */
  function clearAuth() {
    user.value = null;
    token.value = null;
    error.value = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    console.log('🗑️ [Auth] Cleared localStorage');
  }

  /**
   * Update user profile
   */
  async function updateProfile(updates: Partial<User>): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      if (!user.value) {
        error.value = 'Not authenticated';
        return false;
      }

      // REAL API CALL
      const response = await api.put<User>('/auth/profile', updates);
      user.value = response;

      // Update storage
      localStorage.setItem('auth_user', JSON.stringify(user.value));

      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Update failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Change user password
   */
  async function changePassword(currentPassword: string, newPassword: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      if (!user.value) {
        error.value = 'Not authenticated';
        return false;
      }

      // REAL API CALL
      await api.post('/auth/change-password', {
        currentPassword,
        newPassword,
      });

      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Password change failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Check if user has specific role
   */
  function hasRole(role: User['role']): boolean {
    return user.value?.role === role;
  }

  /**
   * Check if user has permission (role hierarchy)
   */
  function hasPermission(requiredRole: User['role']): boolean {
    if (!user.value) return false;

    const roleHierarchy: Record<User['role'], number> = {
      admin: 4,
      manager: 3,
      developer: 2,
      viewer: 1,
    };

    return roleHierarchy[user.value.role] >= roleHierarchy[requiredRole];
  }

  return {
    // State
    user,
    token,
    isLoading,
    error,

    // Computed
    isAuthenticated,
    isAdmin,
    isManager,
    userName,
    userInitials,

    // Actions
    initializeAuth,
    login,
    register,
    logout,
    clearAuth,
    updateProfile,
    changePassword,
    hasRole,
    hasPermission,
  };
});
