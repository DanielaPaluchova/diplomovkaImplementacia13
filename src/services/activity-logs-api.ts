import { api } from './api';

export interface ActivityLog {
  id: number;
  userId: number;
  userName: string | null;
  userEmail: string | null;
  action: string;
  entityType: string;
  projectId: number | null;
  projectName: string | null;
  entityId: number | null;
  details: Record<string, unknown>;
  route: string | null;
  ipAddress: string | null;
  createdAt: string;
}

export interface ActivityLogsResponse {
  logs: ActivityLog[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ActivityLogsFilters {
  userId?: number | undefined;
  projectId?: number | undefined;
  action?: string | undefined;
  entityType?: string | undefined;
  dateFrom?: string | undefined;
  dateTo?: string | undefined;
  search?: string | undefined;
  page?: number | undefined;
  limit?: number | undefined;
}

export const activityLogsApi = {
  async getLogs(filters: Partial<ActivityLogsFilters> = {}): Promise<ActivityLogsResponse> {
    const params = new URLSearchParams();
    if (filters.userId) params.set('userId', String(filters.userId));
    if (filters.projectId) params.set('projectId', String(filters.projectId));
    if (filters.action) params.set('action', filters.action);
    if (filters.entityType) params.set('entityType', filters.entityType);
    if (filters.dateFrom) params.set('dateFrom', filters.dateFrom);
    if (filters.dateTo) params.set('dateTo', filters.dateTo);
    if (filters.search) params.set('search', filters.search);
    if (filters.page) params.set('page', String(filters.page));
    if (filters.limit) params.set('limit', String(filters.limit));

    const query = params.toString();
    return api.get<ActivityLogsResponse>(`/admin/activity-logs${query ? `?${query}` : ''}`);
  },

  async getActions(): Promise<string[]> {
    return api.get<string[]>('/admin/activity-logs/actions');
  },

  async getEntityTypes(): Promise<string[]> {
    return api.get<string[]>('/admin/activity-logs/entity-types');
  },
};
