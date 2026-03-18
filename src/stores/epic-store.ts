import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/services/api';
import type { Task } from 'src/stores/project-store';

export interface PertEstimate {
  optimistic: number | null;
  mostLikely: number | null;
  pessimistic: number | null;
  expected?: number | null;
}

export interface User {
  id: number;
  name: string;
  email: string;
  avatar?: string;
}

export interface Epic {
  id: number;
  projectId: number;
  name: string;
  description: string;
  status: 'to_do' | 'not_started' | 'in_progress' | 'completed';
  ownerId?: number | null;
  owner?: User | null;
  priority: 'low' | 'medium' | 'high';
  labels: string[];
  startDate?: string | null;
  targetDate?: string | null;
  pert: PertEstimate;
  dependencies: number[];
  businessValue: number;
  targetRelease: string | null;
  diagramPositionX: number | null;
  diagramPositionY: number | null;
  createdAt: string;
  updatedAt: string;
  // Optional fields when include_tasks=true
  tasks?: Task[];
  totalStoryPoints?: number;
  completedStoryPoints?: number;
  progress?: number;
}

export interface EpicSchedule {
  epicId: number;
  epicName: string;
  duration: number;
  earlyStart: number;
  earlyFinish: number;
  lateStart: number;
  lateFinish: number;
  slack: number;
  isCritical: boolean;
  variance?: number;
}

export interface EpicCriticalPathResponse {
  criticalPath: number[];
  epicSchedule: Record<number, EpicSchedule>;
  projectDuration: number;
  projectVariance?: number;
  projectStdDev?: number;
}

export const useEpicStore = defineStore('epic', () => {
  const epics = ref<Epic[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Normalize epic data with defaults for new fields
  function normalizeEpic(epic: Partial<Epic> & { id: number; projectId: number; name: string }): Epic {
    // Convert 'not_started' to 'to_do' for consistency
    let status = epic.status || 'to_do';
    if (status === 'not_started') {
      status = 'to_do';
    }
    
    return {
      id: epic.id,
      projectId: epic.projectId,
      name: epic.name,
      description: epic.description || '',
      status: status,
      ownerId: epic.ownerId || null,
      owner: epic.owner || null,
      priority: epic.priority || 'medium',
      labels: epic.labels || [],
      startDate: epic.startDate || null,
      targetDate: epic.targetDate || null,
      pert: epic.pert || { optimistic: null, mostLikely: null, pessimistic: null, expected: null },
      dependencies: epic.dependencies || [],
      businessValue: epic.businessValue || 0,
      targetRelease: epic.targetRelease || null,
      diagramPositionX: epic.diagramPositionX || null,
      diagramPositionY: epic.diagramPositionY || null,
      createdAt: epic.createdAt || new Date().toISOString(),
      updatedAt: epic.updatedAt || new Date().toISOString(),
      progress: epic.progress || 0,
      tasks: epic.tasks || [],
      totalStoryPoints: epic.totalStoryPoints || 0,
      completedStoryPoints: epic.completedStoryPoints || 0,
    };
  }

  // Fetch all epics for a project
  async function fetchEpics(projectId: number, includeTasks = false): Promise<Epic[]> {
    loading.value = true;
    error.value = null;
    try {
      const url = `/projects/${projectId}/epics?include_tasks=${includeTasks}`;
      const data = await api.get<Epic[]>(url);
      epics.value = data.map(normalizeEpic);
      return epics.value;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch epics';
      console.error('Failed to fetch epics:', err);
      return [];
    } finally {
      loading.value = false;
    }
  }

  // Get single epic with details
  async function getEpic(projectId: number, epicId: number, includeTasks = true): Promise<Epic | undefined> {
    loading.value = true;
    error.value = null;
    try {
      const url = `/projects/${projectId}/epics/${epicId}?include_tasks=${includeTasks}`;
      const data = await api.get<Epic>(url);
      const normalized = normalizeEpic(data);
      
      // Update epic in local state
      const index = epics.value.findIndex((e) => e.id === epicId);
      if (index !== -1) {
        epics.value[index] = normalized;
      } else {
        epics.value.push(normalized);
      }
      
      return normalized;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch epic';
      console.error('Failed to fetch epic:', err);
      return undefined;
    } finally {
      loading.value = false;
    }
  }

  // Get epic by ID from local state (sync)
  function getEpicById(epicId: number): Epic | undefined {
    return epics.value.find((e) => e.id === epicId);
  }

  // Create new epic
  async function createEpic(projectId: number, epicData: Partial<Epic>): Promise<Epic | undefined> {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.post<Epic>(`/projects/${projectId}/epics`, epicData);
      epics.value.push(data);
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create epic';
      console.error('Failed to create epic:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Update epic
  async function updateEpic(projectId: number, epicId: number, updates: Partial<Epic>): Promise<Epic | undefined> {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.put<Epic>(`/projects/${projectId}/epics/${epicId}`, updates);
      
      // Update epic in local state
      const index = epics.value.findIndex((e) => e.id === epicId);
      if (index !== -1) {
        epics.value[index] = data;
      }
      
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update epic';
      console.error('Failed to update epic:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Delete epic
  async function deleteEpic(projectId: number, epicId: number): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      await api.delete(`/projects/${projectId}/epics/${epicId}`);
      
      // Remove epic from local state
      const index = epics.value.findIndex((e) => e.id === epicId);
      if (index !== -1) {
        epics.value.splice(index, 1);
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete epic';
      console.error('Failed to delete epic:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Get critical path for epics
  async function getCriticalPath(projectId: number): Promise<EpicCriticalPathResponse> {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.get<EpicCriticalPathResponse>(`/projects/${projectId}/epics/critical-path`);
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to calculate epic critical path';
      console.error('Failed to calculate epic critical path:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Get tasks for a specific epic (from local state)
  function getEpicTasks(epicId: number): Task[] {
    const epic = epics.value.find((e) => e.id === epicId);
    return epic?.tasks || [];
  }

  // Update epic position (for PERT diagram)
  async function updateEpicPosition(projectId: number, epicId: number, x: number | null, y: number | null): Promise<Epic | undefined> {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.put<Epic>(`/projects/${projectId}/epics/${epicId}`, {
        diagramPositionX: x,
        diagramPositionY: y,
      });

      // Update local state
      const index = epics.value.findIndex((e) => e.id === epicId);
      if (index !== -1) {
        epics.value[index] = data;
      }

      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update epic position';
      console.error('Failed to update epic position:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    epics,
    loading,
    error,
    fetchEpics,
    getEpic,
    getEpicById,
    createEpic,
    updateEpic,
    deleteEpic,
    getCriticalPath,
    getEpicTasks,
    updateEpicPosition,
  };
});
