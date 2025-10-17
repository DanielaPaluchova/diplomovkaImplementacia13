<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Method Comparisons</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Compare different project management methodologies and approaches
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="add_chart"
            label="New Comparison"
            @click="showNewComparisonDialog = true"
          />
          <q-btn
            color="primary"
            icon="compare"
            label="Compare Methods"
            @click="showCompareDialog = true"
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Comparison Categories -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-4" v-for="category in comparisonCategories" :key="category.id">
          <q-card class="category-card" @click="selectCategory(category)">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon :name="category.icon" :color="category.color" size="32px" class="q-mr-sm" />
                <div class="col">
                  <div class="text-h6 text-weight-bold">{{ category.name }}</div>
                  <div class="text-caption text-grey-7">{{ category.description }}</div>
                </div>
              </div>

              <div class="comparison-stats">
                <div class="row q-gutter-md">
                  <div class="col text-center">
                    <div class="text-h6 text-weight-bold text-primary">
                      {{ category.comparisons }}
                    </div>
                    <div class="text-caption text-grey-7">Comparisons</div>
                  </div>
                  <div class="col text-center">
                    <div class="text-h6 text-weight-bold text-green">{{ category.methods }}</div>
                    <div class="text-caption text-grey-7">Methods</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Active Comparisons -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Active Comparisons</div>

          <div class="row q-gutter-lg">
            <div class="col-12 col-lg-8">
              <div class="comparison-matrix">
                <div class="matrix-header">
                  <div class="method-cell">Method</div>
                  <div class="criteria-cell" v-for="criteria in comparisonCriteria" :key="criteria">
                    {{ criteria }}
                  </div>
                </div>

                <div v-for="method in comparisonMethods" :key="method.id" class="matrix-row">
                  <div class="method-cell">
                    <div class="method-info">
                      <div class="text-weight-bold">{{ method.name }}</div>
                      <div class="text-caption text-grey-7">{{ method.type }}</div>
                    </div>
                  </div>
                  <div v-for="score in method.scores" :key="score.criteria" class="score-cell">
                    <div class="score-value" :class="getScoreColor(score.value)">
                      {{ score.value }}/10
                    </div>
                    <q-linear-progress
                      :value="score.value / 10"
                      :color="getScoreColorName(score.value)"
                      style="height: 4px"
                      class="q-mt-xs"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div class="col-12 col-lg-4">
              <div class="comparison-summary">
                <div class="text-subtitle1 text-weight-bold q-mb-md">Summary</div>

                <div class="winner-card q-mb-md">
                  <div class="text-center">
                    <q-icon name="emoji_events" color="amber" size="32px" class="q-mb-sm" />
                    <div class="text-h6 text-weight-bold">Overall Winner</div>
                    <div class="text-subtitle1 text-primary">{{ overallWinner.name }}</div>
                    <div class="text-caption text-grey-7">
                      Score: {{ overallWinner.totalScore }}/50
                    </div>
                  </div>
                </div>

                <div class="category-winners">
                  <div class="text-subtitle2 text-weight-medium q-mb-sm">Category Winners</div>
                  <div
                    v-for="winner in categoryWinners"
                    :key="winner.category"
                    class="winner-item q-mb-sm"
                  >
                    <div class="row items-center">
                      <q-icon name="star" color="amber" size="16px" class="q-mr-sm" />
                      <div class="col">
                        <div class="text-weight-medium">{{ winner.category }}</div>
                        <div class="text-caption text-grey-7">{{ winner.method }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Comparison Results -->
      <div class="row q-gutter-lg">
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Methodology Effectiveness</div>

              <div class="effectiveness-chart">
                <div
                  v-for="method in methodEffectiveness"
                  :key="method.name"
                  class="effectiveness-item q-mb-md"
                >
                  <div class="row items-center q-mb-sm">
                    <div class="col">
                      <div class="text-weight-medium">{{ method.name }}</div>
                    </div>
                    <div class="col-auto">
                      <div
                        class="text-weight-bold"
                        :class="getEffectivenessColor(method.effectiveness)"
                      >
                        {{ method.effectiveness }}%
                      </div>
                    </div>
                  </div>
                  <q-linear-progress
                    :value="method.effectiveness / 100"
                    :color="getEffectivenessColorName(method.effectiveness)"
                    style="height: 8px"
                  />
                  <div class="row q-gutter-md q-mt-xs text-caption text-grey-7">
                    <span>Projects: {{ method.projects }}</span>
                    <span>Success Rate: {{ method.successRate }}%</span>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Comparison Insights</div>

              <div class="insights-list">
                <div
                  v-for="insight in comparisonInsights"
                  :key="insight.id"
                  class="insight-item q-mb-md"
                >
                  <div class="row items-start">
                    <q-icon
                      :name="insight.icon"
                      :color="
                        insight.type === 'positive'
                          ? 'green'
                          : insight.type === 'negative'
                            ? 'red'
                            : 'primary'
                      "
                      class="q-mr-sm q-mt-xs"
                    />
                    <div class="col">
                      <div class="text-weight-medium">{{ insight.title }}</div>
                      <div class="text-body2 text-grey-7">{{ insight.description }}</div>
                      <div class="text-caption text-grey-6 q-mt-xs">
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
    </div>

    <!-- New Comparison Dialog -->
    <q-dialog v-model="showNewComparisonDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Create New Comparison</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newComparison.name"
            label="Comparison Name"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Name is required']"
          />

          <q-select
            v-model="newComparison.category"
            :options="['Methodology', 'Tools', 'Frameworks', 'Processes']"
            label="Category"
            filled
            class="q-mb-md"
          />

          <q-select
            v-model="newComparison.methods"
            :options="availableMethods"
            label="Methods to Compare"
            multiple
            use-chips
            filled
            class="q-mb-md"
          />

          <q-select
            v-model="newComparison.criteria"
            :options="availableCriteria"
            label="Comparison Criteria"
            multiple
            use-chips
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelNewComparison" />
          <q-btn
            color="primary"
            label="Create Comparison"
            @click="createComparison"
            :disable="!newComparison.name"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Compare Methods Dialog -->
    <q-dialog v-model="showCompareDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Quick Method Comparison</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="row q-gutter-md">
            <div class="col">
              <q-select
                v-model="quickCompare.method1"
                :options="availableMethods"
                label="Method 1"
                filled
              />
            </div>
            <div class="col">
              <q-select
                v-model="quickCompare.method2"
                :options="availableMethods"
                label="Method 2"
                filled
              />
            </div>
          </div>

          <q-select
            v-model="quickCompare.criteria"
            :options="availableCriteria"
            label="Focus Area"
            filled
            class="q-mt-md"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelQuickCompare" />
          <q-btn
            color="primary"
            label="Compare"
            @click="performQuickCompare"
            :disable="!quickCompare.method1 || !quickCompare.method2"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useMockDataStore } from 'stores/mock-data';

const mockDataStore = useMockDataStore();

// Interfaces
interface ComparisonCategory {
  id: number;
  name: string;
  description: string;
  icon: string;
  color: string;
  comparisons: number;
  methods: number;
}

// Reactive data
const showNewComparisonDialog = ref(false);
const showCompareDialog = ref(false);

const comparisonCategories = ref([
  {
    id: 1,
    name: 'Agile vs Waterfall',
    description: 'Traditional methodology comparison',
    icon: 'compare',
    color: 'primary',
    comparisons: 5,
    methods: 8,
  },
  {
    id: 2,
    name: 'Planning Techniques',
    description: 'PERT, CPM, and Gantt comparisons',
    icon: 'timeline',
    color: 'green',
    comparisons: 3,
    methods: 6,
  },
  {
    id: 3,
    name: 'Risk Management',
    description: 'Risk assessment methodologies',
    icon: 'warning',
    color: 'orange',
    comparisons: 4,
    methods: 7,
  },
  {
    id: 4,
    name: 'Team Management',
    description: 'Team organization approaches',
    icon: 'group',
    color: 'blue',
    comparisons: 2,
    methods: 5,
  },
]);

const comparisonCriteria = ['Flexibility', 'Speed', 'Quality', 'Cost', 'Risk'];

const comparisonMethods = ref([
  {
    id: 1,
    name: 'Agile/Scrum',
    type: 'Iterative',
    scores: [
      { criteria: 'Flexibility', value: 9 },
      { criteria: 'Speed', value: 8 },
      { criteria: 'Quality', value: 7 },
      { criteria: 'Cost', value: 7 },
      { criteria: 'Risk', value: 8 },
    ],
  },
  {
    id: 2,
    name: 'Waterfall',
    type: 'Sequential',
    scores: [
      { criteria: 'Flexibility', value: 4 },
      { criteria: 'Speed', value: 6 },
      { criteria: 'Quality', value: 8 },
      { criteria: 'Cost', value: 8 },
      { criteria: 'Risk', value: 6 },
    ],
  },
  {
    id: 3,
    name: 'Kanban',
    type: 'Continuous',
    scores: [
      { criteria: 'Flexibility', value: 9 },
      { criteria: 'Speed', value: 7 },
      { criteria: 'Quality', value: 7 },
      { criteria: 'Cost', value: 8 },
      { criteria: 'Risk', value: 7 },
    ],
  },
  {
    id: 4,
    name: 'Lean',
    type: 'Efficiency',
    scores: [
      { criteria: 'Flexibility', value: 7 },
      { criteria: 'Speed', value: 9 },
      { criteria: 'Quality', value: 8 },
      { criteria: 'Cost', value: 9 },
      { criteria: 'Risk', value: 7 },
    ],
  },
]);

const methodEffectiveness = ref([
  { name: 'Agile/Scrum', effectiveness: 87, projects: 45, successRate: 89 },
  { name: 'Kanban', effectiveness: 82, projects: 32, successRate: 85 },
  { name: 'Lean', effectiveness: 79, projects: 28, successRate: 92 },
  { name: 'Waterfall', effectiveness: 74, projects: 38, successRate: 78 },
  { name: 'Hybrid', effectiveness: 85, projects: 22, successRate: 86 },
]);

const comparisonInsights = ref([
  {
    id: 1,
    title: 'Agile Shows Superior Adaptability',
    description: 'Agile methodologies demonstrate 40% better adaptability to changing requirements',
    type: 'positive',
    icon: 'trending_up',
    confidence: 92,
  },
  {
    id: 2,
    title: 'Waterfall Excels in Predictability',
    description:
      'Waterfall provides more predictable timelines and budgets for well-defined projects',
    type: 'neutral',
    icon: 'schedule',
    confidence: 87,
  },
  {
    id: 3,
    title: 'Hybrid Approaches Gaining Traction',
    description: 'Combining methodologies shows 25% improvement in project success rates',
    type: 'positive',
    icon: 'merge_type',
    confidence: 78,
  },
  {
    id: 4,
    title: 'Tool Integration Challenges',
    description: 'Methodology switching often faces tool compatibility issues',
    type: 'negative',
    icon: 'warning',
    confidence: 84,
  },
]);

const newComparison = reactive({
  name: '',
  category: '',
  methods: [],
  criteria: [],
});

const quickCompare = reactive({
  method1: '',
  method2: '',
  criteria: '',
});

const availableMethods = [
  'Agile/Scrum',
  'Waterfall',
  'Kanban',
  'Lean',
  'DevOps',
  'Six Sigma',
  'PRINCE2',
  'Critical Chain',
];

const availableCriteria = [
  'Flexibility',
  'Speed',
  'Quality',
  'Cost Effectiveness',
  'Risk Management',
  'Team Satisfaction',
  'Stakeholder Engagement',
  'Documentation',
  'Scalability',
  'Maintenance',
];

// Computed
const overallWinner = computed(() => {
  const totals = comparisonMethods.value.map((method) => ({
    name: method.name,
    totalScore: method.scores.reduce((sum, score) => sum + score.value, 0),
  }));
  return totals.reduce((max, current) => (current.totalScore > max.totalScore ? current : max));
});

const categoryWinners = computed(() => {
  return comparisonCriteria.map((criteria) => {
    const winner = comparisonMethods.value.reduce((max, method) => {
      const score = method.scores.find((s) => s.criteria === criteria)?.value || 0;
      const maxScore = max.scores.find((s) => s.criteria === criteria)?.value || 0;
      return score > maxScore ? method : max;
    });
    return {
      category: criteria,
      method: winner.name,
    };
  });
});

// Methods
function selectCategory(category: ComparisonCategory) {
  console.log('Selected category:', category.name);
}

function getScoreColor(score: number): string {
  if (score >= 8) return 'text-green';
  if (score >= 6) return 'text-orange';
  return 'text-red';
}

function getScoreColorName(score: number): string {
  if (score >= 8) return 'green';
  if (score >= 6) return 'orange';
  return 'red';
}

function getEffectivenessColor(effectiveness: number): string {
  if (effectiveness >= 80) return 'text-green';
  if (effectiveness >= 70) return 'text-orange';
  return 'text-red';
}

function getEffectivenessColorName(effectiveness: number): string {
  if (effectiveness >= 80) return 'green';
  if (effectiveness >= 70) return 'orange';
  return 'red';
}

function createComparison() {
  console.log('Creating comparison:', newComparison);
  cancelNewComparison();
}

function cancelNewComparison() {
  showNewComparisonDialog.value = false;
  Object.assign(newComparison, {
    name: '',
    category: '',
    methods: [],
    criteria: [],
  });
}

function performQuickCompare() {
  console.log('Performing quick comparison:', quickCompare);
  cancelQuickCompare();
}

function cancelQuickCompare() {
  showCompareDialog.value = false;
  Object.assign(quickCompare, {
    method1: '',
    method2: '',
    criteria: '',
  });
}

onMounted(() => {
  mockDataStore.initializeData();
});
</script>

<style scoped>
.category-card {
  transition: all 0.2s ease;
  cursor: pointer;
  height: 100%;
}

.category-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.comparison-matrix {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.matrix-header {
  display: flex;
  background: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
}

.matrix-row {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.method-cell {
  width: 150px;
  min-width: 150px;
  padding: 16px;
  border-right: 1px solid #e0e0e0;
  background: #fafafa;
}

.criteria-cell {
  flex: 1;
  padding: 16px;
  text-align: center;
  font-weight: 600;
  border-right: 1px solid #e0e0e0;
}

.score-cell {
  flex: 1;
  padding: 16px;
  text-align: center;
  border-right: 1px solid #e0e0e0;
}

.score-value {
  font-weight: bold;
  font-size: 14px;
}

.method-info {
  text-align: left;
}

.comparison-summary {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.winner-card {
  padding: 16px;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 8px;
  border: 1px solid #ffc107;
}

.winner-item {
  padding: 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

.effectiveness-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.insight-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}
</style>
