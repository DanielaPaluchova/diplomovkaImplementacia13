/**
 * Maps route paths to entity types for activity logging
 */
export function getEntityTypeFromRoute(path: string): string {
  if (path === '/' || path === '') return 'dashboard';
  if (path === '/projects') return 'projects';
  if (path.match(/^\/projects\/[^/]+$/)) return 'project_detail';
  if (path.match(/^\/projects\/[^/]+\/epics$/)) return 'epics';
  if (path.match(/^\/projects\/[^/]+\/epics\/[^/]+$/)) return 'epic_detail';
  if (path.match(/\/epics\/pert-diagram$/)) return 'epic_pert_diagram';
  if (path === '/team') return 'team';
  if (path === '/workload') return 'workload';
  if (path === '/pert-analysis') return 'pert_analysis';
  if (path === '/raci-matrix') return 'raci_matrix';
  if (path === '/critical-path') return 'critical_path';
  if (path === '/pert-raci-optimization') return 'pert_raci_optimization';
  if (path === '/requirement-changes') return 'requirement_changes';
  if (path === '/smart-sprint-planning') return 'smart_sprint_planning';
  if (path === '/profile') return 'profile';
  if (path.match(/\/admin\/activity-logs/)) return 'admin_activity_logs';
  if (path === '/login') return 'login';
  if (path === '/register') return 'register';
  return 'unknown';
}

export function getProjectIdFromRoute(params: Record<string, string>): number | undefined {
  const id = params.id || params.projectId;
  return id ? parseInt(id, 10) : undefined;
}
