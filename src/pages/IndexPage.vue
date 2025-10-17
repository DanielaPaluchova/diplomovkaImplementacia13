<template>
  <q-page class="bg-grey-1">
    <!-- Header Section -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center q-gutter-md">
        <div class="col">
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Welcome back, Daniela! 👋</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Here's what's happening with your projects today
          </p>
        </div>
        <div class="col-auto">
          <q-btn
            color="primary"
            icon="folder"
            label="View All Projects"
            unelevated
            class="q-px-lg"
            @click="navigateToProjects"
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- KPI Cards Row -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3" v-for="kpi in kpiCards" :key="kpi.title">
          <q-card class="kpi-card" :class="`bg-${kpi.color}-1`">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h6 text-weight-bold" :class="`text-${kpi.color}`">
                    {{ kpi.value }}
                  </div>
                  <div class="text-caption text-grey-7">{{ kpi.title }}</div>
                </div>
                <div class="col-auto">
                  <q-icon :name="kpi.icon" size="32px" :class="`text-${kpi.color}`" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon
                  :name="kpi.trend === 'up' ? 'trending_up' : 'trending_down'"
                  :class="kpi.trend === 'up' ? 'text-green' : 'text-red'"
                  size="16px"
                />
                <span
                  class="text-caption q-ml-xs"
                  :class="kpi.trend === 'up' ? 'text-green' : 'text-red'"
                >
                  {{ kpi.change }}
                </span>
                <span class="text-caption text-grey-7 q-ml-xs">vs last week</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Main Content Row -->
      <div class="row q-gutter-lg">
        <!-- Left Column -->
        <div class="col-12 col-lg-8">
          <!-- Active Projects -->
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="row items-center">
                <div class="text-h6 text-weight-bold">Active Projects</div>
                <q-space />
                <q-btn flat color="primary" label="View All" @click="navigateToProjects" />
              </div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-pa-none">
              <q-list>
                <q-item
                  v-for="project in activeProjects.slice(0, 3)"
                  :key="project.id"
                  clickable
                  class="q-pa-md"
                  @click="navigateToProject(project.id)"
                >
                  <q-item-section avatar>
                    <q-avatar :color="project.color" text-color="white" :icon="project.icon" />
                  </q-item-section>

                  <q-item-section>
                    <q-item-label class="text-weight-medium">
                      {{ project.name }}
                    </q-item-label>
                    <q-item-label caption>
                      {{ project.description }}
                    </q-item-label>
                    <div class="q-mt-sm">
                      <q-linear-progress
                        :value="project.progress / 100"
                        :color="project.color"
                        class="q-mt-xs"
                      />
                      <div class="row items-center q-mt-xs">
                        <span class="text-caption text-grey-7">
                          {{ project.tasksCompleted }}/{{ project.totalTasks }} tasks
                        </span>
                        <q-space />
                        <q-chip
                          :color="getStatusColor(project.status)"
                          text-color="white"
                          size="sm"
                          dense
                        >
                          {{ project.status }}
                        </q-chip>
                      </div>
                    </div>
                  </q-item-section>

                  <q-item-section side>
                    <div class="text-caption text-grey-7">Due:</div>
                    <div class="text-caption text-weight-medium">
                      {{ formatDate(project.dueDate) }}
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>

          <!-- Quick Actions -->
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Quick Actions</div>
              <div class="row q-gutter-md">
                <div class="col-12 col-sm-6 col-md-4">
                  <q-btn
                    unelevated
                    color="primary"
                    icon="add"
                    label="New Project"
                    class="full-width"
                    @click="navigateToProjects"
                  />
                </div>
                <div class="col-12 col-sm-6 col-md-4">
                  <q-btn
                    unelevated
                    color="green"
                    icon="group_add"
                    label="Manage Team"
                    class="full-width"
                    @click="navigateToTeam"
                  />
                </div>
                <div class="col-12 col-sm-6 col-md-4">
                  <q-btn
                    unelevated
                    color="orange"
                    icon="analytics"
                    label="View Analytics"
                    class="full-width"
                    @click="navigateToAnalytics"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Right Column -->
        <div class="col-12 col-lg-4">
          <!-- Recent Activity -->
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold">Recent Activity</div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-pa-none">
              <q-timeline color="primary">
                <q-timeline-entry
                  v-for="activity in recentActivity"
                  :key="activity.id"
                  :icon="activity.icon"
                  :color="activity.color"
                  class="q-pa-md"
                >
                  <template v-slot:title>
                    <div class="text-weight-medium">{{ activity.title }}</div>
                  </template>
                  <template v-slot:subtitle>
                    <div class="text-caption text-grey-7">
                      {{ formatTime(activity.timestamp) }}
                    </div>
                  </template>
                  <div class="text-caption">{{ activity.description }}</div>
                </q-timeline-entry>
              </q-timeline>
            </q-card-section>
          </q-card>

          <!-- Team Availability -->
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Team Availability</div>
              <div v-for="member in teamAvailability" :key="member.id" class="q-mb-md">
                <div class="row items-center q-mb-xs">
                  <q-avatar size="32px" class="q-mr-sm">
                    <img :src="member.avatar" />
                  </q-avatar>
                  <div class="col">
                    <div class="text-weight-medium">{{ member.name }}</div>
                    <div class="text-caption text-grey-7">{{ member.role }}</div>
                  </div>
                  <q-badge
                    :color="member.available ? 'green' : 'red'"
                    :label="member.available ? 'Available' : 'Busy'"
                  />
                </div>
                <q-linear-progress
                  :value="member.workload / 100"
                  :color="member.workload > 80 ? 'red' : member.workload > 60 ? 'orange' : 'green'"
                  class="q-mt-xs"
                />
                <div class="text-caption text-grey-7 q-mt-xs">Workload: {{ member.workload }}%</div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { format, formatDistanceToNow } from 'date-fns';
import { useRouter } from 'vue-router';

const router = useRouter();

// Mock data
const kpiCards = [
  {
    title: 'Active Projects',
    value: '12',
    icon: 'folder',
    color: 'primary',
    trend: 'up',
    change: '+2',
  },
  {
    title: 'Tasks Completed',
    value: '147',
    icon: 'task_alt',
    color: 'green',
    trend: 'up',
    change: '+12%',
  },
  {
    title: 'Team Members',
    value: '8',
    icon: 'group',
    color: 'blue',
    trend: 'up',
    change: '+1',
  },
  {
    title: 'Avg. Efficiency',
    value: '94%',
    icon: 'speed',
    color: 'orange',
    trend: 'down',
    change: '-2%',
  },
];

const activeProjects = [
  {
    id: 1,
    name: 'E-commerce Platform Redesign',
    description: 'Complete UI/UX overhaul of the main platform',
    progress: 75,
    tasksCompleted: 18,
    totalTasks: 24,
    status: 'On Track',
    dueDate: new Date('2024-01-15'),
    color: 'primary',
    icon: 'shopping_cart',
  },
  {
    id: 2,
    name: 'Mobile App Development',
    description: 'Native iOS and Android application',
    progress: 45,
    tasksCompleted: 12,
    totalTasks: 28,
    status: 'In Progress',
    dueDate: new Date('2024-02-20'),
    color: 'green',
    icon: 'phone_android',
  },
  {
    id: 3,
    name: 'Data Migration Project',
    description: 'Legacy system to cloud migration',
    progress: 30,
    tasksCompleted: 8,
    totalTasks: 22,
    status: 'At Risk',
    dueDate: new Date('2024-01-30'),
    color: 'orange',
    icon: 'cloud_upload',
  },
];

const recentActivity = [
  {
    id: 1,
    title: 'Task Completed',
    description: 'Frontend authentication module finished',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    icon: 'check_circle',
    color: 'green',
  },
  {
    id: 2,
    title: 'New Team Member',
    description: 'Lisa Anderson joined the team',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
    icon: 'person_add',
    color: 'blue',
  },
  {
    id: 3,
    title: 'Project Updated',
    description: 'Mobile App Development timeline adjusted',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5),
    icon: 'update',
    color: 'orange',
  },
  {
    id: 4,
    title: 'Risk Identified',
    description: 'Data Migration project needs attention',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8),
    icon: 'warning',
    color: 'red',
  },
];

const teamAvailability = [
  {
    id: 1,
    name: 'John Smith',
    role: 'Frontend Developer',
    avatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
    available: true,
    workload: 75,
  },
  {
    id: 2,
    name: 'Sarah Johnson',
    role: 'Backend Developer',
    avatar: 'https://cdn.quasar.dev/img/avatar2.jpg',
    available: false,
    workload: 90,
  },
  {
    id: 3,
    name: 'Mike Wilson',
    role: 'UI/UX Designer',
    avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    available: true,
    workload: 60,
  },
  {
    id: 4,
    name: 'Emma Davis',
    role: 'Project Manager',
    avatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
    available: true,
    workload: 45,
  },
];

// Methods
function getStatusColor(status: string): string {
  switch (status) {
    case 'On Track':
      return 'green';
    case 'In Progress':
      return 'blue';
    case 'At Risk':
      return 'orange';
    case 'Delayed':
      return 'red';
    default:
      return 'grey';
  }
}

function formatDate(date: Date): string {
  return format(date, 'MMM dd, yyyy');
}

function formatTime(date: Date): string {
  return formatDistanceToNow(date, { addSuffix: true });
}

function navigateToProjects() {
  router.push('/projects');
}

function navigateToProject(projectId: number) {
  router.push(`/projects/${projectId}`);
}

function navigateToTeam() {
  router.push('/team');
}

function navigateToAnalytics() {
  router.push('/analytics');
}
</script>

<style scoped>
.kpi-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
