<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Analytics Dashboard</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Performance metrics and project insights</p>
        </div>
        <div class="row q-gutter-md">
          <q-select
            v-model="selectedTimeRange"
            :options="timeRangeOptions"
            label="Time Range"
            filled
            dense
            style="min-width: 150px"
          />
          <q-btn color="secondary" icon="refresh" label="Refresh" @click="refreshData" />
          <q-btn color="primary" icon="download" label="Export" @click="exportData" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Key Metrics -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-primary-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-primary">
                    {{ kpiMetrics.projectsCompleted }}
                  </div>
                  <div class="text-caption text-grey-7">Projects Completed</div>
                </div>
                <div class="col-auto">
                  <q-icon name="check_circle" size="32px" class="text-primary" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_up" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">+15%</span>
                <span class="text-caption text-grey-7 q-ml-xs">vs last period</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-green-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-green">
                    {{ kpiMetrics.onTimeDelivery }}%
                  </div>
                  <div class="text-caption text-grey-7">On-Time Delivery</div>
                </div>
                <div class="col-auto">
                  <q-icon name="schedule" size="32px" class="text-green" />
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
          <q-card class="stat-card bg-orange-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-orange">
                    {{ kpiMetrics.avgVelocity }}
                  </div>
                  <div class="text-caption text-grey-7">Avg. Velocity</div>
                </div>
                <div class="col-auto">
                  <q-icon name="speed" size="32px" class="text-orange" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_down" class="text-red" size="16px" />
                <span class="text-caption q-ml-xs text-red">-3%</span>
                <span class="text-caption text-grey-7 q-ml-xs">vs target</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-blue-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-blue">
                    {{ kpiMetrics.budgetUtilization }}%
                  </div>
                  <div class="text-caption text-grey-7">Budget Utilization</div>
                </div>
                <div class="col-auto">
                  <q-icon name="euro" size="32px" class="text-blue" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_up" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">+2%</span>
                <span class="text-caption text-grey-7 q-ml-xs">efficiency</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Charts -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Project Performance Trends</div>
              <div class="chart-placeholder text-center q-pa-xl">
                <q-icon name="trending_up" size="64px" color="primary" class="q-mb-md" />
                <div class="text-h6 text-grey-7">Performance Chart</div>
                <div class="text-body2 text-grey-6">
                  Interactive performance trends visualization would be displayed here
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Project Status Distribution</div>
              <div class="chart-placeholder text-center q-pa-lg">
                <q-icon name="donut_large" size="48px" color="primary" class="q-mb-md" />
                <div class="text-body2 text-grey-6">Status distribution chart</div>
                <div class="q-mt-md">
                  <div class="row items-center q-mb-sm">
                    <div class="legend-color bg-green q-mr-sm"></div>
                    <span class="text-caption">Completed (5)</span>
                  </div>
                  <div class="row items-center q-mb-sm">
                    <div class="legend-color bg-primary q-mr-sm"></div>
                    <span class="text-caption">In Progress (8)</span>
                  </div>
                  <div class="row items-center q-mb-sm">
                    <div class="legend-color bg-orange q-mr-sm"></div>
                    <span class="text-caption">At Risk (3)</span>
                  </div>
                  <div class="row items-center">
                    <div class="legend-color bg-red q-mr-sm"></div>
                    <span class="text-caption">Delayed (2)</span>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Team Performance & Risk Analysis -->
      <div class="row q-gutter-lg">
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Team Performance</div>
              <div
                v-for="member in teamPerformance"
                :key="member.id"
                class="performance-item q-mb-md"
              >
                <div class="row items-center q-mb-sm">
                  <q-avatar size="32px" class="q-mr-sm">
                    <img :src="member.avatar" />
                  </q-avatar>
                  <div class="col">
                    <div class="text-weight-medium">{{ member.name }}</div>
                    <div class="text-caption text-grey-7">{{ member.role }}</div>
                  </div>
                  <div class="col-auto">
                    <div class="text-weight-bold" :class="getPerformanceColor(member.score)">
                      {{ member.score }}%
                    </div>
                  </div>
                </div>
                <q-linear-progress
                  :value="member.score / 100"
                  :color="getPerformanceColorName(member.score)"
                  style="height: 8px"
                  class="q-mb-xs"
                />
                <div class="row q-gutter-md text-caption text-grey-7">
                  <span>Tasks: {{ member.tasksCompleted }}</span>
                  <span>Quality: {{ member.qualityScore }}%</span>
                  <span>On-time: {{ member.onTimeDelivery }}%</span>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Risk Analysis</div>
              <div class="risk-overview q-mb-md">
                <div class="row q-gutter-md">
                  <div class="col risk-item bg-green-1">
                    <div class="text-center">
                      <div class="text-h5 text-weight-bold text-green">{{ riskMatrix.low }}</div>
                      <div class="text-caption">Low Risk</div>
                    </div>
                  </div>
                  <div class="col risk-item bg-yellow-1">
                    <div class="text-center">
                      <div class="text-h5 text-weight-bold text-orange">
                        {{ riskMatrix.medium }}
                      </div>
                      <div class="text-caption">Medium Risk</div>
                    </div>
                  </div>
                  <div class="col risk-item bg-orange-1">
                    <div class="text-center">
                      <div class="text-h5 text-weight-bold text-deep-orange">
                        {{ riskMatrix.high }}
                      </div>
                      <div class="text-caption">High Risk</div>
                    </div>
                  </div>
                  <div class="col risk-item bg-red-1">
                    <div class="text-center">
                      <div class="text-h5 text-weight-bold text-red">{{ riskMatrix.critical }}</div>
                      <div class="text-caption">Critical</div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="risk-trends">
                <div class="text-subtitle2 text-weight-medium q-mb-sm">Recent Trends</div>
                <div class="trend-item q-mb-sm">
                  <div class="row items-center">
                    <q-icon name="trending_down" color="green" size="16px" class="q-mr-sm" />
                    <span class="col text-body2">Schedule risks decreased by 15%</span>
                  </div>
                </div>
                <div class="trend-item q-mb-sm">
                  <div class="row items-center">
                    <q-icon name="trending_up" color="orange" size="16px" class="q-mr-sm" />
                    <span class="col text-body2">Budget risks increased by 5%</span>
                  </div>
                </div>
                <div class="trend-item">
                  <div class="row items-center">
                    <q-icon name="trending_flat" color="blue" size="16px" class="q-mr-sm" />
                    <span class="col text-body2">Technical risks remain stable</span>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMockDataStore } from 'stores/mock-data';

const mockDataStore = useMockDataStore();

// Reactive data
const selectedTimeRange = ref('Last 3 Months');

const timeRangeOptions = ['Last Week', 'Last Month', 'Last 3 Months', 'Last 6 Months', 'Last Year'];

const kpiMetrics = ref({
  projectsCompleted: 12,
  onTimeDelivery: 87,
  avgVelocity: 42,
  budgetUtilization: 94,
});

const teamPerformance = ref([
  {
    id: 1,
    name: 'John Smith',
    role: 'Senior Frontend Developer',
    avatar: 'https://cdn.quasar.dev/img/avatar2.jpg',
    score: 92,
    tasksCompleted: 28,
    qualityScore: 95,
    onTimeDelivery: 89,
  },
  {
    id: 2,
    name: 'Sarah Johnson',
    role: 'Backend Developer',
    avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    score: 88,
    tasksCompleted: 25,
    qualityScore: 91,
    onTimeDelivery: 85,
  },
  {
    id: 3,
    name: 'Mike Wilson',
    role: 'DevOps Engineer',
    avatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
    score: 85,
    tasksCompleted: 22,
    qualityScore: 88,
    onTimeDelivery: 82,
  },
  {
    id: 4,
    name: 'Emma Davis',
    role: 'UI/UX Designer',
    avatar: 'https://cdn.quasar.dev/img/avatar5.jpg',
    score: 90,
    tasksCompleted: 20,
    qualityScore: 93,
    onTimeDelivery: 87,
  },
]);

const riskMatrix = ref({
  low: 8,
  medium: 5,
  high: 3,
  critical: 1,
});

// Methods
function getPerformanceColor(score: number): string {
  if (score >= 90) return 'text-green';
  if (score >= 80) return 'text-primary';
  if (score >= 70) return 'text-orange';
  return 'text-red';
}

function getPerformanceColorName(score: number): string {
  if (score >= 90) return 'green';
  if (score >= 80) return 'primary';
  if (score >= 70) return 'orange';
  return 'red';
}

function refreshData() {
  console.log('Refreshing analytics data...');
}

function exportData() {
  console.log('Exporting analytics data...');
}

onMounted(() => {
  mockDataStore.initializeData();
});
</script>

<style scoped>
.stat-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart-placeholder {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.performance-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.risk-item {
  padding: 16px;
  border-radius: 8px;
}

.risk-trends {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.trend-item {
  padding: 4px 0;
}
</style>
