import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/services/api';

export interface Sprint {
  id: number;
  name: string;
  goal: string;
  startDate: Date | string;
  endDate: Date | string;
  status: 'planned' | 'active' | 'completed';
  totalTasks: number;
  completedTasks: number;
  taskIds: number[];
  // Optimization fields
  capacity?: number;
  plannedStoryPoints?: number;
  velocity?: number;
}

export interface ProjectRole {
  memberId: number;
  role: 'owner' | 'admin' | 'developer' | 'viewer';
  permissions: {
    canEdit: boolean;
    canDelete: boolean;
    canManageTeam: boolean;
    canManageSprints: boolean;
  };
}

export interface PertEstimate {
  optimistic: number;
  mostLikely: number;
  pessimistic: number;
  expected?: number;
}

export interface RaciMatrix {
  responsible: number[];
  accountable: number | null;
  consulted: number[];
  informed: number[];
}

export interface Task {
  id: number;
  projectId: number;
  name: string;
  title: string;
  description: string;
  status: 'To Do' | 'In Progress' | 'Done';
  priority: 'High' | 'Medium' | 'Low' | 'high' | 'medium' | 'low';
  type: 'feature' | 'bug' | 'task';
  storyPoints: number;
  sprintId: number | null;
  dueDate: Date | string;
  completed: boolean;
  labels: string[];
  complexity: number;
  pert: PertEstimate;
  raci: RaciMatrix;
  // Gantt chart fields
  startDate?: Date | string | null;
  endDate?: Date | string | null;
  dependencies?: number[];
  // PERT diagram position
  diagramPositionX?: number | null;
  diagramPositionY?: number | null;
  // Optimization fields
  requiredSkills?: string[];
  estimatedHours?: number;
  actualHours?: number;
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
}

export interface PertManualEdge {
  from: number;
  to: number;
  isCritical?: boolean;
}

export interface PertLayoutSettings {
  zoomLevel?: number;
  panX?: number;
  panY?: number;
}

export interface TaskSchedule {
  taskId: number;
  taskName: string;
  duration: number;
  earlyStart: number;
  earlyFinish: number;
  lateStart: number;
  lateFinish: number;
  slack: number;
  isCritical: boolean;
}

export interface CriticalPathResponse {
  criticalPath: number[];
  taskSchedule: Record<number, TaskSchedule>;
  projectDuration: number;
}

export interface RaciWeights {
  responsible: number;
  accountable: number;
  consulted: number;
  informed: number;
}

export interface PertWeights {
  optimistic: number;
  mostLikely: number;
  pessimistic: number;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  template: string;
  icon: string;
  progress: number;
  tasksCompleted: number;
  totalTasks: number;
  status: string;
  dueDate: Date | string;
  createdAt: Date | string;
  teamMemberIds: number[];
  roles: ProjectRole[];
  sprints: Sprint[];
  tasks: Task[];
  totalStoryPoints: number;
  estimatedDuration: number;
  pertManualEdges?: PertManualEdge[];
  pertLayoutSettings?: PertLayoutSettings;
  raciWeights?: RaciWeights;
  pertWeights?: PertWeights;
  maxStoryPointsPerPerson?: number;
}

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Fetch all projects from API
  async function fetchProjects(includeDetails = false) {
    loading.value = true;
    error.value = null;
    try {
      const url = includeDetails ? '/projects?details=true' : '/projects';
      const data = await api.get<Project[]>(url);
      projects.value = data;
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch projects';
      console.error('Failed to fetch projects:', err);
      return [];
    } finally {
      loading.value = false;
    }
  }

  // Get single project with details
  async function getProject(id: number): Promise<Project | undefined> {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.get<Project>(`/projects/${id}`);
      // Update project in local state
      const index = projects.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        projects.value[index] = data;
      } else {
        projects.value.push(data);
      }
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch project';
      console.error('Failed to fetch project:', err);
      return undefined;
    } finally {
      loading.value = false;
    }
  }

  // Get project by ID from local state (sync)
  function getProjectById(id: number): Project | undefined {
    return projects.value.find((p) => p.id === id);
  }

  // Project member management
  function addMemberToProject(projectId: number, memberId: number, role: ProjectRole['role']) {
    const project = projects.value.find((p) => p.id === projectId);
    if (project) {
      const permissions = getRolePermissions(role);
      if (!project.teamMemberIds) {
        project.teamMemberIds = [];
      }
      if (!project.roles) {
        project.roles = [];
      }
      project.teamMemberIds.push(memberId);
      project.roles.push({
        memberId,
        role,
        permissions,
      });
    }
  }

  async function updateMemberRole(projectId: number, memberId: number, role: ProjectRole['role']) {
    loading.value = true;
    error.value = null;
    try {
      // Call API to update role
      await api.put(`/projects/${projectId}/members/${memberId}/role`, { role });
      
      // Update local state
      const project = projects.value.find((p) => p.id === projectId);
      if (project && project.roles) {
        const roleIndex = project.roles.findIndex((r) => r.memberId === memberId);
        if (roleIndex !== -1) {
          project.roles[roleIndex] = {
            memberId,
            role,
            permissions: getRolePermissions(role),
          };
        } else {
          // Add new role if doesn't exist
          project.roles.push({
            memberId,
            role,
            permissions: getRolePermissions(role),
          });
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update member role';
      console.error('Failed to update member role:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function removeMemberFromProject(projectId: number, memberId: number) {
    const project = projects.value.find((p) => p.id === projectId);
    if (project) {
      if (project.teamMemberIds) {
        project.teamMemberIds = project.teamMemberIds.filter((id) => id !== memberId);
      }
      if (project.roles) {
        project.roles = project.roles.filter((r) => r.memberId !== memberId);
      }
    }
  }

  // Create new project
  async function addProject(project: Partial<Project>) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.post<Project>('/projects', project);
      projects.value.push(data);
      return data.id;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create project';
      console.error('Failed to create project:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Update project
  async function updateProject(id: number, updates: Partial<Project>) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.put<Project>(`/projects/${id}`, updates);
      const index = projects.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        projects.value[index] = data;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update project';
      console.error('Failed to update project:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Delete project
  async function deleteProject(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await api.delete(`/projects/${id}`);
      const index = projects.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        projects.value.splice(index, 1);
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete project';
      console.error('Failed to delete project:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Sprint management
  async function addSprint(projectId: number, sprint: Partial<Sprint>) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.post<Sprint>(`/projects/${projectId}/sprints`, sprint);
      const project = projects.value.find((p) => p.id === projectId);
      if (project) {
        if (!project.sprints) {
          project.sprints = [];
        }
        project.sprints.push(data);
      }
      return data.id;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create sprint';
      console.error('Failed to create sprint:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function updateSprint(projectId: number, sprintId: number, updates: Partial<Sprint>) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.put<Sprint>(`/projects/${projectId}/sprints/${sprintId}`, updates);
      const project = projects.value.find((p) => p.id === projectId);
      if (project && project.sprints) {
        const index = project.sprints.findIndex((s) => s.id === sprintId);
        if (index !== -1) {
          project.sprints[index] = data;
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update sprint';
      console.error('Failed to update sprint:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteSprint(projectId: number, sprintId: number) {
    loading.value = true;
    error.value = null;
    try {
      await api.delete(`/projects/${projectId}/sprints/${sprintId}`);
      const project = projects.value.find((p) => p.id === projectId);
      if (project && project.sprints) {
        const index = project.sprints.findIndex((s) => s.id === sprintId);
        if (index !== -1) {
          project.sprints.splice(index, 1);
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete sprint';
      console.error('Failed to delete sprint:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function getActiveSprint(projectId: number): Sprint | undefined {
    const project = projects.value.find((p) => p.id === projectId);
    return project?.sprints?.find((s) => s.status === 'active');
  }

  // Task management
  async function createTask(projectId: number, taskData: Partial<Task>) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.post<Task>('/tasks', taskData);
      // Add task to local state
      const project = projects.value.find((p) => p.id === projectId);
      if (project) {
        if (!project.tasks) {
          project.tasks = [];
        }
        project.tasks.push(data);
      }
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create task';
      console.error('Failed to create task:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTask(taskId: number, updates: Partial<Task>) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.put<Task>(`/tasks/${taskId}`, updates);
      // Update task in local state
      for (const project of projects.value) {
        const taskIndex = project.tasks?.findIndex((t) => t.id === taskId);
        if (taskIndex !== undefined && taskIndex !== -1 && project.tasks) {
          project.tasks[taskIndex] = data;
          break;
        }
      }
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update task';
      console.error('Failed to update task:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTask(taskId: number) {
    loading.value = true;
    error.value = null;
    try {
      await api.delete(`/tasks/${taskId}`);
      // Remove task from local state
      for (const project of projects.value) {
        if (project.tasks) {
          const taskIndex = project.tasks.findIndex((t) => t.id === taskId);
          if (taskIndex !== -1) {
            project.tasks.splice(taskIndex, 1);
            break;
          }
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete task';
      console.error('Failed to delete task:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Local getters (no API calls)
  function getMemberRole(projectId: number, memberId: number): ProjectRole | undefined {
    const project = projects.value.find((p) => p.id === projectId);
    return project?.roles?.find((r) => r.memberId === memberId);
  }

  function getRolePermissions(role: ProjectRole['role']): ProjectRole['permissions'] {
    switch (role) {
      case 'owner':
        return {
          canEdit: true,
          canDelete: true,
          canManageTeam: true,
          canManageSprints: true,
        };
      case 'admin':
        return {
          canEdit: true,
          canDelete: false,
          canManageTeam: true,
          canManageSprints: true,
        };
      case 'developer':
        return {
          canEdit: true,
          canDelete: false,
          canManageTeam: false,
          canManageSprints: false,
        };
      case 'viewer':
        return {
          canEdit: false,
          canDelete: false,
          canManageTeam: false,
          canManageSprints: false,
        };
    }
  }

  // PERT/CPM methods
  async function getCriticalPath(projectId: number): Promise<CriticalPathResponse> {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.get<CriticalPathResponse>(`/projects/${projectId}/critical-path`);
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to calculate critical path';
      console.error('Failed to calculate critical path:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updatePertSettings(
    projectId: number,
    settings: { pertManualEdges?: PertManualEdge[]; pertLayoutSettings?: PertLayoutSettings },
  ) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.patch<Project>(`/projects/${projectId}/pert-settings`, settings);

      // Update local state
      const index = projects.value.findIndex((p) => p.id === projectId);
      if (index !== -1) {
        projects.value[index] = data;
      }

      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update PERT settings';
      console.error('Failed to update PERT settings:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTaskPosition(taskId: number, x: number | null, y: number | null) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.put<Task>(`/tasks/${taskId}`, {
        diagramPositionX: x,
        diagramPositionY: y,
      });

      // Update local state
      for (const project of projects.value) {
        if (!project.tasks) continue; // Skip projects without tasks loaded

        const taskIndex = project.tasks.findIndex((t) => t.id === taskId);
        if (taskIndex !== -1) {
          project.tasks[taskIndex] = data;
          break;
        }
      }

      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update task position';
      console.error('Failed to update task position:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    projects,
    loading,
    error,
    fetchProjects,
    getProject,
    getProjectById,
    addProject,
    updateProject,
    deleteProject,
    addSprint,
    updateSprint,
    deleteSprint,
    getActiveSprint,
    createTask,
    updateTask,
    deleteTask,
    getMemberRole,
    getRolePermissions,
    addMemberToProject,
    updateMemberRole,
    removeMemberFromProject,
    getCriticalPath,
    updatePertSettings,
    updateTaskPosition,
  };
});
