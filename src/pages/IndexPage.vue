<template>
  <q-page class="bg-grey-1">
    <!-- Header Section -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center q-gutter-md">
        <div class="col">
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">
            Welcome back, {{ authStore.userName }}! 👋
          </h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Here's your PERT+RACI research and project management overview
          </p>
        </div>
        <div class="col-auto">
          <q-btn-group>
            <q-btn
              color="primary"
              icon="auto_awesome"
              label="PERT+RACI"
              unelevated
              @click="navigateTo('/pert-raci-optimization')"
            />
            <q-btn
              color="secondary"
              icon="science"
              label="Experiments"
              unelevated
              @click="navigateTo('/experiments')"
            />
          </q-btn-group>
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- PERT+RACI Research Status -->
      <div class="q-mb-md">
        <div class="text-h6 text-weight-bold text-primary q-mb-sm">
          <q-icon name="auto_awesome" class="q-mr-sm" />
          PERT+RACI Integration Status
        </div>
        <q-separator class="q-mb-md" />
      </div>

      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-primary-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-primary">92%</div>
                  <div class="text-caption text-grey-7">PERT Accuracy</div>
                </div>
                <div class="col-auto">
                  <q-icon name="account_tree" size="32px" class="text-primary" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_up" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">+15%</span>
                <span class="text-caption text-grey-7 q-ml-xs">vs traditional</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-green-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-green">+28%</div>
                  <div class="text-caption text-grey-7">Avg. Improvement</div>
                </div>
                <div class="col-auto">
                  <q-icon name="trending_up" size="32px" class="text-green" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="verified" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">93%</span>
                <span class="text-caption text-grey-7 q-ml-xs">confidence</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-blue-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-blue">&lt;5s</div>
                  <div class="text-caption text-grey-7">Adaptation Time</div>
                </div>
                <div class="col-auto">
                  <q-icon name="sync_alt" size="32px" class="text-blue" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="speed" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">99%</span>
                <span class="text-caption text-grey-7 q-ml-xs">faster</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-orange-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-orange">5/5</div>
                  <div class="text-caption text-grey-7">Experiments</div>
                </div>
                <div class="col-auto">
                  <q-icon name="science" size="32px" class="text-orange" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="check_circle" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">4 completed</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

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
                  <div class="text-h4 text-weight-bold text-purple">12</div>
                  <div class="text-caption text-grey-7">Active Projects</div>
                </div>
                <div class="col-auto">
                  <q-icon name="work" size="32px" class="text-purple" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_up" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">+2</span>
                <span class="text-caption text-grey-7 q-ml-xs">this month</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-cyan-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-cyan">89%</div>
                  <div class="text-caption text-grey-7">On-Time Delivery</div>
                </div>
                <div class="col-auto">
                  <q-icon name="schedule" size="32px" class="text-cyan" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_up" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">+8%</span>
                <span class="text-caption text-grey-7 q-ml-xs">improvement</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-indigo-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-indigo">8</div>
                  <div class="text-caption text-grey-7">Team Members</div>
                </div>
                <div class="col-auto">
                  <q-icon name="group" size="32px" class="text-indigo" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="sentiment_satisfied" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">8.5/10</span>
                <span class="text-caption text-grey-7 q-ml-xs">satisfaction</span>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-3">
          <q-card class="kpi-card bg-teal-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-teal">85%</div>
                  <div class="text-caption text-grey-7">Efficiency</div>
                </div>
                <div class="col-auto">
                  <q-icon name="speed" size="32px" class="text-teal" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="check" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">On track</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <div class="row q-gutter-lg q-mb-lg">
        <!-- Recent Experiments -->
        <div class="col-12 col-lg-6">
          <q-card>
            <q-card-section>
              <div class="row items-center q-mb-md">
                <div class="text-h6 text-weight-bold">
                  <q-icon name="science" class="q-mr-sm" />
                  Recent Experiments
                </div>
                <q-space />
                <q-btn flat dense icon="arrow_forward" @click="navigateTo('/experiments')" />
              </div>

              <q-list separator>
                <q-item v-for="experiment in recentExperiments" :key="experiment.id">
                  <q-item-section avatar>
                    <q-icon
                      :name="experiment.status === 'Completed' ? 'check_circle' : 'hourglass_empty'"
                      :color="experiment.status === 'Completed' ? 'green' : 'orange'"
                      size="sm"
                    />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ experiment.name }}</q-item-label>
                    <q-item-label caption>{{ experiment.status }}</q-item-label>
                  </q-item-section>
                  <q-item-section side v-if="experiment.improvement">
                    <q-chip color="green" text-color="white" size="sm">
                      +{{ experiment.improvement }}%
                    </q-chip>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>

        <!-- Active Projects -->
        <div class="col-12 col-lg-6">
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
            <div class="col-12 col-sm-6 col-md-3">
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

            <div class="col-12 col-sm-6 col-md-3">
              <q-btn
                flat
                class="full-width q-pa-md action-btn"
                @click="navigateTo('/requirement-changes')"
              >
                <div class="column items-center">
                  <q-icon name="sync_alt" color="blue" size="48px" class="q-mb-sm" />
                  <div class="text-weight-bold text-blue">Req. Changes</div>
                  <div class="text-caption text-grey-7">Simulate adaptation</div>
                </div>
              </q-btn>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <q-btn flat class="full-width q-pa-md action-btn" @click="navigateTo('/experiments')">
                <div class="column items-center">
                  <q-icon name="science" color="green" size="48px" class="q-mb-sm" />
                  <div class="text-weight-bold text-green">Experiments</div>
                  <div class="text-caption text-grey-7">View research</div>
                </div>
              </q-btn>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <q-btn flat class="full-width q-pa-md action-btn" @click="navigateTo('/analytics')">
                <div class="column items-center">
                  <q-icon name="analytics" color="orange" size="48px" class="q-mb-sm" />
                  <div class="text-weight-bold text-orange">Analytics</div>
                  <div class="text-caption text-grey-7">Performance metrics</div>
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
import { onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'src/stores/auth-store';

const router = useRouter();
const route = useRoute();
const $q = useQuasar();
const authStore = useAuthStore();

// Check for access denied message
onMounted(() => {
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
});

// Recent Experiments
const recentExperiments = [
  { id: 1, name: 'PERT+RACI vs Traditional', status: 'Completed', improvement: 28 },
  { id: 2, name: 'Workload Rebalancing', status: 'Completed', improvement: 42 },
  { id: 3, name: 'Requirement Adaptation', status: 'Completed', improvement: 99 },
  { id: 4, name: 'Risk-Based Optimization', status: 'Completed', improvement: 43 },
  { id: 5, name: 'Multi-Project RACI', status: 'In Progress', improvement: null },
];

// Active Projects
const activeProjects = [
  {
    id: 1,
    name: 'E-commerce Platform',
    icon: 'shopping_cart',
    color: 'primary',
    progress: 75,
    status: 'On Track',
  },
  {
    id: 2,
    name: 'Mobile App',
    icon: 'phone_android',
    color: 'green',
    progress: 45,
    status: 'In Progress',
  },
  {
    id: 3,
    name: 'Data Migration',
    icon: 'storage',
    color: 'orange',
    progress: 30,
    status: 'At Risk',
  },
  {
    id: 4,
    name: 'API Integration',
    icon: 'api',
    color: 'blue',
    progress: 60,
    status: 'On Track',
  },
];

// Helper functions
function navigateTo(path: string) {
  router.push(path);
}

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
