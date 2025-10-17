<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Auto Optimization</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Automatic project optimization using AI algorithms
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="settings"
            label="Configure"
            @click="showConfigDialog = true"
          />
          <q-btn
            color="primary"
            icon="auto_fix_high"
            label="Start Optimization"
            @click="startOptimization"
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Optimization Status -->
      <q-card
        class="q-mb-lg"
        :class="{
          'bg-green-1': optimizationStatus === 'active',
          'bg-grey-2': optimizationStatus === 'idle',
        }"
      >
        <q-card-section>
          <div class="row items-center">
            <q-avatar
              size="48px"
              :color="optimizationStatus === 'active' ? 'green' : 'grey-5'"
              text-color="white"
            >
              <q-icon :name="optimizationStatus === 'active' ? 'auto_fix_high' : 'pause'" />
            </q-avatar>
            <div class="col q-ml-md">
              <div class="text-h6 text-weight-bold">
                {{ optimizationStatus === 'active' ? 'Optimization Active' : 'Optimization Idle' }}
              </div>
              <div class="text-body2 text-grey-7">
                {{
                  optimizationStatus === 'active'
                    ? 'AI is continuously optimizing your projects'
                    : 'Click "Start Optimization" to begin automatic improvements'
                }}
              </div>
            </div>
            <div class="col-auto">
              <q-btn
                :color="optimizationStatus === 'active' ? 'red' : 'green'"
                :icon="optimizationStatus === 'active' ? 'stop' : 'play_arrow'"
                :label="optimizationStatus === 'active' ? 'Stop' : 'Start'"
                @click="toggleOptimization"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Optimization Metrics -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="metric-card bg-primary-1">
            <q-card-section class="text-center">
              <q-icon name="speed" size="32px" class="text-primary q-mb-sm" />
              <div class="text-h4 text-weight-bold text-primary">{{ metrics.efficiency }}%</div>
              <div class="text-caption text-grey-7">Efficiency Gain</div>
              <div class="text-caption text-green">
                +{{ metrics.efficiencyIncrease }}% this week
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="metric-card bg-green-1">
            <q-card-section class="text-center">
              <q-icon name="schedule" size="32px" class="text-green q-mb-sm" />
              <div class="text-h4 text-weight-bold text-green">{{ metrics.timeSaved }}h</div>
              <div class="text-caption text-grey-7">Time Saved</div>
              <div class="text-caption text-green">+{{ metrics.timeSavedIncrease }}h this week</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="metric-card bg-orange-1">
            <q-card-section class="text-center">
              <q-icon name="euro" size="32px" class="text-orange q-mb-sm" />
              <div class="text-h4 text-weight-bold text-orange">
                €{{ metrics.costSaved.toLocaleString() }}
              </div>
              <div class="text-caption text-grey-7">Cost Saved</div>
              <div class="text-caption text-green">
                +€{{ metrics.costSavedIncrease.toLocaleString() }} this week
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="metric-card bg-blue-1">
            <q-card-section class="text-center">
              <q-icon name="trending_up" size="32px" class="text-blue q-mb-sm" />
              <div class="text-h4 text-weight-bold text-blue">{{ metrics.qualityScore }}%</div>
              <div class="text-caption text-grey-7">Quality Score</div>
              <div class="text-caption text-green">+{{ metrics.qualityIncrease }}% this week</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Optimization Areas -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-lg-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Active Optimizations</div>

              <div class="optimization-list">
                <div
                  v-for="optimization in activeOptimizations"
                  :key="optimization.id"
                  class="optimization-item q-mb-md"
                >
                  <div class="row items-center">
                    <q-avatar
                      size="32px"
                      :color="
                        optimization.status === 'running'
                          ? 'primary'
                          : optimization.status === 'completed'
                            ? 'green'
                            : 'grey'
                      "
                      text-color="white"
                    >
                      <q-icon :name="getOptimizationIcon(optimization.type)" />
                    </q-avatar>
                    <div class="col q-ml-md">
                      <div class="text-weight-medium">{{ optimization.title }}</div>
                      <div class="text-body2 text-grey-7">{{ optimization.description }}</div>
                      <div class="row items-center q-mt-sm">
                        <q-chip
                          :color="getStatusColor(optimization.status)"
                          text-color="white"
                          size="sm"
                          :label="optimization.status"
                        />
                        <q-space />
                        <span class="text-caption text-grey-6"
                          >{{ optimization.progress }}% complete</span
                        >
                      </div>
                    </div>
                    <div class="col-auto">
                      <q-linear-progress
                        :value="optimization.progress / 100"
                        :color="optimization.status === 'running' ? 'primary' : 'green'"
                        style="width: 80px; height: 6px"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-lg-4">
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Optimization Queue</div>

              <div class="queue-list">
                <div
                  v-for="(item, index) in optimizationQueue"
                  :key="item.id"
                  class="queue-item q-mb-sm"
                >
                  <div class="row items-center">
                    <div class="queue-number">{{ index + 1 }}</div>
                    <div class="col q-ml-sm">
                      <div class="text-weight-medium">{{ item.title }}</div>
                      <div class="text-caption text-grey-7">{{ item.estimatedTime }}</div>
                    </div>
                    <q-btn flat round dense icon="more_vert" @click="showQueueMenu(item)">
                      <q-menu>
                        <q-list>
                          <q-item clickable @click="prioritizeItem(item)">
                            <q-item-section>Prioritize</q-item-section>
                          </q-item>
                          <q-item clickable @click="removeFromQueue(item)">
                            <q-item-section>Remove</q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">AI Insights</div>

              <div class="insights-list">
                <div v-for="insight in aiInsights" :key="insight.id" class="insight-item q-mb-md">
                  <div class="row items-start">
                    <q-icon
                      :name="insight.icon"
                      :color="
                        insight.type === 'success'
                          ? 'green'
                          : insight.type === 'warning'
                            ? 'orange'
                            : 'primary'
                      "
                      class="q-mr-sm q-mt-xs"
                    />
                    <div class="col">
                      <div class="text-body2">{{ insight.message }}</div>
                      <div class="text-caption text-grey-7">
                        {{ insight.confidence }}% confidence
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Optimization Results -->
      <q-card>
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Recent Optimization Results</div>

          <q-table
            :rows="optimizationResults"
            :columns="resultsColumns"
            row-key="id"
            :pagination="{ rowsPerPage: 10 }"
          >
            <template v-slot:body-cell-impact="props">
              <q-td :props="props">
                <div class="text-weight-bold" :class="getImpactColor(props.value)">
                  {{ props.value > 0 ? '+' : '' }}{{ props.value }}%
                </div>
              </q-td>
            </template>

            <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-chip
                  :color="getStatusColor(props.value)"
                  text-color="white"
                  size="sm"
                  :label="props.value"
                />
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>

    <!-- Configuration Dialog -->
    <q-dialog v-model="showConfigDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Optimization Configuration</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-subtitle2 q-mb-md">Optimization Areas</div>
          <div class="column q-gutter-sm q-mb-lg">
            <q-checkbox v-model="config.scheduleOptimization" label="Schedule Optimization" />
            <q-checkbox v-model="config.resourceAllocation" label="Resource Allocation" />
            <q-checkbox v-model="config.budgetOptimization" label="Budget Optimization" />
            <q-checkbox v-model="config.qualityImprovement" label="Quality Improvement" />
            <q-checkbox v-model="config.riskMitigation" label="Risk Mitigation" />
          </div>

          <div class="text-subtitle2 q-mb-md">Optimization Frequency</div>
          <q-select
            v-model="config.frequency"
            :options="['Real-time', 'Hourly', 'Daily', 'Weekly']"
            label="Frequency"
            filled
            class="q-mb-lg"
          />

          <div class="text-subtitle2 q-mb-md">Aggressiveness Level</div>
          <q-slider
            v-model="config.aggressiveness"
            :min="1"
            :max="10"
            :step="1"
            label
            label-always
            color="primary"
          />
          <div class="text-caption text-grey-7 q-mt-xs">
            {{
              config.aggressiveness <= 3
                ? 'Conservative'
                : config.aggressiveness <= 7
                  ? 'Moderate'
                  : 'Aggressive'
            }}
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelConfig" />
          <q-btn color="primary" label="Save Configuration" @click="saveConfig" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useMockDataStore } from 'stores/mock-data';

const mockDataStore = useMockDataStore();

// Interfaces
interface OptimizationQueueItem {
  id: number;
  title: string;
  estimatedTime: string;
}

// Reactive data
const showConfigDialog = ref(false);
const optimizationStatus = ref('idle');

const metrics = ref({
  efficiency: 87,
  efficiencyIncrease: 12,
  timeSaved: 156,
  timeSavedIncrease: 23,
  costSaved: 45000,
  costSavedIncrease: 8500,
  qualityScore: 92,
  qualityIncrease: 8,
});

const activeOptimizations = ref([
  {
    id: 1,
    title: 'Resource Rebalancing',
    description: 'Optimizing team workload distribution across projects',
    type: 'resource',
    status: 'running',
    progress: 67,
  },
  {
    id: 2,
    title: 'Schedule Compression',
    description: 'Identifying opportunities to accelerate project timelines',
    type: 'schedule',
    status: 'running',
    progress: 34,
  },
  {
    id: 3,
    title: 'Budget Allocation',
    description: 'Optimizing budget distribution for maximum ROI',
    type: 'budget',
    status: 'completed',
    progress: 100,
  },
  {
    id: 4,
    title: 'Quality Assurance',
    description: 'Implementing automated quality checks and improvements',
    type: 'quality',
    status: 'pending',
    progress: 0,
  },
]);

const optimizationQueue = ref([
  { id: 1, title: 'Task Prioritization', estimatedTime: '15 min' },
  { id: 2, title: 'Dependency Optimization', estimatedTime: '25 min' },
  { id: 3, title: 'Risk Assessment Update', estimatedTime: '10 min' },
  { id: 4, title: 'Performance Analysis', estimatedTime: '30 min' },
]);

const aiInsights = ref([
  {
    id: 1,
    message: 'Team velocity can be improved by 15% with current optimizations',
    type: 'success',
    icon: 'trending_up',
    confidence: 89,
  },
  {
    id: 2,
    message: 'Schedule compression may increase risk of quality issues',
    type: 'warning',
    icon: 'warning',
    confidence: 76,
  },
  {
    id: 3,
    message: 'Resource rebalancing will reduce bottlenecks by 23%',
    type: 'info',
    icon: 'balance',
    confidence: 92,
  },
]);

const optimizationResults = ref([
  {
    id: 1,
    optimization: 'Sprint Planning Optimization',
    project: 'E-commerce Platform',
    completedAt: '2024-12-15',
    impact: 18,
    metric: 'Velocity',
    status: 'Applied',
  },
  {
    id: 2,
    optimization: 'Resource Load Balancing',
    project: 'Mobile App',
    completedAt: '2024-12-14',
    impact: 12,
    metric: 'Efficiency',
    status: 'Applied',
  },
  {
    id: 3,
    optimization: 'Risk Mitigation Automation',
    project: 'Data Migration',
    completedAt: '2024-12-13',
    impact: -5,
    metric: 'Risk Score',
    status: 'Applied',
  },
]);

const config = reactive({
  scheduleOptimization: true,
  resourceAllocation: true,
  budgetOptimization: false,
  qualityImprovement: true,
  riskMitigation: true,
  frequency: 'Daily',
  aggressiveness: 5,
});

const resultsColumns = [
  {
    name: 'optimization',
    label: 'Optimization',
    field: 'optimization',
    align: 'left' as const,
    sortable: true,
  },
  { name: 'project', label: 'Project', field: 'project', align: 'left' as const },
  { name: 'completedAt', label: 'Completed', field: 'completedAt', align: 'left' as const },
  { name: 'impact', label: 'Impact', field: 'impact', align: 'center' as const },
  { name: 'metric', label: 'Metric', field: 'metric', align: 'center' as const },
  { name: 'status', label: 'Status', field: 'status', align: 'center' as const },
];

// Methods
function getOptimizationIcon(type: string): string {
  switch (type) {
    case 'resource':
      return 'group';
    case 'schedule':
      return 'schedule';
    case 'budget':
      return 'euro';
    case 'quality':
      return 'verified';
    default:
      return 'auto_fix_high';
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'running':
      return 'primary';
    case 'completed':
      return 'green';
    case 'Applied':
      return 'green';
    case 'pending':
      return 'orange';
    default:
      return 'grey';
  }
}

function getImpactColor(impact: number): string {
  if (impact > 0) return 'text-green';
  if (impact < 0) return 'text-red';
  return 'text-grey-7';
}

function toggleOptimization() {
  optimizationStatus.value = optimizationStatus.value === 'active' ? 'idle' : 'active';
}

function startOptimization() {
  optimizationStatus.value = 'active';
  console.log('Starting auto optimization...');
}

function showQueueMenu(item: OptimizationQueueItem) {
  console.log('Showing menu for:', item.title);
}

function prioritizeItem(item: OptimizationQueueItem) {
  console.log('Prioritizing:', item.title);
}

function removeFromQueue(item: OptimizationQueueItem) {
  const index = optimizationQueue.value.findIndex((q) => q.id === item.id);
  if (index !== -1) {
    optimizationQueue.value.splice(index, 1);
  }
}

function saveConfig() {
  console.log('Saving configuration:', config);
  showConfigDialog.value = false;
}

function cancelConfig() {
  showConfigDialog.value = false;
}

onMounted(() => {
  mockDataStore.initializeData();
});
</script>

<style scoped>
.metric-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.optimization-item {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.queue-item {
  padding: 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

.queue-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--q-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.insight-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}
</style>
