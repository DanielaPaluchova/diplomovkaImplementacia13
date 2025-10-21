import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Sprint {
  id: number;
  name: string;
  goal: string;
  startDate: Date;
  endDate: Date;
  status: 'planned' | 'active' | 'completed';
  totalTasks: number; // Total tasks in sprint
  completedTasks: number; // Completed tasks
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

export interface PertEstimate {
  optimistic: number; // Optimistic time estimate (in hours)
  mostLikely: number; // Most likely time estimate (in hours)
  pessimistic: number; // Pessimistic time estimate (in hours)
  expected?: number; // Calculated: (O + 4M + P) / 6
}

export interface RaciMatrix {
  responsible: number[]; // Team member IDs who do the work
  accountable: number | null; // Team member ID who is accountable
  consulted: number[]; // Team member IDs who are consulted
  informed: number[]; // Team member IDs who are informed
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
  dueDate: Date;
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
  dueDate: Date;
  createdAt: Date;
  teamMemberIds: number[];
  roles: ProjectRole[];
  sprints: Sprint[];
  tasks: Task[];
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
          totalTasks: 15,
          completedTasks: 15,
          taskIds: [1, 2, 3],
        },
        {
          id: 2,
          name: 'Sprint 2',
          goal: 'Product catalog and shopping cart',
          startDate: new Date('2024-01-23'),
          endDate: new Date('2024-02-06'),
          status: 'active',
          totalTasks: 12,
          completedTasks: 8,
          taskIds: [4, 5, 6],
        },
        {
          id: 3,
          name: 'Sprint 3',
          goal: 'Payment integration and checkout',
          startDate: new Date('2024-02-07'),
          endDate: new Date('2024-02-21'),
          status: 'planned',
          totalTasks: 10,
          completedTasks: 0,
          taskIds: [],
        },
      ],
      tasks: [
        {
          id: 1,
          name: 'User Authentication System',
          title: 'User Authentication System',
          description: 'Implement JWT-based authentication with refresh tokens',
          status: 'Done',
          priority: 'high',
          type: 'feature',
          storyPoints: 8,
          assigneeId: 1,
          assignee: 'John Smith',
          sprintId: 1,
          dueDate: new Date('2024-01-22'),
          completed: true,
          labels: ['backend', 'security'],
          complexity: 8,
          pert: {
            optimistic: 24,
            mostLikely: 40,
            pessimistic: 64,
            expected: 41.3,
          },
          raci: {
            responsible: [1],
            accountable: 1,
            consulted: [3],
            informed: [4],
          },
        },
        {
          id: 2,
          name: 'Product Catalog API',
          title: 'Product Catalog API',
          description: 'Create REST API endpoints for product catalog',
          status: 'Done',
          priority: 'high',
          type: 'feature',
          storyPoints: 5,
          assigneeId: 3,
          assignee: 'Mike Wilson',
          sprintId: 1,
          dueDate: new Date('2024-01-22'),
          completed: true,
          labels: ['backend', 'api'],
          complexity: 6,
          pert: {
            optimistic: 16,
            mostLikely: 24,
            pessimistic: 40,
            expected: 25.3,
          },
          raci: {
            responsible: [3],
            accountable: 1,
            consulted: [],
            informed: [4],
          },
        },
        {
          id: 3,
          name: 'Shopping Cart Component',
          title: 'Shopping Cart Component',
          description: 'Build shopping cart UI with add/remove functionality',
          status: 'Done',
          priority: 'high',
          type: 'feature',
          storyPoints: 8,
          assigneeId: 4,
          assignee: 'Emma Davis',
          sprintId: 1,
          dueDate: new Date('2024-01-22'),
          completed: true,
          labels: ['frontend', 'ui'],
          complexity: 7,
          pert: {
            optimistic: 20,
            mostLikely: 32,
            pessimistic: 52,
            expected: 33.3,
          },
          raci: {
            responsible: [4],
            accountable: 1,
            consulted: [3],
            informed: [],
          },
        },
        {
          id: 4,
          name: 'Payment Gateway Integration',
          title: 'Payment Gateway Integration',
          description: 'Integrate Stripe payment processing',
          status: 'In Progress',
          priority: 'high',
          type: 'feature',
          storyPoints: 13,
          assigneeId: 1,
          assignee: 'John Smith',
          sprintId: 2,
          dueDate: new Date('2024-02-06'),
          completed: false,
          labels: ['backend', 'payment'],
          complexity: 9,
          pert: {
            optimistic: 32,
            mostLikely: 52,
            pessimistic: 80,
            expected: 53.3,
          },
          raci: {
            responsible: [1],
            accountable: 1,
            consulted: [3],
            informed: [4],
          },
        },
        {
          id: 5,
          name: 'Order Management Dashboard',
          title: 'Order Management Dashboard',
          description: 'Admin dashboard for managing orders',
          status: 'To Do',
          priority: 'medium',
          type: 'feature',
          storyPoints: 8,
          assigneeId: 4,
          assignee: 'Emma Davis',
          sprintId: 2,
          dueDate: new Date('2024-02-06'),
          completed: false,
          labels: ['frontend', 'admin'],
          complexity: 7,
          pert: {
            optimistic: 24,
            mostLikely: 40,
            pessimistic: 56,
            expected: 40,
          },
          raci: {
            responsible: [4],
            accountable: 1,
            consulted: [1],
            informed: [3],
          },
        },
        {
          id: 6,
          name: 'Email Notification System',
          title: 'Email Notification System',
          description: 'Send order confirmation emails',
          status: 'To Do',
          priority: 'medium',
          type: 'feature',
          storyPoints: 5,
          assigneeId: 3,
          assignee: 'Mike Wilson',
          sprintId: null,
          dueDate: new Date('2024-02-15'),
          completed: false,
          labels: ['backend', 'notifications'],
          complexity: 5,
          pert: {
            optimistic: 12,
            mostLikely: 20,
            pessimistic: 32,
            expected: 20.7,
          },
          raci: {
            responsible: [3],
            accountable: 1,
            consulted: [],
            informed: [4],
          },
        },
        {
          id: 7,
          name: 'Product Search Optimization',
          title: 'Product Search Optimization',
          description: 'Implement full-text search with filters',
          status: 'To Do',
          priority: 'medium',
          type: 'feature',
          storyPoints: 8,
          assigneeId: null,
          sprintId: null,
          dueDate: new Date('2024-02-20'),
          completed: false,
          labels: ['backend', 'search'],
          complexity: 8,
          pert: {
            optimistic: 20,
            mostLikely: 32,
            pessimistic: 48,
            expected: 32.7,
          },
          raci: {
            responsible: [],
            accountable: 1,
            consulted: [3],
            informed: [],
          },
        },
        {
          id: 8,
          name: 'Mobile Responsive Design',
          title: 'Mobile Responsive Design',
          description: 'Make all pages mobile-friendly',
          status: 'To Do',
          priority: 'high',
          type: 'task',
          storyPoints: 5,
          assigneeId: null,
          sprintId: null,
          dueDate: new Date('2024-02-25'),
          completed: false,
          labels: ['frontend', 'mobile'],
          complexity: 6,
          pert: {
            optimistic: 14,
            mostLikely: 24,
            pessimistic: 36,
            expected: 24.3,
          },
          raci: {
            responsible: [],
            accountable: 1,
            consulted: [4],
            informed: [],
          },
        },
        {
          id: 9,
          name: 'Performance Optimization',
          title: 'Performance Optimization',
          description: 'Optimize page load times and API responses',
          status: 'To Do',
          priority: 'low',
          type: 'task',
          storyPoints: 3,
          assigneeId: null,
          sprintId: null,
          dueDate: new Date('2024-03-01'),
          completed: false,
          labels: ['performance'],
          complexity: 4,
          pert: {
            optimistic: 6,
            mostLikely: 12,
            pessimistic: 20,
            expected: 12.3,
          },
          raci: {
            responsible: [],
            accountable: 1,
            consulted: [3],
            informed: [4],
          },
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
          totalTasks: 18,
          completedTasks: 18,
          taskIds: [101, 102],
        },
        {
          id: 5,
          name: 'Sprint 2',
          goal: 'Core features implementation',
          startDate: new Date('2024-01-30'),
          endDate: new Date('2024-02-13'),
          status: 'active',
          totalTasks: 14,
          completedTasks: 6,
          taskIds: [103, 104],
        },
      ],
      tasks: [
        {
          id: 101,
          name: 'Navigation System',
          title: 'Navigation System',
          description: 'Implement React Navigation for app routing',
          status: 'Done',
          priority: 'high',
          type: 'feature',
          storyPoints: 8,
          assigneeId: 1,
          assignee: 'John Smith',
          sprintId: 4,
          dueDate: new Date('2024-01-29'),
          completed: true,
          labels: ['mobile', 'navigation'],
          complexity: 7,
          pert: {
            optimistic: 20,
            mostLikely: 32,
            pessimistic: 48,
            expected: 32.7,
          },
          raci: {
            responsible: [1],
            accountable: 2,
            consulted: [5],
            informed: [],
          },
        },
        {
          id: 102,
          name: 'User Authentication Flow',
          title: 'User Authentication Flow',
          description: 'Build login and registration screens',
          status: 'Done',
          priority: 'high',
          type: 'feature',
          storyPoints: 13,
          assigneeId: 2,
          assignee: 'Sarah Johnson',
          sprintId: 4,
          dueDate: new Date('2024-01-29'),
          completed: true,
          labels: ['mobile', 'auth'],
          complexity: 9,
          pert: {
            optimistic: 32,
            mostLikely: 52,
            pessimistic: 80,
            expected: 53.3,
          },
          raci: {
            responsible: [2],
            accountable: 2,
            consulted: [1],
            informed: [],
          },
        },
        {
          id: 103,
          name: 'Home Screen Dashboard',
          title: 'Home Screen Dashboard',
          description: 'Create main dashboard with widgets',
          status: 'In Progress',
          priority: 'high',
          type: 'feature',
          storyPoints: 8,
          assigneeId: 5,
          assignee: 'Emma Davis',
          sprintId: 5,
          dueDate: new Date('2024-02-13'),
          completed: false,
          labels: ['mobile', 'ui'],
          complexity: 7,
          pert: {
            optimistic: 24,
            mostLikely: 40,
            pessimistic: 56,
            expected: 40,
          },
          raci: {
            responsible: [5],
            accountable: 2,
            consulted: [1],
            informed: [],
          },
        },
        {
          id: 104,
          name: 'Push Notifications',
          title: 'Push Notifications',
          description: 'Implement Firebase push notifications',
          status: 'To Do',
          priority: 'medium',
          type: 'feature',
          storyPoints: 5,
          assigneeId: 1,
          assignee: 'John Smith',
          sprintId: 5,
          dueDate: new Date('2024-02-13'),
          completed: false,
          labels: ['mobile', 'notifications'],
          complexity: 6,
          pert: {
            optimistic: 16,
            mostLikely: 24,
            pessimistic: 40,
            expected: 25.3,
          },
          raci: {
            responsible: [1],
            accountable: 2,
            consulted: [],
            informed: [5],
          },
        },
        {
          id: 105,
          name: 'Offline Data Sync',
          title: 'Offline Data Sync',
          description: 'Enable offline mode with data synchronization',
          status: 'To Do',
          priority: 'high',
          type: 'feature',
          storyPoints: 13,
          assigneeId: 1,
          assignee: 'John Smith',
          sprintId: null,
          dueDate: new Date('2024-02-20'),
          completed: false,
          labels: ['mobile', 'sync'],
          complexity: 10,
          pert: {
            optimistic: 40,
            mostLikely: 64,
            pessimistic: 96,
            expected: 65.3,
          },
          raci: {
            responsible: [1],
            accountable: 2,
            consulted: [],
            informed: [5],
          },
        },
        {
          id: 106,
          name: 'Camera Integration',
          title: 'Camera Integration',
          description: 'Add camera and photo upload functionality',
          status: 'In Progress',
          priority: 'medium',
          type: 'feature',
          storyPoints: 8,
          assigneeId: 2,
          assignee: 'Sarah Johnson',
          sprintId: null,
          dueDate: new Date('2024-02-25'),
          completed: false,
          labels: ['mobile', 'camera'],
          complexity: 7,
          pert: {
            optimistic: 20,
            mostLikely: 32,
            pessimistic: 48,
            expected: 32.7,
          },
          raci: {
            responsible: [2],
            accountable: 2,
            consulted: [5],
            informed: [],
          },
        },
        {
          id: 107,
          name: 'Settings Screen',
          title: 'Settings Screen',
          description: 'Build user settings and preferences',
          status: 'To Do',
          priority: 'low',
          type: 'feature',
          storyPoints: 5,
          assigneeId: 5,
          assignee: 'David Brown',
          sprintId: null,
          dueDate: new Date('2024-03-01'),
          completed: false,
          labels: ['mobile', 'ui'],
          complexity: 5,
          pert: {
            optimistic: 12,
            mostLikely: 20,
            pessimistic: 32,
            expected: 20.7,
          },
          raci: {
            responsible: [5],
            accountable: 2,
            consulted: [],
            informed: [],
          },
        },
        {
          id: 108,
          name: 'App Performance Tuning',
          title: 'App Performance Tuning',
          description: 'Optimize app startup and rendering performance',
          status: 'To Do',
          priority: 'medium',
          type: 'task',
          storyPoints: 3,
          assigneeId: 1,
          assignee: 'John Smith',
          sprintId: null,
          dueDate: new Date('2024-03-05'),
          completed: false,
          labels: ['mobile', 'performance'],
          complexity: 6,
          pert: {
            optimistic: 8,
            mostLikely: 12,
            pessimistic: 20,
            expected: 12.7,
          },
          raci: {
            responsible: [1],
            accountable: 2,
            consulted: [],
            informed: [5],
          },
        },
        {
          id: 109,
          name: 'Social Media Sharing',
          title: 'Social Media Sharing',
          description: 'Integrate social media sharing functionality',
          status: 'To Do',
          priority: 'low',
          type: 'feature',
          storyPoints: 5,
          assigneeId: 2,
          assignee: 'Sarah Johnson',
          sprintId: null,
          dueDate: new Date('2024-03-10'),
          completed: false,
          labels: ['mobile', 'social'],
          complexity: 5,
          pert: {
            optimistic: 14,
            mostLikely: 20,
            pessimistic: 30,
            expected: 20.7,
          },
          raci: {
            responsible: [2],
            accountable: 2,
            consulted: [],
            informed: [],
          },
        },
        {
          id: 110,
          name: 'Location Services',
          title: 'Location Services',
          description: 'Add GPS and location-based features',
          status: 'To Do',
          priority: 'medium',
          type: 'feature',
          storyPoints: 8,
          assigneeId: null,
          sprintId: null,
          dueDate: new Date('2024-03-15'),
          completed: false,
          labels: ['mobile', 'location'],
          complexity: 7,
          pert: {
            optimistic: 20,
            mostLikely: 32,
            pessimistic: 48,
            expected: 32.7,
          },
          raci: {
            responsible: [],
            accountable: 2,
            consulted: [1],
            informed: [5],
          },
        },
        {
          id: 111,
          name: 'Dark Mode Support',
          title: 'Dark Mode Support',
          description: 'Implement dark theme across the app',
          status: 'Done',
          priority: 'medium',
          type: 'feature',
          storyPoints: 5,
          assigneeId: 5,
          assignee: 'David Brown',
          sprintId: null,
          dueDate: new Date('2024-02-28'),
          completed: true,
          labels: ['mobile', 'ui'],
          complexity: 6,
          pert: {
            optimistic: 14,
            mostLikely: 20,
            pessimistic: 30,
            expected: 20.7,
          },
          raci: {
            responsible: [5],
            accountable: 2,
            consulted: [],
            informed: [1, 2],
          },
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
