import { defineStore } from 'pinia';

export interface TeamMember {
  id: number;
  name: string;
  role: string;
  avatar: string;
  status: 'online' | 'busy' | 'away' | 'offline';
  activeProjects: number;
  workload: number;
  skills: string[];
  email: string;
}

export interface Project {
  id: number;
  name: string;
  client: string;
  description: string;
  progress: number;
  status: string;
  dueDate: Date;
  color: string;
  icon: string;
  budget: number;
  budgetUsed: number;
  team: TeamMember[];
  priority: 'high' | 'medium' | 'low';
  methodology: 'Agile' | 'Waterfall' | 'Hybrid';
}

export interface Task {
  id: number;
  title: string;
  description: string;
  storyPoints: number;
  priority: 'high' | 'medium' | 'low';
  type: 'feature' | 'bug' | 'task';
  assignee?: string;
  labels: string[];
  complexity: number;
  status: 'todo' | 'in_progress' | 'review' | 'done';
  projectId: number;
}

export interface Experiment {
  id: number;
  name: string;
  description: string;
  hypothesis: string;
  status: 'planning' | 'running' | 'completed' | 'cancelled';
  methodology: string;
  startDate: Date;
  endDate: Date;
  participants: number;
  results?: {
    success: boolean;
    improvement: number;
    confidence: number;
  };
}

export const useMockDataStore = defineStore('mockData', {
  state: () => ({
    teamMembers: [
      {
        id: 1,
        name: 'John Smith',
        role: 'Senior Frontend Developer',
        avatar: 'https://cdn.quasar.dev/img/avatar2.jpg',
        status: 'online' as const,
        activeProjects: 3,
        workload: 85,
        skills: ['Vue.js', 'TypeScript', 'React', 'Node.js', 'GraphQL'],
        email: 'john.smith@company.com',
      },
      {
        id: 2,
        name: 'Sarah Johnson',
        role: 'Backend Developer',
        avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
        status: 'busy' as const,
        activeProjects: 2,
        workload: 75,
        skills: ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS'],
        email: 'sarah.johnson@company.com',
      },
      {
        id: 3,
        name: 'Mike Wilson',
        role: 'DevOps Engineer',
        avatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
        status: 'away' as const,
        activeProjects: 4,
        workload: 90,
        skills: ['Kubernetes', 'Docker', 'Jenkins', 'AWS', 'Terraform'],
        email: 'mike.wilson@company.com',
      },
      {
        id: 4,
        name: 'Emma Davis',
        role: 'UI/UX Designer',
        avatar: 'https://cdn.quasar.dev/img/avatar5.jpg',
        status: 'online' as const,
        activeProjects: 2,
        workload: 60,
        skills: ['Figma', 'Adobe XD', 'Sketch', 'Prototyping', 'User Research'],
        email: 'emma.davis@company.com',
      },
      {
        id: 5,
        name: 'Alex Chen',
        role: 'Full Stack Developer',
        avatar: 'https://cdn.quasar.dev/img/avatar.png',
        status: 'online' as const,
        activeProjects: 1,
        workload: 70,
        skills: ['Vue.js', 'Python', 'FastAPI', 'MongoDB', 'Redis'],
        email: 'alex.chen@company.com',
      },
      {
        id: 6,
        name: 'Lisa Rodriguez',
        role: 'Project Manager',
        avatar: 'https://cdn.quasar.dev/img/avatar6.jpg',
        status: 'busy' as const,
        activeProjects: 5,
        workload: 95,
        skills: ['Scrum', 'Kanban', 'PERT', 'Risk Management', 'Stakeholder Management'],
        email: 'lisa.rodriguez@company.com',
      },
    ] as TeamMember[],

    projects: [
      {
        id: 1,
        name: 'E-commerce Platform Redesign',
        client: 'TechCorp Inc.',
        description:
          'Complete UI/UX overhaul of the main e-commerce platform with modern design and improved user experience',
        progress: 75,
        status: 'On Track',
        dueDate: new Date('2024-01-15'),
        color: 'primary',
        icon: 'shopping_cart',
        budget: 150000,
        budgetUsed: 112500,
        team: [],
        priority: 'high' as const,
        methodology: 'Agile' as const,
      },
      {
        id: 2,
        name: 'Mobile App Development',
        client: 'StartupXYZ',
        description: 'Native iOS and Android application for food delivery service',
        progress: 45,
        status: 'In Progress',
        dueDate: new Date('2024-02-20'),
        color: 'green',
        icon: 'phone_android',
        budget: 200000,
        budgetUsed: 90000,
        team: [],
        priority: 'high' as const,
        methodology: 'Agile' as const,
      },
      {
        id: 3,
        name: 'Data Migration Project',
        client: 'Enterprise Solutions',
        description: 'Legacy system to cloud migration with data transformation',
        progress: 30,
        status: 'At Risk',
        dueDate: new Date('2024-01-30'),
        color: 'orange',
        icon: 'cloud_upload',
        budget: 300000,
        budgetUsed: 180000,
        team: [],
        priority: 'medium' as const,
        methodology: 'Waterfall' as const,
      },
      {
        id: 4,
        name: 'AI Chatbot Integration',
        client: 'CustomerFirst Ltd.',
        description: 'Integration of AI-powered chatbot for customer support',
        progress: 60,
        status: 'On Track',
        dueDate: new Date('2024-03-10'),
        color: 'blue',
        icon: 'smart_toy',
        budget: 80000,
        budgetUsed: 48000,
        team: [],
        priority: 'medium' as const,
        methodology: 'Agile' as const,
      },
      {
        id: 5,
        name: 'Security Audit & Compliance',
        client: 'FinanceSecure',
        description: 'Complete security audit and GDPR compliance implementation',
        progress: 90,
        status: 'On Track',
        dueDate: new Date('2024-01-05'),
        color: 'red',
        icon: 'security',
        budget: 120000,
        budgetUsed: 108000,
        team: [],
        priority: 'high' as const,
        methodology: 'Waterfall' as const,
      },
      {
        id: 6,
        name: 'API Modernization',
        client: 'TechFlow Systems',
        description: 'Modernizing REST APIs to GraphQL with performance optimization',
        progress: 25,
        status: 'In Progress',
        dueDate: new Date('2024-04-15'),
        color: 'purple',
        icon: 'api',
        budget: 180000,
        budgetUsed: 45000,
        team: [],
        priority: 'low' as const,
        methodology: 'Hybrid' as const,
      },
    ] as Project[],

    experiments: [
      {
        id: 1,
        name: 'PERT vs Traditional Planning',
        description: 'Comparing PERT-based planning with traditional estimation methods',
        hypothesis: 'PERT-based planning will improve estimation accuracy by 25%',
        status: 'completed' as const,
        methodology: 'A/B Testing',
        startDate: new Date('2023-10-01'),
        endDate: new Date('2023-12-01'),
        participants: 50,
        results: {
          success: true,
          improvement: 32,
          confidence: 95,
        },
      },
      {
        id: 2,
        name: 'AI-Assisted Sprint Planning',
        description: 'Testing AI recommendations in sprint planning process',
        hypothesis: 'AI assistance will reduce planning time by 40% while maintaining quality',
        status: 'running' as const,
        methodology: 'Controlled Experiment',
        startDate: new Date('2023-11-15'),
        endDate: new Date('2024-01-15'),
        participants: 30,
      },
      {
        id: 3,
        name: 'RACI Matrix Optimization',
        description: 'Optimizing team collaboration through enhanced RACI matrices',
        hypothesis: 'Clear RACI definitions will reduce communication overhead by 50%',
        status: 'planning' as const,
        methodology: 'Before/After Study',
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-03-01'),
        participants: 40,
      },
      {
        id: 4,
        name: 'Hybrid Methodology Effectiveness',
        description: 'Comparing pure Agile vs Hybrid approaches for complex projects',
        hypothesis: 'Hybrid methodology will improve delivery predictability by 30%',
        status: 'completed' as const,
        methodology: 'Comparative Study',
        startDate: new Date('2023-08-01'),
        endDate: new Date('2023-11-30'),
        participants: 60,
        results: {
          success: true,
          improvement: 28,
          confidence: 88,
        },
      },
    ] as Experiment[],

    tasks: [
      {
        id: 1,
        title: 'User Authentication System',
        description: 'Implement JWT-based authentication with refresh tokens',
        storyPoints: 8,
        priority: 'high' as const,
        type: 'feature' as const,
        assignee: 'John Smith',
        labels: ['backend', 'security'],
        complexity: 8,
        status: 'in_progress' as const,
        projectId: 1,
      },
      {
        id: 2,
        title: 'Dashboard Analytics Widget',
        description: 'Create interactive charts for project metrics',
        storyPoints: 5,
        priority: 'medium' as const,
        type: 'feature' as const,
        labels: ['frontend', 'charts'],
        complexity: 6,
        status: 'todo' as const,
        projectId: 1,
      },
      {
        id: 3,
        title: 'Fix Mobile Responsive Issues',
        description: 'Resolve layout problems on mobile devices',
        storyPoints: 3,
        priority: 'high' as const,
        type: 'bug' as const,
        labels: ['frontend', 'mobile'],
        complexity: 4,
        status: 'review' as const,
        projectId: 2,
      },
    ] as Task[],
  }),

  getters: {
    getProjectById: (state) => {
      return (id: number) => state.projects.find((p) => p.id === id);
    },

    getTeamMemberById: (state) => {
      return (id: number) => state.teamMembers.find((m) => m.id === id);
    },

    getTasksByProject: (state) => {
      return (projectId: number) => state.tasks.filter((t) => t.projectId === projectId);
    },

    getActiveProjects: (state) => {
      return state.projects.filter((p) => p.status !== 'Completed');
    },

    getCompletedExperiments: (state) => {
      return state.experiments.filter((e) => e.status === 'completed');
    },
  },

  actions: {
    // Initialize team assignments for projects
    initializeData() {
      // Assign team members to projects
      this.projects[0]!.team = [this.teamMembers[0]!, this.teamMembers[1]!, this.teamMembers[3]!];
      this.projects[1]!.team = [this.teamMembers[0]!, this.teamMembers[4]!];
      this.projects[2]!.team = [this.teamMembers[1]!, this.teamMembers[2]!, this.teamMembers[5]!];
      this.projects[3]!.team = [this.teamMembers[0]!, this.teamMembers[4]!];
      this.projects[4]!.team = [this.teamMembers[1]!, this.teamMembers[2]!];
      this.projects[5]!.team = [this.teamMembers[4]!, this.teamMembers[5]!];
    },
  },
});
