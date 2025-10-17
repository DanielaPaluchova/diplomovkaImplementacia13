import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface TeamMember {
  id: number;
  name: string;
  email: string;
  role: string;
  avatar: string;
  skills: string[];
  availability: boolean;
  workload: number;
  maxStoryPoints: number;
}

export const useTeamStore = defineStore('team', () => {
  // Global team members pool
  const teamMembers = ref<TeamMember[]>([
    {
      id: 1,
      name: 'John Smith',
      email: 'john.smith@example.com',
      role: 'Frontend Developer',
      avatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
      skills: ['Vue.js', 'TypeScript', 'CSS', 'Quasar'],
      availability: true,
      workload: 75,
      maxStoryPoints: 20,
    },
    {
      id: 2,
      name: 'Sarah Johnson',
      email: 'sarah.johnson@example.com',
      role: 'Backend Developer',
      avatar: 'https://cdn.quasar.dev/img/avatar2.jpg',
      skills: ['Node.js', 'Python', 'PostgreSQL', 'AWS'],
      availability: false,
      workload: 90,
      maxStoryPoints: 20,
    },
    {
      id: 3,
      name: 'Mike Wilson',
      email: 'mike.wilson@example.com',
      role: 'UI/UX Designer',
      avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
      skills: ['Figma', 'Adobe XD', 'Sketch', 'Prototyping'],
      availability: true,
      workload: 60,
      maxStoryPoints: 20,
    },
    {
      id: 4,
      name: 'Emma Davis',
      email: 'emma.davis@example.com',
      role: 'Project Manager',
      avatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
      skills: ['Agile', 'Scrum', 'JIRA', 'Communication'],
      availability: true,
      workload: 45,
      maxStoryPoints: 20,
    },
    {
      id: 5,
      name: 'David Brown',
      email: 'david.brown@example.com',
      role: 'QA Engineer',
      avatar: 'https://cdn.quasar.dev/img/avatar5.jpg',
      skills: ['Testing', 'Selenium', 'Jest', 'Cypress'],
      availability: true,
      workload: 70,
      maxStoryPoints: 20,
    },
    {
      id: 6,
      name: 'Lisa Anderson',
      email: 'lisa.anderson@example.com',
      role: 'DevOps Engineer',
      avatar: 'https://cdn.quasar.dev/img/avatar6.jpg',
      skills: ['Docker', 'Kubernetes', 'CI/CD', 'AWS'],
      availability: true,
      workload: 55,
      maxStoryPoints: 20,
    },
  ]);

  // Actions
  function addTeamMember(member: Omit<TeamMember, 'id'>) {
    const newId = Math.max(...teamMembers.value.map((m) => m.id), 0) + 1;
    teamMembers.value.push({
      ...member,
      id: newId,
    });
    return newId;
  }

  function updateTeamMember(id: number, updates: Partial<TeamMember>) {
    const index = teamMembers.value.findIndex((m) => m.id === id);
    if (index !== -1) {
      const existingMember = teamMembers.value[index]!;
      teamMembers.value[index] = {
        id: existingMember.id,
        name: updates.name ?? existingMember.name,
        email: updates.email ?? existingMember.email,
        role: updates.role ?? existingMember.role,
        avatar: updates.avatar ?? existingMember.avatar,
        skills: updates.skills ?? existingMember.skills,
        availability: updates.availability ?? existingMember.availability,
        workload: updates.workload ?? existingMember.workload,
        maxStoryPoints: updates.maxStoryPoints ?? existingMember.maxStoryPoints,
      };
    }
  }

  function removeTeamMember(id: number) {
    const index = teamMembers.value.findIndex((m) => m.id === id);
    if (index !== -1) {
      teamMembers.value.splice(index, 1);
    }
  }

  function getTeamMember(id: number): TeamMember | undefined {
    return teamMembers.value.find((m) => m.id === id);
  }

  function getAvailableMembers(): TeamMember[] {
    return teamMembers.value.filter((m) => m.availability);
  }

  function getMembersByRole(role: string): TeamMember[] {
    return teamMembers.value.filter((m) => m.role === role);
  }

  function updateMemberWorkload(id: number, workload: number) {
    const member = teamMembers.value.find((m) => m.id === id);
    if (member) {
      member.workload = Math.min(Math.max(workload, 0), 100);
    }
  }

  return {
    teamMembers,
    addTeamMember,
    updateTeamMember,
    removeTeamMember,
    getTeamMember,
    getAvailableMembers,
    getMembersByRole,
    updateMemberWorkload,
  };
});
