<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Experiments</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            A/B testing and experimental research management
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="analytics"
            label="View Results"
            @click="showResultsDialog = true"
          />
          <q-btn
            color="primary"
            icon="science"
            label="New Experiment"
            @click="showNewExperimentDialog = true"
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Stats Cards -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-primary-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-primary">{{ experiments.length }}</div>
                  <div class="text-caption text-grey-7">Total Experiments</div>
                </div>
                <div class="col-auto">
                  <q-icon name="science" size="32px" class="text-primary" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_up" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">+3</span>
                <span class="text-caption text-grey-7 q-ml-xs">this quarter</span>
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
                    {{ runningExperiments.length }}
                  </div>
                  <div class="text-caption text-grey-7">Running</div>
                </div>
                <div class="col-auto">
                  <q-icon name="play_circle" size="32px" class="text-blue" />
                </div>
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
                    {{ completedExperiments.length }}
                  </div>
                  <div class="text-caption text-grey-7">Completed</div>
                </div>
                <div class="col-auto">
                  <q-icon name="check_circle" size="32px" class="text-green" />
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
          <q-card class="stat-card bg-orange-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-orange">{{ successRate }}%</div>
                  <div class="text-caption text-grey-7">Success Rate</div>
                </div>
                <div class="col-auto">
                  <q-icon name="trending_up" size="32px" class="text-orange" />
                </div>
              </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_up" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">+12%</span>
                <span class="text-caption text-grey-7 q-ml-xs">vs last quarter</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Experiment Status Overview -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Experiment Timeline</div>
              <div class="experiment-timeline">
                <div class="timeline-container">
                  <div
                    v-for="experiment in experiments"
                    :key="experiment.id"
                    class="timeline-item"
                    :class="`timeline-${experiment.status}`"
                  >
                    <div class="timeline-content">
                      <div class="text-weight-medium">{{ experiment.name }}</div>
                      <div class="text-caption text-grey-7">
                        {{ formatDateRange(experiment.startDate, experiment.endDate) }}
                      </div>
                      <q-chip
                        :color="getStatusColor(experiment.status)"
                        text-color="white"
                        size="sm"
                        :label="experiment.status"
                        class="q-mt-xs"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Methodology Distribution</div>
              <div class="methodology-chart">
                <div
                  v-for="method in methodologyStats"
                  :key="method.name"
                  class="method-item q-mb-md"
                >
                  <div class="row items-center q-mb-xs">
                    <div class="col">
                      <div class="text-weight-medium">{{ method.name }}</div>
                    </div>
                    <div class="col-auto">
                      <div class="text-caption text-grey-7">{{ method.count }}</div>
                    </div>
                  </div>
                  <q-linear-progress
                    :value="method.count / experiments.length"
                    :color="method.color"
                    style="height: 8px"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Experiments Grid -->
      <div class="row q-gutter-lg">
        <div
          class="col-12 col-md-6 col-xl-4"
          v-for="experiment in experiments"
          :key="experiment.id"
        >
          <q-card class="experiment-card" :class="`border-${getStatusColor(experiment.status)}`">
            <q-card-section>
              <div class="row items-start q-mb-md">
                <div class="col">
                  <div class="text-h6 text-weight-bold">{{ experiment.name }}</div>
                  <div class="text-caption text-grey-7">{{ experiment.methodology }}</div>
                </div>
                <q-chip
                  :color="getStatusColor(experiment.status)"
                  text-color="white"
                  size="sm"
                  :icon="getStatusIcon(experiment.status)"
                  :label="experiment.status"
                />
              </div>

              <div class="text-body2 text-grey-8 q-mb-md">{{ experiment.description }}</div>

              <q-card flat class="bg-grey-1 q-mb-md">
                <q-card-section class="q-pa-sm">
                  <div class="text-caption text-grey-7">Hypothesis</div>
                  <div class="text-body2">{{ experiment.hypothesis }}</div>
                </q-card-section>
              </q-card>

              <div class="row q-gutter-md q-mb-md">
                <div class="col">
                  <div class="text-caption text-grey-7">Duration</div>
                  <div class="text-weight-medium">
                    {{ getDuration(experiment.startDate, experiment.endDate) }} days
                  </div>
                </div>
                <div class="col">
                  <div class="text-caption text-grey-7">Participants</div>
                  <div class="text-weight-medium">{{ experiment.participants }}</div>
                </div>
              </div>

              <!-- Results (if completed) -->
              <div v-if="experiment.results" class="results-section q-mt-md">
                <q-separator class="q-mb-md" />
                <div class="text-subtitle2 text-weight-medium q-mb-sm">Results</div>
                <div class="row q-gutter-md">
                  <div class="col">
                    <div class="text-caption text-grey-7">Success</div>
                    <q-icon
                      :name="experiment.results.success ? 'check_circle' : 'cancel'"
                      :color="experiment.results.success ? 'green' : 'red'"
                      size="20px"
                    />
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Improvement</div>
                    <div
                      class="text-weight-medium"
                      :class="experiment.results.improvement > 0 ? 'text-green' : 'text-red'"
                    >
                      {{ experiment.results.improvement > 0 ? '+' : ''
                      }}{{ experiment.results.improvement }}%
                    </div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Confidence</div>
                    <div class="text-weight-medium">{{ experiment.results.confidence }}%</div>
                  </div>
                </div>
              </div>

              <!-- Progress (if running) -->
              <div v-else-if="experiment.status === 'running'" class="q-mt-md">
                <q-separator class="q-mb-md" />
                <div class="text-subtitle2 text-weight-medium q-mb-sm">Progress</div>
                <q-linear-progress
                  :value="getExperimentProgress(experiment)"
                  color="primary"
                  style="height: 6px"
                />
                <div class="text-caption text-grey-7 q-mt-xs">
                  {{ Math.round(getExperimentProgress(experiment) * 100) }}% complete
                </div>
              </div>
            </q-card-section>

            <q-card-actions align="right">
              <q-btn
                flat
                color="secondary"
                label="View Details"
                @click="viewExperimentDetails(experiment)"
              />
              <q-btn
                v-if="experiment.status === 'planning'"
                flat
                color="primary"
                label="Start"
                @click="startExperiment(experiment)"
              />
              <q-btn
                v-else-if="experiment.status === 'running'"
                flat
                color="orange"
                label="Stop"
                @click="stopExperiment(experiment)"
              />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </div>

    <!-- New Experiment Dialog -->
    <q-dialog v-model="showNewExperimentDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Create New Experiment</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newExperiment.name"
            label="Experiment Name"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Name is required']"
          />

          <q-input
            v-model="newExperiment.description"
            label="Description"
            type="textarea"
            filled
            rows="3"
            class="q-mb-md"
          />

          <q-input
            v-model="newExperiment.hypothesis"
            label="Hypothesis"
            type="textarea"
            filled
            rows="2"
            class="q-mb-md"
            hint="What do you expect to achieve?"
          />

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select
                v-model="newExperiment.methodology"
                :options="methodologyOptions"
                label="Methodology"
                filled
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="newExperiment.participants"
                label="Expected Participants"
                type="number"
                filled
              />
            </div>
          </div>

          <div class="row q-gutter-md">
            <div class="col">
              <q-input
                v-model="newExperiment.startDate"
                label="Start Date"
                filled
                mask="date"
                :rules="['date']"
              >
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="newExperiment.startDate">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
            <div class="col">
              <q-input
                v-model="newExperiment.endDate"
                label="End Date"
                filled
                mask="date"
                :rules="['date']"
              >
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="newExperiment.endDate">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelNewExperiment" />
          <q-btn
            color="primary"
            label="Create Experiment"
            @click="createExperiment"
            :disable="!newExperiment.name"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Results Overview Dialog -->
    <q-dialog v-model="showResultsDialog" maximized>
      <q-card>
        <q-bar class="bg-primary text-white">
          <q-space />
          <div class="text-weight-bold">Experiment Results Overview</div>
          <q-space />
          <q-btn dense flat icon="close" @click="showResultsDialog = false" />
        </q-bar>

        <q-card-section class="q-pa-lg">
          <div class="text-center q-pa-xl">
            <q-icon name="analytics" size="96px" color="grey-5" class="q-mb-md" />
            <div class="text-h5 text-grey-7 q-mb-md">Detailed Analytics</div>
            <div class="text-body1 text-grey-6">
              Comprehensive experiment results and statistical analysis would be displayed here
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useMockDataStore, type Experiment } from 'stores/mock-data';
import { format, differenceInDays } from 'date-fns';

const mockDataStore = useMockDataStore();

// Reactive data
const showNewExperimentDialog = ref(false);
const showResultsDialog = ref(false);

const newExperiment = reactive({
  name: '',
  description: '',
  hypothesis: '',
  methodology: 'A/B Testing',
  participants: 50,
  startDate: '',
  endDate: '',
});

const methodologyOptions = [
  'A/B Testing',
  'Controlled Experiment',
  'Before/After Study',
  'Comparative Study',
];

// Computed
const experiments = computed(() => mockDataStore.experiments);

const runningExperiments = computed(() => experiments.value.filter((e) => e.status === 'running'));

const completedExperiments = computed(() =>
  experiments.value.filter((e) => e.status === 'completed'),
);

const successRate = computed(() => {
  const completed = completedExperiments.value;
  if (completed.length === 0) return 0;
  const successful = completed.filter((e) => e.results?.success).length;
  return Math.round((successful / completed.length) * 100);
});

const methodologyStats = computed(() => {
  const stats: Record<string, number> = {};
  experiments.value.forEach((e) => {
    stats[e.methodology] = (stats[e.methodology] || 0) + 1;
  });

  const colors = ['primary', 'green', 'orange', 'blue', 'purple'];
  return Object.entries(stats).map(([name, count], index) => ({
    name,
    count,
    color: colors[index % colors.length],
  }));
});

// Methods
function getStatusColor(status: string): string {
  switch (status) {
    case 'planning':
      return 'grey';
    case 'running':
      return 'blue';
    case 'completed':
      return 'green';
    case 'cancelled':
      return 'red';
    default:
      return 'grey';
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'planning':
      return 'schedule';
    case 'running':
      return 'play_circle';
    case 'completed':
      return 'check_circle';
    case 'cancelled':
      return 'cancel';
    default:
      return 'circle';
  }
}

function formatDateRange(startDate: Date, endDate: Date): string {
  return `${format(startDate, 'MMM dd')} - ${format(endDate, 'MMM dd, yyyy')}`;
}

function getDuration(startDate: Date, endDate: Date): number {
  return differenceInDays(endDate, startDate);
}

function getExperimentProgress(experiment: Experiment): number {
  const now = new Date();
  const total = differenceInDays(experiment.endDate, experiment.startDate);
  const elapsed = differenceInDays(now, experiment.startDate);
  return Math.max(0, Math.min(1, elapsed / total));
}

function viewExperimentDetails(experiment: Experiment) {
  console.log('View experiment details:', experiment);
}

function startExperiment(experiment: Experiment) {
  console.log('Start experiment:', experiment);
  // Update status in real implementation
}

function stopExperiment(experiment: Experiment) {
  console.log('Stop experiment:', experiment);
  // Update status in real implementation
}

function createExperiment() {
  console.log('Creating experiment:', newExperiment);
  showNewExperimentDialog.value = false;
  cancelNewExperiment();
}

function cancelNewExperiment() {
  Object.assign(newExperiment, {
    name: '',
    description: '',
    hypothesis: '',
    methodology: 'A/B Testing',
    participants: 50,
    startDate: '',
    endDate: '',
  });
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

.experiment-card {
  transition: all 0.2s ease;
  height: 100%;
}

.experiment-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.border-grey {
  border-left: 4px solid #9e9e9e;
}

.border-blue {
  border-left: 4px solid #2196f3;
}

.border-green {
  border-left: 4px solid #4caf50;
}

.border-red {
  border-left: 4px solid #f44336;
}

.experiment-timeline {
  height: 300px;
  overflow-y: auto;
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-item {
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #e0e0e0;
}

.timeline-planning {
  border-left-color: #9e9e9e;
  background: rgba(158, 158, 158, 0.05);
}

.timeline-running {
  border-left-color: #2196f3;
  background: rgba(33, 150, 243, 0.05);
}

.timeline-completed {
  border-left-color: #4caf50;
  background: rgba(76, 175, 80, 0.05);
}

.timeline-cancelled {
  border-left-color: #f44336;
  background: rgba(244, 67, 54, 0.05);
}

.results-section {
  background: rgba(76, 175, 80, 0.05);
  padding: 12px;
  border-radius: 8px;
}
</style>
