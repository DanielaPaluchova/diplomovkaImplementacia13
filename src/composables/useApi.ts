import { ref } from 'vue';
import { useQuasar } from 'quasar';

export interface ApiState<T = unknown> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T = unknown>() {
  const $q = useQuasar();

  const data = ref<T | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Execute an API call with loading and error handling
   */
  async function execute(
    apiCall: () => Promise<T>,
    options?: {
      successMessage?: string;
      errorMessage?: string;
      showLoading?: boolean;
    },
  ): Promise<T | null> {
    loading.value = true;
    error.value = null;

    try {
      const result = await apiCall();
      data.value = result as T;

      if (options?.successMessage) {
        $q.notify({
          message: options.successMessage,
          color: 'positive',
          icon: 'check_circle',
          position: 'top',
        });
      }

      return result;
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : options?.errorMessage || 'An error occurred';
      error.value = errorMsg;

      $q.notify({
        message: errorMsg,
        color: 'negative',
        icon: 'error',
        position: 'top',
      });

      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Reset state
   */
  function reset() {
    data.value = null;
    loading.value = false;
    error.value = null;
  }

  return {
    data,
    loading,
    error,
    execute,
    reset,
  };
}
