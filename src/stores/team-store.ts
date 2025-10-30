import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/services/api';

export interface TeamMember {
  id: number;
  name: string;
  email: string;
  role: string;
  systemRole?: string;
  avatar: string;
  status?: string;
  activeProjects?: number;
  skills: string[];
  availability?: boolean;
  workload: number;
  totalStoryPoints?: number;
  maxStoryPoints?: number;
}

export const useTeamStore = defineStore('team', () => {
  const teamMembers = ref<TeamMember[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Fetch all team members from API
  async function fetchTeamMembers() {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.get<TeamMember[]>('/teams');
      teamMembers.value = data;
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch team members';
      console.error('Failed to fetch team members:', err);
      return [];
    } finally {
      loading.value = false;
    }
  }

  // Get single team member
  async function getTeamMember(id: number): Promise<TeamMember | undefined> {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.get<TeamMember>(`/teams/${id}`);
      // Update in local state
      const index = teamMembers.value.findIndex((m) => m.id === id);
      if (index !== -1) {
        teamMembers.value[index] = data;
      }
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch team member';
      console.error('Failed to fetch team member:', err);
      return undefined;
    } finally {
      loading.value = false;
    }
  }

  // Create new team member
  async function addTeamMember(member: Omit<TeamMember, 'id'>) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.post<TeamMember>('/teams', member);
      teamMembers.value.push(data);
      return data.id;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to add team member';
      console.error('Failed to add team member:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Update team member
  async function updateTeamMember(id: number, updates: Partial<TeamMember>) {
    loading.value = true;
    error.value = null;
    try {
      const data = await api.put<TeamMember>(`/teams/${id}`, updates);
      const index = teamMembers.value.findIndex((m) => m.id === id);
      if (index !== -1) {
        teamMembers.value[index] = data;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update team member';
      console.error('Failed to update team member:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Delete team member
  async function removeTeamMember(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await api.delete(`/teams/${id}`);
      const index = teamMembers.value.findIndex((m) => m.id === id);
      if (index !== -1) {
        teamMembers.value.splice(index, 1);
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to remove team member';
      console.error('Failed to remove team member:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Local getters (no API calls)
  function getAvailableMembers(): TeamMember[] {
    return teamMembers.value.filter((m) => m.availability !== false);
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
    loading,
    error,
    fetchTeamMembers,
    getTeamMember,
    addTeamMember,
    updateTeamMember,
    removeTeamMember,
    deleteTeamMember: removeTeamMember, // Alias for consistency
    getAvailableMembers,
    getMembersByRole,
    updateMemberWorkload,
  };
});
