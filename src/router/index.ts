import { defineRouter } from '#q-app/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import routes from './routes';
import { useAuthStore } from 'src/stores/auth-store';

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

  // Navigation guard for authentication
  Router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    // DON'T call initializeAuth() here - it's already called when store is created!
    // Calling it multiple times causes race conditions and clears the token.

    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth !== false);
    const hideForAuth = to.matched.some((record) => record.meta.hideForAuth === true);
    const requiresManager = to.matched.some((record) => record.meta.requiresManager === true);

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
      // Redirect to home with access denied message
      next({
        path: '/',
        query: { accessDenied: 'true' },
      });
    }
    // Otherwise, allow navigation
    else {
      next();
    }
  });

  return Router;
});
