import { defineStore } from 'pinia';

export interface TeamMember {
  id: number;
  name: string;
  role: string; // Team role (e.g. "Frontend Developer")
  systemRole?: 'admin' | 'manager' | 'developer' | 'viewer'; // Permission role
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
        systemRole: 'manager' as const,
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
        name: 'PERT+RACI vs Traditional Planning',
        description:
          'Comparing integrated PERT+RACI approach with traditional planning methods across 10 projects',
        hypothesis:
          'PERT+RACI integration will improve delivery accuracy by 25% and reduce team conflicts by 30%',
        status: 'completed' as const,
        methodology: 'PERT+RACI vs Traditional',
        startDate: new Date('2023-10-01'),
        endDate: new Date('2023-12-15'),
        participants: 50,
        results: {
          success: true,
          improvement: 28,
          confidence: 93,
        },
      },
      {
        id: 2,
        name: 'Automatic Workload Rebalancing',
        description:
          'Testing automatic RACI reassignment when team members are overloaded (>80% workload)',
        hypothesis:
          'Automatic rebalancing will maintain team utilization under 80% while preserving project deadlines',
        status: 'running' as const,
        methodology: 'Load Balancing Comparison',
        startDate: new Date('2023-11-15'),
        endDate: new Date('2024-01-30'),
        participants: 35,
      },
      {
        id: 3,
        name: 'Requirement Change Adaptation',
        description:
          'Simulating 50 client requirement changes and measuring system adaptation speed and accuracy',
        hypothesis:
          'System will adapt to requirement changes in <5 seconds while maintaining optimal PERT+RACI balance',
        status: 'running' as const,
        methodology: 'Controlled Experiment',
        startDate: new Date('2024-01-05'),
        endDate: new Date('2024-02-05'),
        participants: 25,
      },
      {
        id: 4,
        name: 'Risk-Based PERT Optimization',
        description:
          'Comparing traditional PERT with risk-adjusted PERT (factoring in team overload)',
        hypothesis: 'Risk-aware PERT will reduce project delays by 40% compared to standard PERT',
        status: 'completed' as const,
        methodology: 'Risk-based Adaptation',
        startDate: new Date('2023-09-01'),
        endDate: new Date('2023-11-30'),
        participants: 45,
        results: {
          success: true,
          improvement: 43,
          confidence: 89,
        },
      },
      {
        id: 5,
        name: 'Multi-Project RACI Conflicts',
        description:
          'Identifying and resolving RACI role conflicts when team members work across multiple projects',
        hypothesis: 'Automated conflict detection will reduce role confusion by 60%',
        status: 'planning' as const,
        methodology: 'Before/After Study',
        startDate: new Date('2024-02-01'),
        endDate: new Date('2024-04-01'),
        participants: 40,
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

    addTeamMember(member: Omit<TeamMember, 'id' | 'avatar' | 'status' | 'activeProjects'>) {
      const newMember: TeamMember = {
        id: this.teamMembers.length + 1,
        name: member.name,
        role: member.role,
        avatar: `https://cdn.quasar.dev/img/avatar${(this.teamMembers.length % 6) + 1}.jpg`,
        status: 'online',
        activeProjects: 0,
        workload: member.workload,
        skills: member.skills,
        email: member.email,
      };
      this.teamMembers.push(newMember);
      return newMember;
    },
  },
});
