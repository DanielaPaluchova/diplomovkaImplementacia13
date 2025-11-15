import { defineBoot } from '#q-app/wrappers';
import { useAuthStore } from 'src/stores/auth-store';

/**
 * Initialize authentication state from localStorage
 * This runs before the app is mounted
 */
export default defineBoot(() => {
  const authStore = useAuthStore();
  
  // Initialize auth from localStorage
  authStore.initializeAuth();
  
  console.log('🚀 [Boot] Auth initialized');
});

