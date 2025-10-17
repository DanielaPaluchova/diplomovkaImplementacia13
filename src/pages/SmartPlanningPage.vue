<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Smart Planning</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">AI-powered project planning and optimization</p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="auto_fix_high"
            label="Auto Optimize"
            @click="autoOptimize"
          />
          <q-btn
            color="primary"
            icon="psychology"
            label="Generate Plan"
            @click="showGeneratePlanDialog = true"
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Planning Templates -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-4" v-for="template in planningTemplates" :key="template.id">
          <q-card class="template-card" @click="selectTemplate(template)">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon :name="template.icon" :color="template.color" size="32px" class="q-mr-sm" />
                <div class="col">
                  <div class="text-h6 text-weight-bold">{{ template.name }}</div>
                  <div class="text-caption text-grey-7">{{ template.category }}</div>
                </div>
              </div>

              <div class="text-body2 text-grey-7 q-mb-md">{{ template.description }}</div>

              <div class="row items-center">
                <q-chip
                  size="sm"
                  color="primary"
                  text-color="white"
                  :label="template.methodology"
                />
                <q-space />
                <div class="text-caption text-grey-6">{{ template.duration }}</div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- AI Recommendations -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">AI Planning Recommendations</div>

              <div class="recommendations-list">
                <div
                  v-for="recommendation in aiRecommendations"
                  :key="recommendation.id"
                  class="recommendation-item q-mb-md"
                >
                  <div class="row items-start">
                    <q-icon
                      :name="recommendation.icon"
                      :color="
                        recommendation.priority === 'high'
                          ? 'red'
                          : recommendation.priority === 'medium'
                            ? 'orange'
                            : 'green'
                      "
                      class="q-mr-sm q-mt-xs"
                    />
                    <div class="col">
                      <div class="text-weight-medium">{{ recommendation.title }}</div>
                      <div class="text-body2 text-grey-7 q-mb-sm">
                        {{ recommendation.description }}
                      </div>
                      <div class="row items-center">
                        <q-chip
                          :color="
                            recommendation.priority === 'high'
                              ? 'red'
                              : recommendation.priority === 'medium'
                                ? 'orange'
                                : 'green'
                          "
                          text-color="white"
                          size="sm"
                          :label="recommendation.priority + ' priority'"
                        />
                        <q-space />
                        <q-btn
                          flat
                          color="primary"
                          size="sm"
                          label="Apply"
                          @click="applyRecommendation(recommendation)"
                        />
                      </div>
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
              <div class="text-h6 text-weight-bold q-mb-md">Planning Metrics</div>

              <div class="metrics-list">
                <div class="metric-item q-mb-md">
                  <div class="text-caption text-grey-7">Success Rate</div>
                  <div class="text-h4 text-weight-bold text-green">94%</div>
                  <q-linear-progress
                    :value="0.94"
                    color="green"
                    style="height: 4px"
                    class="q-mt-xs"
                  />
                </div>

                <div class="metric-item q-mb-md">
                  <div class="text-caption text-grey-7">Time Optimization</div>
                  <div class="text-h4 text-weight-bold text-primary">23%</div>
                  <q-linear-progress
                    :value="0.23"
                    color="primary"
                    style="height: 4px"
                    class="q-mt-xs"
                  />
                </div>

                <div class="metric-item q-mb-md">
                  <div class="text-caption text-grey-7">Resource Efficiency</div>
                  <div class="text-h4 text-weight-bold text-orange">87%</div>
                  <q-linear-progress
                    :value="0.87"
                    color="orange"
                    style="height: 4px"
                    class="q-mt-xs"
                  />
                </div>

                <div class="metric-item">
                  <div class="text-caption text-grey-7">Cost Reduction</div>
                  <div class="text-h4 text-weight-bold text-blue">15%</div>
                  <q-linear-progress
                    :value="0.15"
                    color="blue"
                    style="height: 4px"
                    class="q-mt-xs"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Planning Wizard -->
      <q-card>
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Smart Planning Wizard</div>
          <div class="text-center q-pa-xl">
            <q-icon name="psychology" size="96px" color="primary" class="q-mb-md" />
            <div class="text-h5 text-grey-7 q-mb-md">AI-Powered Planning</div>
            <div class="text-body1 text-grey-6 q-mb-lg">
              Let AI analyze your requirements and generate optimized project plans
            </div>
            <q-btn
              color="primary"
              size="lg"
              icon="auto_awesome"
              label="Start Smart Planning"
              @click="showGeneratePlanDialog = true"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Generate Plan Dialog -->
    <q-dialog v-model="showGeneratePlanDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Generate AI-Powered Plan</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-stepper v-model="planningStep" vertical color="primary" animated>
            <q-step :name="1" title="Project Details" icon="info" :done="planningStep > 1">
              <q-input v-model="planData.name" label="Project Name" filled class="q-mb-md" />
              <q-input
                v-model="planData.description"
                label="Description"
                type="textarea"
                filled
                rows="3"
                class="q-mb-md"
              />
              <q-select
                v-model="planData.methodology"
                :options="['Agile', 'Waterfall', 'Hybrid']"
                label="Methodology"
                filled
              />

              <q-stepper-navigation>
                <q-btn @click="planningStep = 2" color="primary" label="Continue" />
              </q-stepper-navigation>
            </q-step>

            <q-step :name="2" title="Requirements" icon="list" :done="planningStep > 2">
              <q-input
                v-model="planData.requirements"
                label="Project Requirements"
                type="textarea"
                filled
                rows="5"
                class="q-mb-md"
              />
              <q-select
                v-model="planData.complexity"
                :options="['Low', 'Medium', 'High']"
                label="Complexity"
                filled
              />

              <q-stepper-navigation>
                <q-btn
                  flat
                  @click="planningStep = 1"
                  color="primary"
                  label="Back"
                  class="q-mr-sm"
                />
                <q-btn @click="planningStep = 3" color="primary" label="Continue" />
              </q-stepper-navigation>
            </q-step>

            <q-step :name="3" title="Constraints" icon="schedule" :done="planningStep > 3">
              <div class="row q-gutter-md q-mb-md">
                <div class="col">
                  <q-input
                    v-model="planData.deadline"
                    label="Deadline"
                    filled
                    mask="date"
                    :rules="['date']"
                  >
                    <template v-slot:append>
                      <q-icon name="event" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                          <q-date v-model="planData.deadline">
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
                    v-model.number="planData.budget"
                    label="Budget (€)"
                    type="number"
                    filled
                  />
                </div>
              </div>
              <q-input v-model.number="planData.teamSize" label="Team Size" type="number" filled />

              <q-stepper-navigation>
                <q-btn
                  flat
                  @click="planningStep = 2"
                  color="primary"
                  label="Back"
                  class="q-mr-sm"
                />
                <q-btn
                  @click="generatePlan"
                  color="primary"
                  label="Generate Plan"
                  :loading="isGenerating"
                />
              </q-stepper-navigation>
            </q-step>
          </q-stepper>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelPlanGeneration" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useMockDataStore } from 'stores/mock-data';
import { format } from 'date-fns';

const mockDataStore = useMockDataStore();

// Interfaces
interface PlanningTemplate {
  id: number;
  name: string;
  category: string;
  description: string;
  icon: string;
  color: string;
  methodology: string;
  duration: string;
}

interface AIRecommendation {
  id: number;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  icon: string;
  impact: string;
}

// Reactive data
const showGeneratePlanDialog = ref(false);
const planningStep = ref(1);
const isGenerating = ref(false);

const planningTemplates = ref([
  {
    id: 1,
    name: 'Agile Sprint Planning',
    category: 'Agile',
    description: 'AI-optimized sprint planning with velocity prediction and capacity allocation',
    icon: 'timeline',
    color: 'primary',
    methodology: 'Scrum',
    duration: '2-4 weeks',
  },
  {
    id: 2,
    name: 'Waterfall Project Plan',
    category: 'Traditional',
    description:
      'Sequential project planning with dependency management and critical path analysis',
    icon: 'waterfall_chart',
    color: 'blue',
    methodology: 'Waterfall',
    duration: '3-6 months',
  },
  {
    id: 3,
    name: 'Hybrid Planning',
    category: 'Mixed',
    description: 'Combines agile and waterfall approaches for optimal project delivery',
    icon: 'merge_type',
    color: 'green',
    methodology: 'Hybrid',
    duration: '1-3 months',
  },
  {
    id: 4,
    name: 'Lean Startup',
    category: 'Innovation',
    description: 'MVP-focused planning with rapid iteration and customer feedback loops',
    icon: 'rocket_launch',
    color: 'orange',
    methodology: 'Lean',
    duration: '2-8 weeks',
  },
]);

const aiRecommendations = ref([
  {
    id: 1,
    title: 'Optimize Sprint Duration',
    description:
      'Based on team velocity, consider reducing sprint length from 3 weeks to 2 weeks for better predictability',
    priority: 'high' as const,
    icon: 'schedule',
    impact: 'Improve delivery predictability by 23%',
  },
  {
    id: 2,
    title: 'Redistribute Tasks',
    description:
      'Mike Wilson is overallocated. Redistribute 2 tasks to Emma Davis to balance workload',
    priority: 'medium' as const,
    icon: 'balance',
    impact: 'Reduce team stress and improve quality',
  },
  {
    id: 3,
    title: 'Add Buffer Time',
    description: 'Historical data suggests adding 15% buffer time for integration tasks',
    priority: 'low' as const,
    icon: 'timer',
    impact: 'Reduce delivery risk by 18%',
  },
  {
    id: 4,
    title: 'Parallel Development',
    description: 'Frontend and backend tasks can be parallelized to reduce overall timeline',
    priority: 'high' as const,
    icon: 'call_split',
    impact: 'Reduce project duration by 3 weeks',
  },
]);

const planData = reactive({
  name: '',
  description: '',
  methodology: '',
  requirements: '',
  complexity: '',
  deadline: format(new Date(), 'yyyy/MM/dd'),
  budget: 0,
  teamSize: 5,
});

// Methods
function selectTemplate(template: PlanningTemplate) {
  console.log('Selected template:', template.name);
}

function applyRecommendation(recommendation: AIRecommendation) {
  console.log('Applying recommendation:', recommendation.title);
}

function autoOptimize() {
  console.log('Auto-optimizing current plans...');
}

function generatePlan() {
  isGenerating.value = true;

  // Simulate AI plan generation
  setTimeout(() => {
    isGenerating.value = false;
    showGeneratePlanDialog.value = false;
    console.log('Generated plan for:', planData.name);

    // Reset form
    Object.assign(planData, {
      name: '',
      description: '',
      methodology: '',
      requirements: '',
      complexity: '',
      deadline: format(new Date(), 'yyyy/MM/dd'),
      budget: 0,
      teamSize: 5,
    });
    planningStep.value = 1;
  }, 3000);
}

function cancelPlanGeneration() {
  showGeneratePlanDialog.value = false;
  planningStep.value = 1;
  Object.assign(planData, {
    name: '',
    description: '',
    methodology: '',
    requirements: '',
    complexity: '',
    deadline: format(new Date(), 'yyyy/MM/dd'),
    budget: 0,
    teamSize: 5,
  });
}

onMounted(() => {
  mockDataStore.initializeData();
});
</script>

<style scoped>
.template-card {
  transition: all 0.2s ease;
  cursor: pointer;
  height: 100%;
}

.template-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.recommendation-item {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  border-left: 4px solid transparent;
}

.recommendation-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.metric-item {
  text-align: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}
</style>
