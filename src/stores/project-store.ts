import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Sprint {
  id: number;
  name: string;
  goal: string;
  startDate: Date;
  endDate: Date;
  status: 'planned' | 'active' | 'completed';
  capacity: number; // Total story points capacity
  completed: number; // Completed story points
  taskIds: number[]; // IDs of tasks in this sprint
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

export interface Task {
  id: number;
  name: string;
  description: string;
  status: 'To Do' | 'In Progress' | 'Done';
  priority: 'High' | 'Medium' | 'Low';
  storyPoints: number;
  assigneeId: number;
  sprintId: number | null;
  dueDate: Date;
  completed: boolean;
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
  dueDate: Date;
  createdAt: Date;
  teamMemberIds: number[];
  roles: ProjectRole[];
  sprints: Sprint[];
  totalStoryPoints: number;
  estimatedDuration: number;
}

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([
    {
      id: 1,
      name: 'E-commerce Platform Redesign',
      description: 'Complete UI/UX overhaul of the main platform',
      template: 'Agile Development',
      icon: 'shopping_cart',
      progress: 75,
      tasksCompleted: 18,
      totalTasks: 24,
      status: 'On Track',
      dueDate: new Date('2024-03-15'),
      createdAt: new Date('2024-01-05'),
      teamMemberIds: [1, 3, 4],
      roles: [
        {
          memberId: 4,
          role: 'owner',
          permissions: {
            canEdit: true,
            canDelete: true,
            canManageTeam: true,
            canManageSprints: true,
          },
        },
        {
          memberId: 1,
          role: 'developer',
          permissions: {
            canEdit: true,
            canDelete: false,
            canManageTeam: false,
            canManageSprints: false,
          },
        },
        {
          memberId: 3,
          role: 'developer',
          permissions: {
            canEdit: true,
            canDelete: false,
            canManageTeam: false,
            canManageSprints: false,
          },
        },
      ],
      sprints: [
        {
          id: 1,
          name: 'Sprint 1',
          goal: 'Setup authentication and user management',
          startDate: new Date('2024-01-08'),
          endDate: new Date('2024-01-22'),
          status: 'completed',
          capacity: 40,
          completed: 38,
          taskIds: [1, 2, 3],
        },
        {
          id: 2,
          name: 'Sprint 2',
          goal: 'Product catalog and shopping cart',
          startDate: new Date('2024-01-23'),
          endDate: new Date('2024-02-06'),
          status: 'active',
          capacity: 42,
          completed: 28,
          taskIds: [4, 5, 6],
        },
        {
          id: 3,
          name: 'Sprint 3',
          goal: 'Payment integration and checkout',
          startDate: new Date('2024-02-07'),
          endDate: new Date('2024-02-21'),
          status: 'planned',
          capacity: 45,
          completed: 0,
          taskIds: [],
        },
      ],
      totalStoryPoints: 180,
      estimatedDuration: 45,
    },
    {
      id: 2,
      name: 'Mobile App Development',
      description: 'Native iOS and Android application',
      template: 'Agile Development',
      icon: 'phone_android',
      progress: 45,
      tasksCompleted: 12,
      totalTasks: 28,
      status: 'In Progress',
      dueDate: new Date('2024-04-20'),
      createdAt: new Date('2024-01-10'),
      teamMemberIds: [1, 2, 5],
      roles: [
        {
          memberId: 2,
          role: 'owner',
          permissions: {
            canEdit: true,
            canDelete: true,
            canManageTeam: true,
            canManageSprints: true,
          },
        },
        {
          memberId: 1,
          role: 'developer',
          permissions: {
            canEdit: true,
            canDelete: false,
            canManageTeam: false,
            canManageSprints: false,
          },
        },
        {
          memberId: 5,
          role: 'developer',
          permissions: {
            canEdit: true,
            canDelete: false,
            canManageTeam: false,
            canManageSprints: false,
          },
        },
      ],
      sprints: [
        {
          id: 4,
          name: 'Sprint 1',
          goal: 'App architecture and navigation',
          startDate: new Date('2024-01-15'),
          endDate: new Date('2024-01-29'),
          status: 'completed',
          capacity: 35,
          completed: 32,
          taskIds: [],
        },
        {
          id: 5,
          name: 'Sprint 2',
          goal: 'Core features implementation',
          startDate: new Date('2024-01-30'),
          endDate: new Date('2024-02-13'),
          status: 'active',
          capacity: 38,
          completed: 15,
          taskIds: [],
        },
      ],
      totalStoryPoints: 150,
      estimatedDuration: 60,
    },
  ]);

  // Actions
  function getProject(id: number): Project | undefined {
    return projects.value.find((p) => p.id === id);
  }

  function addProject(project: Omit<Project, 'id' | 'createdAt'>) {
    const newId = Math.max(...projects.value.map((p) => p.id), 0) + 1;
    projects.value.push({
      ...project,
      id: newId,
      createdAt: new Date(),
    });
    return newId;
  }

  function updateProject(id: number, updates: Partial<Project>) {
    const index = projects.value.findIndex((p) => p.id === id);
    if (index !== -1) {
      const existingProject = projects.value[index]!;
      projects.value[index] = {
        ...existingProject,
        ...updates,
      };
    }
  }

  function deleteProject(id: number) {
    const index = projects.value.findIndex((p) => p.id === id);
    if (index !== -1) {
      projects.value.splice(index, 1);
    }
  }

  // Sprint management
  function addSprint(projectId: number, sprint: Omit<Sprint, 'id'>) {
    const project = getProject(projectId);
    if (project) {
      const newId = Math.max(...project.sprints.map((s) => s.id), 0) + 1;
      project.sprints.push({
        ...sprint,
        id: newId,
      });
      return newId;
    }
    return null;
  }

  function updateSprint(projectId: number, sprintId: number, updates: Partial<Sprint>) {
    const project = getProject(projectId);
    if (project) {
      const index = project.sprints.findIndex((s) => s.id === sprintId);
      if (index !== -1) {
        const existingSprint = project.sprints[index]!;
        project.sprints[index] = {
          ...existingSprint,
          ...updates,
        };
      }
    }
  }

  function deleteSprint(projectId: number, sprintId: number) {
    const project = getProject(projectId);
    if (project) {
      const index = project.sprints.findIndex((s) => s.id === sprintId);
      if (index !== -1) {
        project.sprints.splice(index, 1);
      }
    }
  }

  function getActiveSprint(projectId: number): Sprint | undefined {
    const project = getProject(projectId);
    return project?.sprints.find((s) => s.status === 'active');
  }

  // Role management
  function updateMemberRole(projectId: number, memberId: number, role: ProjectRole['role']) {
    const project = getProject(projectId);
    if (project) {
      const roleIndex = project.roles.findIndex((r) => r.memberId === memberId);
      if (roleIndex !== -1) {
        const permissions = getRolePermissions(role);
        project.roles[roleIndex] = {
          memberId,
          role,
          permissions,
        };
      }
    }
  }

  function addMemberToProject(
    projectId: number,
    memberId: number,
    role: ProjectRole['role'] = 'developer',
  ) {
    const project = getProject(projectId);
    if (project) {
      if (!project.teamMemberIds.includes(memberId)) {
        project.teamMemberIds.push(memberId);
      }
      if (!project.roles.find((r) => r.memberId === memberId)) {
        project.roles.push({
          memberId,
          role,
          permissions: getRolePermissions(role),
        });
      }
    }
  }

  function removeMemberFromProject(projectId: number, memberId: number) {
    const project = getProject(projectId);
    if (project) {
      project.teamMemberIds = project.teamMemberIds.filter((id) => id !== memberId);
      project.roles = project.roles.filter((r) => r.memberId !== memberId);
    }
  }

  function getMemberRole(projectId: number, memberId: number): ProjectRole | undefined {
    const project = getProject(projectId);
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

  // Workload calculation
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  function getMemberWorkloadInProject(projectId: number, memberId: number): number {
    const project = getProject(projectId);
    if (!project) return 0;

    const activeSprint = getActiveSprint(projectId);
    if (!activeSprint) return 0;

    // TODO: Calculate actual workload from tasks assigned to memberId
    // This would be calculated from actual tasks assigned to the member
    // For now, return a mock value
    return 0;
  }

  return {
    projects,
    getProject,
    addProject,
    updateProject,
    deleteProject,
    addSprint,
    updateSprint,
    deleteSprint,
    getActiveSprint,
    updateMemberRole,
    addMemberToProject,
    removeMemberFromProject,
    getMemberRole,
    getRolePermissions,
    getMemberWorkloadInProject,
  };
});
