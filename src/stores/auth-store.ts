import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

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

  // Mock users (pre testovanie bez backendu)
  const mockUsers: (User & { password: string })[] = [
    {
      id: 1,
      email: 'admin@example.com',
      password: 'admin123',
      name: 'Admin User',
      role: 'admin',
      avatar: 'https://cdn.quasar.dev/img/avatar.png',
      createdAt: new Date('2024-01-01'),
    },
    {
      id: 2,
      email: 'manager@example.com',
      password: 'manager123',
      name: 'Project Manager',
      role: 'manager',
      avatar: 'https://cdn.quasar.dev/img/avatar2.jpg',
      createdAt: new Date('2024-01-02'),
    },
    {
      id: 3,
      email: 'developer@example.com',
      password: 'dev123',
      name: 'Developer',
      role: 'developer',
      avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
      createdAt: new Date('2024-01-03'),
    },
  ];

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
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');

    if (storedToken && storedUser) {
      try {
        token.value = storedToken;
        user.value = JSON.parse(storedUser);
      } catch (err) {
        console.error('Failed to parse stored user:', err);
        clearAuth();
      }
    }
  }

  /**
   * Login with email and password
   * TODO: Replace with real API call when backend is ready
   */
  async function login(credentials: LoginCredentials): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Mock authentication
      const foundUser = mockUsers.find(
        (u) => u.email === credentials.email && u.password === credentials.password,
      );

      if (!foundUser) {
        error.value = 'Invalid email or password';
        return false;
      }

      // Generate mock JWT token
      const mockToken = `mock_jwt_${foundUser.id}_${Date.now()}`;

      // Set user and token (remove password from response)
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { password: _password, ...userWithoutPassword } = foundUser;
      user.value = userWithoutPassword;
      token.value = mockToken;

      // Store in localStorage if remember me
      if (credentials.rememberMe) {
        localStorage.setItem('auth_token', mockToken);
        localStorage.setItem('auth_user', JSON.stringify(userWithoutPassword));
      } else {
        // Store in sessionStorage
        sessionStorage.setItem('auth_token', mockToken);
        sessionStorage.setItem('auth_user', JSON.stringify(userWithoutPassword));
      }

      return true;

      /* READY FOR BACKEND:
      const response = await api.post('/auth/login', {
        email: credentials.email,
        password: credentials.password,
      });

      user.value = response.data.user;
      token.value = response.data.token;

      if (credentials.rememberMe) {
        localStorage.setItem('auth_token', token.value);
        localStorage.setItem('auth_user', JSON.stringify(user.value));
      }

      return true;
      */
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Register new user
   * TODO: Replace with real API call when backend is ready
   */
  async function register(data: RegisterData): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Mock validation
      if (mockUsers.some((u) => u.email === data.email)) {
        error.value = 'Email already exists';
        return false;
      }

      // Create new user
      const newUser: User = {
        id: mockUsers.length + 1,
        email: data.email,
        name: data.name,
        role: data.role || 'developer', // Use selected role or default to developer
        avatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
        createdAt: new Date(),
      };

      // Add to mock users (in real app, this would be in backend)
      mockUsers.push({ ...newUser, password: data.password });

      // Generate mock token
      const mockToken = `mock_jwt_${newUser.id}_${Date.now()}`;

      // Set user and token
      user.value = newUser;
      token.value = mockToken;

      // Store in localStorage
      localStorage.setItem('auth_token', mockToken);
      localStorage.setItem('auth_user', JSON.stringify(newUser));

      return true;

      /* READY FOR BACKEND:
      const response = await api.post('/auth/register', {
        email: data.email,
        password: data.password,
        name: data.name,
      });

      user.value = response.data.user;
      token.value = response.data.token;

      localStorage.setItem('auth_token', token.value);
      localStorage.setItem('auth_user', JSON.stringify(user.value));

      return true;
      */
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
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      /* READY FOR BACKEND:
      await api.post('/auth/logout');
      */

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
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('auth_user');
  }

  /**
   * Update user profile
   */
  async function updateProfile(updates: Partial<User>): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));

      if (!user.value) {
        error.value = 'Not authenticated';
        return false;
      }

      // Update user
      user.value = { ...user.value, ...updates };

      // Update storage
      localStorage.setItem('auth_user', JSON.stringify(user.value));

      return true;

      /* READY FOR BACKEND:
      const response = await api.put('/auth/profile', updates);
      user.value = response.data.user;
      localStorage.setItem('auth_user', JSON.stringify(user.value));
      return true;
      */
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Update failed';
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

  /**
   * Get mock users (for demo purposes)
   */
  function getMockUsers() {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    return mockUsers.map(({ password: _password, ...user }) => user);
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
    hasRole,
    hasPermission,
    getMockUsers,
  };
});
