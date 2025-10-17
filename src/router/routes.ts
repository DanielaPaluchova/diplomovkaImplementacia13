import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'projects', component: () => import('pages/ProjectsPage.vue') },
      { path: 'projects/:id', component: () => import('pages/ProjectDetailPage.vue') },
      { path: 'projects/:id/kanban', component: () => import('pages/ProjectKanbanPage.vue') },
      { path: 'team', component: () => import('pages/TeamPage.vue') },
      { path: 'workload', component: () => import('pages/WorkloadDashboardPage.vue') },
      { path: 'sprint-planning', component: () => import('pages/SprintPlanningPage.vue') },
      { path: 'pert-analysis', component: () => import('pages/PertAnalysisPage.vue') },
      { path: 'raci-matrix', component: () => import('pages/RaciMatrixPage.vue') },
      { path: 'kanban', component: () => import('pages/KanbanPage.vue') },
      { path: 'gantt', component: () => import('pages/GanttPage.vue') },
      { path: 'experiments', component: () => import('pages/ExperimentsPage.vue') },
      { path: 'analytics', component: () => import('pages/AnalyticsPage.vue') },
      { path: 'comparisons', component: () => import('pages/ComparisonsPage.vue') },
      { path: 'reports', component: () => import('pages/ReportsPage.vue') },
      {
        path: 'pert-raci-optimization',
        component: () => import('pages/PertRaciOptimizationPage.vue'),
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
