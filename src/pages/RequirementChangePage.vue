<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between q-mb-md">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">
            Requirement Change Simulator
          </h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Simulate client requirement changes and automatic PERT+RACI adaptation
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn color="orange" icon="sync" label="Reset Simulation" @click="resetSimulation" />
          <q-btn color="primary" icon="play_arrow" label="Run Simulation" @click="runSimulation" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Simulation Controls -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Simulation Settings</div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Change Type</div>
                <q-select
                  v-model="simulationSettings.changeType"
                  :options="changeTypeOptions"
                  filled
                  dense
                />
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Number of Changes</div>
                <q-input
                  v-model.number="simulationSettings.numberOfChanges"
                  type="number"
                  :min="1"
                  :max="20"
                  filled
                  dense
                />
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Adaptation Strategy</div>
                <q-select
                  v-model="simulationSettings.adaptationStrategy"
                  :options="adaptationStrategyOptions"
                  filled
                  dense
                />
              </div>

              <q-separator class="q-my-md" />

              <div class="settings-summary">
                <div class="text-subtitle2 text-weight-medium q-mb-sm">Current Project</div>
                <div class="text-body2 text-grey-7">Project Alpha - 15 tasks</div>
                <div class="text-caption text-grey-6">Duration: 45 days</div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Simulation Results</div>

              <!-- Before/After Comparison -->
              <div class="comparison-grid q-mb-lg">
                <div class="comparison-column">
                  <div class="comparison-header bg-grey-3 q-pa-md">
                    <div class="text-h6 text-weight-bold text-center">Before Changes</div>
                  </div>
                  <div class="comparison-content q-pa-md">
                    <div class="metric-item q-mb-md">
                      <div class="row items-center justify-between">
                        <span class="text-grey-7">Total Duration</span>
                        <span class="text-h6 text-weight-bold">{{ beforeMetrics.duration }}d</span>
                      </div>
                    </div>
                    <div class="metric-item q-mb-md">
                      <div class="row items-center justify-between">
                        <span class="text-grey-7">Team Workload</span>
                        <span class="text-h6 text-weight-bold text-orange"
                          >{{ beforeMetrics.workload }}%</span
                        >
                      </div>
                    </div>
                    <div class="metric-item q-mb-md">
                      <div class="row items-center justify-between">
                        <span class="text-grey-7">Risk Score</span>
                        <span class="text-h6 text-weight-bold text-red"
                          >{{ beforeMetrics.riskScore }}/10</span
                        >
                      </div>
                    </div>
                    <div class="metric-item">
                      <div class="row items-center justify-between">
                        <span class="text-grey-7">Balance Score</span>
                        <span class="text-h6 text-weight-bold text-primary"
                          >{{ beforeMetrics.balanceScore }}%</span
                        >
                      </div>
                    </div>
                  </div>
                </div>

                <div class="comparison-arrow">
                  <q-icon name="arrow_forward" size="48px" color="primary" />
                </div>

                <div class="comparison-column">
                  <div class="comparison-header bg-green-1 q-pa-md">
                    <div class="text-h6 text-weight-bold text-center text-green">
                      After Auto-Adaptation
                    </div>
                  </div>
                  <div class="comparison-content q-pa-md">
                    <div class="metric-item q-mb-md">
                      <div class="row items-center justify-between">
                        <span class="text-grey-7">Total Duration</span>
                        <div class="col-auto">
                          <span class="text-h6 text-weight-bold">{{ afterMetrics.duration }}d</span>
                          <span class="text-caption" :class="getDeltaClass(durationDelta)">
                            ({{ durationDelta > 0 ? '+' : '' }}{{ durationDelta }}d)
                          </span>
                        </div>
                      </div>
                    </div>
                    <div class="metric-item q-mb-md">
                      <div class="row items-center justify-between">
                        <span class="text-grey-7">Team Workload</span>
                        <div class="col-auto">
                          <span class="text-h6 text-weight-bold text-green"
                            >{{ afterMetrics.workload }}%</span
                          >
                          <span class="text-caption" :class="getDeltaClass(-workloadDelta)">
                            ({{ workloadDelta > 0 ? '-' : '+' }}{{ Math.abs(workloadDelta) }}%)
                          </span>
                        </div>
                      </div>
                    </div>
                    <div class="metric-item q-mb-md">
                      <div class="row items-center justify-between">
                        <span class="text-grey-7">Risk Score</span>
                        <div class="col-auto">
                          <span class="text-h6 text-weight-bold text-green"
                            >{{ afterMetrics.riskScore }}/10</span
                          >
                          <span class="text-caption" :class="getDeltaClass(-riskDelta)">
                            ({{ riskDelta > 0 ? '-' : '+' }}{{ Math.abs(riskDelta) }})
                          </span>
                        </div>
                      </div>
                    </div>
                    <div class="metric-item">
                      <div class="row items-center justify-between">
                        <span class="text-grey-7">Balance Score</span>
                        <div class="col-auto">
                          <span class="text-h6 text-weight-bold text-green"
                            >{{ afterMetrics.balanceScore }}%</span
                          >
                          <span class="text-caption" :class="getDeltaClass(balanceDelta)">
                            (+{{ balanceDelta }}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Performance Metrics -->
              <q-card flat class="bg-primary-1 q-pa-md">
                <div class="row q-gutter-md text-center">
                  <div class="col">
                    <div class="text-h5 text-weight-bold text-primary">{{ adaptationTime }}ms</div>
                    <div class="text-caption text-grey-7">Adaptation Time</div>
                  </div>
                  <div class="col">
                    <div class="text-h5 text-weight-bold text-green">{{ improvementRate }}%</div>
                    <div class="text-caption text-grey-7">Improvement</div>
                  </div>
                  <div class="col">
                    <div class="text-h5 text-weight-bold text-orange">
                      {{ changesApplied }}
                    </div>
                    <div class="text-caption text-grey-7">Changes Applied</div>
                  </div>
                </div>
              </q-card>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Change Log -->
      <q-card>
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Change Log & Adaptations</div>

          <q-timeline color="primary">
            <q-timeline-entry
              v-for="(change, index) in changeLog"
              :key="index"
              :title="change.title"
              :subtitle="change.timestamp"
              :icon="change.icon"
              :color="change.color"
            >
              <div class="text-body2 q-mb-sm">{{ change.description }}</div>

              <q-card flat class="bg-grey-1 q-pa-sm">
                <div class="text-subtitle2 text-weight-medium q-mb-xs">Automatic Adaptations:</div>
                <ul class="q-ma-none q-pl-md">
                  <li v-for="(adaptation, idx) in change.adaptations" :key="idx">
                    {{ adaptation }}
                  </li>
                </ul>
              </q-card>

              <div class="q-mt-sm">
                <q-chip
                  v-for="metric in change.metrics"
                  :key="metric.label"
                  :color="metric.color"
                  text-color="white"
                  size="sm"
                  :label="`${metric.label}: ${metric.value}`"
                />
              </div>
            </q-timeline-entry>
          </q-timeline>
        </q-card-section>
      </q-card>
    </div>

    <!-- Running Simulation Dialog -->
    <q-dialog v-model="showSimulationDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6 text-center">Running Simulation...</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-center q-mb-md">
            <q-circular-progress
              :value="simulationProgress"
              size="120px"
              :thickness="0.15"
              color="primary"
              track-color="grey-3"
              class="q-ma-md"
            >
              <div class="text-h5">{{ simulationProgress }}%</div>
            </q-circular-progress>
          </div>

          <div class="text-body2 text-center text-grey-7">
            {{ currentSimulationStep }}
          </div>

          <q-linear-progress :value="simulationProgress / 100" color="primary" class="q-mt-md" />
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

// Reactive data
const simulationSettings = ref({
  changeType: 'Add New Task',
  numberOfChanges: 3,
  adaptationStrategy: 'PERT+RACI Optimization',
});

const changeTypeOptions = [
  'Add New Task',
  'Remove Task',
  'Change Task Priority',
  'Modify Task Duration',
  'Reassign Team Members',
  'Mixed Changes',
];

const adaptationStrategyOptions = [
  'PERT+RACI Optimization',
  'Traditional Manual Adjustment',
  'Load Balancing Only',
  'Risk-Based Adaptation',
];

const beforeMetrics = ref({
  duration: 45,
  workload: 85,
  riskScore: 6.5,
  balanceScore: 72,
});

const afterMetrics = ref({
  duration: 48,
  workload: 75,
  riskScore: 4.8,
  balanceScore: 89,
});

const adaptationTime = ref(0);
const improvementRate = ref(0);
const changesApplied = ref(0);

const showSimulationDialog = ref(false);
const simulationProgress = ref(0);
const currentSimulationStep = ref('');

const changeLog = ref([
  {
    title: 'New Feature Request Added',
    timestamp: '2024-01-15 10:30:00',
    icon: 'add_circle',
    color: 'primary',
    description: 'Client requested new authentication feature (8 story points)',
    adaptations: [
      'PERT duration recalculated: +3 days',
      'Assigned to John (R), Sarah (A) based on skills',
      "Rebalanced Mike's workload: 90% → 78%",
      'Updated critical path analysis',
    ],
    metrics: [
      { label: 'Duration Impact', value: '+3d', color: 'orange' },
      { label: 'Team Balance', value: '+12%', color: 'green' },
      { label: 'Risk', value: '-0.5', color: 'green' },
    ],
  },
  {
    title: 'Priority Change: Bug Fix to Critical',
    timestamp: '2024-01-15 11:45:00',
    icon: 'priority_high',
    color: 'red',
    description: 'Security bug escalated to critical priority',
    adaptations: [
      'Moved to top of sprint backlog',
      'Reassigned Emma (R) → John (R) for faster resolution',
      'Adjusted RACI: Added Mike as Consulted for security review',
      'PERT expected time reduced from 5d to 2d',
    ],
    metrics: [
      { label: 'Duration Impact', value: '-3d', color: 'green' },
      { label: 'Risk Reduction', value: '-1.5', color: 'green' },
    ],
  },
  {
    title: 'Team Member Availability Change',
    timestamp: '2024-01-15 14:20:00',
    icon: 'person_off',
    color: 'orange',
    description: 'Sarah unavailable for 2 days due to sick leave',
    adaptations: [
      "Redistributed Sarah's tasks to John and Mike",
      'RACI roles updated: Mike promoted to Accountable on 2 tasks',
      'PERT timeline adjusted for handover overhead',
      'Risk score increased temporarily: 4.8 → 5.2',
    ],
    metrics: [
      { label: 'Duration Impact', value: '+1d', color: 'orange' },
      { label: 'Workload Spike', value: '+15%', color: 'red' },
      { label: 'Recovery Time', value: '2d', color: 'primary' },
    ],
  },
]);

// Computed
const durationDelta = computed(() => afterMetrics.value.duration - beforeMetrics.value.duration);
const workloadDelta = computed(() => beforeMetrics.value.workload - afterMetrics.value.workload);
const riskDelta = computed(
  () => Math.round((beforeMetrics.value.riskScore - afterMetrics.value.riskScore) * 10) / 10,
);
const balanceDelta = computed(
  () => afterMetrics.value.balanceScore - beforeMetrics.value.balanceScore,
);

// Methods
function getDeltaClass(delta: number): string {
  if (delta > 0) return 'text-green';
  if (delta < 0) return 'text-red';
  return 'text-grey';
}

async function runSimulation() {
  showSimulationDialog.value = true;
  simulationProgress.value = 0;

  const steps = [
    'Analyzing current project state...',
    'Applying requirement changes...',
    'Recalculating PERT duration...',
    'Optimizing RACI assignments...',
    'Balancing team workload...',
    'Updating critical path...',
    'Calculating risk impact...',
    'Finalizing adaptations...',
  ];

  for (let i = 0; i < steps.length; i++) {
    currentSimulationStep.value = steps[i]!;
    simulationProgress.value = Math.round(((i + 1) / steps.length) * 100);
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  // Simulate results
  const startTime = Date.now();

  // Simulate adaptation calculations
  await new Promise((resolve) => setTimeout(resolve, 300));

  adaptationTime.value = Date.now() - startTime;
  improvementRate.value = 23.5;
  changesApplied.value = simulationSettings.value.numberOfChanges;

  // Update metrics
  afterMetrics.value = {
    duration: beforeMetrics.value.duration + Math.floor(Math.random() * 5) - 1,
    workload: Math.max(60, beforeMetrics.value.workload - Math.floor(Math.random() * 15)),
    riskScore: Math.max(3, beforeMetrics.value.riskScore - Math.random() * 2),
    balanceScore: Math.min(95, beforeMetrics.value.balanceScore + Math.floor(Math.random() * 20)),
  };

  showSimulationDialog.value = false;

  $q.notify({
    message: 'Simulation completed successfully! System adapted to changes in real-time.',
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });
}

function resetSimulation() {
  beforeMetrics.value = {
    duration: 45,
    workload: 85,
    riskScore: 6.5,
    balanceScore: 72,
  };

  afterMetrics.value = {
    duration: 48,
    workload: 75,
    riskScore: 4.8,
    balanceScore: 89,
  };

  adaptationTime.value = 0;
  improvementRate.value = 0;
  changesApplied.value = 0;

  $q.notify({
    message: 'Simulation reset to initial state',
    color: 'info',
    icon: 'refresh',
    position: 'top',
  });
}
</script>

<style scoped>
.comparison-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
  align-items: center;
}

.comparison-column {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.comparison-header {
  border-bottom: 2px solid #e0e0e0;
}

.comparison-content {
  min-height: 250px;
}

.comparison-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-item {
  padding: 8px 0;
}

.settings-summary {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

@media (max-width: 768px) {
  .comparison-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .comparison-arrow {
    transform: rotate(90deg);
  }
}
</style>
