<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Risk Prediction</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            AI-powered risk assessment and predictive analytics
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="refresh"
            label="Refresh Analysis"
            @click="refreshAnalysis"
          />
          <q-btn color="primary" icon="warning" label="Run Risk Scan" @click="runRiskScan" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Risk Overview -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="risk-card bg-red-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-red">{{ riskMetrics.critical }}</div>
                  <div class="text-caption text-grey-7">Critical Risks</div>
                </div>
                <div class="col-auto">
                  <q-icon name="error" size="32px" class="text-red" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="risk-card bg-orange-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-orange">{{ riskMetrics.high }}</div>
                  <div class="text-caption text-grey-7">High Risks</div>
                </div>
                <div class="col-auto">
                  <q-icon name="warning" size="32px" class="text-orange" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="risk-card bg-yellow-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-amber">{{ riskMetrics.medium }}</div>
                  <div class="text-caption text-grey-7">Medium Risks</div>
                </div>
                <div class="col-auto">
                  <q-icon name="info" size="32px" class="text-amber" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="risk-card bg-green-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-green">{{ riskMetrics.low }}</div>
                  <div class="text-caption text-grey-7">Low Risks</div>
                </div>
                <div class="col-auto">
                  <q-icon name="check_circle" size="32px" class="text-green" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Risk Analysis -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-lg-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Active Risk Analysis</div>

              <q-table
                :rows="activeRisks"
                :columns="riskColumns"
                row-key="id"
                :pagination="{ rowsPerPage: 10 }"
              >
                <template v-slot:body-cell-severity="props">
                  <q-td :props="props">
                    <q-chip
                      :color="getSeverityColor(props.value)"
                      text-color="white"
                      size="sm"
                      :label="props.value"
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-probability="props">
                  <q-td :props="props">
                    <div class="row items-center">
                      <q-linear-progress
                        :value="props.value / 100"
                        :color="getProbabilityColor(props.value)"
                        style="width: 60px; height: 6px"
                        class="q-mr-sm"
                      />
                      <span>{{ props.value }}%</span>
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-actions="props">
                  <q-td :props="props">
                    <q-btn
                      flat
                      round
                      dense
                      icon="visibility"
                      color="primary"
                      @click="viewRiskDetails(props.row)"
                    >
                      <q-tooltip>View Details</q-tooltip>
                    </q-btn>
                    <q-btn
                      flat
                      round
                      dense
                      icon="build"
                      color="orange"
                      @click="createMitigation(props.row)"
                    >
                      <q-tooltip>Create Mitigation</q-tooltip>
                    </q-btn>
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-lg-4">
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Risk Trends</div>
              <div class="chart-placeholder text-center q-pa-lg">
                <q-icon name="trending_up" size="48px" color="orange" class="q-mb-md" />
                <div class="text-body2 text-grey-6">Risk trend analysis chart</div>
                <div class="q-mt-md">
                  <div class="trend-item q-mb-sm">
                    <div class="row items-center">
                      <q-icon name="trending_up" color="red" size="16px" class="q-mr-sm" />
                      <span class="col">Critical risks increased 12%</span>
                    </div>
                  </div>
                  <div class="trend-item q-mb-sm">
                    <div class="row items-center">
                      <q-icon name="trending_down" color="green" size="16px" class="q-mr-sm" />
                      <span class="col">Medium risks decreased 8%</span>
                    </div>
                  </div>
                  <div class="trend-item">
                    <div class="row items-center">
                      <q-icon name="trending_flat" color="blue" size="16px" class="q-mr-sm" />
                      <span class="col">Overall trend stable</span>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">AI Predictions</div>
              <div class="predictions-list">
                <div
                  v-for="prediction in aiPredictions"
                  :key="prediction.id"
                  class="prediction-item q-mb-md"
                >
                  <div class="row items-start">
                    <q-icon
                      :name="prediction.icon"
                      :color="
                        prediction.confidence > 80
                          ? 'green'
                          : prediction.confidence > 60
                            ? 'orange'
                            : 'red'
                      "
                      class="q-mr-sm q-mt-xs"
                    />
                    <div class="col">
                      <div class="text-weight-medium">{{ prediction.title }}</div>
                      <div class="text-body2 text-grey-7 q-mb-xs">{{ prediction.description }}</div>
                      <div class="row items-center">
                        <span class="text-caption">Confidence: {{ prediction.confidence }}%</span>
                        <q-space />
                        <span class="text-caption text-grey-6">{{ prediction.timeframe }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Mitigation Strategies -->
      <q-card>
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Recommended Mitigation Strategies</div>

          <div class="row q-gutter-lg">
            <div
              class="col-12 col-md-6 col-lg-4"
              v-for="strategy in mitigationStrategies"
              :key="strategy.id"
            >
              <div class="mitigation-card">
                <div class="row items-center q-mb-md">
                  <q-icon
                    :name="strategy.icon"
                    :color="
                      strategy.priority === 'high'
                        ? 'red'
                        : strategy.priority === 'medium'
                          ? 'orange'
                          : 'green'
                    "
                    size="24px"
                    class="q-mr-sm"
                  />
                  <div class="col">
                    <div class="text-weight-bold">{{ strategy.title }}</div>
                    <div class="text-caption text-grey-7">{{ strategy.category }}</div>
                  </div>
                </div>

                <div class="text-body2 text-grey-7 q-mb-md">{{ strategy.description }}</div>

                <div class="row items-center q-mb-sm">
                  <span class="text-caption">Effectiveness:</span>
                  <q-space />
                  <q-linear-progress
                    :value="strategy.effectiveness / 100"
                    color="primary"
                    style="width: 80px; height: 4px"
                  />
                  <span class="text-caption q-ml-xs">{{ strategy.effectiveness }}%</span>
                </div>

                <div class="row items-center">
                  <span class="text-caption">Cost: {{ strategy.cost }}</span>
                  <q-space />
                  <q-btn
                    size="sm"
                    color="primary"
                    flat
                    label="Implement"
                    @click="implementStrategy(strategy)"
                  />
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMockDataStore } from 'stores/mock-data';

const mockDataStore = useMockDataStore();

// Interfaces
interface Risk {
  id: number;
  title: string;
  project: string;
  category: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  probability: number;
  impact: 'High' | 'Medium' | 'Low';
  description: string;
}

interface MitigationStrategy {
  id: number;
  title: string;
  category: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  effectiveness: number;
  cost: string;
  icon: string;
}

// Reactive data
const riskMetrics = ref({
  critical: 2,
  high: 5,
  medium: 8,
  low: 12,
});

const activeRisks = ref([
  {
    id: 1,
    title: 'Data Migration Delays',
    project: 'E-commerce Platform',
    category: 'Schedule',
    severity: 'Critical',
    probability: 85,
    impact: 'High',
    description: 'Complex data migration may cause significant delays',
  },
  {
    id: 2,
    title: 'Budget Overrun',
    project: 'Mobile App',
    category: 'Financial',
    severity: 'High',
    probability: 70,
    impact: 'Medium',
    description: 'Current spending rate suggests budget overrun risk',
  },
  {
    id: 3,
    title: 'Key Developer Unavailable',
    project: 'AI Chatbot',
    category: 'Resource',
    severity: 'High',
    probability: 45,
    impact: 'High',
    description: 'Lead developer may be unavailable during critical phase',
  },
  {
    id: 4,
    title: 'Third-party API Changes',
    project: 'Data Migration',
    category: 'Technical',
    severity: 'Medium',
    probability: 60,
    impact: 'Medium',
    description: 'External API provider announced breaking changes',
  },
]);

const aiPredictions = ref([
  {
    id: 1,
    title: 'Schedule Slip Risk',
    description: 'Project likely to slip by 2-3 weeks based on current velocity',
    confidence: 87,
    timeframe: 'Next 2 weeks',
    icon: 'schedule',
  },
  {
    id: 2,
    title: 'Team Burnout Risk',
    description: 'High workload may lead to team burnout and quality issues',
    confidence: 72,
    timeframe: 'Next month',
    icon: 'psychology',
  },
  {
    id: 3,
    title: 'Integration Issues',
    description: 'Complex integrations may cause technical difficulties',
    confidence: 65,
    timeframe: 'Next sprint',
    icon: 'integration_instructions',
  },
]);

const mitigationStrategies = ref([
  {
    id: 1,
    title: 'Add Buffer Time',
    category: 'Schedule Management',
    description: 'Add 20% buffer time to critical path activities',
    priority: 'high' as const,
    effectiveness: 85,
    cost: 'Low',
    icon: 'schedule',
  },
  {
    id: 2,
    title: 'Cross-train Team Members',
    category: 'Resource Management',
    description: 'Train backup resources for critical roles',
    priority: 'medium' as const,
    effectiveness: 75,
    cost: 'Medium',
    icon: 'school',
  },
  {
    id: 3,
    title: 'Implement Daily Standups',
    category: 'Communication',
    description: 'Increase communication frequency to catch issues early',
    priority: 'medium' as const,
    effectiveness: 70,
    cost: 'Low',
    icon: 'groups',
  },
  {
    id: 4,
    title: 'Create Contingency Plan',
    category: 'Planning',
    description: 'Develop alternative approaches for high-risk activities',
    priority: 'high' as const,
    effectiveness: 90,
    cost: 'Medium',
    icon: 'alt_route',
  },
  {
    id: 5,
    title: 'Increase Testing Coverage',
    category: 'Quality Assurance',
    description: 'Add automated tests to reduce integration risks',
    priority: 'medium' as const,
    effectiveness: 80,
    cost: 'High',
    icon: 'bug_report',
  },
  {
    id: 6,
    title: 'External Consultant',
    category: 'Resource Augmentation',
    description: 'Bring in specialist consultant for critical areas',
    priority: 'low' as const,
    effectiveness: 85,
    cost: 'High',
    icon: 'person_add',
  },
]);

const riskColumns = [
  { name: 'title', label: 'Risk Title', field: 'title', align: 'left' as const, sortable: true },
  { name: 'project', label: 'Project', field: 'project', align: 'left' as const },
  { name: 'category', label: 'Category', field: 'category', align: 'left' as const },
  { name: 'severity', label: 'Severity', field: 'severity', align: 'center' as const },
  { name: 'probability', label: 'Probability', field: 'probability', align: 'center' as const },
  { name: 'impact', label: 'Impact', field: 'impact', align: 'center' as const },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' as const },
];

// Methods
function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'Critical':
      return 'red';
    case 'High':
      return 'orange';
    case 'Medium':
      return 'amber';
    case 'Low':
      return 'green';
    default:
      return 'grey';
  }
}

function getProbabilityColor(probability: number): string {
  if (probability >= 80) return 'red';
  if (probability >= 60) return 'orange';
  if (probability >= 40) return 'amber';
  return 'green';
}

function viewRiskDetails(risk: Risk) {
  console.log('Viewing risk details:', risk.title);
}

function createMitigation(risk: Risk) {
  console.log('Creating mitigation for:', risk.title);
}

function implementStrategy(strategy: MitigationStrategy) {
  console.log('Implementing strategy:', strategy.title);
}

function refreshAnalysis() {
  console.log('Refreshing risk analysis...');
}

function runRiskScan() {
  console.log('Running comprehensive risk scan...');
}

onMounted(() => {
  mockDataStore.initializeData();
});
</script>

<style scoped>
.risk-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.risk-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart-placeholder {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.prediction-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.mitigation-card {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  height: 100%;
}

.trend-item {
  padding: 4px 0;
}
</style>
