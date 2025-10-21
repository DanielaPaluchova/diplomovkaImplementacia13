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
  name: string;
  title: string;
  description: string;
  status: 'To Do' | 'In Progress' | 'Done';
  priority: 'High' | 'Medium' | 'Low' | 'high' | 'medium' | 'low';
  type: 'feature' | 'bug' | 'task';
  storyPoints: number;
  assigneeId: number | null;
  assignee?: string;
  sprintId: number | null;
  dueDate: Date | string;
  completed: boolean;
  labels: string[];
  complexity: number;
  pert: PertEstimate;
  raci: RaciMatrix;
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
      if (project) {
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
      if (project) {
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
    return project?.sprints.find((s) => s.status === 'active');
  }

  // Local getters (no API calls)
  function getMemberRole(projectId: number, memberId: number): ProjectRole | undefined {
    const project = projects.value.find((p) => p.id === projectId);
    return project?.roles.find((r) => r.memberId === memberId);
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

  return {
    projects,
    loading,
    error,
    fetchProjects,
    getProject,
    addProject,
    updateProject,
    deleteProject,
    addSprint,
    updateSprint,
    deleteSprint,
    getActiveSprint,
    getMemberRole,
    getRolePermissions,
  };
});
