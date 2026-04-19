import { onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from 'src/stores/auth-store';
import { api } from 'src/services/api';

export interface LogOptions {
  projectId?: number;
  entityId?: number;
  details?: Record<string, unknown>;
  route?: string;
}

/**
 * Composable for logging user activity.
 * Logs are sent asynchronously and do not block the UI.
 */
export function useActivityLog() {
  const route = useRoute();
  const authStore = useAuthStore();

  const currentRoute = () => route.fullPath;

  async function log(
    action: string,
    entityType: string,
    options: Partial<LogOptions> = {},
  ): Promise<void> {
    if (!authStore.token) return;

    try {
      await api.post('/activity-logs', {
        action,
        entityType,
        projectId: options.projectId ?? null,
        entityId: options.entityId ?? null,
        details: options.details ?? {},
        route: options.route ?? currentRoute(),
      });
    } catch (err) {
      // Silently fail - don't disrupt user experience
      console.warn('[ActivityLog] Failed to log:', action, err);
    }
  }

  /**
   * Log page view on mount. Call in onMounted.
   */
  function setupPageView(entityType: string, details?: Record<string, unknown>) {
    onMounted(() => {
      log('page_view', entityType, {
        details: details ?? {},
        route: currentRoute(),
      });
    });
  }

  /**
   * Log page leave on unmount. Call in onBeforeUnmount.
   */
  function setupPageLeave(entityType: string) {
    onBeforeUnmount(() => {
      log('page_leave', entityType, { route: currentRoute() });
    });
  }

  /**
   * Full page tracking: logs page_view on mount and page_leave on unmount.
   */
  function trackPage(entityType: string, details?: Record<string, unknown>) {
    setupPageView(entityType, details);
    setupPageLeave(entityType);
  }

  return {
    log,
    setupPageView,
    setupPageLeave,
    trackPage,
  };
}
