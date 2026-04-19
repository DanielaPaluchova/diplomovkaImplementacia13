<template>
  <q-page class="bg-grey-1">
    <!-- Header Section -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center q-gutter-md">
        <div class="col">
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">
            Welcome back, {{ authStore.userName }}! 👋
          </h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Here's your project management overview</p>
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Project Management Overview -->
      <div class="q-mb-md">
        <div class="text-h6 text-weight-bold text-primary q-mb-sm">
          <q-icon name="folder" class="q-mr-sm" />
          Project Management Overview
        </div>
        <q-separator class="q-mb-md" />
      </div>

      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-purple-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-purple">{{ totalProjects }}</div>
                  <div class="text-caption text-grey-7">Total Projects</div>
                </div>
                <div class="col-auto">
                  <q-icon name="work" size="32px" class="text-purple" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="check_circle" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">{{ projectsOnTrack }}</span>
                <span class="text-caption text-grey-7 q-ml-xs">in progress</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-cyan-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-cyan">{{ averageProgress }}%</div>
                  <div class="text-caption text-grey-7">Average Progress</div>
                </div>
                <div class="col-auto">
                  <q-icon name="schedule" size="32px" class="text-cyan" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="insights" class="text-blue" size="16px" />
                <span class="text-caption q-ml-xs text-grey-7">across all projects</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-indigo-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-indigo">{{ totalTeamMembers }}</div>
                  <div class="text-caption text-grey-7">Team Members</div>
                </div>
                <div class="col-auto">
                  <q-icon name="group" size="32px" class="text-indigo" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="percent" class="text-blue" size="16px" />
                <span class="text-caption q-ml-xs text-blue">{{ averageWorkload }}%</span>
                <span class="text-caption text-grey-7 q-ml-xs">avg workload</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-teal-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-teal">{{ totalTasks }}</div>
                  <div class="text-caption text-grey-7">Total Tasks</div>
                </div>
                <div class="col-auto">
                  <q-icon name="assignment" size="32px" class="text-teal" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="check" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">{{ completedTasks }}</span>
                <span class="text-caption text-grey-7 q-ml-xs">completed</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <div class="row q-gutter-lg q-mb-lg">
        <!-- Active Projects -->
        <div class="col-12">
          <q-card>
            <q-card-section>
              <div class="row items-center q-mb-md">
                <div class="text-h6 text-weight-bold">
                  <q-icon name="work" class="q-mr-sm" />
                  Active Projects
                </div>
                <q-space />
                <q-btn flat dense icon="arrow_forward" @click="navigateTo('/projects')" />
              </div>

              <div class="projects-list">
                <div
                  v-for="project in activeProjects"
                  :key="project.id"
                  class="project-item q-mb-md"
                >
                  <div class="row items-center q-mb-xs">
                    <q-icon :name="project.icon" :color="project.color" size="sm" class="q-mr-sm" />
                    <div class="text-body2 text-weight-medium">{{ project.name }}</div>
                    <q-space />
                    <q-chip :color="getStatusColor(project.status)" text-color="white" size="xs">
                      {{ project.status }}
                    </q-chip>
                  </div>
                  <div class="row items-center">
                    <div class="col">
                      <q-linear-progress
                        :value="project.progress / 100"
                        :color="project.color"
                        size="6px"
                      />
                    </div>
                    <div class="text-caption text-grey-7 q-ml-sm">{{ project.progress }}%</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Quick Actions -->
      <q-card>
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">
            <q-icon name="bolt" class="q-mr-sm" />
            Quick Actions
          </div>

          <div class="row q-gutter-md">
            <div class="col-12 col-sm-6 col-md-4">
              <q-btn
                flat
                class="full-width q-pa-md action-btn"
                @click="navigateTo('/pert-analysis')"
              >
                <div class="column items-center">
                  <q-icon name="account_tree" color="purple" size="48px" class="q-mb-sm" />
                  <div class="text-weight-bold text-purple">PERT Analysis</div>
                  <div class="text-caption text-grey-7">Task estimation</div>
                </div>
              </q-btn>
            </div>

            <div class="col-12 col-sm-6 col-md-4">
              <q-btn flat class="full-width q-pa-md action-btn" @click="navigateTo('/raci-matrix')">
                <div class="column items-center">
                  <q-icon name="assignment_ind" color="blue" size="48px" class="q-mb-sm" />
                  <div class="text-weight-bold text-blue">RACI Matrix</div>
                  <div class="text-caption text-grey-7">Role assignment</div>
                </div>
              </q-btn>
            </div>

            <div class="col-12 col-sm-6 col-md-4">
              <q-btn
                flat
                class="full-width q-pa-md action-btn"
                @click="navigateTo('/pert-raci-optimization')"
              >
                <div class="column items-center">
                  <q-icon name="auto_awesome" color="primary" size="48px" class="q-mb-sm" />
                  <div class="text-weight-bold text-primary">PERT+RACI</div>
                  <div class="text-caption text-grey-7">Run optimization</div>
                </div>
              </q-btn>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'src/stores/auth-store';
import { useProjectStore } from 'src/stores/project-store';
import { useTeamStore } from 'src/stores/team-store';
import { useActivityLog } from 'src/composables/useActivityLog';

const router = useRouter();
const route = useRoute();
const $q = useQuasar();
const authStore = useAuthStore();
const projectStore = useProjectStore();
const teamStore = useTeamStore();
const { log } = useActivityLog();

// Check for access denied message and fetch data
onMounted(async () => {
  if (route.query.accessDenied === 'true') {
    $q.notify({
      message: 'Access Denied: You need Manager or Admin privileges to access that page.',
      color: 'negative',
      icon: 'block',
      position: 'top',
      timeout: 4000,
    });
    // Clear the query parameter
    router.replace({ query: {} });
  }

  // Fetch projects and team data
  await Promise.all([
    projectStore.fetchProjects(true), // Include details
    teamStore.fetchTeamMembers(),
  ]);
});

// Computed statistics from real data
const totalProjects = computed(() => projectStore.projects.length);

const projectsOnTrack = computed(() => {
  return projectStore.projects.filter((p) => p.status === 'In progress').length;
});

const averageProgress = computed(() => {
  if (projectStore.projects.length === 0) return 0;
  const total = projectStore.projects.reduce((sum, p) => sum + (p.progress || 0), 0);
  return Math.round(total / projectStore.projects.length);
});

const totalTeamMembers = computed(() => teamStore.teamMembers.length);

const averageWorkload = computed(() => {
  if (teamStore.teamMembers.length === 0) return 0;
  const total = teamStore.teamMembers.reduce((sum, m) => sum + (m.workload || 0), 0);
  return Math.round(total / teamStore.teamMembers.length);
});

const totalTasks = computed(() => {
  return projectStore.projects.reduce((sum, p) => {
    return sum + (p.totalTasks || 0); // Use backend-calculated value
  }, 0);
});

const completedTasks = computed(() => {
  return projectStore.projects.reduce((sum, p) => {
    return sum + (p.tasksCompleted || 0); // Use backend-calculated value
  }, 0);
});

// Active Projects - Get real data from project store
const activeProjects = computed(() => {
  return projectStore.projects
    .slice(0, 6) // Show max 6 projects
    .map((project) => {
      // Use backend-calculated progress value
      return {
        id: project.id,
        name: project.name,
        icon: project.icon || 'work',
        color: getProjectColor(project.status),
        progress: project.progress, // Backend now calculates this dynamically
        status: project.status || 'Not started',
      };
    });
});

function getProjectColor(status: string): string {
  switch (status) {
    case 'Not started':
      return 'grey';
    case 'In progress':
      return 'primary';
    case 'Completed':
      return 'green';
    default:
      return 'primary';
  }
}

// Helper functions
function navigateTo(path: string) {
  if (path === '/projects') log('navigate_to_projects', 'dashboard');
  else log('quick_action_click', 'dashboard', { details: { path } });
  router.push(path);
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
</script>

<style scoped>
.kpi-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  cursor: pointer;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.project-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  transition: background 0.2s;
}

.project-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.action-btn {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
