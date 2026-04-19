import { defineRouter } from '#q-app/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import routes from './routes';
import { useAuthStore } from 'src/stores/auth-store';
import { api } from 'src/services/api';
import { getEntityTypeFromRoute, getProjectIdFromRoute } from 'src/utils/activityLogRouteMap';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  // Activity logging: log page_leave when navigating away (run first)
  // Only log when user actually was on a real page (from.matched.length > 0).
  // On initial load, from has no matched routes, so we'd incorrectly log page_leave for "/".
  Router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    const wasOnRealPage = from.matched.length > 0;
    if (
      authStore.token &&
      wasOnRealPage &&
      from.path &&
      from.path !== to.path &&
      !from.path.startsWith('/login')
    ) {
      const entityType = getEntityTypeFromRoute(from.path);
      const projectId = getProjectIdFromRoute(from.params as Record<string, string>);
      api.post('/activity-logs', {
        action: 'page_leave',
        entityType,
        projectId: projectId ?? null,
        route: from.fullPath,
      }).catch(() => {});
    }
    next();
  });

  // Navigation guard for authentication
  Router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    // DON'T call initializeAuth() here - it's already called in the auth boot file!
    // Calling it multiple times causes race conditions and clears the token.

    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth !== false);
    const hideForAuth = to.matched.some((record) => record.meta.hideForAuth === true);
    const requiresManager = to.matched.some((record) => record.meta.requiresManager === true);
    const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin === true);

    // If route requires auth and user is not authenticated
    if (requiresAuth && !authStore.isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      });
    }
    // If user is authenticated and tries to access login/register
    else if (hideForAuth && authStore.isAuthenticated) {
      next('/');
    }
    // If route requires manager role and user is not manager/admin
    else if (requiresManager && !authStore.isManager) {
      next({ path: '/', query: { accessDenied: 'true' } });
    }
    // If route requires admin role and user is not admin
    else if (requiresAdmin && !authStore.isAdmin) {
      next({ path: '/', query: { accessDenied: 'true' } });
    }
    // Otherwise, allow navigation
    else {
      next();
    }
  });

  // Activity logging: log page_view when navigation completes
  Router.afterEach((to) => {
    const authStore = useAuthStore();
    if (authStore.token && to.path && !to.path.startsWith('/login')) {
      const entityType = getEntityTypeFromRoute(to.path);
      const projectId = getProjectIdFromRoute(to.params as Record<string, string>);
      api.post('/activity-logs', {
        action: 'page_view',
        entityType,
        projectId: projectId ?? null,
        route: to.fullPath,
      }).catch(() => {});
    }
  });

  return Router;
});
