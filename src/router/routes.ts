import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  // Auth routes (no authentication required)
  {
    path: '/login',
    component: () => import('pages/auth/LoginPage.vue'),
    meta: { requiresAuth: false, hideForAuth: true },
  },
  {
    path: '/register',
    component: () => import('pages/auth/RegisterPage.vue'),
    meta: { requiresAuth: false, hideForAuth: true },
  },

  // Main routes (authentication required)
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'projects', component: () => import('pages/ProjectsPage.vue') },
      { path: 'projects/:id', component: () => import('pages/ProjectDetailPage.vue') },
      { path: 'projects/:id/kanban', component: () => import('pages/ProjectKanbanPage.vue') },
      { path: 'team', component: () => import('pages/TeamPage.vue') },
      { path: 'workload', component: () => import('pages/WorkloadDashboardPage.vue') },
      { path: 'sprint-planning', component: () => import('pages/SprintPlanningPage.vue') },
      // Project Management routes (Manager/Admin only)
      {
        path: 'pert-analysis',
        component: () => import('pages/PertAnalysisPage.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'raci-matrix',
        component: () => import('pages/RaciMatrixPage.vue'),
        meta: { requiresManager: true },
      },
      { path: 'kanban', component: () => import('pages/KanbanPage.vue') },
      {
        path: 'pert-raci-optimization',
        component: () => import('pages/PertRaciOptimizationPage.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'requirement-changes',
        component: () => import('pages/RequirementChangePage.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'smart-sprint-planning',
        component: () => import('pages/SmartSprintPlanningPage.vue'),
        meta: { requiresManager: true },
      },
      // Profile
      {
        path: 'profile',
        component: () => import('pages/auth/ProfilePage.vue'),
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
