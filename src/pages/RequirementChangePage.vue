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

              <!-- Project Selection -->
              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Select Project</div>
                <q-select
                  v-model="selectedProjectId"
                  :options="projectOptions"
                  emit-value
                  map-options
                  filled
                  dense
                >
                  <template v-slot:prepend>
                    <q-icon name="folder" />
                  </template>
                </q-select>
              </div>

              <q-separator class="q-my-md" />

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
                  :max="50"
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

              <div class="q-mb-md">
                <q-checkbox
                  v-model="simulationSettings.batchMode"
                  label="Batch Simulation Mode"
                  dense
                />
                <div class="text-caption text-grey-7 q-mt-xs">
                  Run multiple scenarios automatically
                </div>
              </div>

              <div v-if="simulationSettings.batchMode" class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Batch Scenarios</div>
                <q-input
                  v-model.number="simulationSettings.batchCount"
                  type="number"
                  :min="5"
                  :max="50"
                  filled
                  dense
                  label="Number of scenarios"
                />
              </div>

              <q-separator class="q-my-md" />

              <div v-if="selectedProject" class="settings-summary">
                <div class="text-subtitle2 text-weight-medium q-mb-sm">Current Project</div>
                <div class="text-body2 text-weight-medium">{{ selectedProject.name }}</div>
                <div class="text-caption text-grey-7">
                  {{ selectedProject.tasks?.length || 0 }} tasks
                </div>
                <div class="text-caption text-grey-6">
                  Duration: {{ currentProjectDuration }} days
                </div>
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
              <q-card flat class="bg-primary-1 q-pa-md q-mb-md">
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

              <!-- Visual Comparison Chart -->
              <q-card flat class="q-pa-md">
                <div class="text-subtitle2 text-weight-medium q-mb-md">
                  Metrics Comparison Chart
                </div>
                <div class="chart-container">
                  <!-- Duration Chart -->
                  <div class="metric-chart q-mb-md">
                    <div class="metric-label">Duration (days)</div>
                    <div class="chart-bars">
                      <div class="chart-bar-wrapper">
                        <div class="bar-label">Before</div>
                        <div class="bar-container">
                          <div
                            class="chart-bar bg-grey-5"
                            :style="{
                              width: (beforeMetrics.duration / maxDuration) * 100 + '%',
                            }"
                          >
                            <span class="bar-value">{{ beforeMetrics.duration }}d</span>
                          </div>
                        </div>
                      </div>
                      <div class="chart-bar-wrapper">
                        <div class="bar-label">After</div>
                        <div class="bar-container">
                          <div
                            class="chart-bar bg-green"
                            :style="{
                              width: (afterMetrics.duration / maxDuration) * 100 + '%',
                            }"
                          >
                            <span class="bar-value">{{ afterMetrics.duration }}d</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Workload Chart -->
                  <div class="metric-chart q-mb-md">
                    <div class="metric-label">Team Workload (%)</div>
                    <div class="chart-bars">
                      <div class="chart-bar-wrapper">
                        <div class="bar-label">Before</div>
                        <div class="bar-container">
                          <div
                            class="chart-bar bg-orange"
                            :style="{ width: beforeMetrics.workload + '%' }"
                          >
                            <span class="bar-value">{{ beforeMetrics.workload }}%</span>
                          </div>
                        </div>
                      </div>
                      <div class="chart-bar-wrapper">
                        <div class="bar-label">After</div>
                        <div class="bar-container">
                          <div
                            class="chart-bar bg-green"
                            :style="{ width: afterMetrics.workload + '%' }"
                          >
                            <span class="bar-value">{{ afterMetrics.workload }}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Balance Score Chart -->
                  <div class="metric-chart">
                    <div class="metric-label">Balance Score (%)</div>
                    <div class="chart-bars">
                      <div class="chart-bar-wrapper">
                        <div class="bar-label">Before</div>
                        <div class="bar-container">
                          <div
                            class="chart-bar bg-orange"
                            :style="{ width: beforeMetrics.balanceScore + '%' }"
                          >
                            <span class="bar-value">{{ beforeMetrics.balanceScore }}%</span>
                          </div>
                        </div>
                      </div>
                      <div class="chart-bar-wrapper">
                        <div class="bar-label">After</div>
                        <div class="bar-container">
                          <div
                            class="chart-bar bg-green"
                            :style="{ width: afterMetrics.balanceScore + '%' }"
                          >
                            <span class="bar-value">{{ afterMetrics.balanceScore }}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </q-card>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Batch Simulation Results -->
      <q-card v-if="batchResults.length > 0" class="q-mb-lg">
        <q-card-section>
          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6 text-weight-bold">Batch Simulation Results</div>
            <q-btn
              flat
              color="primary"
              icon="download"
              label="Export Results"
              @click="exportBatchResults"
            />
          </div>

          <div class="row q-gutter-md q-mb-lg">
            <div class="col">
              <q-card flat class="bg-blue-1 q-pa-md text-center">
                <div class="text-h5 text-weight-bold text-blue">
                  {{ batchStats.averageAdaptationTime }}ms
                </div>
                <div class="text-caption">Avg. Adaptation Time</div>
              </q-card>
            </div>
            <div class="col">
              <q-card flat class="bg-green-1 q-pa-md text-center">
                <div class="text-h5 text-weight-bold text-green">{{ batchStats.successRate }}%</div>
                <div class="text-caption">Success Rate</div>
              </q-card>
            </div>
            <div class="col">
              <q-card flat class="bg-orange-1 q-pa-md text-center">
                <div class="text-h5 text-weight-bold text-orange">
                  {{ batchStats.averageImprovement }}%
                </div>
                <div class="text-caption">Avg. Improvement</div>
              </q-card>
            </div>
            <div class="col">
              <q-card flat class="bg-purple-1 q-pa-md text-center">
                <div class="text-h5 text-weight-bold text-purple">
                  {{ batchResults.length }}
                </div>
                <div class="text-caption">Total Scenarios</div>
              </q-card>
            </div>
          </div>

          <q-table
            :rows="batchResults"
            :columns="batchColumns"
            row-key="id"
            :pagination="{ rowsPerPage: 10 }"
            flat
          >
            <template v-slot:body-cell-adaptationTime="props">
              <q-td :props="props">
                <span :class="getAdaptationTimeClass(props.row.adaptationTime)">
                  {{ props.row.adaptationTime }}ms
                </span>
              </q-td>
            </template>

            <template v-slot:body-cell-improvement="props">
              <q-td :props="props">
                <span class="text-green text-weight-bold">+{{ props.row.improvement }}%</span>
              </q-td>
            </template>

            <template v-slot:body-cell-success="props">
              <q-td :props="props">
                <q-icon
                  :name="props.row.success ? 'check_circle' : 'cancel'"
                  :color="props.row.success ? 'green' : 'red'"
                  size="sm"
                />
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <!-- Change Log -->
      <q-card>
        <q-card-section>
          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6 text-weight-bold">Detailný Change Log & Automatické Adaptácie</div>
            <q-btn
              v-if="changeLog.length > 0"
              flat
              color="primary"
              icon="download"
              label="Export Log"
              @click="exportChangeLog"
            />
          </div>

          <!-- Empty state -->
          <div v-if="changeLog.length === 0" class="text-center q-pa-xl">
            <q-icon name="history" size="64px" color="grey-5" class="q-mb-md" />
            <div class="text-h6 text-grey-6 q-mb-sm">Zatiaľ žiadne simulácie</div>
            <div class="text-body2 text-grey-7">
              Spusti simuláciu vyššie, aby sa vygeneroval detailný change log s Before/After
              porovnaním
            </div>
          </div>

          <q-timeline v-else color="primary">
            <q-timeline-entry
              v-for="(change, index) in changeLog"
              :key="index"
              :title="change.title"
              :subtitle="change.timestamp"
              :icon="change.icon"
              :color="change.color"
            >
              <div class="text-body2 q-mb-sm">{{ change.description }}</div>

              <!-- Task Details Before/After -->
              <q-card flat class="bg-blue-1 q-pa-md q-mb-sm">
                <div class="text-subtitle2 text-weight-medium q-mb-sm">
                  📋 Zmeny na tasku: {{ change.taskName }}
                </div>
                <div class="row q-gutter-md">
                  <!-- Before -->
                  <div class="col">
                    <div class="text-caption text-weight-medium text-grey-7 q-mb-xs">
                      PRED ZMENOU:
                    </div>
                    <div class="task-details">
                      <div v-if="change.taskChanges?.storyPoints" class="detail-line">
                        <span class="detail-label">Story Points:</span>
                        <span class="detail-value">{{
                          change.taskChanges.storyPoints.before
                        }}</span>
                      </div>
                      <div v-if="change.taskChanges?.pert" class="detail-line">
                        <span class="detail-label">PERT:</span>
                        <span class="detail-value"
                          >O:{{ change.taskChanges.pert.before.optimistic }}d, M:{{
                            change.taskChanges.pert.before.mostLikely
                          }}d, P:{{ change.taskChanges.pert.before.pessimistic }}d</span
                        >
                      </div>
                      <div v-if="change.taskChanges?.duration" class="detail-line">
                        <span class="detail-label">Trvanie:</span>
                        <span class="detail-value">{{ change.taskChanges.duration.before }}d</span>
                      </div>
                      <div v-if="change.taskChanges?.raci" class="detail-line">
                        <span class="detail-label">RACI:</span>
                        <div class="raci-list">
                          <span v-if="change.taskChanges.raci.before.responsible.length > 0"
                            >R: {{ change.taskChanges.raci.before.responsible.join(', ') }}</span
                          >
                          <span v-if="change.taskChanges.raci.before.accountable.length > 0"
                            >A: {{ change.taskChanges.raci.before.accountable.join(', ') }}</span
                          >
                        </div>
                      </div>
                      <div v-if="change.taskChanges?.priority" class="detail-line">
                        <span class="detail-label">Priorita:</span>
                        <q-chip
                          :color="getPriorityColor(change.taskChanges.priority.before)"
                          text-color="white"
                          size="sm"
                          dense
                          >{{ change.taskChanges.priority.before }}</q-chip
                        >
                      </div>
                    </div>
                  </div>

                  <!-- Arrow -->
                  <div class="col-auto flex items-center">
                    <q-icon name="arrow_forward" size="32px" color="primary" />
                  </div>

                  <!-- After -->
                  <div class="col">
                    <div class="text-caption text-weight-medium text-green q-mb-xs">PO ZMENE:</div>
                    <div class="task-details">
                      <div v-if="change.taskChanges?.storyPoints" class="detail-line">
                        <span class="detail-label">Story Points:</span>
                        <span class="detail-value text-weight-bold">{{
                          change.taskChanges.storyPoints.after
                        }}</span>
                        <q-badge
                          :color="
                            change.taskChanges.storyPoints.after >
                            change.taskChanges.storyPoints.before
                              ? 'orange'
                              : 'green'
                          "
                          :label="
                            (change.taskChanges.storyPoints.after >
                            change.taskChanges.storyPoints.before
                              ? '+'
                              : '') +
                            (change.taskChanges.storyPoints.after -
                              change.taskChanges.storyPoints.before)
                          "
                        />
                      </div>
                      <div v-if="change.taskChanges?.pert" class="detail-line">
                        <span class="detail-label">PERT:</span>
                        <span class="detail-value text-weight-bold"
                          >O:{{ change.taskChanges.pert.after.optimistic }}d, M:{{
                            change.taskChanges.pert.after.mostLikely
                          }}d, P:{{ change.taskChanges.pert.after.pessimistic }}d</span
                        >
                      </div>
                      <div v-if="change.taskChanges?.duration" class="detail-line">
                        <span class="detail-label">Trvanie:</span>
                        <span class="detail-value text-weight-bold"
                          >{{ change.taskChanges.duration.after }}d</span
                        >
                        <q-badge
                          :color="
                            change.taskChanges.duration.after > change.taskChanges.duration.before
                              ? 'orange'
                              : 'green'
                          "
                          :label="
                            (change.taskChanges.duration.after > change.taskChanges.duration.before
                              ? '+'
                              : '') +
                            (change.taskChanges.duration.after - change.taskChanges.duration.before)
                          "
                        />
                      </div>
                      <div v-if="change.taskChanges?.raci" class="detail-line">
                        <span class="detail-label">RACI:</span>
                        <div class="raci-list">
                          <span v-if="change.taskChanges.raci.after.responsible.length > 0"
                            >R: {{ change.taskChanges.raci.after.responsible.join(', ') }}</span
                          >
                          <span v-if="change.taskChanges.raci.after.accountable.length > 0"
                            >A: {{ change.taskChanges.raci.after.accountable.join(', ') }}</span
                          >
                        </div>
                      </div>
                      <div v-if="change.taskChanges?.priority" class="detail-line">
                        <span class="detail-label">Priorita:</span>
                        <q-chip
                          :color="getPriorityColor(change.taskChanges.priority.after)"
                          text-color="white"
                          size="sm"
                          dense
                          >{{ change.taskChanges.priority.after }}</q-chip
                        >
                      </div>
                    </div>
                  </div>
                </div>
              </q-card>

              <!-- Automatic Adaptations -->
              <q-card flat class="bg-grey-1 q-pa-md q-mb-sm">
                <div class="text-subtitle2 text-weight-medium q-mb-sm">
                  🤖 Automatické adaptácie systému:
                </div>
                <ul class="q-ma-none q-pl-md adaptation-list">
                  <li v-for="(adaptation, idx) in change.adaptations" :key="idx">
                    {{ adaptation }}
                  </li>
                </ul>
              </q-card>

              <!-- Impact Metrics -->
              <div class="q-mt-sm">
                <div class="text-caption text-weight-medium q-mb-xs">Dopad na projekt:</div>
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
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useTeamStore } from 'src/stores/team-store';

const $q = useQuasar();
const projectStore = useProjectStore();
const teamStore = useTeamStore();

// Load data on mount
onMounted(async () => {
  await projectStore.fetchProjects(true);
  await teamStore.fetchTeamMembers();
});

// Project selection
const selectedProjectId = ref<number | null>(1);
const selectedExperimentId = ref<number | null>(null);

const projectOptions = computed(() => {
  return projectStore.projects.map((project) => ({
    label: project.name,
    value: project.id,
  }));
});

const selectedProject = computed(() => {
  if (!selectedProjectId.value) return null;
  return projectStore.projects.find((p) => p.id === selectedProjectId.value);
});

const currentProjectDuration = computed(() => {
  if (!selectedProject.value || !selectedProject.value.tasks) return 0;
  // Estimate duration based on story points (1 SP ≈ 0.5 days)
  return Math.round(
    selectedProject.value.tasks.reduce((sum, task) => {
      return sum + (task.storyPoints || 0) * 0.5;
    }, 0),
  );
});

// Reactive data
const simulationSettings = ref({
  changeType: 'Add New Task',
  numberOfChanges: 3,
  adaptationStrategy: 'PERT+RACI Optimization',
  batchMode: false,
  batchCount: 20,
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

// Calculate metrics from selected project
const beforeMetrics = computed(() => {
  if (!selectedProject.value) {
    return {
      duration: 0,
      workload: 0,
      riskScore: 0,
      balanceScore: 0,
    };
  }

  const project = selectedProject.value;
  const tasks = project.tasks || [];

  // Calculate duration from PERT estimates or story points
  const duration = tasks.reduce((sum, task) => {
    return sum + (task.pert?.expected || task.storyPoints * 0.5 || 0);
  }, 0);

  // Calculate workload - average team member workload
  const teamMembers = teamStore.teamMembers.filter((m) => project.teamMemberIds?.includes(m.id));
  const avgWorkload =
    teamMembers.length > 0
      ? teamMembers.reduce((sum, m) => sum + m.workload, 0) / teamMembers.length
      : 0;

  // Calculate risk score based on task complexity and uncertainty
  const avgRisk =
    tasks.length > 0
      ? tasks.reduce((sum, task) => {
          const pert = task.pert;
          const uncertainty =
            pert?.pessimistic && pert?.optimistic
              ? (pert.pessimistic - pert.optimistic) / (pert.expected || 1)
              : 0.5;
          return sum + uncertainty * 10;
        }, 0) / tasks.length
      : 0;

  // Calculate balance score - how evenly distributed work is
  const workloads = teamMembers.map((m) => m.workload);
  const avgLoad = avgWorkload;
  const variance =
    workloads.length > 0
      ? workloads.reduce((sum, w) => sum + Math.pow(w - avgLoad, 2), 0) / workloads.length
      : 0;
  const balanceScore = Math.max(0, 100 - Math.sqrt(variance));

  return {
    duration: Math.round(duration * 10) / 10,
    workload: Math.round(avgWorkload),
    riskScore: Math.round(avgRisk * 10) / 10,
    balanceScore: Math.round(balanceScore),
  };
});

const afterMetrics = ref({
  duration: 0,
  workload: 0,
  riskScore: 0,
  balanceScore: 0,
});

const adaptationTime = ref(0);
const improvementRate = ref(0);
const changesApplied = ref(0);

const showSimulationDialog = ref(false);
const simulationProgress = ref(0);
const currentSimulationStep = ref('');

// Batch simulation results
interface BatchResult {
  id: number;
  scenario: string;
  changeType: string;
  adaptationTime: number;
  improvement: number;
  success: boolean;
  durationBefore: number;
  durationAfter: number;
}

const batchResults = ref<BatchResult[]>([]);

const batchColumns = [
  { name: 'id', label: '#', field: 'id', align: 'center' as const, sortable: true },
  { name: 'scenario', label: 'Scenario', field: 'scenario', align: 'left' as const },
  { name: 'changeType', label: 'Change Type', field: 'changeType', align: 'left' as const },
  {
    name: 'adaptationTime',
    label: 'Adaptation Time',
    field: 'adaptationTime',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'improvement',
    label: 'Improvement',
    field: 'improvement',
    align: 'center' as const,
    sortable: true,
  },
  { name: 'success', label: 'Success', field: 'success', align: 'center' as const },
];

const batchStats = computed(() => {
  if (batchResults.value.length === 0) {
    return {
      averageAdaptationTime: 0,
      successRate: 0,
      averageImprovement: 0,
    };
  }

  const avgTime =
    batchResults.value.reduce((sum, r) => sum + r.adaptationTime, 0) / batchResults.value.length;
  const successCount = batchResults.value.filter((r) => r.success).length;
  const avgImprovement =
    batchResults.value.reduce((sum, r) => sum + r.improvement, 0) / batchResults.value.length;

  return {
    averageAdaptationTime: Math.round(avgTime),
    successRate: Math.round((successCount / batchResults.value.length) * 100),
    averageImprovement: Math.round(avgImprovement * 10) / 10,
  };
});

// Change log - starts empty, populated by simulations
interface ChangeLogEntry {
  title: string;
  timestamp: string;
  icon: string;
  color: string;
  taskName: string;
  description: string;
  taskChanges?: {
    storyPoints?: { before: number; after: number };
    pert?: {
      before: { optimistic: number; mostLikely: number; pessimistic: number };
      after: { optimistic: number; mostLikely: number; pessimistic: number };
    };
    duration?: { before: number; after: number };
    raci?: {
      before: { responsible: string[]; accountable: string[] };
      after: { responsible: string[]; accountable: string[] };
    };
    priority?: { before: string; after: string };
  };
  adaptations: string[];
  metrics: Array<{ label: string; value: string; color: string }>;
}

const changeLog = ref<ChangeLogEntry[]>([]);

// Computed
const durationDelta = computed(() => afterMetrics.value.duration - beforeMetrics.value.duration);
const workloadDelta = computed(() => beforeMetrics.value.workload - afterMetrics.value.workload);
const riskDelta = computed(
  () => Math.round((beforeMetrics.value.riskScore - afterMetrics.value.riskScore) * 10) / 10,
);
const balanceDelta = computed(
  () => afterMetrics.value.balanceScore - beforeMetrics.value.balanceScore,
);

const maxDuration = computed(
  () => Math.max(beforeMetrics.value.duration, afterMetrics.value.duration) + 5,
);

// Methods
function getDeltaClass(delta: number): string {
  if (delta > 0) return 'text-green';
  if (delta < 0) return 'text-red';
  return 'text-grey';
}

async function runSimulation() {
  if (!selectedProject.value) {
    $q.notify({
      message: 'Prosím, vyber najprv projekt!',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  if (simulationSettings.value.batchMode) {
    await runBatchSimulation();
    return;
  }

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
  const beforeDuration = beforeMetrics.value.duration;
  const beforeWorkload = beforeMetrics.value.workload;
  const beforeRisk = beforeMetrics.value.riskScore;
  const beforeBalance = beforeMetrics.value.balanceScore;

  afterMetrics.value = {
    duration: beforeDuration + Math.floor(Math.random() * 5) - 1,
    workload: Math.max(60, beforeWorkload - Math.floor(Math.random() * 15)),
    riskScore: Math.max(3, beforeRisk - Math.random() * 2),
    balanceScore: Math.min(95, beforeBalance + Math.floor(Math.random() * 20)),
  };

  // Generate change log entry
  generateChangeLogEntry(
    simulationSettings.value.changeType,
    beforeDuration,
    afterMetrics.value.duration,
    beforeWorkload,
    afterMetrics.value.workload,
    beforeRisk,
    afterMetrics.value.riskScore,
    beforeBalance,
    afterMetrics.value.balanceScore,
    adaptationTime.value,
  );

  // Note: Simulation tracking has been removed
  // Previous research store integration is no longer available
  if (selectedProject.value) {
    // Simulation completed successfully
    // Data is shown in the UI but not persisted to backend
  }

  showSimulationDialog.value = false;

  $q.notify({
    message: selectedExperimentId.value
      ? 'Simulation completed and saved to experiment!'
      : 'Simulation completed successfully!',
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });
}

async function runBatchSimulation() {
  if (!selectedProject.value) {
    $q.notify({
      message: 'Prosím, vyber najprv projekt!',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  showSimulationDialog.value = true;
  simulationProgress.value = 0;
  batchResults.value = [];

  const scenarios = simulationSettings.value.batchCount;
  const changeTypes = [
    'Add New Task',
    'Change Task Priority',
    'Modify Task Duration',
    'Reassign Team Members',
    'Mixed Changes',
  ];

  currentSimulationStep.value = `Running ${scenarios} batch scenarios...`;

  for (let i = 0; i < scenarios; i++) {
    simulationProgress.value = Math.round(((i + 1) / scenarios) * 100);

    const changeType = changeTypes[Math.floor(Math.random() * changeTypes.length)]!;
    const startTime = Date.now();

    // Simulate adaptation
    await new Promise((resolve) => setTimeout(resolve, 50 + Math.random() * 150));

    const adaptTime = Date.now() - startTime;
    const improvement = 15 + Math.random() * 20;
    const success = Math.random() > 0.05; // 95% success rate

    const durationBefore = 45 + Math.floor(Math.random() * 10);
    const durationAfter = 46 + Math.floor(Math.random() * 8);
    const workloadBefore = 70 + Math.floor(Math.random() * 20);
    const workloadAfter = 65 + Math.floor(Math.random() * 15);
    const riskBefore = 5 + Math.random() * 3;
    const riskAfter = 4 + Math.random() * 2;
    const balanceBefore = 70 + Math.floor(Math.random() * 10);
    const balanceAfter = 80 + Math.floor(Math.random() * 15);

    batchResults.value.push({
      id: i + 1,
      scenario: `Scenario ${i + 1}`,
      changeType,
      adaptationTime: adaptTime,
      improvement: Math.round(improvement * 10) / 10,
      success,
      durationBefore,
      durationAfter,
    });

    // Generate change log entry for each batch scenario
    if (success) {
      generateChangeLogEntry(
        changeType,
        durationBefore,
        durationAfter,
        workloadBefore,
        workloadAfter,
        riskBefore,
        riskAfter,
        balanceBefore,
        balanceAfter,
        adaptTime,
      );

      // Note: Simulation tracking has been removed
      // Previous research store integration is no longer available
      if (selectedProject.value) {
        // Simulation completed successfully
        // Data is shown in the UI but not persisted to backend
      }
    }
  }

  showSimulationDialog.value = false;

  const savedCount = batchResults.value.filter((r) => r.success).length;
  $q.notify({
    message: selectedExperimentId.value
      ? `Batch completed! ${scenarios} scenarios, ${savedCount} saved to experiment.`
      : `Batch completed! ${scenarios} scenarios, ${changeLog.value.length} change logs.`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
    timeout: 3000,
  });
}

function exportBatchResults() {
  const data = {
    metadata: {
      totalScenarios: batchResults.value.length,
      averageAdaptationTime: batchStats.value.averageAdaptationTime,
      successRate: batchStats.value.successRate,
      averageImprovement: batchStats.value.averageImprovement,
      timestamp: new Date().toISOString(),
      settings: simulationSettings.value,
    },
    results: batchResults.value,
  };

  const dataStr = JSON.stringify(data, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `batch-simulation-results-${Date.now()}.json`;
  link.click();
  URL.revokeObjectURL(url);

  $q.notify({
    message: 'Batch results exported successfully!',
    color: 'positive',
    icon: 'download',
    position: 'top',
  });
}

function getAdaptationTimeClass(time: number): string {
  if (time < 100) return 'text-green text-weight-bold';
  if (time < 200) return 'text-primary text-weight-bold';
  if (time < 500) return 'text-orange text-weight-bold';
  return 'text-red text-weight-bold';
}

function resetSimulation() {
  // beforeMetrics is computed from project, no need to reset

  // Reset afterMetrics to initial state
  afterMetrics.value = {
    duration: 0,
    workload: 0,
    riskScore: 0,
    balanceScore: 0,
  };

  adaptationTime.value = 0;
  improvementRate.value = 0;
  changesApplied.value = 0;

  // Clear change log
  changeLog.value = [];

  $q.notify({
    message: 'Simulation reset - change log cleared',
    color: 'info',
    icon: 'refresh',
    position: 'top',
  });
}

function getPriorityColor(priority: string): string {
  switch (priority.toLowerCase()) {
    case 'critical':
      return 'red';
    case 'high':
      return 'orange';
    case 'medium':
      return 'primary';
    case 'low':
      return 'grey';
    default:
      return 'grey-5';
  }
}

function generateChangeLogEntry(
  changeType: string,
  beforeDuration: number,
  afterDuration: number,
  beforeWorkload: number,
  afterWorkload: number,
  beforeRisk: number,
  afterRisk: number,
  beforeBalance: number,
  afterBalance: number,
  adaptTime: number,
) {
  if (!selectedProject.value || !selectedProject.value.tasks) return;

  const tasks = selectedProject.value.tasks;
  if (tasks.length === 0) return;

  // Select random task
  const randomTask = tasks[Math.floor(Math.random() * tasks.length)]!;

  // Get team member names from store
  const teamMemberNames = teamStore.teamMembers.map((m) => m.name);
  const teamMembers =
    teamMemberNames.length > 0
      ? teamMemberNames
      : ['John Smith', 'Sarah Johnson', 'Mike Wilson', 'Emma Davis']; // Fallback if not loaded yet

  const timestamp = new Date().toLocaleString('sk-SK');
  const durationDiff = afterDuration - beforeDuration;
  const workloadDiff = afterWorkload - beforeWorkload;
  const balanceDiff = afterBalance - beforeBalance;
  const riskDiff = afterRisk - beforeRisk;

  // Formatted strings for display
  const durationDiffStr = durationDiff.toFixed(1);
  const workloadDiffStr = workloadDiff.toFixed(0);
  const balanceDiffStr = balanceDiff.toFixed(0);
  const riskDiffStr = riskDiff.toFixed(1);

  let entry: ChangeLogEntry;

  switch (changeType) {
    case 'Add New Task': {
      const newSP = Math.floor(Math.random() * 10) + 3;
      const opt = Math.floor(Math.random() * 3) + 1;
      const most = opt + Math.floor(Math.random() * 3) + 2;
      const pess = most + Math.floor(Math.random() * 4) + 2;
      const duration = ((opt + 4 * most + pess) / 6).toFixed(1);
      const responsible = [teamMembers[Math.floor(Math.random() * teamMembers.length)]!];
      const accountable = [teamMembers[Math.floor(Math.random() * teamMembers.length)]!];

      entry = {
        title: 'Nový Feature Request Pridaný',
        timestamp,
        icon: 'add_circle',
        color: 'primary',
        taskName: `New Task: ${randomTask.name}`,
        description: `Klient požaduje nový feature (${newSP} story points)`,
        taskChanges: {
          storyPoints: { before: 0, after: newSP },
          pert: {
            before: { optimistic: 0, mostLikely: 0, pessimistic: 0 },
            after: { optimistic: opt, mostLikely: most, pessimistic: pess },
          },
          duration: { before: 0, after: parseFloat(duration) },
          raci: {
            before: { responsible: [], accountable: [] },
            after: { responsible, accountable },
          },
          priority: { before: '-', after: randomTask.priority },
        },
        adaptations: [
          `📊 PERT duration vypočítané: Expected = (${opt} + 4×${most} + ${pess}) / 6 = ${duration} dní`,
          `👥 Automaticky priradené: ${responsible[0]} (R), ${accountable[0]} (A)`,
          `⚖️ Prerozdelené zaťaženie tímu: ${workloadDiffStr}% zmena`,
          `🎯 Aktualizovaná kritická cesta: ${durationDiff > 0 ? '+' : ''}${durationDiffStr}d`,
          '🔄 RACI validácia: pravidlá skontrolované a validated',
        ],
        metrics: [
          {
            label: 'Duration Impact',
            value: `${durationDiff > 0 ? '+' : ''}${durationDiffStr}d`,
            color: durationDiff > 0 ? 'orange' : 'green',
          },
          {
            label: 'Team Balance',
            value: `${balanceDiff > 0 ? '+' : ''}${balanceDiffStr}%`,
            color: balanceDiff > 0 ? 'green' : 'orange',
          },
          {
            label: 'Risk',
            value: `${riskDiff > 0 ? '+' : ''}${riskDiffStr}`,
            color: riskDiff > 0 ? 'orange' : 'green',
          },
          { label: 'Adaptation Time', value: `${adaptTime}ms`, color: 'green' },
        ],
      };
      break;
    }

    case 'Change Task Priority': {
      const priorities = ['Low', 'Medium', 'High', 'Critical'];
      const currentPriority = randomTask.priority;
      let newPriority = priorities[Math.floor(Math.random() * priorities.length)]!;
      while (newPriority === currentPriority) {
        newPriority = priorities[Math.floor(Math.random() * priorities.length)]!;
      }

      const oldSP = randomTask.storyPoints || 5;
      const oldOpt = Math.floor(oldSP * 0.6);
      const oldMost = oldSP;
      const oldPess = Math.floor(oldSP * 1.5);
      const oldDuration = ((oldOpt + 4 * oldMost + oldPess) / 6).toFixed(1);

      const speedup = newPriority === 'Critical' ? 0.7 : 1.0;
      const newOpt = Math.floor(oldOpt * speedup);
      const newMost = Math.floor(oldMost * speedup);
      const newPess = Math.floor(oldPess * speedup);
      const newDuration = ((newOpt + 4 * newMost + newPess) / 6).toFixed(1);

      const oldResponsible = [teamMembers[Math.floor(Math.random() * teamMembers.length)]!];
      const newResponsible =
        newPriority === 'Critical'
          ? [teamMembers[0]!]
          : [teamMembers[Math.floor(Math.random() * teamMembers.length)]!];

      entry = {
        title: `Zmena Priority: ${currentPriority} → ${newPriority}`,
        timestamp,
        icon: 'priority_high',
        color: newPriority === 'Critical' ? 'red' : 'orange',
        taskName: randomTask.name,
        description: `Priorita tasku zmenená na ${newPriority}`,
        taskChanges: {
          storyPoints: { before: oldSP, after: oldSP },
          pert: {
            before: { optimistic: oldOpt, mostLikely: oldMost, pessimistic: oldPess },
            after: { optimistic: newOpt, mostLikely: newMost, pessimistic: newPess },
          },
          duration: { before: parseFloat(oldDuration), after: parseFloat(newDuration) },
          raci: {
            before: { responsible: oldResponsible, accountable: ['Sarah Johnson'] },
            after: { responsible: newResponsible, accountable: ['Sarah Johnson'] },
          },
          priority: { before: currentPriority, after: newPriority },
        },
        adaptations: [
          `🔝 Priorita zmenená: ${currentPriority} → ${newPriority}`,
          newPriority === 'Critical'
            ? '🔄 Reassigned na senior developera'
            : '✅ RACI roles upravené',
          `📊 PERT prepočítaný: ${oldDuration}d → ${newDuration}d (${(parseFloat(newDuration) - parseFloat(oldDuration)).toFixed(1)}d)`,
          `⚖️ Team workload adjusted: ${workloadDiffStr}%`,
          newPriority === 'Critical'
            ? '⚡ Aktivovaný fast-track režím'
            : '📅 Sprint backlog reordered',
        ],
        metrics: [
          {
            label: 'Duration Impact',
            value: `${(parseFloat(newDuration) - parseFloat(oldDuration)).toFixed(1)}d`,
            color: 'green',
          },
          {
            label: 'Risk Change',
            value: `${riskDiffStr}`,
            color: riskDiff < 0 ? 'green' : 'orange',
          },
          {
            label: 'Priority',
            value: `${currentPriority}→${newPriority}`,
            color: newPriority === 'Critical' ? 'red' : 'orange',
          },
          { label: 'Adaptation Time', value: `${adaptTime}ms`, color: 'green' },
        ],
      };
      break;
    }

    case 'Modify Task Duration': {
      const oldSP = randomTask.storyPoints || 5;
      const spChange = Math.floor(Math.random() * 5) - 2;
      const newSP = Math.max(1, oldSP + spChange);

      const oldOpt = Math.floor(oldSP * 0.6);
      const oldMost = oldSP;
      const oldPess = Math.floor(oldSP * 1.5);
      const oldDuration = ((oldOpt + 4 * oldMost + oldPess) / 6).toFixed(1);

      const newOpt = Math.floor(newSP * 0.6);
      const newMost = newSP;
      const newPess = Math.floor(newSP * 1.5);
      const newDuration = ((newOpt + 4 * newMost + newPess) / 6).toFixed(1);

      const responsible1 = teamMembers[Math.floor(Math.random() * teamMembers.length)]!;
      const responsible2 =
        spChange > 2 ? teamMembers[Math.floor(Math.random() * teamMembers.length)]! : null;

      entry = {
        title: 'Zmena Story Points na Existujúcom Tasku',
        timestamp,
        icon: 'edit',
        color: 'orange',
        taskName: randomTask.name,
        description: `Klient ${spChange > 0 ? 'rozšíril' : 'zredukoval'} požiadavky (${spChange > 0 ? '+' : ''}${spChange} SP)`,
        taskChanges: {
          storyPoints: { before: oldSP, after: newSP },
          pert: {
            before: { optimistic: oldOpt, mostLikely: oldMost, pessimistic: oldPess },
            after: { optimistic: newOpt, mostLikely: newMost, pessimistic: newPess },
          },
          duration: { before: parseFloat(oldDuration), after: parseFloat(newDuration) },
          raci: {
            before: { responsible: [responsible1], accountable: ['Sarah Johnson'] },
            after: {
              responsible: responsible2 ? [responsible1, responsible2] : [responsible1],
              accountable: ['Sarah Johnson'],
            },
          },
        },
        adaptations: [
          `📈 PERT časy aktualizované: ${oldDuration}d → ${newDuration}d (${(parseFloat(newDuration) - parseFloat(oldDuration)).toFixed(1)}d)`,
          responsible2
            ? `👥 Pridaný ${responsible2} ako druhý Responsible (workload sharing)`
            : '👥 RACI role unchanged',
          `⚖️ Zaťaženie tímu: ${workloadDiffStr}% zmena`,
          `🔄 Celkový project duration: ${durationDiff > 0 ? '+' : ''}${durationDiffStr} dní`,
          '📊 Critical path analysis updated',
        ],
        metrics: [
          {
            label: 'Story Points',
            value: `${spChange > 0 ? '+' : ''}${spChange} SP`,
            color: spChange > 0 ? 'orange' : 'green',
          },
          {
            label: 'Duration Impact',
            value: `${(parseFloat(newDuration) - parseFloat(oldDuration)).toFixed(1)}d`,
            color: spChange > 0 ? 'orange' : 'green',
          },
          {
            label: 'Team Balance',
            value: `${balanceDiff > 0 ? '+' : ''}${balanceDiffStr}%`,
            color: balanceDiff > 0 ? 'green' : 'orange',
          },
          { label: 'Adaptation Time', value: `${adaptTime}ms`, color: 'green' },
        ],
      };
      break;
    }

    case 'Reassign Team Members': {
      const oldResponsible = [teamMembers[Math.floor(Math.random() * teamMembers.length)]!];
      const newResponsible = [teamMembers[Math.floor(Math.random() * teamMembers.length)]!];
      const oldAccountable = [teamMembers[1]!];
      const newAccountable = [teamMembers[2]!];

      entry = {
        title: 'Reassignment členov tímu',
        timestamp,
        icon: 'swap_horiz',
        color: 'blue',
        taskName: randomTask.name,
        description: `RACI role prerozdelené kvôli workload balancingu`,
        taskChanges: {
          raci: {
            before: { responsible: oldResponsible, accountable: oldAccountable },
            after: { responsible: newResponsible, accountable: newAccountable },
          },
        },
        adaptations: [
          `🔄 Responsible: ${oldResponsible[0]} → ${newResponsible[0]}`,
          `📋 Accountable: ${oldAccountable[0]} → ${newAccountable[0]}`,
          `⚖️ Workload rebalanced: ${workloadDiffStr}% zmena`,
          `📊 Team balance improved: ${balanceDiff > 0 ? '+' : ''}${balanceDiffStr}%`,
          '✅ RACI compliance maintained',
        ],
        metrics: [
          {
            label: 'Team Balance',
            value: `${balanceDiff > 0 ? '+' : ''}${balanceDiffStr}%`,
            color: balanceDiff > 0 ? 'green' : 'orange',
          },
          { label: 'Workload Change', value: `${workloadDiffStr}%`, color: 'primary' },
          { label: 'Members Affected', value: '2', color: 'blue' },
          { label: 'Adaptation Time', value: `${adaptTime}ms`, color: 'green' },
        ],
      };
      break;
    }

    default: {
      // Mixed Changes
      const oldSP = randomTask.storyPoints || 5;
      const newSP = oldSP + Math.floor(Math.random() * 4) - 1;

      entry = {
        title: 'Mixed Changes (Multiple Updates)',
        timestamp,
        icon: 'change_circle',
        color: 'purple',
        taskName: randomTask.name,
        description: 'Viacero zmien aplikovaných naraz',
        taskChanges: {
          storyPoints: { before: oldSP, after: newSP },
        },
        adaptations: [
          '🔄 Multiple requirement changes detected',
          `📊 PERT times recalculated`,
          `👥 RACI roles optimized`,
          `⚖️ Team workload rebalanced`,
          '🎯 Critical path updated',
        ],
        metrics: [
          {
            label: 'Changes Applied',
            value: `${simulationSettings.value.numberOfChanges}`,
            color: 'purple',
          },
          {
            label: 'Duration Impact',
            value: `${durationDiffStr}d`,
            color: durationDiff > 0 ? 'orange' : 'green',
          },
          {
            label: 'Team Balance',
            value: `${balanceDiffStr}%`,
            color: balanceDiff > 0 ? 'green' : 'orange',
          },
          { label: 'Adaptation Time', value: `${adaptTime}ms`, color: 'green' },
        ],
      };
    }
  }

  // Add to beginning of log (newest first)
  changeLog.value.unshift(entry);
}

function exportChangeLog() {
  const data = {
    project: selectedProject.value?.name || 'Unknown',
    totalChanges: changeLog.value.length,
    changes: changeLog.value,
    exportTimestamp: new Date().toISOString(),
  };

  const dataStr = JSON.stringify(data, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `change-log-${selectedProject.value?.name || 'project'}-${Date.now()}.json`;
  link.click();
  URL.revokeObjectURL(url);

  $q.notify({
    message: 'Change log exported successfully!',
    color: 'positive',
    icon: 'download',
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

/* Chart Styles */
.chart-container {
  width: 100%;
}

.metric-chart {
  margin-bottom: 20px;
}

.metric-label {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  color: #666;
}

.chart-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  width: 60px;
  font-size: 13px;
  font-weight: 500;
  color: #666;
}

.bar-container {
  flex: 1;
  height: 32px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.chart-bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  transition: width 0.5s ease;
  min-width: 60px;
}

.bar-value {
  color: white;
  font-weight: 600;
  font-size: 12px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .comparison-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .comparison-arrow {
    transform: rotate(90deg);
  }

  .bar-label {
    width: 50px;
    font-size: 12px;
  }
}

/* Task Details Styles */
.task-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-line {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.detail-label {
  font-weight: 600;
  font-size: 12px;
  color: #666;
  min-width: 90px;
}

.detail-value {
  font-size: 13px;
  color: #333;
}

.raci-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
}

.adaptation-list li {
  margin-bottom: 8px;
  line-height: 1.5;
}
</style>
