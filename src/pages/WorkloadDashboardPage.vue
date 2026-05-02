<template>
  <q-page class="bg-grey-1">
    <!-- Header Section -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center q-gutter-md">
        <div class="col">
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">
            Cross-Project Workload Dashboard
          </h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Monitor team member workload across all projects and sprints
          </p>
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Summary Cards -->
      <div class="summary-grid q-mb-lg">
        <div>
          <q-card class="summary-card">
            <q-card-section>
              <div class="text-h6 text-weight-bold text-primary">{{ totalTeamMembers }}</div>
              <div class="text-caption text-grey-7">Team Members with Projects</div>
            </q-card-section>
          </q-card>
        </div>
        <div>
          <q-card class="summary-card">
            <q-card-section>
              <div class="text-h6 text-weight-bold text-orange">{{ overloadedMembers }}</div>
              <div class="text-caption text-grey-7">Overloaded Members (&gt;80%)</div>
            </q-card-section>
          </q-card>
        </div>
        <div>
          <q-card class="summary-card">
            <q-card-section>
              <div class="text-h6 text-weight-bold text-blue">{{ averageWorkload }}%</div>
              <div class="text-caption text-grey-7">Average Workload</div>
            </q-card-section>
          </q-card>
        </div>
        <div>
          <q-card class="summary-card" :class="{ 'cursor-pointer': membersWithoutProjects > 0 }" @click="showUnassignedMembers">
            <q-card-section>
              <div class="text-h6 text-weight-bold text-grey-7">{{ membersWithoutProjects }}</div>
              <div class="text-caption text-grey-7">Members Without Projects</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Info Banner for Unassigned Members -->
      <q-banner v-if="membersWithoutProjects > 0" class="bg-info text-white q-mb-lg" rounded>
        <template v-slot:avatar>
          <q-icon name="info" />
        </template>
        <div class="text-body2">
          <strong>{{ membersWithoutProjects }}</strong> team member(s) are not assigned to any project and won't appear in the workload view below.
          <q-btn 
            flat 
            dense 
            color="white" 
            label="View Unassigned" 
            class="q-ml-sm"
            @click="showUnassignedMembers"
          />
        </div>
      </q-banner>

      <!-- Cross-Project Sprint Overview -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="row items-center q-mb-md">
            <div class="text-h6 text-weight-bold">
              <q-icon name="event_note" class="q-mr-sm" />
              Active Sprints Overview
            </div>
            <q-space />
            <q-chip color="green" text-color="white" icon="play_circle">
              {{ activeSprintsCount }} Active
            </q-chip>
          </div>

          <div class="sprint-overview-grid">
            <div
              v-for="sprint in activeSprintsOverview"
              :key="sprint.id"
            >
              <q-card flat bordered class="sprint-overview-card">
                <q-card-section class="bg-green-1">
                  <div class="row items-center">
                    <q-icon name="play_circle" color="green" size="sm" class="q-mr-sm" />
                    <div class="col">
                      <div class="text-weight-bold">{{ sprint.projectName }}</div>
                      <div class="text-caption text-grey-7">{{ sprint.sprintName }}</div>
                    </div>
                  </div>
                </q-card-section>

                <q-card-section>
                  <div class="row items-center q-mb-sm">
                    <q-icon name="event" size="xs" class="q-mr-xs text-grey-6" />
                    <span class="text-caption text-grey-7">
                      {{ formatDate(sprint.startDate) }} - {{ formatDate(sprint.endDate) }}
                    </span>
                  </div>

                  <div class="row q-gutter-sm q-mb-md">
                    <div class="col">
                      <div class="text-caption text-grey-7">Total Tasks</div>
                      <div class="text-h6 text-primary text-weight-bold">
                        {{ sprint.totalTasks }}
                      </div>
                    </div>
                    <div class="col">
                      <div class="text-caption text-grey-7">Completed Tasks</div>
                      <div class="text-h6 text-green text-weight-bold">
                        {{ sprint.completedTasks }}
                      </div>
                    </div>
                    <div class="col">
                      <div class="text-caption text-grey-7">Remaining Tasks</div>
                      <div class="text-h6 text-orange text-weight-bold">
                        {{ sprint.remainingTasks }}
                      </div>
                    </div>
                  </div>

                  <q-linear-progress
                    :value="sprint.totalTasks > 0 ? sprint.completedTasks / sprint.totalTasks : 0"
                    color="green"
                    size="8px"
                    class="q-mb-md rounded-borders"
                  />

                  <div class="text-caption text-grey-7 q-mb-xs">Team Members</div>
                  <div class="row q-gutter-xs">
                    <q-avatar
                      v-for="member in sprint.teamMembers.slice(0, 5)"
                      :key="member.id"
                      size="28px"
                    >
                      <img :src="member.avatar" />
                      <q-tooltip>{{ member.name }} ({{ member.storyPoints }} SP)</q-tooltip>
                    </q-avatar>
                    <q-chip
                      v-if="sprint.teamMembers.length > 5"
                      size="sm"
                      dense
                      color="grey-3"
                      text-color="grey-8"
                    >
                      +{{ sprint.teamMembers.length - 5 }}
                    </q-chip>
                  </div>
                </q-card-section>

                <q-separator />

                <q-card-actions>
                  <q-btn
                    flat
                    color="primary"
                    icon="visibility"
                    label="View Sprint"
                    size="sm"
                    @click="navigateToProject(sprint.projectId)"
                  />
                </q-card-actions>
              </q-card>
            </div>

            <div v-if="activeSprintsOverview.length === 0" class="grid-empty">
              <div class="text-center text-grey-6 q-pa-lg">
                <q-icon name="event_busy" size="48px" class="q-mb-sm" />
                <div class="text-body1">No active sprints at the moment</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Filters -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="row q-gutter-md items-center">
            <div class="col-12 col-md-3">
              <q-input v-model="searchQuery" placeholder="Search members..." outlined dense>
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-3">
              <q-select
                v-model="roleFilter"
                :options="roleOptions"
                label="Filter by Role"
                outlined
                dense
                clearable
              />
            </div>
            <div class="col-12 col-md-3">
              <q-select
                v-model="workloadFilter"
                :options="workloadOptions"
                label="Filter by Workload"
                outlined
                dense
                clearable
              />
            </div>
            <div class="col-12 col-md-3">
              <q-select
                v-model="projectFilter"
                :options="projectOptions"
                option-label="name"
                option-value="id"
                label="Filter by Project"
                outlined
                dense
                clearable
                emit-value
                map-options
              />
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Team Member Workload Cards -->
      <div class="workload-members-grid">
        <div v-for="member in filteredMembers" :key="member.id">
          <q-card class="workload-card">
            <q-card-section>
              <!-- Member Header -->
              <div class="row items-center q-mb-md">
                <q-avatar size="48px" class="q-mr-md">
                  <img :src="member.avatar" />
                </q-avatar>
                <div class="col">
                  <div class="text-h6 text-weight-bold">{{ member.name }}</div>
                  <div class="text-caption text-grey-7">{{ member.role }}</div>
                </div>
                <q-badge
                  :color="getWorkloadColor(member.totalWorkload)"
                  :label="`${member.totalWorkload}%`"
                  class="text-weight-bold"
                />
              </div>

              <!-- Overall Workload -->
              <div class="q-mb-md">
                <div class="row items-center q-mb-xs">
                  <span class="text-caption text-grey-7">Overall Workload</span>
                  <q-space />
                  <span class="text-caption text-weight-bold">
                    {{ member.totalStoryPoints }}/{{ member.maxStoryPoints }} SP
                  </span>
                </div>
                <q-linear-progress
                  :value="Math.min(1, member.totalWorkload / 100)"
                  :color="getWorkloadColor(member.totalWorkload)"
                  size="12px"
                  class="rounded-borders"
                />
              </div>

              <!-- Projects Breakdown -->
              <div class="q-mb-md">
                <div class="text-caption text-grey-7 q-mb-sm">
                  Projects ({{ member.projects.length }})
                </div>
                <div v-for="project in member.projects" :key="project.id" class="q-mb-sm">
                  <div class="row items-center q-mb-xs">
                    <q-icon :name="project.icon" size="xs" class="q-mr-xs" />
                    <span class="text-caption">{{ project.name }}</span>
                    <q-space />
                    <span class="text-caption text-weight-medium">
                      {{ project.storyPoints }} SP
                      <span
                        class="text-grey-6"
                        v-if="project.totalStoryPoints !== project.storyPoints"
                      >
                        ({{ project.totalStoryPoints }} total)
                      </span>
                    </span>
                  </div>
                  <q-linear-progress
                    :value="project.storyPoints / member.maxStoryPoints"
                    color="primary"
                    size="4px"
                  />
                </div>
              </div>

              <!-- Active Sprints -->
              <div class="q-mb-md">
                <div class="text-caption text-grey-7 q-mb-sm">
                  Active Sprints ({{ member.activeSprints }})
                </div>
                <div class="row q-gutter-xs">
                  <q-chip
                    v-for="sprint in member.sprintDetails"
                    :key="sprint.id"
                    size="sm"
                    color="blue-1"
                    text-color="blue-9"
                    dense
                  >
                    {{ sprint.name }}
                  </q-chip>
                </div>
              </div>

              <!-- Skills -->
              <div>
                <div class="text-caption text-grey-7 q-mb-sm">Skills</div>
                <div class="row q-gutter-xs">
                  <q-chip
                    v-for="skill in member.skills"
                    :key="skill"
                    size="sm"
                    outline
                    color="primary"
                    dense
                  >
                    {{ skill }}
                  </q-chip>
                </div>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-actions>
              <q-btn
                flat
                color="primary"
                icon="visibility"
                label="View Details"
                @click="viewMemberDetails(member)"
              />
            </q-card-actions>
          </q-card>
        </div>

        <!-- Empty State -->
        <div v-if="filteredMembers.length === 0" class="grid-empty">
          <q-card class="text-center q-pa-xl">
            <q-icon name="people_off" size="64px" class="text-grey-5 q-mb-md" />
            <div class="text-h6 text-grey-7 q-mb-sm">No team members found</div>
            <div class="text-caption text-grey-6">Try adjusting your filters</div>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Member Details Dialog -->
    <q-dialog v-model="showDetailsDialog" persistent>
      <q-card style="min-width: 700px; max-width: 900px">
        <q-card-section>
          <div class="row items-center">
            <q-avatar size="64px" class="q-mr-md">
              <img :src="selectedMember?.avatar || ''" />
            </q-avatar>
            <div class="col">
              <div class="text-h5 text-weight-bold">{{ selectedMember?.name }}</div>
              <div class="text-caption text-grey-7">{{ selectedMember?.role }}</div>
            </div>
            <q-btn flat round icon="close" v-close-popup />
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-tabs v-model="detailsTab" dense class="text-grey" active-color="primary">
            <q-tab name="workload" label="Workload" />
            <q-tab name="projects" label="Projects" />
            <q-tab name="tasks" label="Tasks" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="detailsTab" animated>
            <q-tab-panel name="workload">
              <div class="text-h6 q-mb-md">Workload Distribution</div>
              <div class="q-mb-lg">
                <div class="text-caption text-grey-7 q-mb-sm">Total Capacity</div>
                <q-linear-progress
                  :value="
                    (selectedMember?.totalStoryPoints || 0) / (selectedMember?.maxStoryPoints || 20)
                  "
                  :color="getWorkloadColor(selectedMember?.totalWorkload || 0)"
                  size="20px"
                  class="rounded-borders"
                >
                  <div class="absolute-full flex flex-center">
                    <div class="text-weight-bold text-white">
                      {{ selectedMember?.totalStoryPoints }}/{{ selectedMember?.maxStoryPoints }} SP
                      ({{ selectedMember?.totalWorkload }}%)
                    </div>
                  </div>
                </q-linear-progress>
              </div>

              <div class="text-h6 q-mb-md">By Project</div>
              <q-list bordered separator>
                <q-item v-for="project in selectedMember?.projects" :key="project.id">
                  <q-item-section avatar>
                    <q-icon :name="project.icon" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ project.name }}</q-item-label>
                    <q-item-label caption>
                      Current Sprint: {{ project.storyPoints }} SP
                      <span v-if="project.totalStoryPoints !== project.storyPoints">
                        | Total: {{ project.totalStoryPoints }} SP
                      </span>
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-linear-progress
                      :value="project.storyPoints / (selectedMember?.maxStoryPoints || 20)"
                      color="primary"
                      size="8px"
                      style="width: 100px"
                    />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>

            <q-tab-panel name="projects">
              <div class="text-h6 q-mb-md">Active Projects</div>
              <q-list bordered separator>
                <q-item
                  v-for="project in selectedMember?.projects"
                  :key="project.id"
                  clickable
                  @click="navigateToProject(project.id)"
                >
                  <q-item-section avatar>
                    <q-avatar :icon="project.icon" color="primary" text-color="white" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ project.name }}</q-item-label>
                    <q-item-label caption>Role: {{ project.role }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-chip :color="getStatusColor(project.status)" text-color="white" size="sm">
                      {{ project.status }}
                    </q-chip>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>

            <q-tab-panel name="tasks">
              <div class="text-h6 q-mb-md">Assigned Tasks</div>
              <q-list bordered separator>
                <q-item v-for="task in selectedMember?.tasks" :key="task.id">
                  <q-item-section avatar>
                    <q-checkbox :model-value="task.completed" disable />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ task.name }}</q-item-label>
                    <q-item-label caption
                      >{{ task.projectName }} - {{ task.sprintName }}</q-item-label
                    >
                  </q-item-section>
                  <q-item-section side>
                    <q-chip :color="getPriorityColor(task.priority)" text-color="white" size="sm">
                      {{ task.priority }}
                    </q-chip>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>
          </q-tab-panels>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Unassigned Members Dialog -->
    <q-dialog v-model="showUnassignedDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Team Members Without Projects</div>
          <div class="text-caption text-grey-7">
            These members are not assigned to any project yet
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-pt-none">
          <q-list bordered separator>
            <q-item v-for="member in unassignedMembersList" :key="member.id">
              <q-item-section avatar>
                <q-avatar>
                  <img :src="member.avatar" />
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ member.name }}</q-item-label>
                <q-item-label caption>{{ member.email }}</q-item-label>
                <q-item-label caption class="q-mt-xs">
                  <q-badge outline color="primary">{{ member.role }}</q-badge>
                  <q-badge 
                    v-for="skill in member.skills.slice(0, 3)" 
                    :key="skill" 
                    outline 
                    color="grey" 
                    class="q-ml-xs"
                  >
                    {{ skill }}
                  </q-badge>
                  <q-badge 
                    v-if="member.skills.length > 3" 
                    outline 
                    color="grey" 
                    class="q-ml-xs"
                  >
                    +{{ member.skills.length - 3 }}
                  </q-badge>
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <div class="q-mt-md text-caption text-grey-7">
            <q-icon name="info" size="xs" class="q-mr-xs" />
            To assign members to projects, go to Projects page and add them to a project team.
          </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <q-btn flat color="primary" label="Go to Projects" @click="router.push('/projects')" />
          <q-btn flat label="Close" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { format } from 'date-fns';
import { useRouter } from 'vue-router';
import { useTeamStore } from 'src/stores/team-store';
import { useProjectStore } from 'src/stores/project-store';

const router = useRouter();
const teamStore = useTeamStore();
const projectStore = useProjectStore();

// Fetch data from API
onMounted(async () => {
  await Promise.all([teamStore.fetchTeamMembers(), projectStore.fetchProjects(true)]);
});

// Reactive data
const searchQuery = ref('');
const roleFilter = ref<string | null>(null);
const workloadFilter = ref<string | null>(null);
const projectFilter = ref<number | null>(null);
const showDetailsDialog = ref(false);
const selectedMember = ref<MemberWorkload | null>(null);
const detailsTab = ref('workload');

interface ProjectWorkload {
  id: number;
  name: string;
  icon: string;
  storyPoints: number; // Current sprint SP
  totalStoryPoints: number; // Total project SP
  role: string;
  status: string;
}

interface SprintDetail {
  id: number;
  name: string;
}

interface TaskDetail {
  id: number;
  name: string;
  projectName: string;
  sprintName: string;
  priority: string;
  completed: boolean;
}

interface MemberWorkload {
  id: number;
  name: string;
  email: string;
  role: string;
  avatar: string;
  skills: string[];
  totalWorkload: number;
  totalStoryPoints: number;
  maxStoryPoints: number;
  projects: ProjectWorkload[];
  activeSprints: number;
  sprintDetails: SprintDetail[];
  tasks: TaskDetail[];
}

const roleOptions = [
  'Frontend Developer',
  'Backend Developer',
  'UI/UX Designer',
  'Project Manager',
  'QA Engineer',
  'DevOps Engineer',
];

const workloadOptions = ['Available (< 60%)', 'Normal (60-80%)', 'Overloaded (> 80%)'];

// Computed
const projectOptions = computed(() => projectStore.projects);

const membersWithWorkload = computed((): MemberWorkload[] => {
  return teamStore.teamMembers
    .map((member) => {
      const maxStoryPoints = member.maxStoryPoints || 20;

      // Calculate project-level breakdown
      const memberProjects: ProjectWorkload[] = [];
      projectStore.projects.forEach((project) => {
        if (project.teamMemberIds && project.teamMemberIds.includes(member.id)) {
          const memberRole = projectStore.getMemberRole(project.id, member.id);

          // Get active sprint for this project
          const activeSprint = projectStore.getActiveSprint(project.id);

          // Calculate story points for CURRENT SPRINT only (including Done - Sprint Commitment)
          let sprintStoryPoints = 0;
          if (project.tasks && activeSprint) {
            const sprintTasks = project.tasks.filter((task) => {
              const isInSprint = task.sprintId === activeSprint.id;
              const isAssigned = task.raci?.responsible && task.raci.responsible.includes(member.id);
              return isInSprint && isAssigned;
            });
            sprintStoryPoints = sprintTasks.reduce((sum, task) => sum + (task.storyPoints || 0), 0);
          }

          // Calculate TOTAL story points (all tasks in project including Done)
          let totalStoryPoints = 0;
          if (project.tasks) {
            const allTasks = project.tasks.filter((task) => {
              const isAssigned = task.raci?.responsible && task.raci.responsible.includes(member.id);
              return isAssigned;
            });
            totalStoryPoints = allTasks.reduce((sum, task) => sum + (task.storyPoints || 0), 0);
          }

          if (sprintStoryPoints > 0 || totalStoryPoints > 0 || memberRole) {
            memberProjects.push({
              id: project.id,
              name: project.name,
              icon: project.icon,
              storyPoints: sprintStoryPoints,
              totalStoryPoints,
              role: memberRole?.role || 'developer',
              status: project.status,
            });
          }
        }
      });

      // Calculate overall workload based on SUM of sprint story points from all projects
      const totalStoryPoints = memberProjects.reduce(
        (sum, project) => sum + project.storyPoints,
        0,
      );
      const totalWorkload =
        maxStoryPoints > 0 ? Math.round((totalStoryPoints / maxStoryPoints) * 100) : 0;

      // Get active sprints
      const activeSprints = projectStore.projects.filter(
        (p) =>
          p.teamMemberIds &&
          p.teamMemberIds.includes(member.id) &&
          projectStore.getActiveSprint(p.id),
      );

      const sprintDetails: SprintDetail[] = activeSprints
        .map((p) => {
          const sprint = projectStore.getActiveSprint(p.id);
          return sprint ? { id: sprint.id, name: sprint.name } : null;
        })
        .filter((s): s is SprintDetail => s !== null);

      // Get all tasks assigned to this member (not just active sprints)
      const tasks: TaskDetail[] = [];
      projectStore.projects.forEach((project) => {
        if (project.tasks && project.teamMemberIds?.includes(member.id)) {
          const memberTasks = project.tasks.filter((task) => {
            const isAssigned = task.raci?.responsible && task.raci.responsible.includes(member.id);
            return isAssigned;
          });

          memberTasks.forEach((task) => {
            const sprint = project.sprints?.find((s) => s.id === task.sprintId);
            tasks.push({
              id: task.id,
              name: task.name || task.title,
              projectName: project.name,
              sprintName: sprint?.name || 'Backlog',
              priority: typeof task.priority === 'string' ? task.priority : 'Medium',
              completed: task.status === 'Done',
            });
          });
        }
      });

      return {
        id: member.id,
        name: member.name,
        email: member.email,
        role: member.role,
        avatar: member.avatar,
        skills: member.skills,
        totalWorkload,
        totalStoryPoints,
        maxStoryPoints,
        projects: memberProjects,
        activeSprints: activeSprints.length,
        sprintDetails,
        tasks,
      };
    })
    .filter((member) => member.projects.length > 0); // Only show members with project assignments
});

const filteredMembers = computed(() => {
  let filtered = [...membersWithWorkload.value];

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(
      (m) =>
        m.name.toLowerCase().includes(query) ||
        m.email.toLowerCase().includes(query) ||
        m.role.toLowerCase().includes(query),
    );
  }

  // Role filter
  if (roleFilter.value) {
    filtered = filtered.filter((m) => m.role === roleFilter.value);
  }

  // Workload filter
  if (workloadFilter.value) {
    if (workloadFilter.value === 'Available (< 60%)') {
      filtered = filtered.filter((m) => m.totalWorkload < 60);
    } else if (workloadFilter.value === 'Normal (60-80%)') {
      filtered = filtered.filter((m) => m.totalWorkload >= 60 && m.totalWorkload <= 80);
    } else if (workloadFilter.value === 'Overloaded (> 80%)') {
      filtered = filtered.filter((m) => m.totalWorkload > 80);
    }
  }

  // Project filter
  if (projectFilter.value) {
    filtered = filtered.filter((m) => m.projects.some((p) => p.id === projectFilter.value));
  }

  return filtered;
});

const totalTeamMembers = computed(() => membersWithWorkload.value.length);

const overloadedMembers = computed(
  () => membersWithWorkload.value.filter((m) => m.totalWorkload > 80).length,
);

const averageWorkload = computed(() => {
  if (membersWithWorkload.value.length === 0) return 0;
  const total = membersWithWorkload.value.reduce((sum, m) => sum + m.totalWorkload, 0);
  return Math.round(total / membersWithWorkload.value.length);
});

// Active sprints overview
interface SprintOverview {
  id: number;
  projectId: number;
  projectName: string;
  sprintName: string;
  startDate: Date;
  endDate: Date;
  totalTasks: number;
  completedTasks: number;
  remainingTasks: number;
  teamMembers: {
    id: number;
    name: string;
    avatar: string;
    storyPoints: number;
  }[];
}

const activeSprintsOverview = computed((): SprintOverview[] => {
  const sprints: SprintOverview[] = [];

  projectStore.projects.forEach((project) => {
    const activeSprint = projectStore.getActiveSprint(project.id);
    if (activeSprint && project.teamMemberIds) {
      // Get team members for this sprint
      const teamMembers = project.teamMemberIds
        .map((memberId) => {
          const member = teamStore.teamMembers.find((tm) => tm.id === memberId);
          if (!member) return null;

          // Calculate story points from actual tasks in this sprint assigned to this member
          let storyPoints = 0;
          if (project.tasks) {
            const memberTasks = project.tasks.filter((task) => {
              const isInSprint = task.sprintId === activeSprint.id;
              const isAssigned = task.raci?.responsible && task.raci.responsible.includes(member.id);
              return isInSprint && isAssigned;
            });
            storyPoints = memberTasks.reduce((sum, task) => sum + (task.storyPoints || 0), 0);
          }

          return {
            id: member.id,
            name: member.name,
            avatar: member.avatar,
            storyPoints,
          };
        })
        .filter((m): m is NonNullable<typeof m> => m !== null);

      // Calculate tasks dynamically from actual task array
      const sprintTasks = project.tasks?.filter((task) => task.sprintId === activeSprint.id) || [];
      const totalTasks = sprintTasks.length;
      const completedTasks = sprintTasks.filter((task) => task.status === 'Done').length;
      const remainingTasks = totalTasks - completedTasks;

      sprints.push({
        id: activeSprint.id,
        projectId: project.id,
        projectName: project.name,
        sprintName: activeSprint.name,
        startDate:
          typeof activeSprint.startDate === 'string'
            ? new Date(activeSprint.startDate)
            : activeSprint.startDate,
        endDate:
          typeof activeSprint.endDate === 'string'
            ? new Date(activeSprint.endDate)
            : activeSprint.endDate,
        totalTasks,
        completedTasks,
        remainingTasks,
        teamMembers,
      });
    }
  });

  return sprints;
});

const activeSprintsCount = computed(() => activeSprintsOverview.value.length);

// Members without projects
const membersWithoutProjects = computed(() => {
  return teamStore.teamMembers.filter((member) => {
    const hasProjects = projectStore.projects.some(
      (project) => project.teamMemberIds && project.teamMemberIds.includes(member.id)
    );
    return !hasProjects;
  }).length;
});

const unassignedMembersList = computed(() => {
  return teamStore.teamMembers.filter((member) => {
    const hasProjects = projectStore.projects.some(
      (project) => project.teamMemberIds && project.teamMemberIds.includes(member.id)
    );
    return !hasProjects;
  });
});

const showUnassignedDialog = ref(false);

// Methods
function formatDate(date: Date): string {
  return format(date, 'MMM dd, yyyy');
}
function getWorkloadColor(workload: number): string {
  if (workload > 80) return 'red';
  if (workload > 60) return 'orange';
  return 'green';
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'Not started':
      return 'grey';
    case 'In progress':
      return 'blue';
    case 'Completed':
      return 'green';
    default:
      return 'grey';
  }
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'High':
      return 'red';
    case 'Medium':
      return 'orange';
    case 'Low':
      return 'blue';
    default:
      return 'grey';
  }
}

function viewMemberDetails(member: MemberWorkload) {
  selectedMember.value = member;
  showDetailsDialog.value = true;
}

function navigateToProject(projectId: number) {
  showDetailsDialog.value = false;
  router.push(`/projects/${projectId}`);
}

function showUnassignedMembers() {
  if (membersWithoutProjects.value > 0) {
    showUnassignedDialog.value = true;
  }
}
</script>

<style scoped>
.summary-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.summary-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.cursor-pointer {
  cursor: pointer;
}

.workload-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  height: 100%;
}

.workload-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.rounded-borders {
  border-radius: 8px;
}

.sprint-overview-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.sprint-overview-card {
  border-left: 4px solid #21ba45;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.sprint-overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.workload-members-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
}

.grid-empty {
  grid-column: 1 / -1;
}

@media (max-width: 1240px) {
  .sprint-overview-grid,
  .workload-members-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1023px) {
  .summary-grid,
  .sprint-overview-grid,
  .workload-members-grid {
    grid-template-columns: 1fr;
  }
}
</style>
